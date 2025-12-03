import streamlit as st
# Comando de instalación: pip install streamlit
# Streamlit se utiliza para crear aplicaciones web interactivas para ciencia de datos de forma rápida.

import pandas as pd
# Comando de instalación: pip install pandas
# Pandas es la librería estándar para la manipulación y análisis de datos estructurados (DataFrames).

from datetime import datetime
# Librería estándar de Python (no requiere instalación).
# Se usa para obtener la fecha y hora actual.

# streamlitPlotlyMarginChart.py
import plotly.express as px
# Comando de instalación: pip install plotly
# Plotly Express es una interfaz de alto nivel para crear gráficos interactivos y complejos con poco código.

# Configuración de la página de la aplicación
st.set_page_config(page_title="Gráficos de dispersión mejorados", layout="wide")

# URL del dataset (formato CSV)
DATA_URL = "https://raw.githubusercontent.com/gcastano/datasets/refs/heads/main/gapminder_data.csv"

@st.cache_data
def load_data(url: str) -> pd.DataFrame:
    """
    Carga datos desde una URL remota y los almacena en caché para optimizar el rendimiento.
    
    Args:
        url (str): La dirección URL del archivo CSV.
        
    Returns:
        pd.DataFrame: Un DataFrame de pandas con los datos cargados.
    """
    df = pd.read_csv(url)
    return df

# Carga inicial de datos
df = load_data(DATA_URL)

st.title("Gráficos de Dispersión mejorados con gráficós de Margen y animaciones")

# --- SECCIÓN: BARRA LATERAL (SIDEBAR) Y FILTROS ---
st.sidebar.header("Filtros")

# 1. Obtener lista de años únicos y ordenarlos
anos = sorted(df['year'].unique())
ano_actual = datetime.now().year

# Selector de año (Slider)
# Nota: Si el año actual es mayor al máximo del dataset, el slider se ajustará al valor más cercano permitido.
ano = st.sidebar.select_slider("Ano", options=anos, value=ano_actual)

# 2. Obtener lista de continentes únicos
continentes = df['continent'].unique().tolist()
# Multiselector para continentes
continentes_seleccionados = st.sidebar.multiselect("Continentes", options=continentes, default=continentes)

# 3. Filtrado dinámico de países basado en los continentes seleccionados
# Pandas: df[condición] filtra las filas. .unique() obtiene valores únicos.
paises = df[df['continent'].isin(continentes_seleccionados)]['country'].unique().tolist()
paises_seleccionados = st.sidebar.multiselect("Paises (opcional)", options=paises, default=[])

# --- SECCIÓN: TRANSFORMACIÓN DE DATOS (FILTRADO) ---

# Filtrar por año seleccionado
filtrado = df[df['year'] == ano]

# Filtrar por continentes si hay selección
if continentes_seleccionados:
    # Pandas: .isin() verifica si el valor de la columna está en la lista dada
    filtrado = filtrado[filtrado['continent'].isin(continentes_seleccionados)]

# Filtrar por países si el usuario seleccionó alguno específicamente
if paises_seleccionados:
    filtrado = filtrado[filtrado['country'].isin(paises_seleccionados)]

# Definición de variables numéricas disponibles para los ejes
variables = ['fertility', 'lifeExpectancy',
             'mean_house_income', 'median_age_year', 'population']

# Tipos de gráficos marginales disponibles en Plotly
margen_grafico = ["Ninguno","histogram", "rug", "box", "violin"]

# --- SECCIÓN: CONFIGURACIÓN DE EJES Y GRÁFICOS ---

# Selectores para el Eje X
with st.container(horizontal=True): # Disposición horizontal
    var_x = st.selectbox("Variable X", options=variables, index=0)
    margen_x = st.selectbox("Margen X", options=margen_grafico, index=2)
    if margen_x == "Ninguno":
        margen_x = None

# Selectores para el Eje Y
with st.container(horizontal=True):
    var_y = st.selectbox("Variable Y", options=variables, index=1)
    margen_y = st.selectbox("Margen Y", options=margen_grafico, index=3)
    if margen_y == "Ninguno":
        margen_y = None

# Selector de color (variable categórica para agrupar)
color = st.selectbox("Color", options=['Ninguno', 'continent', 'country'], index=0)
if color == 'Ninguno':
    color = None

# --- GRÁFICO 1: SCATTER PLOT ESTÁTICO CON MÁRGENES ---
# px.scatter crea un gráfico de dispersión.
# marginal_x/y añade un gráfico secundario en los márgenes para ver la distribución de esa variable.
fig = px.scatter(filtrado, x=var_x, y=var_y, 
                 color=color, hover_name="country",
                 title=f"{var_x} vs {var_y} Ano: {ano}",
                 marginal_x=margen_x, marginal_y=margen_y,
                 )

# Mostrar el gráfico en Streamlit dentro de un contenedor con borde
with st.container(border=True):
    st.plotly_chart(fig, use_container_width=True)

# --- GRÁFICO 2: ANIMACIÓN TEMPORAL ---

# Slider para seleccionar un rango de años
parRangoAnos = st.slider("Rango de Anos", min_value=min(anos), max_value=max(anos), value=(ano_actual-10, ano_actual), step=1)

# Pandas: Filtrado complejo con múltiples condiciones (& significa AND)
# Seleccionamos filas donde el año sea mayor/igual al inicio Y menor/igual al fin del rango
df_rango = df[(df['year'] >= parRangoAnos[0]) & (df['year'] <= parRangoAnos[1])]

# Crear gráfico animado
# animation_frame: define la variable que cambia en cada frame (el tiempo)
# animation_group: define qué entidad se rastrea a través de los frames (el país)
fig2 = px.scatter(df_rango, x=var_x, y=var_y, 
                 color=color, hover_name="country",
                 title=f"{var_x} vs {var_y} Rango Anos: {parRangoAnos[0]} - {parRangoAnos[1]}",
                 animation_frame="year", animation_group="country",
                 )

with st.container(border=True):
    st.subheader("Gráfico Animado por Rango de Años")
    st.plotly_chart(fig2, use_container_width=True)