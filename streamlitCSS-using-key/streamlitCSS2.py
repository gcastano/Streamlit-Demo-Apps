# Importa las librerías necesarias
import plotly.express as px  # Para crear gráficos interactivos. Instalación: pip install plotly.express
import streamlit as st  # Para crear la aplicación web. Instalación: pip install streamlit
import pandas as pd  # Para manipulación de datos. Instalación: pip install pandas
import utils # Importa un módulo personalizado, para estilos y funciones auxiliares.

# Configura la página de Streamlit
st.set_page_config(
    page_title="Dashboard vuelos Estados Unidos",  # Título de la página
    page_icon="✈️",  # Icono de la página
    layout="wide",  # Diseño de página ancho
    initial_sidebar_state="expanded"  # Barra lateral expandida al inicio
)

# Obtiene los colores de fondo y texto del tema actual
backgroundColor = st.get_option('theme.secondaryBackgroundColor')
textColor = st.get_option('theme.textColor')
# Aplica estilos CSS personalizados desde el archivo "estilos.css"
utils.local_css("estilos.css", backgroundColor)

# Define una paleta de colores para los gráficos
paleta = ['#DA4D4A', '#3F79E4', '#26B559', '#E3E2D8', '#397074', '#41A2E6', '#EDA51B', '#C58CBB', '#32527B', '#793C50']

# Lee el conjunto de datos desde una URL
dfDatos = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2011_february_us_airport_traffic.csv')
# Muestra un título en la aplicación
st.title('Dashboard con Streamlit y CSS')

# Crea una barra lateral
with st.sidebar:
    # Agrega un control selectbox a la barra lateral para seleccionar un estado
    parEstado = st.selectbox('Selecciona un estado', ['Todos'] + dfDatos['state'].unique().tolist(), key="par-estado")

# Filtra los datos según el estado seleccionado
if parEstado != 'Todos':
    dfDatos = dfDatos[dfDatos['state'] == parEstado]

# Agrupa los datos por estado y los ordena
dfDatosEstado = dfDatos.groupby('state').sum().reset_index().sort_values('cnt', ascending=False).reset_index()
# Crea un grupo "Otros" si se selecciona "Todos" los estados
if parEstado == 'Todos':
    valor10 = dfDatosEstado.iloc[9]['cnt']
    dfDatosEstado['grupo'] = dfDatosEstado.apply(lambda row: row['state'] if row['cnt'] >= valor10 else 'Otros', axis=1)
else:
    dfDatosEstado['grupo'] = dfDatosEstado['state']

# Crea un gráfico de dispersión geográfico con Plotly Express
fig = px.scatter_geo(
    dfDatos,
    lat='lat',
    lon='long',
    color='airport',
    hover_name='airport',
    size='cnt',
    projection='albers usa',
    title="Tráfico de Aeropuertos en USA",
    color_discrete_sequence=paleta
)

# Actualiza la configuración del mapa
fig.update_geos(
    bgcolor=backgroundColor,
    showcoastlines=True,
    coastlinecolor="white",
    showland=True,
    landcolor="black",
    showocean=True,
    oceancolor="black"
)

fig.update_layout(map_style="dark")

# Crea un gráfico de barras con Plotly Express
fig2 = px.bar(
    dfDatos,
    x='airport',
    y='cnt',
    title="Tráfico de Aeropuertos en USA",
    color_continuous_scale=paleta
)

# Crea un gráfico de pastel con Plotly Express
fig3 = px.pie(
    dfDatosEstado,
    values='cnt',
    names='grupo',
    title='Tráfico por estados en USA',
    color_discrete_sequence=paleta,
)
fig3.update_traces(textposition='outside', textinfo='percent+label')

# Calcula algunas métricas
aeropuertos = dfDatos['airport'].nunique()
estados = dfDatos['state'].nunique()
maxVuelos = dfDatos['cnt'].max()
totalVuelos = dfDatos['cnt'].sum()

# Crea columnas para mostrar las métricas
columnas = st.columns(4)
with st.container(key='container-indicadores'):
    with columnas[0]:
        st.metric(label='Aeropuertos', value=f"{aeropuertos:,.0f}")
    with columnas[1]:
        st.metric(label='Estados', value=f"{estados:,.0f}")
    with columnas[2]:
        st.metric(label='Vuelos', value=f"{totalVuelos:,.0f}")
    with columnas[3]:
        st.metric(label='Máximo de vuelos', value=f"{maxVuelos:,.0f}")

# Crea dos columnas para mostrar los gráficos
c1, c2 = st.columns([6, 4])
with c1:
    st.plotly_chart(
        utils.aplicarFormatoChart(
            fig, 
            legend=True, 
            backgroundColor=backgroundColor, 
            textcolor=textColor
        ), 
        key='chart-aeropuertos' # genera clases CSS st-key-chart-aeropuertos
    )
with c2:
    st.plotly_chart(
        utils.aplicarFormatoChart(
            fig3, 
            backgroundColor=backgroundColor, 
            textcolor=textColor
        ), 
        key='chart-pie' # genera clases CSS st-key-chart-pie
    )

# Crea dos columnas para mostrar un gráfico y una tabla de datos
c3, c4 = st.columns([6, 4])
with c3:
    st.plotly_chart(
        utils.aplicarFormatoChart(
            fig2, 
            controls=True, 
            backgroundColor=backgroundColor, 
            textcolor=textColor
        ), 
        key='chart-barras' # genera clases CSS st-key-chart-barras
    )
with c4:
    st.subheader('Tabla de datos')
    st.dataframe(dfDatosEstado, key='tabla-estados', use_container_width=True)

with st.container(key='container-texto'):
    st.write('Este es un ejemplo de cómo aplicar estilos CSS a una aplicación de Streamlit utilizando la clave `key` para identificar los elementos y evitar que se recarguen al cambiar de estado.')