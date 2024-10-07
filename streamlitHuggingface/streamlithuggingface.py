# Importación de librerías necesarias
import requests
import streamlit as st
import pandas as pd
from annotated_text import annotated_text,annotation # https://github.com/tvst/st-annotated-text
from iteration_utilities import unique_everseen # https://pypi.org/project/iteration-utilities/




# Configuración de la página de Streamlit
st.set_page_config(
    page_title="Extractor de entidades en textos",
    page_icon="",  
    layout='wide',
    initial_sidebar_state="expanded"
)

# Obtención de la API key de Hugging Face desde secrets.toml de Streamlit
HUGGINGFACE_API = st.secrets["HUGGINGFACE_API"]

# Lista de modelos disponibles para el análisis de entidades tomados de Hugging Face    https://huggingface.co/
modelos=["MMG/xlm-roberta-large-ner-spanish",
        "dslim/bert-base-NER",
        "51la5/roberta-large-NER",
        "FacebookAI/xlm-roberta-large-finetuned-conll03-english",
        "Babelscape/wikineural-multilingual-ner"]

# Configuración de los headers para la API de Hugging Face
headers = {"Authorization": f"Bearer {HUGGINGFACE_API}"}

# Función para realizar la consulta a la API de Hugging Face
def query(payload,API_URL):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()

# Título principal de la aplicación
st.header("Extractor de entidades con :orange[Hugging Face]")

# Creación de dos columnas para la interfaz
c1,c2 =st.columns(2)

# Columna izquierda: Entrada de datos
with c1:
    parModelo = st.selectbox("Modelo",options=modelos)
    parTexto = st.text_area("Texto a analizar",height=600)    
    API_URL = f"https://api-inference.huggingface.co/models/{parModelo}"

# Columna derecha: Resultados
with c2:
    if parTexto:
        # Realizar la consulta a la API con el texto ingresado
        output = query({
            "inputs": parTexto,
        },API_URL)        
        
        # Crear pestañas para mostrar diferentes vistas de los resultados
        tabTexto,tabEntidades,tabJson = st.tabs(["Texto resaltado","Entidades","Resultado modelo"])
        
        # Pestaña de Texto resaltado
        with tabTexto:
            entidades = output
            listaentidades = [x["word"] for x in output]
            entidades=list(unique_everseen(entidades))
            textoAnotado = list()
            posicionAnterior = 0
            
            # Crear texto anotado con las entidades resaltadas
            for entidad in entidades:
                textoSimple=parTexto[posicionAnterior:entidad["start"]] 
                textoAnotado.append(textoSimple)		
                textoAnotado.append(annotation(entidad["word"],entidad["entity_group"]))
                posicionAnterior=entidad["end"]
            textoSimple=parTexto[posicionAnterior:] 
            textoAnotado.append(textoSimple)            
            st.subheader("Resultado")
            annotated_text(*textoAnotado)
        
        # Pestaña de Entidades
        with tabEntidades:
            entidades = [{"Entidad":x["word"],"Tipo":x["entity_group"]} for x in output]
            dfEntidades = pd.DataFrame.from_dict(entidades)
            st.table(dfEntidades.drop_duplicates())
        
        # Pestaña de Resultado JSON
        with tabJson:
            with st.container(height=600):
                st.json(output)     
    else:
        st.warning("Por favor ingrese un texto para procesar")