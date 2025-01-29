# Importa las librerías necesarias
import duckdb  # DuckDB: Base de datos embebida de alto rendimiento. Instalación: pip install duckdb
import streamlit as st  # Streamlit: Framework para crear aplicaciones web interactivas para Machine Learning y Data Science. Instalación: pip install streamlit
from io import StringIO  # StringIO: Clase para manejar streams de texto en memoria.  Forma parte de la librería estándar de Python.
from code_editor import code_editor # code-editor: Componente de Streamlit para editar código. Instalación: pip install streamlit-code-editor


# Configura la página de Streamlit
st.set_page_config(
    page_title="Consultas con DuckDB",  # Título de la página
    page_icon="🤖",  # Icono de la página
    layout="wide",  # Diseño de página ancho
    initial_sidebar_state="expanded"  # Barra lateral expandida al inicio
)

def eliminarTablas():
    """
    Elimina todas las tablas existentes en la base de datos DuckDB.

    Esta función obtiene una lista de todas las tablas presentes en la base de datos DuckDB
    y las elimina una por una. Utiliza la consulta "SHOW TABLES;" para obtener los nombres
    de las tablas y luego ejecuta "DROP TABLE IF EXISTS" para eliminar cada tabla.

    Returns:
        None
    """
    tablas = duckdb.query("SHOW TABLES;").df() 
    # Elimina todas las tablas existentes en DuckDB
    for tabla in tablas['name'].values:        
        duckdb.query("DROP TABLE IF EXISTS " + tabla + ";")

st.header("Streamlit con DuckDB") # Título principal de la aplicación

# Verifica si la clave "archivos" está en el estado de la sesión de Streamlit
if "archivos" not in st.session_state:
    # Si no está, inicializa la clave "archivos" con el valor 0
    st.session_state.archivos = 0    
# Crea un expander para cargar las fuentes de datos
with st.expander("Fuentes de datos"):
    # Permite al usuario subir múltiples archivos CSV
    listaArchivos = st.file_uploader("Choose CSV files", accept_multiple_files=True, type="csv")        

# Procesa los archivos subidos si existen
if listaArchivos:
    # Obtiene las tablas existentes en DuckDB
    tablas = duckdb.query("SHOW TABLES;").df() 
    
    # Verifica si es la primera vez que se suben archivos
    if st.session_state.archivos == 0:
        # Actualiza el estado de la sesión con el número de archivos subidos
        st.session_state.archivos = len(listaArchivos)
    # Si el número de archivos subidos ha cambiado
    elif st.session_state.archivos != len(listaArchivos):
        # Eliminamos las tablas existentes en DuckDB        
        eliminarTablas()
        # Actualiza la lista de tablas existentes en DuckDB
        tablas = duckdb.query("SHOW TABLES;").df()
    
    # Itera sobre los archivos CSV subidos
    for archivo in listaArchivos:
        # Lee el contenido del archivo en memoria
        bytes_data = StringIO(archivo.getvalue().decode("utf-8"))        
        # Define el nombre de la tabla a partir del nombre del archivo
        table_name = archivo.name[:-4]
        # Crea la tabla en DuckDB si no existe
        if table_name not in tablas['name'].values:
            duckdb.read_csv(bytes_data).to_table(table_name)        
    # Obtiene las tablas existentes en DuckDB
    tablas = duckdb.query("SHOW TABLES;").df()
    # Crea dos columnas en el layout
    c1,c2 = st.columns([3,7])
    # En la primera columna, muestra las tablas y sus columnas.
    with c1:
        st.subheader(":material/database: Tablas")
        arrayTablas = [] # Crea un array para almacenar la información de las tablas y columnas para el autocompletado.
        # Recorre las tablas
        for tabla in tablas['name'].values:
            st.write(f'##### :material/table: {tabla}') # Muestra el nombre de la tabla.
            # Obtiene la información de las columnas de la tabla
            columnas = duckdb.query(f"DESCRIBE {tabla};").df()
            st.table(columnas) # Muestra la información de las columnas
            # Agrega la información de la tabla al array para el autocompletado
            itemTabla= {
                        "caption": tabla,
                        "value": tabla,
                        "meta": "TABLA",
                        "name": "Tabla",
                        "score": 400
                    }
            arrayTablas.append(itemTabla)
            # Recorre las columnas de la tabla
            for columna in columnas['column_name'].values:
                # Agrega la información de la columna al array para el autocompletado
                itemColumna = {
                        "caption": columna,
                        "value": f"{columna}",
                        "meta": "COLUMNA",
                        "name": "Columna",
                        "score": 300
                    }
                arrayTablas.append(itemColumna)
    # En la segunda columna, permite al usuario ingresar y ejecutar consultas SQL.
    with c2:
        st.subheader(":material/search: Consulta")
        st.info("ctrl+enter para ejecutar la consulta") # Muestra un mensaje informativo sobre como ejecutar la consulta.
        # Muestra el editor de código SQL con autocompletado.        
        res = code_editor(code="", lang="sql", key="editor",height="300px", completions=arrayTablas)
        st.subheader(":material/table_view: Resultado")
        # Si se ha ingresado una consulta:
        if res["text"]:
            # Ejecuta la consulta en DuckDB.
            dfResultado = duckdb.query(res["text"]).df()
            # Convierte el resultado a CSV y permite descargarlo.
            csv = dfResultado.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Descargar CSV",
                data=csv,
                file_name='resultado.csv',
                mime='text/csv',
            )
            # Muestra el resultado en una tabla.
            st.dataframe(dfResultado,use_container_width=True)
else:
    eliminarTablas()