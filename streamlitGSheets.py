import streamlit as st
import pandas as pd
import plotly.express as px 

# Definimos los parámetros de configuración de la aplicación
st.set_page_config(
    page_title="Demo carga datos desde Google Sheets", #Título de la página
    page_icon="📊", # Ícono
    layout="wide", # Forma de layout ancho o compacto
    initial_sidebar_state="expanded" # Definimos si el sidebar aparece expandido o colapsado
)

gsheetid='1SHgetxf8JaTkgHFKhz78qX6V2Y6LXrRTVBIsFYL9xjE'
sheetid='0'
url = f'https://docs.google.com/spreadsheets/d/{gsheetid}/export?format=csv&gid={sheetid}&format'
st.write(url)
sheetid='117226359'
url2 = f'https://docs.google.com/spreadsheets/d/{gsheetid}/export?format=csv&gid={sheetid}&format'
st.write(url2)
url2 = f'https://docs.google.com/spreadsheets/d/{gsheetid}/export?format=csv&gid={sheetid}&format'
sheetid='1884410336'
url3 = f'https://docs.google.com/spreadsheets/d/{gsheetid}/export?format=csv&gid={sheetid}&format'
st.write(url3)

dfDatos = pd.read_csv(url)
dfDatosCategorias = pd.read_csv(url2)

dfDatosMes = pd.read_csv(url3,usecols=[0,1]) # Limitamos las columnas a cargar para no mostrar los filtros

# st.dataframe(dfDatos,use_container_width=True)
# st.dataframe(dfDatosCategorias,use_container_width=True)
# st.dataframe(dfDatosMes,use_container_width=True)

@st.experimental_fragment(run_every=2)
def cargarVentasCategoria(url):
    dfDatosCategorias = pd.read_csv(url)
    dfDatosGrupo = dfDatosCategorias.groupby('categoria')['ventas'].sum().reset_index()
    fig = px.bar(dfDatosGrupo, x='categoria',y='ventas')
    st.plotly_chart(fig,use_container_width=True)

@st.experimental_fragment(run_every=2)
def cargarVentasMes(url):
    dfDatosMes = pd.read_csv(url)    
    fig = px.bar(dfDatosMes, x='categoria',y='sum Total')
    st.plotly_chart(fig,use_container_width=True)

c1,c2 = st.columns(2)
with c1:
    cargarVentasCategoria(url2)
with c2:
    cargarVentasMes(url3)


