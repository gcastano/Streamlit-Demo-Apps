# Importa las librerías necesarias
import plotly.express as px  # Para crear gráficos interactivos. Instalación: pip install plotly.express
import streamlit as st  # Para crear la aplicación web. Instalación: pip install streamlit
import pandas as pd  # Para manipulación de datos. Instalación: pip install pandas
import utils # Importa un módulo personalizado, para estilos y funciones auxiliares.
import accesodatos as ad # Importa el módulo para el acceso a los datos.

# Configura la página de Streamlit
st.set_page_config(
    page_title="Dashboard de Cultivos por País",  # Título de la página
    page_icon="🌱",  # Icono de la página
    layout="wide",  # Diseño de página ancho
    initial_sidebar_state="expanded"  # Barra lateral expandida al inicio
)

# Obtiene los colores de fondo y texto del tema actual
backgroundColor = st.get_option('theme.secondaryBackgroundColor')
textColor = st.get_option('theme.textColor')
# Aplica estilos CSS personalizados desde el archivo "estilos.css"
# utils.local_css("estilos.css", backgroundColor)
utils.local_css("https://raw.githubusercontent.com/gcastano/Streamlit-Demo-Apps/refs/heads/main/streamlitMongo/estilos.css", backgroundColor)

# Define una paleta de colores para los gráficos
paleta = ['#97935C', '#95BB76', '#8BE3E1', '#E3E2D8', '#397074', '#41A2E6', '#EDA51B', '#C58CBB', '#32527B', '#793C50']

# Obtiene los tipos de datos disponibles para la selección
opcionTipoDatos=ad.obtenertipoDatos()

# Título principal del dashboard
st.title(':material/psychiatry: Dashboard Cultivos del mundo')
# Muestra información sobre la fuente de datos
st.info("2,507,765 registros [Fuente: FAO](https://www.fao.org/faostat/en/#data/QCL)")

# Agrega un control selectbox a la barra lateral para seleccionar un cultivo
opcionCultivos=ad.obtenerCultivos()
parCultivo = st.selectbox('Selecciona un cultivo', opcionCultivos, key="par-cultivos")    

# Si se ha seleccionado un cultivo
if parCultivo:
    # Obtiene los países que cultivan el cultivo seleccionado
    paisesCultivo = ad.obtenerPaises(parCultivo)
    # Obtiene las estadísticas del cultivo seleccionado
    dfEstadisticasCultivo,ultimoAnio = ad.obtenerEstadisticasCultivo(parCultivo)
    # Extrae las estadísticas totales de hectáreas, producción y rendimiento
    hecTotal=dfEstadisticasCultivo[dfEstadisticasCultivo["_id"]=="Area harvested"]["totales"].values[0]
    prodTotal=dfEstadisticasCultivo[dfEstadisticasCultivo["_id"]=="Production"]["totales"].values[0]
    yieldProm=dfEstadisticasCultivo[dfEstadisticasCultivo["_id"]=="Yield"]["totales"].values[0]
    # Calcula el número de países que cultivan el cultivo seleccionado
    paisesCultivadores = len(paisesCultivo)
    # Crea columnas para mostrar las métricas
    cols = st.columns([2,2,2,1,1])
    with cols[0]:
        # Muestra la métrica de hectáreas de cultivo
        st.metric("Hectareas de cultivo", f"{hecTotal:,.2f} has.")
    with cols[1]:
        # Muestra la métrica de producción
        st.metric("Producción", f"{prodTotal:,.2f} ton.")
    with cols[2]:
        # Muestra la métrica de rendimiento promedio
        st.metric("Rendimiento promedio", f"{yieldProm:,.2f} ton./has.")
    with cols[3]:
        # Muestra la métrica de países cultivadores
        st.metric("Paises cultivadores", paisesCultivadores)
    with cols[4]:
        # Muestra la métrica del último año de datos
        st.metric("Ultimo año", ultimoAnio)
    
    # Obtiene las estadísticas del cultivo por año
    dfDatos=ad.obtenerEstadisticasCultivoAnio(parCultivo)
    # Crea columnas para mostrar los gráficos
    cols = st.columns(3)
    # Crea el gráfico de área para las hectáreas de cultivo
    figHectareas = px.area(dfDatos[dfDatos["Element"]=="Area harvested"], x="Year", y="totales", title="Hectareas de cultivo", labels={"Area harvested":"Hectareas de cultivo"}, color_discrete_sequence=paleta)
    # Crea el gráfico de área para la producción
    figProduccion = px.area(dfDatos[dfDatos["Element"]=="Production"], x="Year", y="totales", title="Producción en toneladas", labels={"Production":"Producción"}, color_discrete_sequence=paleta[1:])
    # Crea el gráfico de área para el rendimiento
    figRendimiento = px.area(dfDatos[dfDatos["Element"]=="Yield"], x="Year", y="totales", title="Rendimiento ton/has.", labels={"Yield":"Rendimiento"}, color_discrete_sequence=paleta[2:])

    cols[0].plotly_chart(utils.aplicarFormatoChart(figHectareas,backgroundColor=backgroundColor),key="chart-hectareas")
    cols[1].plotly_chart(utils.aplicarFormatoChart(figProduccion,backgroundColor=backgroundColor),key="chart-produccion")
    cols[2].plotly_chart(utils.aplicarFormatoChart(figRendimiento,backgroundColor=backgroundColor),key="chart-rendimiento")
    
    dfDatos=ad.obtenerDatosCultivo(parCultivo)
    
    dfDatosPaisAnio = dfDatos[dfDatos["Year"]==ultimoAnio]
    cols = st.columns(3)
    figPaisesArea = px.bar(dfDatosPaisAnio.sort_values("Area harvested",ascending=False).head(10), x="Area", y="Area harvested", title="Top 10 Paises por Hectareas de cultivo", labels={"Area harvested":"Hectareas de cultivo"}, color_discrete_sequence=paleta)
    figPaisesProd = px.bar(dfDatosPaisAnio.sort_values("Production",ascending=False).head(10), x="Area", y="Production", title="Top 10 países por Producción toneladas", labels={"Production":"Producción"}, color_discrete_sequence=paleta[1:])
    figPaisesRendimiento = px.bar(dfDatosPaisAnio.sort_values("Yield",ascending=False).head(10), x="Area", y="Yield", title="Top 10 países por rendimiento", labels={"Yield":"Rendimiento"}, color_discrete_sequence=paleta[2:])
    cols[0].plotly_chart(utils.aplicarFormatoChart(figPaisesArea,backgroundColor=backgroundColor),key="chart-paises-area")
    cols[1].plotly_chart(utils.aplicarFormatoChart(figPaisesProd,backgroundColor=backgroundColor),key="chart-paises-prod")
    cols[2].plotly_chart(utils.aplicarFormatoChart(figPaisesRendimiento,backgroundColor=backgroundColor),key="chart-paises-rendimiento")

    cols = st.columns(2)
    with cols[0]:
        parDatoAnimacion= st.selectbox('Selecciona un tipo de dato para la animación', opcionTipoDatos, key="par-tipo-datos")    
        if parDatoAnimacion=="Yield":
            titulo="Rendimiento por país a lo largo de los años"
        elif parDatoAnimacion=="Area harvested":
            titulo="Hectareas de cultivo por país a lo largo de los años"
        else:
            titulo="Producción por país a lo largo de los años"
        figMapa = px.choropleth(dfDatos.sort_values("Year"), locations="Area", locationmode="country names", color=parDatoAnimacion,
                            hover_name="Area", animation_frame="Year", title=titulo,
                            color_continuous_scale=px.colors.sequential.Greens)
        st.plotly_chart(utils.aplicarFormatoChart(figMapa, backgroundColor=backgroundColor), key="chart-mapa")

    with cols[1]:
        colsint = st.columns(2)
        with colsint[0]:            
            parVariable1= st.selectbox('Selecciona variable eje x', opcionTipoDatos, key="par-variablex")    
        with colsint[1]:            
            parVariable2= st.selectbox('Selecciona variable eje y', opcionTipoDatos, key="par-variabley")
        figPlotProdvsRen = px.scatter(dfDatosPaisAnio, x=parVariable1, y=parVariable2, title=f"{parVariable1} vs {parVariable2}", labels={"Production":"Producción","Yield":"Rendimiento"}, color="Area", color_discrete_sequence=paleta)
        st.plotly_chart(utils.aplicarFormatoChart(figPlotProdvsRen, backgroundColor=backgroundColor), key="chart-prodvsren")

    with st.container(key="panel-paises"):
        colsint = st.columns(2)
        with colsint[0]:            
            parPaises = st.multiselect('Selecciona paises', paisesCultivo, key="par-paises")
        with colsint[1]:            
            parVariablePais= st.selectbox('Selecciona variable eje x', opcionTipoDatos, key="par-variablePais")    
        if parVariablePais=="Yield":
            titulo="Rendimiento por país a lo largo de los años"
        elif parVariablePais=="Area harvested":
            titulo="Hectareas de cultivo por país a lo largo de los años"
        else:
            titulo="Producción por país a lo largo de los años"
        if parPaises:
            dfDatosPais = dfDatos[dfDatos["Area"].isin(parPaises)]
            figPaises = px.line(dfDatosPais, x="Year", y=parVariablePais, title=titulo, labels={"Yield":"Rendimiento"}, color="Area", color_discrete_sequence=paleta)
            figPaises.update_traces(mode='lines+markers')
            figPaises.update_layout(hovermode='x unified')
            st.plotly_chart(utils.aplicarFormatoChart(figPaises, backgroundColor=backgroundColor, legend=True), key="chart-paises")
        else:
            st.warning("Seleccione al menos un país")
else:
    st.warning("Seleccione al menos un país y un cultivo")
