import requests
import streamlit as st
import pandas as pd
from annotated_text import annotated_text,annotation
from iteration_utilities import unique_everseen


st.set_page_config(
    page_title="Extractor de entidades en textos",
    page_icon="",  
    layout='wide',
    initial_sidebar_state="expanded"
)

HUGGINGFACE_API = st.secrets["HUGGINGFACE_API"]
modelos=["MMG/xlm-roberta-large-ner-spanish",
        "dslim/bert-base-NER",
        "51la5/roberta-large-NER",
        "FacebookAI/xlm-roberta-large-finetuned-conll03-english"]


headers = {"Authorization": f"Bearer {HUGGINGFACE_API}"}

def query(payload,API_URL):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()


st.header("Extractor de entidades con :orange[Hugging Face]")
c1,c2 =st.columns(2)
with c1:
    parModelo = st.selectbox("Modelo",options=modelos)
    parTexto = st.text_area("Texto a analizar",height=600)    
    API_URL = f"https://api-inference.huggingface.co/models/{parModelo}"
with c2:
    if parTexto:
        output = query({
            "inputs": parTexto,
        },API_URL)        
        tabTexto,tabEntidades,tabJson = st.tabs(["Texto resaltado","Entidades","Resultado modelo"])
        with tabTexto:
            entidades = output
            listaentidades = [x["word"] for x in output]
            entidades=list(unique_everseen(entidades))
            textoAnotado = list()
            posicionAnterior = 0
            for entidad in entidades:
                textoSimple=parTexto[posicionAnterior:entidad["start"]] 
                textoAnotado.append(textoSimple)		
                textoAnotado.append(annotation(entidad["word"],entidad["entity_group"]))
                posicionAnterior=entidad["end"]
            textoSimple=parTexto[posicionAnterior:] 
            textoAnotado.append(textoSimple)
            st.subheader("Resultado")
            annotated_text(*textoAnotado)
        with tabEntidades:
            entidades = [{"Entidad":x["word"],"Tipo":x["entity_group"]} for x in output]
            dfEntidades = pd.DataFrame.from_dict(entidades)
            st.table(dfEntidades.drop_duplicates())
        with tabJson:
            with st.container(height=600):
                st.json(output)     
    else:
        st.warning("Por favor ingrese un texto para procesar")