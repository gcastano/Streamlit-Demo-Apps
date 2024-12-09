import base64
import streamlit as st
from mistralai import Mistral

# Instalación de las librerías necesarias:
# streamlit: `pip install streamlit`
# mistralai: `pip install mistralai`

# Configuración de la página de Streamlit.
# Se establece el título, ícono (vacío en este caso), diseño ancho y barra lateral expandida.
st.set_page_config(
    page_title="Generador de blog post desde imágenes",
    page_icon="",  
    layout='wide',
    initial_sidebar_state="expanded"
)

# Encabezado principal de la aplicación.
st.header('Analizador de imágenes con Pixtral de Mistral AI')
st.subheader("https://mistral.ai/")
# Se crean dos columnas para organizar la interfaz.
c1, c2 = st.columns([2, 8])

# Primera columna (c1): Control de carga de imagen.
with c1:
    # Widget para cargar un archivo de imagen, acepta formatos JPG y PNG.
    archivo_cargado = st.file_uploader("Elige una imagen", type=['jpg', 'png'])
    if archivo_cargado is not None:
        # Si se carga un archivo, se lee su contenido en bytes.
        bytes_data = archivo_cargado    

        # Se convierte la imagen a una cadena base64 para poder usarla con la API.
        base64_image = base64.b64encode(bytes_data.getvalue()).decode("utf-8")

        # Se muestra la imagen cargada en un expander.
        with st.expander("Imagen cargada", expanded=True):
            st.image(bytes_data)

# Segunda columna (c2): Input del prompt y botón de ejecución.
with c2:
    # Área de texto para ingresar el prompt que describe la tarea a realizar con la imagen.
    par_Prompt = st.text_area("Qué deseas hacer con la imagen:")
    # Botón para iniciar el análisis de la imagen con Mistral AI.
    btnEjecutarAnalisis = st.button("Generar", type="primary")

# Lógica principal de la aplicación. Se ejecuta cuando se presiona el botón "Generar".
if btnEjecutarAnalisis:
    # Se obtiene la clave de API de Mistral AI desde los secretos de Streamlit.
    # Es crucial configurar esto en la sección "Secrets" de la aplicación de Streamlit.
    api_key = st.secrets["MISTRAL_API_KEY"]

    # Se especifica el modelo de Mistral AI a utilizar (Pixtral en este caso).
    model = "pixtral-12b-2409"

    # Se inicializa el cliente de la API de Mistral.
    client = Mistral(api_key=api_key)

    # Se construye el mensaje para la API, incluyendo el prompt del usuario y la imagen en base64.
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": par_Prompt
                },
                {
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{base64_image}" 
                }
            ]
        }
    ]

    # Se muestra un subencabezado para el resultado.
    st.subheader("Resultado")

    # Se realiza la llamada a la API de Mistral para obtener la respuesta.
    chat_response = client.chat.complete(
        model=model,
        messages=messages
    )

    # Se muestra el contenido de la respuesta en la aplicación Streamlit.
    st.write(chat_response.choices[0].message.content)