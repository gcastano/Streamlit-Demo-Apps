import streamlit as st
import pandas as pd
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_groq import ChatGroq


def reiniciarChat():
    """Función que reinicia el chat cuando se cambia de archivo
    """    
    st.toast("Archivo cargado",icon='📄')
    # Inicializamos el historial de chat
    if "messages" in st.session_state:
        st.session_state.messages = []
        promtpSistema = "Vas a actuar como un analista de datos experto, dando siempre respuestas claras y concretas y siempre en idioma español, si te piden tablas o listas, las generas siempre en markdown"
        st.session_state.messages.append({"role": "system", "content": promtpSistema})

llm = ChatGroq(
    model="llama3-70b-8192",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=st.secrets["GROQ_API"],
    
)

# Definimos los parámetros de configuración de la aplicación
st.set_page_config(
    page_title="Habla con tus datos", #Título de la página
    page_icon="📊", # Ícono
    layout="wide", # Forma de layout ancho o compacto
    initial_sidebar_state="expanded" # Definimos si el sidebar aparece expandido o colapsado
)

st.header('Habla con tus datos')

# Menú lateral
with st.sidebar:
    st.subheader('Parámetros')
    archivo_cargado = st.file_uploader("Elige un archivo",type=['csv','xls','xlsx'],on_change =reiniciarChat)
    parUsarMemoria = st.checkbox("Recordar la conversacion",value=True)
    # Si existe un archivo cargado ejecutamos el código
    if archivo_cargado is not None:           
        # Se puede cargar con pandas si se tiene detectado el tipo de archivo
        if '.csv' in archivo_cargado.name:
            df = pd.read_csv(archivo_cargado)
        elif '.xls' in archivo_cargado.name:
            df = pd.read_excel(archivo_cargado)
        # Creamos el agente con el dataframe
        agent = create_pandas_dataframe_agent(llm,df,allow_dangerous_code=True)    
# Inicializamos el historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = []
    
   

# Muestra mensajes de chat desde la historia en la aplicación cada vez que la aplicación se ejecuta
with st.container():
    for message in st.session_state.messages:
        if message["role"]!="system": # Omitimos el prompt de sistem
            with st.chat_message(message["role"]):
                st.markdown(message["content"])


# Mostramos el campo para el prompt del usuario
prompt=st.chat_input("Qué quieres saber?")


if prompt:
     # Mostrar mensaje de usuario en el contenedor de mensajes de chat
    st.chat_message("user").markdown(prompt)
    # Agregar mensaje de usuario al historial de chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Si requerimos usar la memoria entregamos siempre el historial de chat
    if parUsarMemoria:
        messages=[                
                    {
                        "role": m["role"],
                        "content": m["content"]
                    }
                    for m in st.session_state.messages
                ]
    else:
        # Si no se usa la memoria solo se entrega el prompt de sistema y la consulta del usuario
        messages=[                
                    {
                        "role": m["role"],
                        "content": m["content"]
                    }
                    for m in [st.session_state.messages[0],st.session_state.messages[-1]]
                ]    
    respuesta=agent.run(messages)
    
    # Mostrar respuesta del asistente en el contenedor de mensajes de chat
    with st.chat_message("assistant"):                        
        # Mostramos la respuesta
        st.write(respuesta)                                    
    # Agregar respuesta de asistente al historial de chat
    st.session_state.messages.append({"role": "assistant", "content": respuesta})
    