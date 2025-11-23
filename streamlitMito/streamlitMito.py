# ----------------------------------------------------------------------------
# 1. IMPORTACIÓN DE LIBRERÍAS
# ----------------------------------------------------------------------------

# Importamos la librería Streamlit, que nos permite construir la aplicación web.
# La renombramos a 'st' por convención para que el código sea más corto y legible.
import streamlit as st

# De la librería de Mito, importamos específicamente el componente 'spreadsheet',
# que es la hoja de cálculo interactiva que se integrará en nuestra app de Streamlit.
# pip install mitosheet
from mitosheet.streamlit.v1 import spreadsheet

# ----------------------------------------------------------------------------
# 2. CONFIGURACIÓN DE LA PÁGINA DE STREAMLIT
# ----------------------------------------------------------------------------

# st.set_page_config() configura los ajustes generales de la página de la aplicación.
# - layout="wide": Hace que el contenido de la aplicación ocupe todo el ancho de la pantalla.
# - page_title: Establece el título que aparecerá en la pestaña del navegador.
st.set_page_config(layout="wide", page_title='Mito in Streamlit')

# st.title() añade un título principal visible en la parte superior de la aplicación.
st.title('Mito in Streamlit')

# st.container() crea un contenedor para agrupar varios elementos.
# - horizontal=True: Permite que los elementos dentro del contenedor se organicen uno al lado del otro si hay espacio.
with st.container(horizontal=True):
    # st.info() muestra un mensaje informativo con un ícono de información.
    st.info('Esta es una demostración de [Mito Python Spreadsheet automation](https://www.trymito.io/) integrada con Streamlit.')
    st.info("Documentación de Mito: https://docs.trymito.io/mito-for-streamlit/getting-started-with-mito-for-streamlit")

# st.markdown() permite escribir texto con formato Markdown para descripciones, enlaces, etc.
st.markdown('Sube un archivo CSV para comenzar, o utiliza los datos de ejemplo proporcionados.')

# ----------------------------------------------------------------------------
# 3. LÓGICA DE CARGA DE DATOS
# ----------------------------------------------------------------------------

# st.file_uploader() crea un widget en la app que permite al usuario subir un archivo.
# - "Carga un archivo CSV": Es el texto que se muestra en el widget.
# - type=["csv"]: Especifica que solo se aceptan archivos con la extensión .csv.
# La variable 'uploaded_file' contendrá el archivo subido por el usuario, o será 'None' si no se ha subido nada.
uploaded_file = st.file_uploader("Carga un archivo CSV", type=["csv"])

# Se evalúa si el usuario ha subido un archivo.
if uploaded_file is not None:
    # Si se subió un archivo, importamos la librería pandas.
    import pandas as pd
    
    # Leemos el archivo CSV subido y lo cargamos en un DataFrame de pandas.
    # Un DataFrame es una estructura de datos tabular, similar a una hoja de cálculo.
    df = pd.read_csv(uploaded_file)
    
    # Llamamos a la función spreadsheet() de Mito, pasándole el DataFrame que acabamos de crear.
    # Esta función renderiza la hoja de cálculo interactiva en la app de Streamlit.
    # Devuelve dos valores:
    # - new_dfs: Un diccionario que contiene los DataFrames resultantes de las modificaciones del usuario.
    # - code: Una cadena de texto con el código Python generado automáticamente por Mito.
    new_dfs, code = spreadsheet(df)
else:
    # Si no se ha subido ningún archivo, Mito cargará los datos de ejemplo que se encuentren
    # en la carpeta especificada en 'import_folder'. En este caso, la carpeta 'data'.
    new_dfs, code = spreadsheet(import_folder='./data/')

# ----------------------------------------------------------------------------
# 4. VISUALIZACIÓN DE RESULTADOS
# ----------------------------------------------------------------------------

# Verificamos si el diccionario 'new_dfs' contiene algún DataFrame.
# Esto es para asegurarnos de que el usuario ha interactuado con Mito y hay algo que mostrar.
if len(new_dfs.keys()) > 0:
    # st.tabs() crea pestañas para organizar el contenido.
    # En este caso, creamos una para ver los datos y otra para ver el código.
    tabDataframe, tabCode = st.tabs(["DataFrame", "Código"])

    # Contenido de la primera pestaña: "DataFrame"
    with tabDataframe:
        # st.selectbox() crea una lista desplegable para que el usuario elija qué DataFrame ver.
        # Esto es útil porque en Mito se pueden crear varios DataFrames a partir del original.
        # - "Selecciona dataframe:": El texto que se muestra sobre el selector.
        # - options: La lista de opciones, que son los nombres (keys) de los DataFrames en el diccionario 'new_dfs'.
        parDataframe = st.selectbox("Selecciona dataframe:", options=list(new_dfs.keys()))
        
        # st.dataframe() muestra el DataFrame seleccionado por el usuario en una tabla interactiva.
        st.dataframe(new_dfs[parDataframe])
    
    # Contenido de la segunda pestaña: "Código"
    with tabCode:
        # st.code() muestra un bloque de código con formato y resaltado de sintaxis.
        # Aquí mostramos el código Python generado por Mito.
        st.code(code)