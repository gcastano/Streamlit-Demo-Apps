import streamlit as st
import pandas as pd
import plotly.express as px
import datetime

# Obtenemos año actual
today = datetime.date.today()
year = today.year

# Cargamos el dataframe desde un CSV
dfDatos = pd.read_csv('https://raw.githubusercontent.com/gcastano/datasets/main/gapminder_data.csv')

# Cargamos las variables que usaremos como opcion seleccionable
opciones = dfDatos.columns[3:]

# Agrupamnos los datos por continente
dfDatosContiente=dfDatos.groupby(['year','continent']).agg({'fertility':'mean', 'lifeExpectancy':'mean', 'mean_house_income':'mean', 'median_age_year':'mean','population':'sum'})
dfDatosContiente= dfDatosContiente.reset_index()


# Interfaz Streamlit
st.title('Datos por países')
with st.sidebar:
    parVariable=st.selectbox('Variable',options=opciones)

fig= px.line(dfDatosContiente,x='year',y=parVariable,title=f'{parVariable} per Continent',color='continent')
st.plotly_chart(fig,use_container_width=True)

if parVariable=='population':
    fig= px.pie(dfDatosContiente[dfDatosContiente['year']==year].sort_values(by=parVariable, ascending=False),names='continent',values=parVariable,title=f'{parVariable} por Continente {year}')
else:
    fig= px.bar(dfDatosContiente[dfDatosContiente['year']==year].sort_values(by=parVariable, ascending=False),y='continent',x=parVariable,title=f'{parVariable} promedio por Continente {year}', color='continent')
st.plotly_chart(fig,use_container_width=True)