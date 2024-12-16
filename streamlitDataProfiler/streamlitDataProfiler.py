# Instalar las librerías necesarias
# streamlit: framework web para crear interfaces de usuario interactivas para aplicaciones de Python.
# pip install streamlit
import streamlit as st

# pandas:  librería para manipulación y análisis de datos.
# pip install pandas
import pandas as pd

# pandas-profiling: librería para generar reportes de análisis exploratorio de datos.
# pip install pandas-profiling
import pandas_profiling as pp


# streamlit-pandas-profiling: librería para integrar pandas-profiling con streamlit.
# pip install streamlit-pandas-profiling
from streamlit_pandas_profiling import st_profile_report


# Configura la página de Streamlit
st.set_page_config(
    page_title="Herramienta de análisis de datos",  # Título de la página
    page_icon="🔍",  # Icono de la página
    layout="wide",  # Diseño de página amplio
    initial_sidebar_state="expanded"  # Barra lateral expandida al inicio
)

# Título de la aplicación
st.title("Perfilador de datos con Ydata ")
# Enlace a la documentación de Ydata Profiling
st.markdown("https://docs.profiling.ydata.ai/latest/")

# Crea una barra lateral
sb = st.sidebar
# Crea un widget para subir archivos
archivo = sb.file_uploader("Seleccione un archivo csv o excel", type=["xlsx", "csv"])

# Si se ha seleccionado un archivo
if archivo is not None:
    # Obtiene la extensión del archivo
    file_extension = archivo.name.split(".")[-1].lower()

    # Lee el archivo según su extensión
    if file_extension == "csv":
        archivo1 = pd.read_csv(archivo)
    elif file_extension in ["xls", "xlsx"]:
        archivo1 = pd.read_excel(archivo)
    else:
        # Muestra un mensaje de error si el archivo no es soportado
        st.error("Error: Archivo no soportado")
        archivo1 = None

    # Si el archivo se cargó correctamente y no está vacío
    if archivo1 is not None and not archivo1.empty:
        # Crea un botón para generar el reporte
        btnGenerar = sb.button("Generar Reporte")
    else:
        # Muestra un mensaje si no se ha cargado un archivo
        st.write("Por favor cargar un archivo de tipo CSV o Excel")

    # Si se presiona el botón "Generar Reporte"
    if btnGenerar:
        # Genera el reporte de pandas-profiling
        pr = archivo1.profile_report()
        # Muestra el reporte en Streamlit
        st_profile_report(pr)