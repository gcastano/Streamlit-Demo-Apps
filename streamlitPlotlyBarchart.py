import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import datetime
import plotly.graph_objects as go

# Definimos los parámetros de configuración de la aplicación
st.set_page_config(
    page_title="Ejemplos de gráficos de Barra Plotly",
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
dfAnoActual = dfDatos[dfDatos['year']==year]

st.subheader('Gráficos de barras simples')
cols = st.columns(2)
cols[0].link_button('Ver documentación gráfico de barras en Plotly','https://plotly.com/python/bar-charts/')
cols[1].link_button('Herramienta de paleta de colores en Plotly','https://plotly-tools.streamlit.app/')

c1,c2,c3 = st.columns(3)
with c1:
    # Gráfico sin agrupar, muestra datos por categoría pero no son barras completas    
    fig = px.bar(dfAnoActual, 
                x='continent',
                y='population',                
                title='Gráfico de barra sin agrupar sin texto')
    st.plotly_chart(fig,use_container_width=True)
with c2:
    # Agrupamos el valor para que la barra sea completa
    dfGrupo =dfAnoActual.groupby('continent')['population'].sum().reset_index().sort_values(by='population', ascending=False)
    fig = px.bar(dfGrupo, 
                x='continent',
                y='population', 
                text_auto=True,
                color='population',
                labels={'year':'Año','population':'Población','continent':'Continente'},
                color_continuous_scale = paleta_continua,
                title='Gráfico de barra agrupado color por valor')
                
    st.plotly_chart(fig,use_container_width=True)
with c3:    
    dfGrupo =dfAnoActual.groupby('continent').agg({'population':'sum','fertility':'mean'}).reset_index().sort_values(by='population', ascending=False)
    fig = px.bar(dfGrupo, 
                x='continent',
                y='population', 
                color='continent',
                text='continent',
                custom_data=['fertility'],
                labels={'year':'Año','fertility':'Fertilidad','population':'Población','continent':'Continente'},
                color_discrete_sequence=paleta_discreta,
                title='Gráfico de barra agrupado color por categoría y texto')
    # Se puede modificar la posición del texto
    fig.update_traces(textposition='outside')
    # Se pueden crear plantillas para el texto en cada barra
    fig.update_traces(texttemplate='<b>%{text}</b><br>Población: %{y:,.0f}')
    # Se pueden crear plantillas para tooltip que aparece al poner el mouse sobre el gráfico
    fig.update_traces(hovertemplate='<b>%{text}</b><br>Población: %{y:,.0f}<br>Fertilidad: %{customdata[0]:,.1f} hijos')
    st.plotly_chart(fig,use_container_width=True)

st.subheader('Gráficos de barras múltiples o verticales')
c1,c2,c3 = st.columns(3)
with c1:
    dfGrupo =dfAnoActual.groupby('continent')['population'].sum().reset_index().sort_values(by='population')
    fig = px.bar(dfGrupo, 
                x='population',
                y='continent', 
                text_auto=True,
                color='population',
                color_discrete_sequence=paleta_discreta,
                title='Gráfico de barra agrupado color por valor')
    st.plotly_chart(fig,use_container_width=True)
with c2:
    # Agrupamos el valor para que la barra sea completa
    dfGrupo =dfDatos[dfDatos['year'].isin([2022,2023,2024])].groupby(['year','continent'])['population'].sum().reset_index().sort_values(by='population', ascending=False)
    fig = px.bar(dfGrupo, 
                x='year',
                y='population',                 
                color='continent',
                text_auto=True,
                color_discrete_sequence=paleta_discreta,
                labels={'year':'Año','population':'Población','continent':'Continente'},
                title='Gráfico de barras apiladas')
    st.plotly_chart(fig,use_container_width=True)
with c3:
    dfGrupo =dfDatos[dfDatos['year'].isin([2022,2023,2024])].groupby(['year','continent']).agg({'population':'sum','fertility':'mean'}).reset_index().sort_values(by='population', ascending=False)
    fig = px.bar(dfGrupo, 
                x='year',
                y='population', 
                color='continent',                
                barmode='group',
                custom_data=['continent','fertility'],                
                color_discrete_sequence= paleta_personalizada,
                title='Gráfico de barra agrupado color por categoría y texto')        
    # Se pueden crear plantillas para tooltip que aparece al poner el mouse sobre el gráfico
    fig.update_traces(hovertemplate='<b>%{customdata[0]}</b><br>Población: %{y:,.0f}<br>Fertilidad: %{customdata[1]:,.1f} hijos')
    st.plotly_chart(fig,use_container_width=True)

st.subheader('Gráficos de barras ejes múltiples y líneas de control')
c1,c2,c3 = st.columns(3)
with c1:
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    dfGrupo =dfDatos[dfDatos['year'].isin([2020,2021,2022,2023,2024])].groupby('year').agg({'lifeExpectancy':'mean','mean_house_income':'mean'}).reset_index()
    
    fig1=go.Bar(x=dfGrupo['year'], y=dfGrupo['lifeExpectancy'], name="Expectativa de vida (Años)", offsetgroup=1)
    fig2=go.Bar(x=dfGrupo['year'], y=dfGrupo['mean_house_income'], name="Ingreso promedio anual en USD", offsetgroup=2)
    fig.add_trace(fig1,secondary_y=False)
    
    # Usar la función add_trace y especificar secondary_y axes = True.
    fig.add_trace(fig2,secondary_y=True,)
    
    # Agregar texto de título a la figura
    fig.update_layout(
        title_text="Gráfico con ejes múltiples"
    )
    
    # Nombrar x-axis
    fig.update_xaxes(title_text="Años")

    # Nombrar y-axes
    fig.update_yaxes(title_text="Edad en Años", secondary_y=False)
    fig.update_yaxes(title_text="Ingresos anuales promedio USD", secondary_y=True)
    st.plotly_chart(fig,use_container_width=True)    
with c2:
    fig = px.bar(dfAnoActual.sort_values('lifeExpectancy',ascending=False),
                 x='country',
                 y='lifeExpectancy',
                 title='Expectativa de vida por país',
                 color='continent',
                 color_discrete_sequence=paleta_discreta,
                 hover_name='continent')
    fig.update_traces(hovertemplate='<br>País: %{x}<br>Expectativa de vida: %{y:,.1f} años')
    #Línea horizontal
    fig.add_hline(y=80, #Punto del eje Y donde se desea la línea
              line_width=3, #Ancho de la línea
              line_dash="dash", #Punteada, sólida o con guiones
              line_color="green", #Color de la línea
              annotation_text="80 años", #Texto asociado a la línea
              annotation_position="top right" #Positión del texto asociado a la línea
              )
    st.plotly_chart(fig,use_container_width=True)    
with c3:
    dfSurAmerica = dfAnoActual[dfAnoActual['continent']=='South America'].sort_values('mean_house_income',ascending=False)
    fig = px.bar(dfSurAmerica, 
                    x='country',
                    y='mean_house_income',                                         
                    custom_data=['country','fertility'],
                    color = 'country',
                    color_discrete_sequence=['#387ADF'],
                    color_discrete_map ={'Colombia':'#A0153E'},
                    labels={'year':'Año','mean_house_income':'Ingresos anuales promedio USD','country':'País'},
                    title='Gráfico de barra resaltando una barra')        
    # Ocultamos la leyenda
    fig.update_layout(showlegend=False)
    # Se pueden crear plantillas para tooltip que aparece al poner el mouse sobre el gráfico
    fig.update_traces(hovertemplate='<b>%{customdata[0]}</b><br>Ingreso anual prom.: $ %{y:,.0f} USD<br>Fertilidad: %{customdata[1]:,.1f} hijos')
    st.plotly_chart(fig,use_container_width=True)

st.subheader('Gráfico de barras separado por una categoría')
dfEdadPromedio = dfDatos[dfDatos['year']<=year].groupby(['year','continent'])['median_age_year'].mean().reset_index()
fig = px.bar(dfEdadPromedio,
             x='year',
            y='median_age_year',                                                     
            labels={'year':'Año','median_age_year':'Edad promedio en años','continent':'Continente'},
            facet_col='continent',
            color='continent',            
            facet_col_wrap=3,
            color_discrete_sequence=paleta_discreta,
            height=1000,
            title='Gráfico de barra separado por continente')
fig.update_layout(legend=dict(
    orientation="h",
    yanchor="top",
    y=-0.1,
    xanchor="right",
    x=1
))
fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[1]))
st.plotly_chart(fig,use_container_width=True)

st.subheader('Gráfico de barras apiladas 100%')
fig = px.histogram(dfAnoActual.sort_values('population'), x="continent",
                   y="population", color="country",
                   barnorm='percent', text_auto=',.2f',
                   labels={'country':'País','population':'Población','continent':'Continente'},
                   color_discrete_sequence=paleta_discreta,
                   title="Barras apiladas 100%")

st.plotly_chart(fig,use_container_width=True)

st.subheader('Gráfico de Histograma de Frecuencias')
st.link_button('Ver documentacion Histogramas Plotly','https://plotly.com/python/histograms/')
c1,c2= st.columns(2)
with c1:
    fig = px.histogram(dfAnoActual.sort_values('lifeExpectancy'), 
                    x="lifeExpectancy",
                    labels={'country':'País','population':'Población','continent':'Continente'},
                    title="Histogramama de Expectativa de vida 2024",
                    nbins=10,  
                    color_discrete_sequence=paleta_discreta,
                    )
    fig.update_layout(bargap=0.2)
    st.plotly_chart(fig,use_container_width=True)
with c2:
    fig = px.histogram(dfAnoActual.sort_values('median_age_year'), 
                    x="median_age_year",
                    labels={'country':'País','population':'Población','continent':'Continente'},
                    title="Histogramama de edades promedio 2024",
                    nbins=10,  
                    color='continent',
                    color_discrete_sequence=paleta_discreta,
                    )
    fig.update_layout(bargap=0.2)
    st.plotly_chart(fig,use_container_width=True)