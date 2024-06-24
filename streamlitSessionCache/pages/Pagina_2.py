import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Ejemplo caché y session state", #Título de la página    
    layout="wide", # Forma de layout ancho o compacto
)
st.header('Página 2')

# dfDatos = pd.read_csv('https://raw.githubusercontent.com/gcastano/datasets/main/TVMaze_Shows_Genres_encoded_10K.csv')

# Uso de cache
@st.cache_data(ttl=600)
def cargarDatos():
    dfDatos = pd.read_csv('https://raw.githubusercontent.com/gcastano/datasets/main/TVMaze_Shows_Genres_encoded_10K.csv')
    return dfDatos

dfDatos=cargarDatos()

st.write(st.session_state)

# Uso de st.session_state
if 'parFiltro' in st.session_state:    
    parFiltro=st.session_state['parFiltro']
    if parFiltro!='TODOS':
        dfDatos=dfDatos[dfDatos['language']==parFiltro]
    st.subheader(f'Filtro por idioma: {parFiltro}')    

st.dataframe(dfDatos)