# coding=cp1252
# Esta l�nea define la codificaci�n de caracteres del archivo. cp1252 es com�n en sistemas Windows m�s antiguos.
# Hoy en d�a se prefiere usar UTF-8 para una mejor compatibilidad.

# --- LIBRER�AS ---
# A continuaci�n, se importan las librer�as necesarias para el proyecto.

# streamlit: Es un framework de c�digo abierto para crear y compartir aplicaciones web para ciencia de datos y machine learning de forma r�pida y sencilla.
# Comando de instalaci�n: pip install streamlit
import streamlit as st

# requests: Es una librer�a muy popular en Python que facilita la realizaci�n de solicitudes HTTP (como llamar a una API o webhook).
# Comando de instalaci�n: pip install requests
import requests

# json: Es una librer�a est�ndar de Python (no necesita instalaci�n) que permite trabajar con datos en formato JSON (JavaScript Object Notation),
# que es un est�ndar com�n para el intercambio de datos en la web.
import json

# uuid: Es una librer�a est�ndar de Python (no necesita instalaci�n) que se utiliza para generar identificadores �nicos universales (UUIDs).
# En este caso, se usa para crear un ID de sesi�n �nico para cada conversaci�n.
import uuid

# --- CONFIGURACI�N DE LA P�GINA DE STREAMLIT ---
# st.set_page_config() configura los metadatos y el layout de la p�gina.
# page_title: Establece el t�tulo que aparece en la pesta�a del navegador.
# layout="wide": Hace que el contenido de la p�gina ocupe todo el ancho disponible.
st.set_page_config(page_title="Chatbot con n8n", layout="wide")

# --- DEFINICI�N DE LA FUNCI�N ---

def consultarChatbot(sesion, mensaje):
    """
    Realiza una consulta a un webhook de n8n para obtener una respuesta del chatbot.

    Esta funci�n env�a el ID de la sesi�n y el mensaje del usuario a un punto final (endpoint)
    de n8n. n8n procesa la solicitud y devuelve la respuesta generada por el chatbot.

    Args:
        sesion (str): Un identificador �nico para la sesi�n de chat actual.
                      Esto permite que el backend mantenga el contexto de la conversaci�n.
        mensaje (str): El mensaje o pregunta que el usuario ha escrito.

    Returns:
        str: La respuesta del chatbot en formato de texto plano.
    """
    # URL del webhook en n8n que recibir� la solicitud del chatbot.
    url = "URL_DE_TU_WEBHOOK_DE_N8N"    
    
    # Se crea el cuerpo (payload) de la solicitud en formato de diccionario Python.
    # Este diccionario contiene el ID de la sesi�n y el mensaje del usuario.
    payload_dict = {
        "session": sesion,
        "message": mensaje
    }
    # Se convierte el diccionario de Python a una cadena de texto en formato JSON.
    # Esto es necesario para enviarlo correctamente a trav�s de la solicitud HTTP.
    payload = json.dumps(payload_dict)
    
    # Se definen las cabeceras (headers) de la solicitud.
    # 'Content-Type': 'application/json' le indica al servidor que el cuerpo de la solicitud est� en formato JSON.
    headers = {
        'Content-Type': 'application/json'
    }
    
    # Se realiza la solicitud HTTP POST a la URL de n8n.
    # requests.post env�a los datos (payload) y las cabeceras (headers) al servidor.
    response = requests.post(url, headers=headers, data=payload)
    
    # Se convierte la respuesta recibida del servidor (que est� en formato JSON) a un diccionario de Python.
    response_json = response.json()
    
    # Se extrae y devuelve el valor asociado a la clave "output", que contiene la respuesta del chatbot.
    return response_json["output"]

# --- L�GICA PRINCIPAL DE LA APLICACI�N STREAMLIT ---

# Muestra el t�tulo principal en la aplicaci�n web.
# El �cono :material/robot_2: es parte de la sintaxis de Streamlit para a�adir �conos.
st.title(":material/robot_2: Chatbot con n8n")
   
# --- GESTI�N DEL ESTADO DE LA SESI�N (st.session_state) ---
# st.session_state es un objeto similar a un diccionario que Streamlit proporciona para
# almacenar variables que deben persistir entre las interacciones del usuario (reruns).

# Se comprueba si la clave "messages" no existe en el estado de la sesi�n.
# Si es la primera vez que el usuario abre la app, se inicializa como una lista vac�a.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Se comprueba si la clave "sesion" no existe en el estado de la sesi�n.
# Si no existe, se genera un ID de sesi�n �nico usando uuid y se almacena.
# Esto asegura que cada conversaci�n tenga un identificador �nico.
if "sesion" not in st.session_state:
    st.session_state.sesion = uuid.uuid4().hex

# --- VISUALIZACI�N DEL HISTORIAL DEL CHAT ---
# Se itera sobre la lista de mensajes almacenada en st.session_state.messages.
for message in st.session_state.messages:
    # st.chat_message() crea un contenedor de mensaje de chat con un rol ('user' o 'assistant').
    # Se asigna un avatar diferente dependiendo de si el mensaje es del usuario o del asistente.
    with st.chat_message(message["role"],avatar="robot-one-svgrepo-com.png" if message["role"] == "assistant" else "user-svgrepo-com.png"):
        # st.markdown() renderiza el contenido del mensaje.
        st.markdown(message["content"])

# --- ENTRADA DE USUARIO ---
# st.chat_input() crea un campo de entrada de texto fijo en la parte inferior de la p�gina.
# El operador Walrus (:=) asigna el valor del input a la variable `prompt` y, al mismo tiempo,
# eval�a si `prompt` tiene un valor (es decir, si el usuario escribi� algo y presion� Enter).
if prompt := st.chat_input("En qu� te puedo ayudar?"):

    # Almacena y muestra el mensaje del usuario.
    # Se a�ade el nuevo mensaje a la lista en el estado de la sesi�n.
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Se muestra el mensaje del usuario en la interfaz inmediatamente.
    with st.chat_message("user", avatar="user-svgrepo-com.png"):
        st.markdown(prompt)

    # Se llama a la funci�n para obtener la respuesta del chatbot.
    # Se pasa el ID de la sesi�n y el mensaje del usuario.
    respuesta_chatbot = consultarChatbot(
        st.session_state.sesion,
        mensaje=prompt
    )

    # Muestra la respuesta del asistente.
    with st.chat_message("assistant", avatar="robot-one-svgrepo-com.png"):
        # st.write() muestra la respuesta del chatbot en la interfaz.
        st.write(respuesta_chatbot)
    
    # Se a�ade la respuesta del asistente a la lista en el estado de la sesi�n para guardarla en el historial.
    st.session_state.messages.append({"role": "assistant", "content": respuesta_chatbot})
