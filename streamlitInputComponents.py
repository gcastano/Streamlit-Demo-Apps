import streamlit as st
import pandas as pd
import datetime

# Definimos los parámetros de configuración de la aplicación
st.set_page_config(
    page_title="Ejemplos de controles de captura de datos",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

dfDatos = pd.read_csv('https://raw.githubusercontent.com/gcastano/datasets/main/gapminder_data.csv')

st.header('Controles de ingreso de datos de Streamlit')
with st.sidebar:
    par_nombrePais= st.text_input('País',placeholder='Nombre del país')
    par_fertility= st.number_input('Mínimo número de hijos',min_value=0,max_value=100,step=1)
    par_rangoLifeExpectancy = st.slider('Rango expectativa vida',min_value=10,max_value=100,value=(10,100))
    par_continente =st.selectbox('Continente',options=dfDatos['continent'].unique(),index =None)
    par_pais = st.multiselect('País',options=dfDatos['country'].unique())
    # par_fecha=st.date_input('Fecha',value=None)
    par_fechaRango=st.date_input('Rango fechas',value=(datetime.date(2019, 1, 1),datetime.date(2030, 12, 31)))
    par_cambiarHorizontal=st.checkbox('Ver opción años horizontal')      
    par_tipoAnos = st.radio('Ver años',options=['Solo año actual','Todos los años'],horizontal=par_cambiarHorizontal)
    with st.form('formaPoblacion'):        
        par_poblacionMax=st.select_slider('Población máxima',options=[500000,5000000,10000000,50000000,70000000,1000000000])
        btnAplicar=st.form_submit_button('Aplicar')

if par_nombrePais!='':
    dfDatos=dfDatos[dfDatos['country'].str.upper().str.contains(par_nombrePais.upper())]
if par_fertility>0:
    dfDatos=dfDatos[dfDatos['fertility']>=par_fertility]
if par_continente!=None:
    dfDatos=dfDatos[dfDatos['continent']==par_continente]
if len(par_pais)>0:
    dfDatos=dfDatos[dfDatos['country'].isin(par_pais)]
if par_tipoAnos=='Solo año actual':
        dfDatos=dfDatos[dfDatos['year']==datetime.date.today().year]

# Fitro por rango de números

dfDatos=dfDatos[(dfDatos['lifeExpectancy']>=par_rangoLifeExpectancy[0]) & (dfDatos['lifeExpectancy']<=par_rangoLifeExpectancy[1])]

# Fitro por rango de fechas
if len(par_fechaRango)==2:
    dfDatos=dfDatos[(dfDatos['year']>=par_fechaRango[0].year) & (dfDatos['year']<=par_fechaRango[1].year)]

if btnAplicar:    
    dfDatos=dfDatos[dfDatos['population']<=par_poblacionMax]

st.metric('Registros',len(dfDatos))
st.dataframe(dfDatos,use_container_width=True)