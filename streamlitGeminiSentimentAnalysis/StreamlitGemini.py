import streamlit as st
# Librería para acceder a Google Gemini
import google.generativeai as genai # pip install -q -U google-generativeai
import pandas as pd
import json

st.set_page_config(
    page_title="Análisis de Sentimiento con Google Gemini",
    page_icon="😊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def darColorResultado(x):
    style_rojo = "background-color: #F7A4A4;font-weight: bold;"
    style_naranja = "background-color: #FEBE8C; font-weight: bold;"
    style_verde = "background-color: #B6E2A1; font-weight: bold;"
    if x=="POSITIVO":
        resultado= style_verde
    elif x=="NEUTRAL":
        resultado= style_naranja
    elif x=="NEGATIVO":
        resultado= style_rojo

    return resultado
    

#Prompt del sistema
systemPrompt="""
Eres un experto analizando el sentimiento de textos entregados, 
el usuario te va a entregar una lista de comentarios y para cada uno 
vas a responder si su sentimiento es POSITIVO, NEGATIVO o NEUTRAL 
en formato JSON con un array de los campos comentario y sentimiento, no generar markdown
"""
# Cargamos la API Key de secrets.toml
# GOOGLE_API_KEY="_API_KEY_COPIADA_DE_GOOGLE_AI_STUDIO"
# La API se obtiene de https://aistudio.google.com/
genai.configure(api_key = st.secrets["GOOGLE_API_KEY"])

# Cargamos el modelo con el prompt del sistema
model = genai.GenerativeModel('gemini-1.5-pro-latest',system_instruction=systemPrompt)

st.header('Analizador de sentimientos con :blue[Google Gemini]')
c1,c2=st.columns(2)
with c1:
    txtComentarios = st.text_area("Comentarios para revisar",height=600)
    btnConsultar = st.button("Consultar",type='primary')
with c2:    
    
    if btnConsultar:
        prompt=[
            {
            "role": "user",
            "parts": [
                txtComentarios,
            ],
            }]
        with st.spinner("Procesando..."): #Usamos el spinner para mostrar que el proceso está corriendo
            # Enviamos el prompt
            response = model.generate_content(prompt)
            # Cargamos el resultado como JSON
            resultado = json.loads(str(response.text))
            # Convertimos el resultado en dataframe
            dfElementos = pd.DataFrame(resultado)  
            # Calculamos las métricas
            negativos = len(dfElementos[dfElementos["sentimiento"]=="NEGATIVO"])
            neutrales = len(dfElementos[dfElementos["sentimiento"]=="NEUTRAL"])
            positivos = len(dfElementos[dfElementos["sentimiento"]=="POSITIVO"])
            c1,c2,c3 =  st.columns(3)
            with c1:
                st.metric("Positivos",positivos)
            with c2:
                st.metric("Neutrales",neutrales)
            with c3:
                st.metric("Negativos",negativos)
                
            tabTabla,tabJson = st.tabs(["Resultados","Json"]) 
            with tabTabla:
                st.dataframe(dfElementos.style.applymap(darColorResultado,subset="sentimiento"),use_container_width=True)        
            with tabJson:
                st.json(response.text)