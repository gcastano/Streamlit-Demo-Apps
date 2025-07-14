# ==============================================================================
# LIBRERÍAS Y SU INSTALACIÓN
# ==============================================================================

# Streamlit: Una librería para crear aplicaciones web interactivas para ciencia de datos y machine learning en Python.
# Es ideal para construir dashboards y prototipos de forma rápida.
# Comando de instalación: pip install streamlit
import streamlit as st

# Pandas: Una librería fundamental para la manipulación y análisis de datos en Python. Ofrece estructuras de datos 
# como el DataFrame, que es esencial para trabajar con datos tabulares.
# Comando de instalación: pip install pandas
import pandas as pd

# st_mui_table: Un componente personalizado de Streamlit para crear tablas interactivas y avanzadas, basadas en la 
# librería Material-UI de React. Permite características como paginación, ordenamiento, filas expandibles y más,
# superando las capacidades de las tablas nativas de Streamlit.
# Comando de instalación: pip install st-mui-table
# Repositorio y documentación: https://github.com/flucas96/st-mui-table
from st_mui_table import st_mui_table

# ==============================================================================
# CONFIGURACIÓN DE LA PÁGINA DE STREAMLIT
# ==============================================================================

# st.set_page_config() configura los metadatos y el layout de la página. Debe ser el primer comando de Streamlit en ejecutarse.
# - layout="wide": Hace que el contenido de la aplicación ocupe todo el ancho de la pantalla, ideal para dashboards.
# - page_title: El título que aparece en la pestaña del navegador.
# - page_icon: El favicon que aparece en la pestaña del navegador (puede ser un emoji o una URL a una imagen).
st.set_page_config(layout="wide", page_title="Datos Demográficos de Población Mundial 2025", page_icon=":globe_with_meridians:")

# ==============================================================================
# DEFINICIÓN DE FUNCIONES
# ==============================================================================

def generarHTMLBandera_flagsapi(genc):
    """
    Genera una etiqueta HTML <img> para mostrar la bandera de un país utilizando la API de flagsapi.com.

    Esta función construye una URL a partir del código de país y la retorna dentro de una etiqueta
    de imagen HTML que Streamlit puede renderizar.

    Args:
        genc (str): El código de país GENC de 2 letras (ej. "US" para Estados Unidos).

    Returns:
        str: Una cadena de texto con el código HTML para renderizar la imagen de la bandera.
    """
    # URL base del servicio de API para las banderas.
    url_base = "https://flagsapi.com/"
    
    # Se construye la URL completa de la imagen de la bandera en formato PNG de 64x64 píxeles.
    url_bandera = f"{url_base}{genc}/flat/64.png"
    
    # Se retorna la etiqueta HTML <img> con la URL de la bandera y un texto alternativo para accesibilidad.
    return f'<img src="{url_bandera}" alt="Bandera de {genc}" style="width: 64px; height: 64px;">'

def generarHTMLBandera_flagcdn(genc):
    """
    Genera una etiqueta HTML <img> para mostrar la bandera de un país utilizando la API de flagcdn.com.

    A diferencia de la otra API, esta requiere el código de país en minúsculas.

    Args:
        genc (str): El código de país GENC de 2 letras (ej. "US" para Estados Unidos).

    Returns:
        str: Una cadena de texto con el código HTML para renderizar la imagen de la bandera.
    """
    # Se asegura que el código GENC sea una cadena de texto y se eliminan espacios en blanco al inicio o final.
    genc = str(genc).strip()
    
    # URL base del servicio de API para las banderas.
    url_base = "https://flagcdn.com/w80/"
    
    # Se construye la URL completa, convirtiendo el código GENC a minúsculas, como requiere esta API.
    url_bandera = f"{url_base}{genc.lower()}.png"
    
    # Se retorna la etiqueta HTML <img>. Streamlit renderizará este HTML como una imagen real en la tabla.
    # Documentación de esta API de Banderas: https://flagpedia.net/download/api
    return f'<img src="{url_bandera}" alt="Bandera de {genc}">'

def cargarDatos():
    """
    Carga los datos de población desde un archivo CSV, los procesa y los retorna como un DataFrame de Pandas.

    Esta función es crucial para la preparación de los datos. Realiza las siguientes transformaciones:
    1. Define los tipos de datos correctos para columnas numéricas para asegurar que el ordenamiento y los cálculos funcionen.
    2. Lee el archivo "population.csv" especificando cómo interpretar los separadores de miles (punto) y decimales (coma),
       lo cual es fundamental para trabajar con formatos de datos no anglosajones.

    Returns:
        pandas.DataFrame: Un DataFrame con los datos de población listos para ser utilizados en la aplicación.
    """
    
    # Diccionario para especificar el tipo de dato de cada columna. Esto previene que Pandas interprete
    # números como texto y asegura que las operaciones numéricas (como ordenar) funcionen correctamente.
    columnas_int = {
        "Total Population": float, "Growth Rate": float, "Population Density (per sq km)": float,
        "Total Fertility Rate": float, "Life Expectancy at Birth": float, "Under-5 Mortality Rate": float,
        "Sex Ratio of the Population": float, "Youth and Old Age (0-14 and 65+)": float,
        "Youth (0-14)": float, "Old Age (65+)": float, "Both Sexes": float, "Male": float, "Female": float
    }
    
    # pd.read_csv() lee el archivo CSV y lo convierte en un DataFrame.
    # - "population.csv": El nombre del archivo de datos fuente.
    # - dtype=columnas_int: Aplica los tipos de datos definidos previamente a cada columna durante la carga.
    # - thousands='.': Indica a Pandas que el punto (.) es un separador de miles (ej. "1.234.567").
    # - decimal=',': Indica a Pandas que la coma (,) es el separador decimal (ej. "3,14").
    # Esta configuración es vital para la correcta interpretación de datos en formatos europeos/latinos.
    dfPaises=pd.read_csv("population.csv", dtype=columnas_int, thousands='.', decimal=',')
 
    return dfPaises 

# ==============================================================================
# LÓGICA PRINCIPAL DE LA APLICACIÓN
# ==============================================================================

# Se llama a la función para cargar y pre-procesar los datos. El resultado es un DataFrame de Pandas.
dfPaises = cargarDatos()

# Se muestra el título principal de la aplicación en la página web.
st.title("Datos Demográficos de Población Mundial 2025")

# --- Controles en la Barra Lateral (Sidebar) ---
# st.sidebar crea una barra lateral para colocar widgets de control, manteniendo la interfaz principal limpia.
parPaginacion = st.sidebar.checkbox("Habilitar Paginación", value=True)
parDetalles = st.sidebar.checkbox("Habilitar Detalles", value=True)
parMostrarEncabezados = st.sidebar.checkbox("Mostrar Encabezados", value=True)
parTipoBanderas = st.sidebar.selectbox("Tipo de Banderas", ["flagsapi", "flagcdn"], index=1)
parOrdenar = st.sidebar.selectbox("Ordenar por", ["GENC", "Total Population", "Growth Rate", "Population Density (per sq km)"], index=0)
parTipoOrden = st.sidebar.selectbox("Tipo de Orden", ["ascendente", "descendente"], index=0)

# --- Transformaciones de Datos Basadas en la Interacción del Usuario ---

# Ordenar el DataFrame según la selección del usuario en la barra lateral.
# Se utiliza el método .sort_values() de Pandas, que es altamente eficiente para esta tarea.
if parTipoOrden == "ascendente":
    # ascending=True para orden ascendente (A-Z, 0-9).
    dfPaises = dfPaises.sort_values(by=parOrdenar, ascending=True)
else:
    # ascending=False para orden descendente (Z-A, 9-0).
    dfPaises = dfPaises.sort_values(by=parOrdenar, ascending=False)

# Añadir dinámicamente la columna de banderas al DataFrame.
# Primero, se selecciona la función generadora de HTML correcta según la elección del usuario.
if parTipoBanderas == "flagsapi":
    generarHTMLBandera = generarHTMLBandera_flagsapi
else:
    generarHTMLBandera = generarHTMLBandera_flagcdn

# Se inserta una nueva columna llamada "Bandera" en la primera posición (loc=0).
# El contenido de esta columna se genera aplicando la función `generarHTMLBandera` a cada elemento de la columna "GENC".
# El método .apply() de Pandas es una herramienta muy potente para aplicar una función a toda una columna (Series).
dfPaises.insert(loc=0, column="Bandera", value=dfPaises["GENC"].apply(generarHTMLBandera))


# Se crea una copia del DataFrame antes de aplicar el formato visual.
# Esta copia (`dfPaisesBase`) conservará los datos numéricos originales para futuros cálculos o visualizaciones.
dfPaisesBase = dfPaises.copy()

# Se definen las columnas numéricas que se van a formatear para una mejor visualización.
columnas_a_formatear = [
    'Total Population', 'Growth Rate', 'Population Density (per sq km)', 'Total Fertility Rate',
    'Life Expectancy at Birth', 'Under-5 Mortality Rate', 'Sex Ratio of the Population', 
    'Youth and Old Age (0-14 and 65+)', 'Youth (0-14)', 'Old Age (65+)', 'Both Sexes', 'Male', 'Female'
]
# Se itera sobre la lista de columnas para aplicar un formato de cadena.
for columna in columnas_a_formatear:
    # Se utiliza .apply() con una función lambda para transformar cada valor numérico en una cadena de texto formateada.
    # - f'{x:,.2f}': Es un f-string que formatea el número `x`. La coma (,) añade separadores de miles y `.2f` lo formatea como un flotante con 2 decimales.
    # - `<span>`: Se envuelve el resultado en una etiqueta HTML span con CSS para alinear el texto a la derecha, mejorando la legibilidad de las columnas numéricas.
    dfPaises[columna] = dfPaises[columna].apply(lambda x: f'<span style="text-align:right; display:inline-block; width:100%">{x:,.2f}</span>')

# --- Diseño de la Interfaz y Visualización de la Tabla ---

# st.columns crea un layout de columnas. [8, 2] significa que la primera columna será 4 veces más ancha que la segunda.
c1,c2 = st.columns([8,2])

# El contexto `with c1:` asegura que todo el código indentado debajo se renderice en la primera columna (la más ancha).
with c1:     
    # Se llama al componente st_mui_table para mostrar la tabla interactiva.
    celdaSeleccionada = st_mui_table(
        dfPaises,
        # Habilita o deshabilita la paginación según el control del sidebar.
        enablePagination=parPaginacion,
        # Permite aplicar CSS personalizado para ajustar el estilo de la tabla. Aquí se ajusta el padding y la fuente del encabezado.
        customCss=" .MuiTableCell-root { padding: 8px; } .MuiTableCell-head { font-weight: bold; font-size:larger;}",
        # Define los tamaños de página disponibles en el selector de paginación.
        paginationSizes=[10, 30, 50],
        # Define el espaciado y tamaño de las celdas ('small', 'medium').
        size="medium",
        padding="normal",
        # Muestra u oculta los encabezados de la tabla.
        showHeaders=parMostrarEncabezados,
        # Clave única para el componente. Es fundamental para que Streamlit mantenga el estado del componente entre re-ejecuciones.
        key="mui_table",
        # Fija el encabezado en la parte superior de la tabla al hacer scroll, muy útil para tablas largas.
        stickyHeader=True,
        # Estilos CSS para el contenedor principal de la tabla (el "papel" de Material-UI).
        paperStyle={
            "width": '100%', "overflow": 'hidden', "paddingBottom": '1px', 
            "border": '2px solid rgba(224, 224, 224, 1)'
        },
        # Define qué columnas se mostrarán en la vista de detalle expandible.
        # Si parDetalles es False, se pasa una lista vacía, desactivando la funcionalidad.
        detailColumns=["Growth Rate","Population Density (per sq km)","Total Fertility Rate","Life Expectancy at Birth","Under-5 Mortality Rate","Sex Ratio of the Population","Youth and Old Age (0-14 and 65+)","Youth (0-14)","Old Age (65+)","Both Sexes","Male","Female"] if parDetalles else [],
        # Número de columnas para la vista de detalles.
        detailColNum=4,
        detailsHeader="Detalles de Población",
        # Oculta la columna de índice del DataFrame, que a menudo no es relevante para el usuario final.
        showIndex=False,
        # Habilita el ordenamiento nativo del componente (haciendo clic en los encabezados).
        enable_sorting=True,
        # Altura máxima de la tabla antes de que aparezca una barra de scroll vertical.
        maxHeight=800,
        # Si es True, el componente devolverá información sobre la celda en la que el usuario hizo clic.
        return_clicked_cell=True
    )

# El contexto `with c2:` renderiza el contenido en la segunda columna, más pequeña.
with c2:
    # Muestra la información de la celda que fue seleccionada por el usuario. El objeto retornado es un diccionario.
    st.write("Celda seleccionada:", celdaSeleccionada)
    
    # Comprueba si el usuario ha hecho clic en alguna celda. 'celdaSeleccionada' no será None si hubo un clic.
    if celdaSeleccionada is not None:
        # Si se hizo clic, usa .iloc[] de Pandas para obtener la fila completa correspondiente al índice de la fila clickeada.
        # Se usa `dfPaisesBase` para mostrar los datos numéricos originales, sin el formato HTML.
        dfSeleccionada = dfPaisesBase.iloc[celdaSeleccionada["row"]]
    else:
        # Si no se ha hecho clic, crea un DataFrame vacío para evitar errores al intentar mostrarlo.
        dfSeleccionada = pd.DataFrame()
    
    # Muestra la fila seleccionada en un DataFrame de Streamlit, ideal para ver los datos crudos de una fila.
    st.dataframe(dfSeleccionada)