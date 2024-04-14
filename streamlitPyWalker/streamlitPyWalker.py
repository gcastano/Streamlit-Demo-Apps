import streamlit as st
import pandas as pd
from pygwalker.api.streamlit import StreamlitRenderer

# Definimos los parámetros de configuración de la aplicación
st.set_page_config(
    page_title="Análisis de datos con PYWalker", #Título de la página
    page_icon="📊", # Ícono
    layout="wide", # Forma de layout ancho o compacto
    initial_sidebar_state="expanded" # Definimos si el sidebar aparece expandido o colapsado
)

@st.cache_resource
def get_pyg_renderer(df) -> "StreamlitRenderer":    
    # If you want to use feature of saving chart config, set `spec_io_mode="rw"`
    return StreamlitRenderer(df, spec="./gw_config.json", spec_io_mode="rw")

st.header('Análisis de datos con PyWalker')
with st.expander('Información de PyWalker'):
    st.link_button('Github','https://github.com/Kanaries/pygwalker')
    st.write('Instalación')
    st.code('pip install pygwalker')

# declaramos el control para cargar archivos
archivo_cargado = st.file_uploader("Elige un archivo",type=['csv','xlsx'])
# Si existe un archivo cargado ejecutamos el código
if archivo_cargado is not None:   
    if '.csv' in archivo_cargado.name:    
        df = pd.read_csv(archivo_cargado,encoding='Latin-1')
    elif '.xlsx' in archivo_cargado.name:
        df = pd.read_excel(archivo_cargado)    

    #Creamos los tabs
    tab1,tab2 = st.tabs(['Explorer','Viewer'])

    # Generamos la carga de PyWalker
    renderer = get_pyg_renderer(df)
    with tab1:
        renderer.explorer()
    with tab2:
        btnRecargar = st.button('Recargar Gráficos')
        if btnRecargar:
            renderer = get_pyg_renderer(df)
        renderer.viewer()