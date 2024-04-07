import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import datetime
import plotly.graph_objects as go

# Definimos los parámetros de configuración de la aplicación
st.set_page_config(
    page_title="Ejemplos de gráficos de Líneas Plotly",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Definición de paletas de colores
paleta_discreta= px.colors.carto.Safe
paleta_continua = px.colors.sequential.Jet
paleta_personalizada = ['#124076','#7F9F80','#F9E897','#FFC374','#EE99C2','#387ADF']

# Obtenemos año actual
today = datetime.date.today()
year = today.year

# Cargamos el dataframe desde un CSV
dfDatos = pd.read_csv('https://raw.githubusercontent.com/gcastano/datasets/main/gapminder_data.csv')
# Campos: continent,country,year,fertility,lifeExpectancy,mean_house_income,median_age_year,population
dfDatosDecada=dfDatos[(dfDatos['year']<=today.year) & (dfDatos['year']>=today.year-10)]
dfAnoActual = dfDatos[dfDatos['year']==year]

data = pd.DataFrame(dict(
        number=[1000000, 800000,600000,100000],
        percent=[1,0.8,0.6,0.1],
        stage=["Etapa 1","Etapa 2","Etapa 3","Etapa 4"]))

st.subheader('Gráficos de embudo o funnel')
with st.container(border=True):
    parOrientation = st.radio('Orientación',options=['Horizontal','Vertical'],index=0,horizontal=True)
    # Dependiendo de la orientación se debe ajustar los valores en los ejes X y Y
    if parOrientation=='Horizontal':
        orientation = 'h'
        campox='number'
        campoy='stage'         
    else:
        orientation='v'
        campoy='number'
        campox='stage'
        data=data.sort_values(by='number',ascending=False)

    col1,col2 = st.columns(2)
    with col1:

        figFunnelGeneral = px.funnel(data, 
                                    x=campox, 
                                    y=campoy,
                                    text='number', 
                                    custom_data=['percent'], 
                                    color_discrete_sequence=paleta_discreta,
                                    orientation=orientation,
                                    title="Gráfico de embudo")
        figFunnelGeneral.update_traces(texttemplate= '<b>%{text:,.0f} </b><br> %{customdata[0]:,.2%}') 
        # figFunnelGeneral.update_layout(hovermode=False)
        st.plotly_chart(figFunnelGeneral, use_container_width=True)
    with col2:
        figFunnelGeneral = px.funnel(data, 
                                    x=campox, 
                                    y=campoy,
                                    text='number', 
                                    custom_data=['percent'], 
                                    color_discrete_sequence=paleta_discreta,
                                    color='stage',
                                    orientation=orientation,
                                    title="Gráfico de embudo")
        figFunnelGeneral.update_traces(texttemplate= '<b>%{text:,.0f}</b><br> %{customdata[0]:,.2%}') 
        # figFunnelGeneral.update_layout(hovermode=False)
        st.plotly_chart(figFunnelGeneral, use_container_width=True)

col1,col2 = st.columns(2)
with col1:
    figFunnelGeneral = px.funnel_area(data,
                                    names='stage', 
                                    values='number',
                                    color_discrete_sequence=paleta_discreta,                                
                                    title="Gráfico de embudo")
    st.plotly_chart(figFunnelGeneral, use_container_width=True)
with col2:
    fig = go.Figure(go.Funnelarea(
        text = data['stage'],
        values = data['number']
        ))
    fig.update_layout(showlegend=False)
    fig.update_traces(texttemplate= '<b>%{text}</b><br> %{value:,.0f}') 
    st.plotly_chart(fig, use_container_width=True)

st.subheader('Pie chart y doughnut chart')
dfGrupo =dfAnoActual.groupby('continent').agg({'population':'sum','fertility':'mean'}).reset_index().sort_values(by='population', ascending=False)
col1,col2 = st.columns(2)
with col1:
    fig = px.pie(dfGrupo,
                 names='continent',
                 values='population',
                 labels={'population':'Población','continent':'Continente'},)
    st.plotly_chart(fig, use_container_width=True)
with col2:    
    fig = px.pie(data_frame=dfGrupo,
                 names='continent',
                 values='population',
                 labels={'population':'Población','continent':'Continente'},
                 hole=0.5
                 )
    fig = fig.update_traces(textposition='outside', textinfo='percent+label+value', showlegend=False)
    fig.update_traces(texttemplate= '<b>%{label}</b><br> %{value:,.0f} (%{percent:,.1%})') 
    fig = fig.update_layout(uniformtext_minsize=20, uniformtext_mode="show", )
    
    st.plotly_chart(fig, use_container_width=True)

st.subheader('Scatter plot y Bubble Chart')
# dfGrupo =dfAnoActual.groupby('continent').agg({'population':'sum','fertility':'mean'}).reset_index().sort_values(by='population', ascending=False)
col1,col2 = st.columns(2)
with col1:
    fig = px.scatter(dfAnoActual,x='fertility', y='mean_house_income',color='continent',hover_data=['country'],
                     labels={'year':'Año','fertility':'Fertilidad','mean_house_income':'Ingreso Anual en USD','population':'Población','continent':'Continente','country':'País'},
                     title='Scatter plot simple')
    st.plotly_chart(fig, use_container_width=True)
with col2:
    fig = px.scatter(dfAnoActual,x='fertility', y='mean_house_income',color='median_age_year',hover_data=['country'], size='population',
                     labels={'year':'Año','fertility':'Fertilidad','median_age_year':'Edad promedio','mean_house_income':'Ingreso Anual en USD','population':'Población','continent':'Continente','country':'País'},
                     title='Scatter plot con burbujas y escala de colores')
                     
    st.plotly_chart(fig, use_container_width=True)

col1,col2 = st.columns(2)
with col1:
    fig = px.scatter(dfAnoActual,x='fertility', y='mean_house_income',color='continent',hover_data=['country'],marginal_x="histogram", marginal_y="violin",
                     labels={'year':'Año','fertility':'Fertilidad','mean_house_income':'Ingreso Anual en USD','population':'Población','continent':'Continente','country':'País'},
                     title='Scatter plot con gráficas al margen')
    st.plotly_chart(fig, use_container_width=True)
with col2:
    fig = px.scatter(dfAnoActual,x='mean_house_income', y='lifeExpectancy',hover_data=['country'], size='population',marginal_x="histogram", marginal_y="box",
                     trendline="ols", trendline_options=dict(log_x=True),
                     labels={'year':'Año','fertility':'Fertilidad','lifeExpectancy':'Expectativa de vida','median_age_year':'Edad promedio','population':'Población','continent':'Continente','country':'País'},
                     title='Scatter plot con gráficas al margen y línea de tendencia')
    st.plotly_chart(fig, use_container_width=True)