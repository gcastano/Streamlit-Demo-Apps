# --------------------------------------------------------------------------------
# LIBRERÍAS Y DEPENDENCIAS
# --------------------------------------------------------------------------------
# A continuación se detallan las librerías utilizadas en este proyecto.

# streamlit: Una librería de código abierto para crear y compartir aplicaciones web
# para ciencia de datos y machine learning de forma rápida y sencilla.
# Instalación: pip install streamlit
import streamlit as st

# openai: La librería oficial de OpenAI para interactuar con sus modelos de IA.
# En este caso, la configuramos para que apunte a un endpoint de Hugging Face,
# lo que nos permite usar otros modelos de lenguaje.
# Instalación: pip install openai
from openai import OpenAI


# --------------------------------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA DE STREAMLIT
# --------------------------------------------------------------------------------
# st.set_page_config() configura los metadatos y el layout de la página.
# page_title: El título que aparece en la pestaña del navegador.
# layout: "wide" para que el contenido ocupe todo el ancho de la pantalla.
st.set_page_config(page_title="Consulta con la imagen", layout="wide")

# --------------------------------------------------------------------------------
# FUNCIÓN PRINCIPAL
# --------------------------------------------------------------------------------

def consultarImagen(mensaje, urlimagen):
    """
    Envía un mensaje de texto y la URL de una imagen a un modelo de lenguaje multimodal
    alojado en OpenRouter y muestra la respuesta en la interfaz de Streamlit.

    Esta función utiliza la librería de OpenAI, pero la redirige a un endpoint de
    OpenRouter para poder usar modelos de código abierto como Qwen.

    Args:
        mensaje (str): La pregunta o el texto que el usuario quiere enviar al modelo.
        urlimagen (str): La URL pública de la imagen que se analizará junto con el texto.
    """
    # Se inicializa el cliente de OpenAI.
    # Es crucial notar que estamos cambiando la 'base_url' para apuntar al
    # router de inferencia de OpenRouter en lugar de la API de OpenAI.
    # https://openrouter.ai/
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        # La 'api_key' se obtiene de los secretos de Streamlit (st.secrets),
        # que es una forma segura de manejar claves y tokens sin exponerlos en el código.
        # En este caso, se espera una clave de API de Hugging Face.
        api_key=st.secrets["OR_API_KEY"],
    )

    # Se realiza la llamada al modelo de chat para obtener una compleción (respuesta).
    completion = client.chat.completions.create(
        # Se especifica el modelo a utilizar. En este caso, es un modelo multimodal (VL)
        # de la familia Qwen, capaz de procesar tanto texto como imágenes.
        model="qwen/qwen-vl-plus",
        # Se construye el mensaje que se enviará al modelo.
        messages=[
            {
                "role": "user",  # El rol es 'user' para indicar que es una entrada del usuario.
                # El contenido es una lista, ya que estamos enviando múltiples tipos de datos.
                "content": [
                    {
                        "type": "text",  # El primer elemento es el texto.
                        "text": mensaje  # Aquí se pasa la pregunta del usuario.
                    },
                    {
                        "type": "image_url",  # El segundo elemento es la imagen.
                        "image_url": {
                            # Se proporciona la URL de la imagen. El modelo la descargará y procesará.
                            "url": urlimagen
                        }
                    }
                ]
            }
        ],
    )

    # Se extrae el contenido de la respuesta del modelo y se muestra en la aplicación
    # de Streamlit usando st.write().
    st.write(completion.choices[0].message.content)

# --------------------------------------------------------------------------------
# INTERFAZ DE USUARIO CON STREAMLIT
# --------------------------------------------------------------------------------

# Define el título principal de la aplicación web. El ícono es de la librería Material Icons.
st.title(":material/robot_2: Chatbot que analiza imágenes")
st.subheader("Usando Qwen-VL con OpenRouter")
# Inicializa el estado de la sesión para guardar los mensajes.

# Se crea un layout de dos columnas para organizar la interfaz.
c1,c2 = st.columns(2)

# Columna 1: Carga de la imagen.
with c1:
    # Campo de texto para que el usuario ingrese la URL de la imagen.
    parURLImagen = st.text_input("URL de la imagen", "")
    # Si el usuario hace clic en el botón "Cargar imagen" o si ya ha introducido una URL,
    # se muestra la imagen en la interfaz.
    if st.button("Cargar imagen", type='primary') or parURLImagen:
        # st.image() muestra una imagen a partir de una URL, archivo local o array de NumPy.
        st.image(parURLImagen, caption='Imagen cargada', use_container_width=True)

# Columna 2: Interacción con el chatbot.
with c2:
    # Campo de texto para que el usuario escriba su pregunta sobre la imagen.
    mensaje = st.text_input("Pregunta sobre la imagen", "")
    # Si el usuario hace clic en "Enviar" Y ha escrito un mensaje, se ejecuta la consulta.
    if st.button("Enviar", type='primary') and mensaje:
        # Llama a la función principal con el mensaje y la URL de la imagen.
        consultarImagen(mensaje,parURLImagen)