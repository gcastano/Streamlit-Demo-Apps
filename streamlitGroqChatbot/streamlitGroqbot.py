import streamlit as st
import time
from groq import Groq
from typing import Generator

st.title("Groq Bot")
client = Groq(
    api_key=st.secrets["ngroqAPIKey"],
)

modelos=['llama3-8b-8192','llama3-70b-8192','mixtral-8x7b-32768']


def generate_chat_responses(chat_completion) -> Generator[str, None, None]:    
    for chunk in chat_completion:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Muestra mensajes de chat desde la historia en la aplicación Rerun
with st.container():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

parModelo = st.sidebar.selectbox('Modelos',options=modelos,index=0)
# Reaccionar a la entrada del usuario
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
                    "role": "assistant",
                    "content": prompt
                },                            
            ],            
            stream=True
        )        
        # Use the generator function with st.write_stream
        # Mostrar respuesta del asistente en el contenedor de mensajes de chat
        with st.chat_message("assistant"):
            # response = st.write_stream(response_generator(chat_completion.choices[0].message.content))
            chat_responses_generator = generate_chat_responses(chat_completion)
            full_response = st.write_stream(chat_responses_generator)
            # response=chat_completion.choices[0].message.content
            # st.write(response)        
        # Agregar respuesta de asistente al historial de chat
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    except Exception as e:
        st.error(e, icon="🚨")