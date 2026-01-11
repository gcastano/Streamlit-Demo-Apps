# Script de Agregador y Analizador RSS con Streamlit.

# Descripción:
# ------------
# Este script permite cargar feeds RSS desde una URL o un archivo XML local.
# Su objetivo es enseñar cómo parsear contenido XML, transformarlo en estructuras
# de datos manejables (DataFrames de Pandas) y visualizarlo en una aplicación web interactiva.

# Características principales:
# 1. Ingesta de datos: Peticiones HTTP o carga de archivos.
# 2. Procesamiento XML: Uso de ElementTree para navegar por el árbol de etiquetas.
# 3. Transformación de datos: Conversión de listas de diccionarios a DataFrames de Pandas.
# 4. Visualización: Tablas interactivas y tarjetas personalizadas con Streamlit.
# 5. Análisis de texto: Conteo de frecuencias de palabras (NLP básico).

# Librerías necesarias (Instalación):
# -----------------------------------
# Ejecuta el siguiente comando en tu terminal para instalar las dependencias externas:
# pip install streamlit pandas requests

# (Las librerías 'xml', 'collections' e 'io' vienen incluidas en la instalación base de Python)


import streamlit as st  # Framework para crear aplicaciones web de ciencia de datos rápidamente sin saber HTML/CSS
import pandas as pd     # Librería estándar para manipulación y análisis de datos estructurados (DataFrames)
from collections import Counter # Herramienta de alto rendimiento para contar elementos hashables (usado para frecuencia de palabras)
import requests         # Librería "de facto" en Python para realizar peticiones HTTP (GET, POST) a servidores web

import xml.etree.ElementTree as ET # Librería estándar y ligera para parsear y navegar por árboles de documentos XML

# Configuración inicial de la página de Streamlit (Título de la pestaña del navegador y layout)
st.set_page_config(page_title="Agregador RSS", layout="wide")

st.title(":material/rss_feed: Agregador y Analizador de RSS")

# --- BARRA LATERAL (SIDEBAR) ---
# Se utiliza para inputs de configuración que controlan el flujo de la app
with st.sidebar:
    st.header("Configuración")
    # Widget de selección única para elegir el origen de los datos
    rss_source = st.radio("Selecciona la fuente:", ["URL", "Archivo XML"])
    
    xml_content = None # Inicializamos la variable que contendrá el XML crudo
    
    if rss_source == "URL":
        rss_url = st.text_input("Ingresa la URL del RSS:")
        if rss_url:
            try:
                # Realizamos la petición GET a la URL proporcionada
                # timeout=10 es crucial para evitar que la app se congele indefinidamente si el servidor no responde
                response = requests.get(rss_url, timeout=10)
                xml_content = response.content # Obtenemos el contenido en bytes
                st.success("✓ RSS cargado exitosamente")
            except Exception as e:
                st.error(f"Error al cargar URL: {e}")
    else:
        # Widget específico de Streamlit para subir archivos desde la computadora del usuario
        uploaded_file = st.file_uploader("Carga un archivo XML", type=["xml"])
        if uploaded_file:
            # Leemos el contenido binario del archivo subido
            xml_content = uploaded_file.read()
            st.success("✓ Archivo cargado exitosamente")

# --- PROCESAMIENTO PRINCIPAL ---
if xml_content:
    # try:
        # ET.fromstring convierte el string binario/texto en un objeto Element (la raíz del árbol XML)
        # Esto nos permite navegar por las etiquetas como si fueran objetos de Python.
        root = ET.fromstring(xml_content)
        
        # Buscamos todas las etiquetas <item> recursivamente (.// significa "en cualquier nivel de profundidad")
        # En los RSS estándar, cada noticia está dentro de una etiqueta <item>
        items = root.findall(".//item")        
        
        if items:
            # --- EXTRACCIÓN DE DATOS ---
            # Inicializamos una lista vacía para almacenar los datos limpios.
            # Esta lista de diccionarios es el formato ideal para luego crear un DataFrame de Pandas.
            articulos = []
            
            for item in items:
                # findtext busca la etiqueta hija y devuelve su contenido textual.
                # El segundo argumento es el valor por defecto si la etiqueta no existe (Manejo de errores básico).
                titulo = item.findtext("title", "Sin título")
                descripcion = item.findtext("description", "Sin descripción")
                link = item.findtext("link", "#")
                pubDate = item.findtext("pubDate", "Fecha desconocida")
                
                # Manejo de Namespaces (Espacios de nombres):
                # Muchas imágenes en RSS están bajo el namespace 'media' (ej: <media:content url="...">)
                namespaces = {'media': 'http://search.yahoo.com/mrss/'}
                media_content = item.find('media:content', namespaces)
                
                # Obtenemos el atributo 'url' si la etiqueta media existe
                url = media_content.get('url') if media_content is not None else "No disponible"
                
                # Agregamos el diccionario a nuestra lista procesada
                articulos.append({
                    "Título": titulo,
                    "Descripción": descripcion,
                    "Link": link,
                    "Fecha": pubDate,
                    "Imagen": url if url else "No disponible"
                })
            
            # Creamos pestañas para organizar la visualización sin saturar la pantalla
            tab1, tab2, tab3, tab4 = st.tabs([":material/news: Artículos", ":material/bar_chart_4_bars: Análisis", ":material/1k: Estadísticas",":material/code_blocks: XML"])
            
            # --- TAB 1: VISUALIZACIÓN DE DATOS CON PANDAS ---
            with tab1:
                st.subheader(f"Total de artículos: {len(articulos)}")
                
                # ---------------------------------------------------------
                # TRANSFORMACIÓN CON PANDAS
                # ---------------------------------------------------------
                # Convertimos la lista de diccionarios en un DataFrame.
                # Un DataFrame es como una hoja de cálculo en memoria: tiene filas, columnas e índices.
                # Ventajas: Permite filtrar, ordenar, limpiar y exportar datos masivamente con una sola línea.
                df = pd.DataFrame(articulos)
                
                # Widget de control segmentado para cambiar la UI dinámicamente
                parVista = st.segmented_control(
                    label="Selecciona el modo de vista:",
                    options=["Tabla", "Tarjeta"], default="Tabla")              
                
                if parVista == "Tabla":
                    # st.data_editor es un componente poderoso que muestra el DataFrame.
                    # column_config nos permite formatear columnas específicas (ej: convertir texto URL en link clicable)
                    st.data_editor(df, disabled=True, column_config={
                        "Título": st.column_config.TextColumn("Título del artículo"),
                        "Descripción": st.column_config.TextColumn("Descripción del artículo"),
                        "Link": st.column_config.LinkColumn("Enlace del artículo"), # Transforma texto en hipervínculo
                        "Fecha": st.column_config.TextColumn("Fecha de publicación")
                    }, hide_index=True) # Ocultamos el índice numérico (0, 1, 2...) de Pandas
                else:
                    # Vista tipo "Tarjeta": Iteramos sobre el DataFrame fila por fila
                    with st.container(horizontal=True):
                        # df.iterrows() devuelve el índice y la serie (fila) en cada iteración
                        for index, row in df.iterrows():
                            with st.container(width=300, border=True):
                                st.subheader(row["Título"]) # Accedemos a la columna "Título"
                                if row["Imagen"] != "No disponible":
                                    st.image(row["Imagen"], width='stretch')
                                st.caption(row["Fecha"])
                                st.write(row["Descripción"])
                                st.link_button(label="Leer más", url=row["Link"])
                                

                # --- EXPORTACIÓN DE DATOS ---
                # Pandas permite exportar el DataFrame a CSV fácilmente con .to_csv()
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Descargar CSV",
                    data=csv,
                    file_name="articulos.csv",
                    mime="text/csv"
                )
            
            # --- TAB 2: ANÁLISIS DE TEXTO (NLP Básico) ---
            with tab2:
                st.subheader("Análisis de Títulos y Descripciones")
                
                for seccion in ["Título", "Descripción"]:
                    st.subheader(f"Análisis de {seccion}")
                    
                    # 1. Unificar todo el texto en una lista plana
                    todas_palabras = []
                    for art in articulos:
                        # .lower() normaliza a minúsculas
                        # .split() divide el texto por espacios en blanco convirtiéndolo en lista de palabras
                        palabras = art[seccion].lower().split()
                        todas_palabras.extend(palabras)
                    
                    # 2. Definir Stop Words (Palabras vacías)
                    # Usamos un set (conjunto) porque la búsqueda en sets es mucho más rápida que en listas
                    stop_words = {"de", "la", "el", "en", "y", "a", "los", "las", "un", "una", "que","antes","después","con","por","para","es","al","se","del","lo","su","como","más","o","pero","sus","le","ya","o","si","sin","sobre","todo","también","entre","cuando","muy","hasta","hay","donde","quien","desde"}
                    stop_wordsEN = {"the","and","is","in","to","of","a","that","it" ,"on" ,"for" ,"with" ,"as" ,"was" ,"at" ,"by" ,"an" ,"be" ,"this" ,"are" ,"from" ,"or" ,"which" ,"but" ,"not" ,"have" ,"has" ,"they" ,"you" ,"all" ,"we" ,"his" , "her", "there", "their","about","more","one","what","when","so","if","no","my","your"}
                    stop_words.update(stop_wordsEN) # Combinamos stopwords en español e inglés
                    
                    # 3. Filtrar palabras usando List Comprehension (Pythonic way)
                    # Solo pasan palabras que NO están en stop_words Y tienen longitud > 3
                    palabras_filtradas = [p for p in todas_palabras if p not in stop_words and len(p) > 3]
                    
                    if palabras_filtradas:
                        # Counter crea un diccionario hashmap con la cuenta de cada elemento
                        contador = Counter(palabras_filtradas)
                        
                        # Obtenemos las 10 más comunes
                        top_palabras = dict(contador.most_common(10))                        
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.bar_chart(top_palabras) # Gráfico de barras automático de Streamlit
                        with col2:
                            st.write("**Top 10 palabras más frecuentes:**")
                            # Creamos un DataFrame simple para mostrar la tabla de frecuencias limpia
                            df_analisis = pd.DataFrame(top_palabras.items(), columns=["Palabra", "Frecuencia"])
                            st.data_editor(df_analisis, disabled=True, hide_index=True)

            # --- TAB 3: ESTADÍSTICAS GENERALES ---
            with tab3:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total de artículos", len(articulos))
                
                with col2:
                    # Cálculo de promedio usando generadores dentro de sum() para eficiencia de memoria
                    long_promedio = sum(len(a["Descripción"]) for a in articulos) // len(articulos)
                    st.metric("Longitud promedio descripción", f"{long_promedio} caracteres")
                
                with col3:
                    # set() elimina duplicados automáticamente, útil para contar valores únicos
                    st.metric("Fuentes únicas", len(set(a["Link"] for a in articulos)))
            
            # --- TAB 4: VISOR XML Y XPATH ---
            # Esta sección es puramente educativa para entender la estructura del archivo
            # y cómo funcionan las consultas XPath básicas.
            # NOTA: XPath es un lenguaje para navegar por elementos y atributos en documentos XML.
            # Referencia de Xpath: https://quickref.me/xpath.html
            # Prueba Xpath: https://xpather.com/
            # Aquí usamos ElementTree que tiene soporte limitado para XPath.
            # Para soporte completo, se recomienda usar lxml (no incluido en este script por simplicidad).
            with tab4:
                st.subheader("Contenido XML")
                c1,c2=st.columns([6,4])
                with c1:
                    st.code(xml_content.decode('utf-8'), language='xml')
                with c2:
                    # Input para probar consultas XPath en tiempo real sobre el objeto 'root'
                    parXpath=st.text_input("Filtrar con XPath (ejemplo: .//item/title):",".//item/title")
                    
                    try:
                        elementos_filtrados = root.findall(parXpath,namespaces)                    
                        st.write(f"Se encontraron {len(elementos_filtrados)} elementos con el XPath proporcionado.")
                        resultado = ""
                        parTipoDatos=st.selectbox("Tipo de datos a mostrar:",["Completo","Solo texto"])
                        
                        for elem in elementos_filtrados:
                            if parTipoDatos=="Solo texto":
                                # .text obtiene solo el contenido textual dentro de la etiqueta
                                resultado += elem.text + "\n"
                            else:
                                # ET.tostring recupera la representación XML completa del elemento
                                resultado += ET.tostring(elem, encoding='unicode') + "\n"
                        st.code(resultado, language='xml')
                    except Exception as e:
                        st.error(f"Error en XPath:{parXpath}\n   {e}")
        else:
            st.warning("No se encontraron artículos en el RSS")
    
    # except ET.ParseError:
    #     st.error("Error: El archivo no es un XML válido")
    # except Exception as e:
    #     st.error(f"Error procesando RSS: {e}")
else:
    st.info("👈 Carga un RSS desde el panel lateral para comenzar")