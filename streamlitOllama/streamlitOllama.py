import streamlit as st
import ollama #https://github.com/ollama/ollama-python # pip install ollama
from typing import Generator

st.set_page_config(
    page_title="Asistende de código con Ollama y CodeQwen",
    page_icon="🤓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargamos la lista de modelos de ollama
modelos = ollama.list()['models']

# Función para mostra la información del modelo seleccionado
@st.dialog("Información modelo",width ="large")
def mostrarInfoModelo(modelo):        
    """Muestar la información del seleccionado

    Args:
        modelo (str): Modelo que se desea mostrar
    """    
    modelo = [x for x in modelos if x['name']==modelo]
    st.write(modelo)

# Función para generar lista de modelos
def generarListaModelos():  
    """Genera la lista de modelos de Ollama

    Returns:
        array: Array con los nombres de los modelos
    """     
    listaModelos = [x['name'] for x in modelos]
    return listaModelos

def generate_chat_responses(chat_completion) -> Generator[str, None, None]:   
    """ Generated Chat Responses
        Genera respuestas de chat a partir de la información de completado de chat, mostrando caracter por caracter.

        Args: chat_completion (str): La información de completado de chat.

        Yields: str: Cada respuesta generada. 
    """ 
    for chunk in chat_completion:        
        if chunk['message']['content']:
            yield chunk['message']['content']

# Inicializamos el historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = []
    promtpSistema = """Siempre vas a responder en español, Te llamas CodiBot y vas a actuar como programador experto 
                    en Python y Streamlit, vas a responder a las preguntas de manera amable y completa, 
                    y a preguntar cualquier cosa que requiera para dar una mejor respuesta.
                    
                    """
    st.session_state.messages.append({"role": "system", "content": promtpSistema})

with st.sidebar:
    param_Modelo = st.selectbox("Modelos disponibles",options=generarListaModelos())
    #Mostramos la información del modelo
    btnVerInfoModelo = st.button("Ver información")
    if btnVerInfoModelo:
        mostrarInfoModelo(param_Modelo)

# Muestra mensajes de chat desde la historia en la aplicación cada vez que la aplicación se ejecuta
with st.container():
    for message in st.session_state.messages:
        if message["role"]!="system": #Ocultamos el prompt de sistema
            with st.chat_message(message["role"]):
                st.markdown(message["content"])


prompt=st.chat_input("Qué quieres saber?")

if prompt:

    # Mostrar mensaje de usuario en el contenedor de mensajes de chat
    st.chat_message("user").markdown(prompt)
    # Agregar mensaje de usuario al historial de chat
    st.session_state.messages.append({"role": "user", "content": prompt})

    chat_completion = ollama.chat(
        model=param_Modelo,
        messages=[
                {
                    "role": m["role"],
                    "content": m["content"]
                }
                for m in st.session_state.messages
            ],
        stream=True,
    )
    

    with st.chat_message("assistant"):            
            chat_responses_generator = generate_chat_responses(chat_completion)
            # Usamos st.write_stream para simular escritura
            full_response = st.write_stream(chat_responses_generator)                                    
        # Agregar respuesta de asistente al historial de chat
    st.session_state.messages.append({"role": "assistant", "content": full_response})