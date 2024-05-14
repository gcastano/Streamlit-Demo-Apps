import streamlit as st
import time
from groq import Groq
from typing import Generator

st.title("Groq Bot")

# Declaramos el cliente de Groq
client = Groq(
    api_key=st.secrets["ngroqAPIKey"], # Cargamos la API key del .streamlit/secrets.toml
)

# Lista de modelos pare elegir
modelos=['llama3-8b-8192','llama3-70b-8192','mixtral-8x7b-32768']

def generate_chat_responses(chat_completion) -> Generator[str, None, None]:   
    """ Generated Chat Responses
        Genera respuestas de chat a partir de la información de completado de chat, mostrando caracter por caracter.

        Args: chat_completion (str): La información de completado de chat.

        Yields: str: Cada respuesta generada. 
    """ 
    for chunk in chat_completion:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


# Inicializamos el historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = []


# Muestra mensajes de chat desde la historia en la aplicación cada vez que la aplicación se ejecuta
with st.container():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Mostramos la lista de modelos en el sidebar
parModelo = st.sidebar.selectbox('Modelos',options=modelos,index=0)
# Mostramos el campo para el prompt del usuario
prompt=st.chat_input("Qué quieres saber?")

if prompt:
     # Mostrar mensaje de usuario en el contenedor de mensajes de chat
    st.chat_message("user").markdown(prompt)
    # Agregar mensaje de usuario al historial de chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    try:
        chat_completion = client.chat.completions.create(
            model=parModelo,                       
            messages=[
                {
                    "role": m["role"],
                    "content": m["content"]
                }
                for m in st.session_state.messages
            ], # Entregamos el historial de los mensajes para que el modelo tenga algo de memoria
            stream=True
        )  
        # Mostrar respuesta del asistente en el contenedor de mensajes de chat
        with st.chat_message("assistant"):            
            chat_responses_generator = generate_chat_responses(chat_completion)
            # Usamos st.write_stream para simular escritura
            full_response = st.write_stream(chat_responses_generator)                                    
        # Agregar respuesta de asistente al historial de chat
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    except Exception as e: # Informamos si hay un error
        st.error(e)