# Importar Streamlit para crear la interfaz web
# instalar con: pip install streamlit
import streamlit as st  
# Importar requests para hacer solicitudes HTTP
# instalar con: pip install requests
import requests

# Configuración de la URL base de la API de FastAPI
API_URL = "http://localhost:8000"

# Título de la aplicación
st.title("Aplicación de Análisis de Sentimientos")

# Descripción de la aplicación
st.write("""
Esta aplicación utiliza un modelo generativo de Google para analizar el sentimiento de un texto proporcionado por el usuario.
""")

# Entrada de texto para el análisis de sentimiento
texto = st.text_area("Ingrese un comentario para analizar el sentimiento:")

# Botón para enviar el texto a la API de análisis de sentimiento
if st.button("Analizar Sentimiento"):
    if texto:
        # Realiza la solicitud a la API de FastAPI
        response = requests.post(f"{API_URL}/evaluarSentimiento", json={"texto": texto})
        if response.status_code == 200:
            resultado = response.json()
            st.write(f"Sentimiento del comentario: {resultado['sentimiento']}")
        else:
            st.write("Error al analizar el sentimiento. Intente nuevamente.")
    else:
        st.write("Por favor, ingrese un comentario.")

# Entrada de selección para generar un comentario con un sentimiento específico
sentimiento = st.selectbox("Seleccione un sentimiento para generar un comentario:", ["POSITIVO", "NEGATIVO", "NEUTRAL"])

# Botón para generar el comentario
if st.button("Generar Comentario"):
    if sentimiento:
        # Realiza la solicitud a la API de FastAPI
        response = requests.get(f"{API_URL}/comentario/{sentimiento}")
        if response.status_code == 200:
            resultado = response.json()
            st.write(f"Comentario generado: {resultado['comentario']}")
        else:
            st.write("Error al generar el comentario. Intente nuevamente.")
    else:
        st.write("Por favor, seleccione un sentimiento.")