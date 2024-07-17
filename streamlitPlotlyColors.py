import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Definimos los parámetros de configuración de la aplicación
st.set_page_config(
    page_title="Demo colores en Plotly", #Título de la página
    page_icon="📊", # Ícono
    layout="wide", # Forma de layout ancho o compacto
    initial_sidebar_state="expanded" # Definimos si el sidebar aparece expandido o colapsado
)

dfPeliculas = pd.read_csv('https://raw.githubusercontent.com/gcastano/datasets/main/TVMaze_Shows_Genres_encoded_1K.csv')

# Combinación de paletas
paletasCombinadas = px.colors.qualitative.Alphabet + px.colors.qualitative.Dark24
# Paletas personalizadas
# Paletas categóricas
paletaCualitativaPersonalizada=['#36BA98','#E9C46A','#F4A261',"E76F51"]
paletaCualitativaPersonalizada2=["#ef476f","#ffd166","#06d6a0","#118ab2","#073b4c"]

# Paletas contínuas
paletaContinuaPersonalizada=["#90be6d","#f9c74f","#f94144"]
paletaContinuaPersonalizadaRangos1= [(0, "red"), (0.5, "green"), (1, "blue")]
paletaContinuaPersonalizadaRangos2=[(0,"#EE4E4E"),(0.5,"#FFC700"),(0.8,"#FFF455"),(1,"#219C90")]

# carga de datos
dfPeliculasIdioma = dfPeliculas.groupby('language')['id'].count().reset_index().rename(columns={'id':'Movies'}).sort_values('Movies', ascending=False)

fig1= px.bar(dfPeliculasIdioma, x='language', y='Movies',color='language',
             title='Grafico con paleta por defecto')
fig2= px.bar(dfPeliculasIdioma, x='language', y='Movies',color='language',
             color_discrete_sequence=paletaCualitativaPersonalizada2, # Uso de paleta personalizada
             title='Grafico con paleta con menos colores que categorías')
fig3= px.bar(dfPeliculasIdioma, x='language', y='Movies',color='language',
             color_discrete_sequence=paletasCombinadas, # Uso de paletas combinadas
             title='Grafico con paletas estándar combinadas')

st.header('Manejo de colores en plotly')

cols = st.columns(3)

with cols[0]:
    st.plotly_chart(fig1)
with cols[1]:
    st.plotly_chart(fig2)
with cols[2]:
    st.plotly_chart(fig3)

dfPeliculas['Anio']=dfPeliculas['premiered'].str[:4]

dfPeliculasTipo = dfPeliculas.groupby(['type','status'])['id'].count().reset_index().rename(columns={'id':'Movies'}).sort_values('Movies', ascending=False)
dfPeliculasAnio = dfPeliculas.groupby('Anio')['id'].count().reset_index().rename(columns={'id':'Movies'}).sort_values('Movies', ascending=False)


fig1= px.bar(dfPeliculasTipo, x='type', y='Movies',color='status',
             color_discrete_sequence=paletaCualitativaPersonalizada2,
             title='Grafico con colores por defecto')
# Gráfico con paleta de colores asociado de manera personalizada para cada categoría
fig2= px.pie(dfPeliculasTipo.sort_values('Movies', ascending=False), names='status', values='Movies',color='status',
             color_discrete_map={'Ended':paletaCualitativaPersonalizada2[0],
                                 'Running':paletaCualitativaPersonalizada2[2],
                                 'To Be Determined':paletaCualitativaPersonalizada2[3],
                                 'In Development':paletaCualitativaPersonalizada2[1]
                                 },
             title='Grafico con colores asignados por etiqueta')

# Creación de diccionario de mapeo de colores para resaltar el año 2020
mapaResaltarAnio = {a: paletaCualitativaPersonalizada2[0] if a == '2020' 
                    else paletaCualitativaPersonalizada2[3] 
                    for a in dfPeliculasAnio['Anio'].unique()}

# Gráfico con barra resaltada
fig3= px.bar(dfPeliculasAnio, x='Anio', y='Movies',color='Anio',
             color_discrete_map=mapaResaltarAnio,
             title='Grafico con barra resaltada por mapeo de etiquetas')
# Ocultamos la leyenda ya que aparecerían muchos colores iguales y uno solo diferente
fig3.update_traces(showlegend=False)

cols = st.columns(3)

with cols[0]:
    st.plotly_chart(fig1)
with cols[1]:
    st.plotly_chart(fig2)
with cols[2]:
    st.plotly_chart(fig3)

# Cargamos los datos para mostrar los mapas
df = px.data.gapminder().query("year==2007")

cols = st.columns(3)
with cols[0]:
    # Mapa de calor con colores estándar
    parOrden1 = st.radio('Orden paleta',options=['Normal','Invertida'],horizontal=True,key='orden1')
    paleta=px.colors.sequential.Aggrnyl
    if parOrden1=='Invertida':
        # Los mapas estándar se invierten adicionano _r al nombre de la paleta
        paleta=px.colors.sequential.Aggrnyl_r

    fig1 = px.choropleth(df, locations="iso_alpha",
                    color="gdpPercap", 
                    hover_name="country", 
                    color_continuous_scale=paleta,
                    title="Mapa de calor con paleta de plotly")
    st.plotly_chart(fig1)
with cols[1]:
    # Mapa de calor con paleta personalizada de 3 niveles
    parOrden2 = st.radio('Orden paleta',options=['Normal','Invertida'],horizontal=True,key='orden2')
    paleta=paletaContinuaPersonalizada
    if parOrden2=='Invertida':
        paleta=paletaContinuaPersonalizada[::-1]
    
    fig2 = px.choropleth(df, locations="iso_alpha",
                        color="pop", 
                        hover_name="country", 
                        color_continuous_scale=paleta,
                        title="Mapa con paleta personalizada 3 colores")
    st.plotly_chart(fig2)
with cols[2]:            
    # Mapa de calor con paleta personalizada en colores y rangos
    fig3 = px.choropleth(df, locations="iso_alpha",
                    color="lifeExp", 
                    hover_name="country", 
                    color_continuous_scale=paletaContinuaPersonalizadaRangos2,
                    title="Mapa con paleta personalizada 4 rangos y segementos personalizados")
    st.plotly_chart(fig3)