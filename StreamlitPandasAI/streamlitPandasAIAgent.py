# --- LIBRERÍAS ---
# Para instalar las librerías necesarias, ejecuta los siguientes comandos en tu terminal:
# pip install pandasai
# pip install pandasai[litellm]  (o pip install litellm si ya tienes pandasai)
# pip install pandas
# pip install streamlit
# pip install Pillow

# https://github.com/sinaptik-ai/pandas-ai
import pandasai as pai # Importa la biblioteca PandasAI, que permite interactuar con DataFrames de pandas usando lenguaje natural.
from pandasai_litellm import LiteLLM # Importa LiteLLM desde pandasai_litellm, que actúa como un conector para usar diversos modelos de lenguaje grandes (LLMs) con PandasAI.
import pandas as pd # Importa la biblioteca pandas, fundamental para la manipulación y análisis de datos en Python, especialmente con estructuras como DataFrames.
import streamlit as st # Importa la biblioteca Streamlit, utilizada para crear aplicaciones web interactivas de forma rápida y sencilla, ideal para visualización de datos y dashboards.
import io # Importa el módulo io, que proporciona herramientas para trabajar con flujos de E/S (entrada/salida), como flujos de bytes en memoria.
from PIL import Image # Importa la clase Image de la biblioteca Pillow (PIL Fork), que permite abrir, manipular y guardar diversos formatos de archivos de imagen.
import os # Importa el módulo os, que proporciona una forma de usar funcionalidades dependientes del sistema operativo, como interactuar con el sistema de archivos (crear, eliminar archivos/directorios).

# --- CONFIGURACIÓN DEL MODELO DE LENGUAJE GRANDE (LLM) ---
# Configura el modelo de lenguaje grande (LLM) que PandasAI utilizará.
# LiteLLM permite conectar con varios proveedores de LLM.
llm = LiteLLM(
    model="mistral/mistral-medium-latest",  # Especifica el modelo a usar (en este caso, uno de Mistral).
    temperature=0,  # Controla la aleatoriedad de la salida. 0 hace la salida más determinista y enfocada.
    max_tokens=None,  # Número máximo de tokens (palabras/subpalabras) que el modelo puede generar en su respuesta. None significa sin límite explícito aquí, aunque el modelo subyacente puede tener uno.
    max_retries=2,  # Número máximo de reintentos si la llamada a la API del LLM falla.
    api_key=st.secrets["MISTRAL_API_KEY"],  # Clave API para acceder al servicio del LLM. ¡RECUERDA CAMBIAR ESTO POR TU PROPIA CLAVE!
)

# --- CONFIGURACIÓN DE PANDASAI ---
# Establece configuraciones globales para PandasAI.
pai.config.set({
    "llm": llm, # Asigna el LLM configurado previamente para que PandasAI lo utilice.
    'history_size': 10, # Define cuántas interacciones previas (preguntas y respuestas) se recordarán en la conversación para mantener el contexto.
    'system_prompt': "You are a helpful assistant that answers questions about data always in the same language as the question. If the question is in Spanish, you answer in Spanish. If the question is in English, you answer in English.",
    # 'system_prompt': Define un mensaje de sistema que guía el comportamiento general del LLM. Aquí se le instruye para responder en el mismo idioma de la pregunta.
})

# --- CONFIGURACIÓN DE LA PÁGINA DE STREAMLIT ---
# Configura la página de la aplicación Streamlit (título en la pestaña del navegador, ícono, y layout).
st.set_page_config(
    page_title="Streamlit PandasAI Agent", # Título que aparece en la pestaña del navegador.
    page_icon=":bar_chart:", # Ícono que aparece en la pestaña del navegador (emoji de gráfico de barras).
    layout="wide", # Define el layout de la página como "ancho" para usar más espacio horizontal.
)

# --- TÍTULO DE LA APLICACIÓN ---
# Establece el título principal que se mostrará en la aplicación Streamlit.
st.title(":material/robot: Streamlit PandasAI Agent") # Título principal de la aplicación con un ícono de robot.

# --- CARGA DE DATOS ---
# Crea un "expander" en Streamlit, que es una sección colapsable.
# 'expanded=True' significa que estará abierto por defecto.
with st.expander("Datos cargados", expanded=True):
    # Crea un widget en Streamlit para que el usuario pueda cargar archivos.
    # 'label' es el texto que se muestra al usuario.
    # 'type' especifica los tipos de archivo permitidos (CSV y XLSX en este caso).
    uploaded_file = st.file_uploader("Escoger archivo para cargar", type=["csv", "xlsx"])

# --- PROCESAMIENTO DEL ARCHIVO CARGADO ---
# Verifica si un archivo ha sido cargado por el usuario.
if uploaded_file is not None:
    # Si el archivo cargado es un CSV:
    if uploaded_file.name.endswith('.csv'):
        # Lee el archivo CSV y lo carga en un DataFrame de pandas.
        # 'uploaded_file' es un objeto tipo archivo que pandas puede leer directamente.
        dfArchivo = pd.read_csv(uploaded_file)
    # Si el archivo cargado es un XLSX (Excel):
    elif uploaded_file.name.endswith('.xlsx'):
        # Lee el archivo XLSX y lo carga en un DataFrame de pandas.
        dfArchivo = pd.read_excel(uploaded_file)

    # Convierte el DataFrame de pandas (`dfArchivo`) en un DataFrame inteligente de PandasAI (`df`).
    # Este DataFrame de PandasAI es el que puede procesar consultas en lenguaje natural.
    df = pai.DataFrame(dfArchivo)
    
    # Crea un campo de entrada de chat en Streamlit para que el usuario ingrese su consulta.
    par_prompt = st.chat_input("Qué deseas consultar de los datos")
    
    # Si el usuario ha ingresado un prompt (una pregunta/consulta):
    if par_prompt:
        # Muestra el mensaje del usuario en la interfaz de chat.
        with st.chat_message("human"):
            st.write(par_prompt)
        
        # Muestra un contenedor para la respuesta de la IA.
        with st.chat_message("ai"):
            # Envía el prompt del usuario al DataFrame de PandasAI para obtener una respuesta.
            # PandasAI interpretará la pregunta, generará código Python (si es necesario),
            # lo ejecutará sobre el DataFrame y devolverá el resultado.
            response = df.chat(par_prompt)
            
            # Verifica el tipo de respuesta obtenida de PandasAI.
            if response.type == 'dataframe':
                # Si la respuesta es un DataFrame (por ejemplo, una tabla filtrada o resumida).
                # Crea dos pestañas: "Resultado" y "Código".
                tabResultado, tabCodigo = st.tabs(["Resultado", "Código"])
                with tabResultado:
                    # Muestra el DataFrame resultante en la pestaña "Resultado".
                    # 'use_container_width=True' hace que la tabla ocupe todo el ancho disponible.
                    # 'hide_index=True' oculta el índice del DataFrame en la visualización.
                    st.dataframe(response.value, use_container_width=True, hide_index=True)
                with tabCodigo:
                    # Muestra el último código Python ejecutado por PandasAI para generar la respuesta.
                    st.code(response.last_code_executed, language='python')
            
            elif response.type == "chart":
                # Si la respuesta es un gráfico.
                # 'response.value' contiene la ruta al archivo de imagen del gráfico generado.
                # Abre el archivo de imagen en modo lectura binaria ("rb").
                with open(response.value, "rb") as f:
                    # Lee los bytes de la imagen.
                    img_bytes = f.read()
                # Crea un objeto Imagen de Pillow a partir de los bytes leídos.
                # 'io.BytesIO' crea un flujo de bytes en memoria.
                img = Image.open(io.BytesIO(img_bytes))
                
                # Crea dos pestañas: "Resultado" y "Código".
                tabResultado, tabCodigo = st.tabs(["Resultado", "Código"])
                with tabResultado:
                    # Muestra la imagen (gráfico) en la pestaña "Resultado".
                    st.image(img)
                with tabCodigo:
                    # Muestra el último código Python ejecutado por PandasAI para generar el gráfico.
                    st.code(response.last_code_executed, language='python')
                
                # Elimina el archivo de imagen temporal generado por PandasAI después de mostrarlo
                # para no acumular archivos en el servidor.
                os.remove(response.value)
            
            else:
                # Si la respuesta es de otro tipo (generalmente texto plano).
                # Muestra el valor de la respuesta directamente.
                # Crea dos pestañas: "Resultado" y "Código".
                tabResultado, tabCodigo = st.tabs(["Resultado", "Código"])
                with tabResultado:
                    st.write(response.value)
                with tabCodigo:
                    # Muestra el último código Python ejecutado por PandasAI para generar la respuesta.
                    st.code(response.last_code_executed, language='python')
                
