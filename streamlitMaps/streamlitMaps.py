import streamlit as st
import pandas as pd
import plotly.express as px
import folium #Librería de mapas en Python
from streamlit_folium import st_folium #Widget de Streamlit para mostrar los mapas
from folium.plugins import MarkerCluster #Plugin para agrupar marcadores

st.set_page_config(
    page_title="Visor de Mapas en Streamlit",
    page_icon="🌐",  
    layout='wide',
    initial_sidebar_state="expanded"
)

st.header('Visor de Mapas en Streamlit')
dfRestaurantes= pd.read_csv('googlemaps_comida china.csv')
dfRestaurantes['review_count']=dfRestaurantes['review_count'].fillna(1)

tab1,tab2,tab3,tab4=st.tabs(['Mapa Plotly','Mapa Choropleth','Mapa Folium' ,'Datos'])
with tab1:    
    parMapa = st.selectbox('Tipo Mapa',options=["open-street-map", "carto-positron","carto-darkmatter"])        
    parTamano = st.checkbox('Tamaño por cantidad de reviews')
    if parTamano:
        fig = px.scatter_mapbox(dfRestaurantes,lat='latitude',lon='longitude', 
                                color='rating', hover_name='name',hover_data=['review_count','full_address'],
                                zoom=10, size='review_count',height=600)
    else:
        fig = px.scatter_mapbox(dfRestaurantes,lat='latitude',lon='longitude', 
                                color='rating', hover_name='name',hover_data=['review_count','full_address'],                                
                                zoom=10,height=600)
    fig.update_layout(mapbox_style=parMapa)
    st.plotly_chart(fig,use_container_width=True)
with tab2:
    df = px.data.gapminder().query("year==2007")    
    fig = px.choropleth(df, locations="iso_alpha",
                        color="lifeExp", # lifeExp is a column of gapminder
                        hover_name="country", # column to add to hover information
                        color_continuous_scale=px.colors.sequential.Plasma)
    st.plotly_chart(fig,use_container_width=True)
    st.dataframe(df)
with tab3:
    parTipoMapa = st.radio('Tipo de marcadores',options=['Cluster','Individuales'],horizontal=True)
    m = folium.Map(location=[6.242827227796505, -75.6132478], zoom_start=15)
    if parTipoMapa=='Cluster':
        marker_cluster = MarkerCluster().add_to(m)

    for index, row in dfRestaurantes.iterrows():        
        marker = folium.Marker(        
                location=[row['latitude'], row['longitude']],
                popup=row['name'],
                icon=folium.Icon(color="red", icon="ok-sign"),
            )
        if parTipoMapa=='Cluster':
            marker.add_to(marker_cluster)
        else:
            marker.add_to(m)
    folium.plugins.Fullscreen(
        position="topright",
        title="Pantalla completa",
        title_cancel="Cancelar",
        force_separate_button=True,
    ).add_to(m)
    out = st_folium(m, height=600,use_container_width=True)
    st.write(out)
with tab4:
    st.dataframe(dfRestaurantes,use_container_width=True)

