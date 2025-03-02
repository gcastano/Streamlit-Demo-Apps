# Importar las librerías necesarias
import streamlit as st  # Librería para crear aplicaciones web interactivas. Instalar con: pip install streamlit
import tempfile # Librería para crear archivos temporales. #Ya viene instalada con python
# https://github.com/microsoft/markitdown
from markitdown import MarkItDown # Librería para convertir documentos a Markdown. Instalar con: pip install markitdown
# https://github.com/lfoppiano/streamlit-pdf-viewer
from streamlit_pdf_viewer import pdf_viewer # Librería para visualizar archivos PDF en Streamlit. Instalar con: pip install streamlit-pdf-viewer

# Configurar la página de Streamlit
st.set_page_config(
    page_title="Convertidor de documentos a Markdown", # Título de la página
    page_icon="📄", # Icono de la página
    layout="wide", # Diseño de página ancha
    initial_sidebar_state="auto", # Estado inicial de la barra lateral
)

# Mostrar un encabezado
st.header(":material/network_intelligence: Convertidor de documentos a Markdown")

# Crear un widget para subir archivos
archivo_subido = st.file_uploader("Elegir archivo", type=["pdf", "xlsx", "xls", "docx", "pptx", "csv"])

# Si se ha subido un archivo
if archivo_subido is not None:
    # Crear un archivo temporal
    with tempfile.NamedTemporaryFile(delete=False) as archivo_temporal:
        # Escribir el contenido del archivo subido en el archivo temporal
        archivo_temporal.write(archivo_subido.read())
        # Obtener la ruta del archivo temporal
        ruta_archivo_temporal = archivo_temporal.name

        # Crear una instancia de MarkItDown
        md = MarkItDown() # Set to True to enable plugins
        # Convertir el archivo a Markdown
        resultado = md.convert(ruta_archivo_temporal)
        
        #Crear tres columnas
        c1,c2,c3 = st.columns([4,4,2])
        # Mostrar el archivo original o el texto convertido en la primera columna
        with c1:
            with st.container(height=500):
                if archivo_subido.name.endswith(".pdf"):
                    pdf_viewer(archivo_temporal.name)
                else:
                    st.write(resultado.text_content)
        # Mostrar el código Markdown en la segunda columna
        with c2:
            with st.container(height=500):
                st.code(resultado.text_content)
        #Botón de descarga en la tercer columna
        with c3:
            # Obtener el nombre del archivo sin la extensión
            nombreArchivo = archivo_subido.name.split(".")[0] + ".md"
            # Crear un botón de descarga para el archivo Markdown
            st.download_button(
                label="Descargar Markdown", # Etiqueta del botón
                data=resultado.text_content, # Datos del archivo
                file_name=nombreArchivo, # Nombre del archivo descargado
                mime="text/markdown", # Tipo MIME del archivo
                icon=":material/download:",  # Icono del botón
                type="primary", # Tipo de botón
            )