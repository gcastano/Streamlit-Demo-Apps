import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from numerize.numerize import numerize
import utils

 
 
# https://www.behance.net/search/projects/dashboard%20green?tracking_source=typeahead_search_direct

st.set_page_config(
    page_title="Dashboard análisis demográfico mundial",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# color_discrete_sequence=px.colors.carto.Pastel
color_discrete_sequence=["#1ea47e","#e33f2b",'#fbac5d','#82858d','#4ce1ee','#ffa111']
color_continuous_scale=['#2effc3','#25c99a','#105743']

# https://medium.muz.li/dashboards-inspiration-2018-77b3ab185483

# Cargamos archivo de estilos
utils.local_css('estilo.css')


# Obtenemos año actual
today = datetime.date.today()
year = today.year

# Cargamos el dataframe desde un CSV
dfDatos = pd.read_csv('https://raw.githubusercontent.com/gcastano/datasets/main/gapminder_data.csv')

# Declaramos los parámetros en la barra lateral
with st.sidebar:
    # Filtro de continente
    parContinente=st.multiselect('Continente',options=dfDatos['continent'])
    # Filtro de rango de números
    parAno =  st.slider('Ano',min_value=dfDatos['year'].min(),max_value=dfDatos['year'].max(),value=(dfDatos['year'].min(),dfDatos['year'].max()))    
    anoIni =parAno[0]
    anoFin=parAno[1]

# Si hay continente seleccionado aplicamos filtro
if len(parContinente)>0:
    dfDatos=dfDatos[dfDatos['continent'].isin(parContinente)]

# Obtenemos los datos del año actual
dfAnoActual = dfDatos[dfDatos['year']==year]
# Obtenemos los datos del año anterior
dfAnoAnterior = dfDatos[dfDatos['year']==year-1]

# Filtramos los datos en el rango de años
dfDatos=dfDatos.query(f'year >={anoIni} and year<={anoFin}')

st.header('Tablero de indicadores básicos de población mundial')

# Mostramos las métricas
st.subheader(f'Indicadores {year}')
# Declaramos 5 columnas de igual tamaño
c1,c2,c3,c4,c5 = st.columns(5)
with c1:
    fertilityAct= dfAnoActual['fertility'].mean()
    fertilityAnt= dfAnoAnterior['fertility'].mean()
    variacion=fertilityAnt-fertilityAct            
    st.metric(f"Fertilidad promedio",f'{fertilityAct:.2f} hijos')
with c2:
    lifeExpectancyAct= dfAnoActual['lifeExpectancy'].mean()
    lifeExpectancyAnt= dfAnoAnterior['lifeExpectancy'].mean()
    variacion=lifeExpectancyAnt-lifeExpectancyAct    
    st.metric(f"Expectativa de vida al nacer",f'{lifeExpectancyAct:.0f} años', f'{variacion:.1f}')    
with c3:
    mean_house_incomeAct= dfAnoActual['mean_house_income'].mean()
    mean_house_incomeAnt= dfAnoAnterior['mean_house_income'].mean()
    variacion=mean_house_incomeAnt-mean_house_incomeAct
    dato=numerize(mean_house_incomeAct)    
    st.metric(f"Ingreso familiar promedio",f'US $ {dato}', f'{variacion:.2f}')          
    
with c4:
    median_age_yearAct= dfAnoActual['median_age_year'].mean()
    median_age_yearAnt= dfAnoAnterior['median_age_year'].mean()
    variacion=median_age_yearAnt-median_age_yearAct    
    st.metric(f"Edad promedio",f'{median_age_yearAct:,.2f} años', f'{variacion:.2f}')    
with c5:
    populationAct= dfAnoActual['population'].sum()
    populationAnt= dfAnoAnterior['population'].sum()
    variacion=populationAnt-populationAct
    dato=numerize(populationAct)
    st.metric(f"Población mundial",f'{dato}', f'{variacion:,.0f}')

# Declaramos 2 columnas en una proporción de 60% y 40%
c1,c2 = st.columns([60,40])
with c1:
    dfPoblacionAno = dfDatos.groupby('year').agg({'population':'sum'}).reset_index()
    fig = px.line(dfPoblacionAno,x='year',y='population', title='Población mundial', color_discrete_sequence=color_discrete_sequence)
    fig.add_vline(x=year, #Punto del eje X donde se desea la línea
                line_width=3, #Ancho de la línea
                line_dash="dash", #Punteada, sólida o con guiones
                line_color="green", #Color de la línea
                annotation_text="Año actual", #Texto asociado a la línea
                annotation_position="top left" #Positión del texto asociado a la línea
                )    
    st.plotly_chart(utils.aplicarFormatoChart(fig),use_container_width=True)    
    
with c2:
    dfPoblacionContinente = dfAnoActual.groupby('continent').agg({'population':'sum'}).reset_index()
    fig = px.bar(dfPoblacionContinente,x='continent',y='population', title=f'Población por continente {year}', color='continent',text_auto=',.0f',
                 color_discrete_sequence=color_discrete_sequence)
    fig.update_layout(showlegend=False) #Determina si se muestra o no la leyenda
    st.plotly_chart(utils.aplicarFormatoChart(fig),use_container_width=True)

c1,c2 = st.columns([60,40])
with c1:
    dfExpectativaVida = dfDatos.groupby(['year','continent']).agg({'lifeExpectancy':'mean'}).reset_index()
    fig = px.line(dfExpectativaVida,x='year',y='lifeExpectancy', title='Expectativa de vida al nacer por continente',color='continent',
                  color_discrete_sequence=color_discrete_sequence)
    fig.add_vline(x=year, #Punto del eje X donde se desea la línea
                line_width=3, #Ancho de la línea
                line_dash="dash", #Punteada, sólida o con guiones
                line_color="green", #Color de la línea
                annotation_text="Año actual", #Texto asociado a la línea
                annotation_position="top left" #Positión del texto asociado a la línea
                )
    st.plotly_chart(utils.aplicarFormatoChart(fig),use_container_width=True)
with c2:
    dfExpectativaVidaActual = dfAnoActual.groupby('continent').agg({'lifeExpectancy':'mean'}).reset_index().sort_values(by='lifeExpectancy')
    fig = px.bar(dfExpectativaVidaActual,x='lifeExpectancy',y='continent', title=f'Expectativa de vida {year}', color='continent',text_auto=',.0f',
                 color_discrete_sequence=color_discrete_sequence)
    fig.update_layout(showlegend=False) #Determina si se muestra o no la leyenda
    st.plotly_chart(utils.aplicarFormatoChart(fig),use_container_width=True)

c1,c2= st.columns(2)
with c1:    
    st.subheader('Top 10 países más pobres')
    # st.dataframe(dfAnoActual.sort_values(by='mean_house_income').head(10)[['continent','country','mean_house_income']],hide_index=True, use_container_width=True)
    utils.generarTabla(dfAnoActual.sort_values(by='mean_house_income').head(10)[['continent','country','mean_house_income']])
with c2:    
    st.subheader('Top 10 países más ricos')
    # st.dataframe(dfAnoActual.sort_values(by='mean_house_income',ascending=False).head(10)[['continent','country','mean_house_income']],hide_index=True, use_container_width=True)
    utils.generarTabla(dfAnoActual.sort_values(by='mean_house_income',ascending=False).head(10)[['continent','country','mean_house_income']])

with st.container():
    df = px.data.gapminder().query("year==2007")
    dfMapa = dfAnoActual.merge(df,how='inner',on='country')    
    fig = px.choropleth(dfMapa, locations="iso_alpha",
                        color="mean_house_income", # lifeExp is a column of gapminder
                        hover_name="country", # column to add to hover information
                        color_continuous_scale= color_continuous_scale,#px.colors.sequential.Purples,
                        title='Mapa de ingresos anuales en dólares')
    st.plotly_chart(utils.aplicarFormatoChart(fig),use_container_width=True)