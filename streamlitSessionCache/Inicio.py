import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Ejemplo caché y session state", #Título de la página    
    layout="wide", # Forma de layout ancho o compacto
)

st.header('Inicio')


# dfDatos = pd.read_csv('https://raw.githubusercontent.com/gcastano/datasets/main/TVMaze_Shows_Genres_encoded_10K.csv')

# Uso de cache
@st.cache_data(ttl=600)
def cargarDatos():
    dfDatos = pd.read_csv('https://raw.githubusercontent.com/gcastano/datasets/main/TVMaze_Shows_Genres_encoded_10K.csv')
    return dfDatos

dfDatos=cargarDatos()

with st.sidebar:
    btnLimpiarCache = st.button('Limpiar Cache')
    if btnLimpiarCache:
        st.cache_data.clear()
        st.toast('Caché eliminada')



parFiltro=st.selectbox('Idioma',options=list(['TODOS'])+list(dfDatos['language'].unique()))
parTipos= st.multiselect('Tipos',options=dfDatos['type'].unique())
st.session_state['parFiltro'] =parFiltro
st.session_state['parTipos'] =parTipos

st.write(st.session_state)

if parFiltro!='TODOS':
    dfDatos=dfDatos[dfDatos['language']==parFiltro]

st.dataframe(dfDatos)