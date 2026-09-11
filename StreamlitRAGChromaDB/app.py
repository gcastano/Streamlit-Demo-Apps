# ==========================================
# IMPORTACIÓN DE LIBRERÍAS Y HERRAMIENTAS
# ==========================================

# ==========================================
# GUÍA DE INSTALACIÓN DE LIBRERÍAS (Para YouTube / Alumnos):
# Ejecuta el siguiente comando en tu terminal para instalar las dependencias:
# pip install streamlit chromadb markitdown langchain-text-splitters langchain-chroma langchain-mistralai langchain-core
#
# EXPLICACIÓN DE LIBRERÍAS UTILIZADAS:
# - streamlit: Framework para crear interfaces gráficas interactivas en Python web rápidamente sin usar HTML/CSS.
# - os: Librería nativa de Python para interactuar con el sistema operativo (ej. borrar archivos temporales).
# - chromadb: Base de datos vectorial (Vector DB) de código abierto para almacenar y buscar embeddings (vectores de datos).
# - tempfile: Librería nativa de Python para crear archivos y directorios temporales de forma segura.
# - markitdown: Herramienta reciente respaldada por Microsoft para convertir múltiples formatos (PDF, Word, etc.) a Markdown limpio.
# - langchain_text_splitters: Utilidad de LangChain para dividir (chunking) textos largos en fragmentos más pequeños.
# - langchain_chroma: Integración de LangChain específica para interactuar con bases de datos ChromaDB.
# - langchain_mistralai: Integración oficial de LangChain para conectarse con la API de modelos de Mistral AI.
# - langchain_core: El núcleo de LangChain que maneja componentes como Prompts, Runnables (para cadenas de ejecución) y Parsers.
# ==========================================

import streamlit as st
import os
import chromadb
import tempfile
from markitdown import MarkItDown
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_mistralai import MistralAIEmbeddings, ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# ==========================================
# 1. Configuración inicial de la Interfaz
# ==========================================
# Aquí definimos el diseño general de nuestra aplicación web con Streamlit
st.set_page_config(
    page_title="RAG Educativo con ChromaDB y Mistral",
    page_icon=":material/psychology:",
    layout="wide"
)

# ==========================================
# 2. Funciones Utilitarias Compartidas
# ==========================================

def extraer_texto_de_documento(archivo_subido):
    """
    Extrae el contenido textual de un archivo cargado en la memoria y lo convierte a formato Markdown.

    Esta función toma un archivo binario subido a través de Streamlit, crea un archivo temporal
    en el disco (ya que MarkItDown requiere rutas físicas), extrae su contenido y luego
    elimina el archivo temporal para no llenar el almacenamiento.

    Parámetros:
    ----------
    archivo_subido : UploadedFile
        Un objeto de archivo de Streamlit que contiene el documento subido por el usuario.

    Retorna:
    -------
    str
        El contenido completo del documento transformado en texto plano (Markdown).
    """
    md = MarkItDown()
    extension = archivo_subido.name.split(".")[-1]
    
    # Manejo de almacenamiento temporal para procesar el archivo físico
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{extension}") as archivo_temporal:
        archivo_temporal.write(archivo_subido.read())
        ruta_temporal = archivo_temporal.name
    try:
        resultado = md.convert(ruta_temporal)
        return resultado.text_content
    finally:
        # Aseguramos de eliminar la memoria residual sin importar si hubo un error o no
        os.remove(ruta_temporal)


def formatear_documentos_con_metadatos(lista_documentos):
    """
    Formatea una lista de objetos Document recuperados de la base de datos vectorial
    en un solo bloque de texto continuo para inyectar en el Prompt del modelo de lenguaje.

    Se extraen los metadatos (como el nombre del archivo de origen) y se concatenan con
    el texto para que la Inteligencia Artificial sepa exactamente de dónde provino la información.

    Parámetros:
    ----------
    lista_documentos : list[Document]
        Lista de documentos recuperados por LangChain desde ChromaDB.

    Retorna:
    -------
    str
        Cadena de texto estructurada con etiquetas de [Fuente] y el contenido original.
    """
    textos = []
    # Iteramos sobre los documentos recuperados para darles formato de texto plano
    for doc in lista_documentos:
        metadata_segura = doc.metadata or {}
        # Usamos .get() de diccionarios Python para evitar errores si no existe la llave
        fuente = metadata_segura.get("archivo_fuente", "Desconocido")
        textos.append(f"[Fuente del fragmento: {fuente}]\n{doc.page_content}")
    # Se unifica todo mediante dobles saltos de línea para facilitar la lectura del LLM
    return "\n\n".join(textos)


# ==========================================
# 3. Inicialización del Estado Compartido
# ==========================================
# Leemos la API Key una sola vez y la guardamos en session_state (memoria del navegador)
# para que ambas páginas puedan acceder sin repetir el bloque try/except.
if "clave_api_mistral" not in st.session_state:
    try:
        st.session_state.clave_api_mistral = st.secrets["MISTRAL_API_KEY"]
    except KeyError:
        st.session_state.clave_api_mistral = None

# ==========================================
# 4. Sidebar: API Key + Configuración ChromaDB
# ==========================================
with st.sidebar:
    st.header(":material/settings: Configuración")

    # Validación visual del estado de la clave API
    if st.session_state.clave_api_mistral:
        st.success("API Key cargada desde secrets.", icon=":material/check_circle:")
    else:
        st.error(
            "No se encontró `MISTRAL_API_KEY` en `.streamlit/secrets.toml`.",
            icon=":material/error:"
        )
        st.stop()  # Detiene la ejecución de la app si no hay clave

    st.divider()

    with st.expander(":material/database: Configuración Avanzada de ChromaDB"):
        # Selección del modo de Base de Datos Vectorial
        modo_chroma = st.radio(
            "Modo de conexión:",
            ["Local (PersistentClient)", "Servidor (HttpClient)"],
            help="Local guarda los datos en carpeta local. Servidor se conecta a un Chroma HTTP separado."
        )

        if modo_chroma == "Local (PersistentClient)":
            # Cliente persistente: crea/usa una base de datos en la carpeta local './chroma_db'
            st.session_state.cliente_chroma = chromadb.PersistentClient(path="./chroma_db")
            st.caption("Almacenando en carpeta local: `./chroma_db`")
        else:
            # Cliente Servidor: Permite arquitecturas donde la DB está en un docker o servidor remoto
            st.info(
                "**¿Cómo levantar el servidor?**\n\n"
                "Abre una nueva terminal y ejecuta:\n"
                "```bash\nchroma run --path ./chroma_data --port 8000\n```\n"
                "Esto iniciará ChromaDB como un servicio independiente.",
                icon=":material/lightbulb:"
            )
            host_chroma = st.text_input("Host del Servidor Chroma", value="localhost")
            puerto_chroma = st.number_input("Puerto del Servidor", value=8000, step=1)
            try:
                st.session_state.cliente_chroma = chromadb.HttpClient(host=host_chroma, port=puerto_chroma)
                st.caption(f"Conectado a `http://{host_chroma}:{puerto_chroma}`")
            except Exception:
                st.error("No se pudo conectar al servidor de ChromaDB.", icon=":material/error:")
                st.stop()


# ==========================================
# 5. Definición de Páginas como Funciones
# ==========================================

def pagina_gestionar():
    """
    Página 1: Gestión de documentos y colecciones en ChromaDB.

    Esta interfaz permite a los usuarios:
    1. Subir archivos de distintos formatos.
    2. Convertirlos a texto y segmentarlos (chunking).
    3. Convertir cada segmento a vectores semánticos (embeddings).
    4. Guardarlos en una base de datos (colección).
    5. Visualizar estadísticas (transformación de datos sobre metadatos).
    6. Eliminar colecciones existentes.
    """
    cliente_chroma = st.session_state.cliente_chroma
    clave_api_mistral = st.session_state.clave_api_mistral

    st.title(":material/folder_open: Gestionar Documentos")
    st.write("Sube documentos para procesarlos y convertirlos en conocimiento matemático útil para el chatbot.")

    # Obtenemos las colecciones actuales en la base de datos
    colecciones_actuales = cliente_chroma.list_collections()
    nombres_colecciones = [c.name for c in colecciones_actuales]

    columna_izquierda, columna_derecha = st.columns(2)

    # --- Columna Izquierda: Vectorizar nuevo documento ---
    with columna_izquierda:
        st.subheader(":material/add_circle: Vectorizar Nuevo Documento")
        nombre_nueva_coleccion = st.text_input("Nombre de la nueva colección (ej: manual_rrhh):").strip()
        archivos_subidos = st.file_uploader(
            "Sube uno o más documentos (PDF, DOCX, PPTX, XLSX...)",
            type=["pdf", "docx", "pptx", "xlsx", "csv", "html", "txt"],
            accept_multiple_files=True
        )

        if st.button("Procesar y Guardar en Base de Datos"):
            if not nombre_nueva_coleccion or not archivos_subidos:
                st.error("Proporciona un nombre y sube al menos un documento.", icon=":material/error:")
            elif " " in nombre_nueva_coleccion:
                st.error("El nombre de la colección no debe contener espacios.", icon=":material/error:")
            else:
                with st.spinner("Procesando documentos, extrayendo texto y calculando embeddings..."):
                    try:
                        todos_fragmentos = []
                        todas_metadatas = []
                        # Dividir el texto en fragmentos (chunks) de 1000 caracteres.
                        # El "chunk_overlap=200" permite que los fragmentos compartan algo de texto,
                        # evitando que una frase se corte a la mitad de forma perjudicial.
                        divisor_texto = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

                        for archivo in archivos_subidos:
                            # Paso A: Extraer texto usando nuestra función que implementa MarkItDown
                            texto_crudo = extraer_texto_de_documento(archivo)
                            # Paso B: Chunking del documento
                            fragmentos = divisor_texto.split_text(texto_crudo)
                            todos_fragmentos.extend(fragmentos)
                            # Paso B.2: Añadir Metadata (fundamental para saber la fuente al recuperar)
                            todas_metadatas.extend([{"archivo_fuente": archivo.name} for _ in fragmentos])

                        # Paso C: Iniciar el modelo de embeddings de Mistral (convierte texto a números)
                        modelo_embeddings = MistralAIEmbeddings(mistral_api_key=clave_api_mistral)

                        # Paso D: Persistir/Guardar los vectores de conocimiento en ChromaDB
                        Chroma.from_texts(
                            texts=todos_fragmentos,
                            metadatas=todas_metadatas,
                            embedding=modelo_embeddings,
                            collection_name=nombre_nueva_coleccion,
                            client=cliente_chroma
                        )
                        st.success(
                            f"¡Completado! {len(todos_fragmentos)} fragmentos de "
                            f"{len(archivos_subidos)} documento(s) guardados en '{nombre_nueva_coleccion}'.",
                            icon=":material/check_circle:"
                        )
                        st.rerun() # Refresca la interfaz
                    except Exception as e:
                        st.error(f"Error al procesar los archivos: {e}", icon=":material/error:")

    # --- Columna Derecha: Eliminar colección ---
    with columna_derecha:
        st.subheader(":material/delete: Limpiar Base de Datos")
        if nombres_colecciones:
            coleccion_a_eliminar = st.selectbox("Selecciona la colección a eliminar:", nombres_colecciones)
            if st.button("Eliminar Permanentemente", type="primary"):
                try:
                    cliente_chroma.delete_collection(coleccion_a_eliminar)
                    st.success(f"Colección '{coleccion_a_eliminar}' eliminada.", icon=":material/check_circle:")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al eliminar: {e}", icon=":material/error:")
        else:
            st.info("La base de datos está vacía. No hay colecciones para eliminar.", icon=":material/info:")

    # --- Panel de Estadísticas y Transformación de Datos ---
    if nombres_colecciones:
        st.divider()
        st.subheader(":material/bar_chart: Estadísticas de Colección")
        coleccion_stats = st.selectbox(
            "Selecciona una colección para inspeccionar:",
            nombres_colecciones,
            key="stats_selector"
        )

        if coleccion_stats:
            # Extraemos la data "cruda" en formato diccionario desde ChromaDB
            coleccion_nativa = cliente_chroma.get_collection(coleccion_stats)
            resultados = coleccion_nativa.get(include=["metadatas"])
            total_chunks = len(resultados["ids"])

            # TRANSFORMACIÓN DE DATOS ANÁLOGA A PANDAS:
            # En Pandas, esta operación sería equivalente a crear un DataFrame con los metadatos
            # y aplicar: df['archivo_fuente'].value_counts()
            # Al no usar Pandas en este proyecto (por eficiencia e independencia del entorno), 
            # utilizamos una lógica manual de Agregación / Map-Reduce sobre un diccionario nativo.
            conteo_por_fuente = {}
            for meta in resultados["metadatas"]:
                fuente = (meta or {}).get("archivo_fuente", "Sin fuente registrada")
                conteo_por_fuente[fuente] = conteo_por_fuente.get(fuente, 0) + 1

            st.metric(label=":material/data_object: Total de Chunks (Fragmentos)", value=total_chunks)
            st.markdown("**Distribución de Chunks por Archivo Fuente:**")
            
            # Ordenamiento equivalente a df.sort_values(ascending=False)
            for fuente, cantidad in sorted(conteo_por_fuente.items(), key=lambda x: x[1], reverse=True):
                col_fuente, col_num = st.columns([3, 1])
                with col_fuente:
                    st.write(f":material/description: `{fuente}`")
                with col_num:
                    st.write(f"**{cantidad}** chunks")
                porcentaje = int((cantidad / total_chunks) * 100) if total_chunks > 0 else 0
                st.progress(porcentaje / 100, text=f"{porcentaje}%")


def pagina_chat():
    """
    Página 2: Chatbot interactivo (RAG) para consultar los documentos subidos.

    Esta interfaz:
    1. Instancia el modelo de chat y de embeddings de MistralAI.
    2. Conecta LangChain al retriever (recuperador) vectorial.
    3. Genera un Prompt enriquecido con contexto.
    4. Muestra un chat con efecto "streaming" estilo ChatGPT.
    """
    cliente_chroma = st.session_state.cliente_chroma
    clave_api_mistral = st.session_state.clave_api_mistral
    modelo_seleccionado = "open-mistral-7b"

    st.title(":material/chat: Chatear con Documentos (RAG)")

    colecciones_actuales = cliente_chroma.list_collections()
    nombres_colecciones = [c.name for c in colecciones_actuales]

    if not nombres_colecciones:
        st.warning(
            "No hay datos indexados. Ve a 'Gestionar Documentos' para vectorizar documentos primero.",
            icon=":material/warning:"
        )
        return

    col_chat1, col_chat2 = st.columns(2)
    with col_chat1:
        coleccion_seleccionada = st.selectbox(
            ":material/library_books: Base de conocimiento:",
            nombres_colecciones
        )
    with col_chat2:
        st.caption(":material/smart_toy: Modelo LLM")
        st.info(f"`{modelo_seleccionado}`", icon=":material/check_circle:")

    if not coleccion_seleccionada:
        return

    # --- Preparación del pipeline RAG (Retrieval-Augmented Generation) ---
    modelo_lenguaje = ChatMistralAI(mistral_api_key=clave_api_mistral, model=modelo_seleccionado)
    modelo_embeddings = MistralAIEmbeddings(mistral_api_key=clave_api_mistral)

    # Conectar LangChain a la colección seleccionada en ChromaDB
    base_datos_vectorial = Chroma(
        client=cliente_chroma,
        collection_name=coleccion_seleccionada,
        embedding_function=modelo_embeddings
    )

    # Recuperador: El "search_kwargs={'k': 3}" indica que traerá los 3 fragmentos más relevantes
    recuperador = base_datos_vectorial.as_retriever(search_kwargs={"k": 3})

    # System Prompt: Instruye al LLM, es el cerebro restrictivo del bot para evitar "alucinaciones"
    prompt_del_sistema = (
        "Eres un asistente útil, experto y muy educado.\n"
        "Para responder a la pregunta del usuario, básate EXCLUSIVAMENTE en los fragmentos de contexto proporcionados abajo.\n"
        "Si la respuesta no se encuentra en dicho contexto, admite con honestidad que no lo sabes.\n"
        "Sé claro, directo y responde siempre en español.\n\n"
        "CONTEXTO RECUPERADO DE LA BASE DE DATOS:\n{context}"
    )
    plantilla_prompt = ChatPromptTemplate.from_messages([
        ("system", prompt_del_sistema),
        ("human", "{input}"),
    ])

    # Cadena (Chain) de ejecución con la sintaxis simplificada de LangChain (LCEL)
    # prompt → LLM → Salida en texto plano
    cadena_streaming = plantilla_prompt | modelo_lenguaje | StrOutputParser()

    # --- Interfaz del Chat ---
    # Inicialización del historial de mensajes en la memoria de la sesión
    if "mensajes_chat" not in st.session_state:
        st.session_state.mensajes_chat = []

    # Renderizamos el historial de mensajes previos para mantener contexto visual
    for mensaje in st.session_state.mensajes_chat:
        with st.chat_message(mensaje["rol"]):
            st.markdown(mensaje["contenido"])

    # Capturamos la nueva pregunta del usuario usando el widget de chat
    if entrada_usuario := st.chat_input(f"Pregunta algo sobre '{coleccion_seleccionada}'..."):

        st.session_state.mensajes_chat.append({"rol": "user", "contenido": entrada_usuario})
        with st.chat_message("user"):
            st.markdown(entrada_usuario)

        with st.chat_message("assistant"):
            try:
                # 1. Recuperación: Buscar en ChromaDB similitudes con la pregunta
                documentos_recuperados = recuperador.invoke(entrada_usuario)

                # 2. Contexto: Preparar el texto transformando metadatos 
                contexto_formateado = formatear_documentos_con_metadatos(documentos_recuperados)

                # 3. Generación (Streaming): Mostrar la respuesta generada letra por letra
                respuesta_texto = st.write_stream(
                    cadena_streaming.stream({"context": contexto_formateado, "input": entrada_usuario})
                )

                # 4. Transparencia: Mostrar las fuentes de datos reales (los 3 fragmentos utilizados)
                with st.expander(":material/auto_stories: Ver los fragmentos que alimentaron a la IA"):
                    st.caption("Recuperados por similitud semántica en ChromaDB:")
                    for indice, documento in enumerate(documentos_recuperados):
                        meta = documento.metadata or {}
                        fuente = meta.get("archivo_fuente") or meta.get("source") or "Sin fuente registrada"
                        st.write(f"**Fragmento #{indice+1}** — :material/description: Fuente: `{fuente}`")
                        st.info(documento.page_content)

                # 5. Guardar la respuesta final del asistente en el historial
                st.session_state.mensajes_chat.append({"rol": "assistant", "contenido": respuesta_texto})

            except Exception as e:
                st.error(f"Ocurrió un error en el proceso RAG: {e}", icon=":material/error:")


# ==========================================
# 6. Navegación con st.navigation + st.Page
# ==========================================
# st.navigation reemplaza el st.radio manual: genera el menú lateral
# automáticamente con íconos y estilos nativos de Streamlit.
paginas = st.navigation([
    st.Page(pagina_gestionar, title="Gestionar Documentos", icon=":material/folder_open:"),
    st.Page(pagina_chat,      title="Chatear con Documentos", icon=":material/chat:"),
])
# Ejecución del sistema de navegación multicapas
paginas.run()