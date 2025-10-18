# --- LIBRERÍAS Y CÓMO INSTALARLAS ---

# Streamlit: Es el framework principal para construir la aplicación web.
# Permite crear dashboards y aplicaciones de datos interactivas con Python puro.
# Instalación: pip install streamlit
import streamlit as st

# Pandas: Es una librería fundamental para la manipulación y análisis de datos en Python.
# La usamos para leer el archivo CSV y para aplicar los filtros sobre el DataFrame.
# Instalación: pip install pandas
import pandas as pd

# Streamlit Condition Tree: Un componente personalizado para Streamlit que permite
# construir de forma visual una lógica de filtrado compleja (con condiciones Y/O anidadas).
# Es ideal para usuarios que necesitan crear consultas sin escribir código.
# Instalación: pip install streamlit-condition-tree
# https://github.com/cedricvlt/streamlit-condition-tree
from streamlit_condition_tree import condition_tree, config_from_dataframe

# Streamlit Extras: Una colección de componentes útiles para Streamlit que añaden
# funcionalidades extra. Aquí usamos el 'dataframe_explorer' para filtros tipo Excel.
# Instalación: pip install streamlit-extras
# https://arnaudmiribel.github.io/streamlit-extras/extras/dataframe_explorer/
from streamlit_extras.dataframe_explorer import dataframe_explorer

# Streamlit Dynamic Filters: Una librería que simplifica la creación de filtros dinámicos
# (como menús desplegables o campos de búsqueda) basados en las columnas de un DataFrame.
# Es muy útil para dashboards donde el usuario necesita filtrar por varias categorías.
# Instalación: pip install streamlit-dynamic-filters
# https://github.com/arsentievalex/streamlit-dynamic-filters
from streamlit_dynamic_filters import DynamicFilters

# --- CONFIGURACIÓN DE LA PÁGINA ---

# st.set_page_config() configura los metadatos y el layout de la página.
# Debe ser el primer comando de Streamlit que se ejecuta en el script.
# layout="wide": Hace que el contenido ocupe todo el ancho de la pantalla, ideal para tablas de datos.
# page_title: El título que aparece en la pestaña del navegador.
# page_icon: El favicon (icono) que aparece en la pestaña del navegador.
st.set_page_config(layout="wide", page_title="Filtro de DataFrames con Streamlit", page_icon="🔍")

# --- TÍTULO DE LA APLICACIÓN ---

# st.title() muestra un texto grande como el título principal de la aplicación.
st.title("Filtro Interactivo de Datos con Streamlit y Pandas")

# --- CARGA DE ARCHIVO ---

# st.file_uploader() crea un widget que permite al usuario subir un archivo desde su computadora.
# El primer argumento es la etiqueta que se muestra al usuario.
# 'type="csv"': Limita los tipos de archivo permitidos a solo CSV para asegurar que Pandas pueda leerlo.
uploaded_file = st.file_uploader("Sube un archivo CSV para comenzar", type="csv")

# --- LÓGICA PRINCIPAL DE LA APLICACIÓN ---

# Este bloque condicional se ejecuta solo si el usuario ha subido un archivo.
# 'uploaded_file' no será 'None' una vez que el archivo esté cargado en memoria.
if uploaded_file is not None:
    # pd.read_csv() es la función de Pandas para leer un archivo CSV y cargarlo en un DataFrame.
    # Streamlit maneja el objeto 'uploaded_file' de forma que Pandas puede leerlo directamente.
    dfBase = pd.read_csv(uploaded_file,parse_dates=True)
    # Creamos una copia del DataFrame original. Es una buena práctica para no modificar
    # el DataFrame base, ya que lo necesitaremos intacto para las diferentes pestañas de filtrado.
    df = dfBase.copy()

    # st.tabs() crea una interfaz con pestañas. Recibe una lista de strings, donde cada
    # string es el título de una pestaña. Devuelve un objeto por cada pestaña.
    tab1, tab2, tab3 = st.tabs(["Filtro por Árbol de Condiciones", "Filtro tipo Excel", "Filtros Dinámicos"])

    # --- PESTAÑA 1: FILTRADO CON CONDITION TREE ---
    # El bloque 'with' asigna todo el código siguiente a la pestaña 'tab1'.
    with tab1:
        st.header("1. Crea filtros complejos con un árbol de condiciones")
        
        # La función config_from_dataframe() analiza el DataFrame (columnas y tipos de datos)
        # y genera automáticamente un diccionario de configuración necesario para el widget condition_tree.
        # Esto evita tener que definir manualmente qué tipo de filtro usar para cada columna.
        config = config_from_dataframe(df)

        # st.expander() crea una sección colapsable en la interfaz. Útil para ocultar
        # elementos complejos y mantener la UI limpia.
        with st.expander("Ver y construir el árbol de filtros"):
            # condition_tree() es el componente principal de esta librería.
            # Renderiza la interfaz gráfica para que el usuario construya las condiciones lógicas.
            # Devuelve una cadena de texto (query_string) que es una consulta válida para el método df.query() de Pandas.
            query_string = condition_tree(
                config,
                always_show_buttons=True, # Muestra siempre los botones de añadir/eliminar condición.
                placeholder="No hay condiciones seleccionadas", # Texto que se muestra si no hay filtros.
            )

        # st.code() muestra la consulta de Pandas generada. Es muy útil para que el usuario
        # pueda ver (y aprender) la sintaxis de la consulta que se está aplicando.
        st.write("Consulta de Pandas generada:")
        st.code(query_string, language='python')

        # df.query() es un método muy potente de Pandas que filtra el DataFrame
        # evaluando la cadena de texto de la consulta. Es más legible que usar
        # máscaras booleanas complejas. Si la cadena está vacía, devuelve el DataFrame original.
        df_filtered_tree = df.query(query_string)

        st.write("Datos del DataFrame filtrados:")
        # st.container(horizontal=True) permite agrupar elementos horizontalmente para un mejor diseño.
        with st.container(horizontal=True):
            # st.metric() muestra una métrica o KPI (Key Performance Indicator).
            # 'label' es el título de la métrica.
            # 'value' es el valor principal a mostrar.
            # 'delta' calcula y muestra la diferencia entre el valor actual y un valor de referencia.
            # Aquí muestra cuántas filas se eliminaron respecto al DataFrame original.
            st.metric("Filas", df_filtered_tree.shape[0], delta=df_filtered_tree.shape[0] - dfBase.shape[0])
            st.metric("Columnas", df_filtered_tree.shape[1])
        
        # st.dataframe() muestra el DataFrame filtrado en una tabla interactiva en la aplicación.
        st.dataframe(df_filtered_tree)

    # --- PESTAÑA 2: FILTRADO CON DATAFRAME EXPLORER ---
    with tab2:
        st.header("2. Filtra columnas de forma individual (estilo Excel)")
        
        # dataframe_explorer() es un componente de streamlit-extras que toma un DataFrame
        # y le añade automáticamente widgets de filtro en la parte superior de la tabla.
        # Devuelve directamente el DataFrame ya filtrado según las interacciones del usuario.
        # case=False: Hace que los filtros de texto no distingan entre mayúsculas y minúsculas.
        filtered_df_explorer = dataframe_explorer(dfBase, case=False)
        
        with st.container(horizontal=True):
            # Mostramos las mismas métricas que en la pestaña anterior, pero para este método de filtrado.
            st.metric("Filas", filtered_df_explorer.shape[0], delta=filtered_df_explorer.shape[0] - dfBase.shape[0])
            st.metric("Columnas", filtered_df_explorer.shape[1])
        
        # Mostramos el DataFrame filtrado con el segundo método.
        # use_container_width=True hace que la tabla ocupe todo el ancho disponible.
        st.dataframe(filtered_df_explorer, use_container_width=True)

    # --- PESTAÑA 3: FILTRADO CON DYNAMIC FILTERS ---
    with tab3:
        st.header("3. Aplica filtros dinámicos con selectores")
        
        # Se inicializa el objeto DynamicFilters con el DataFrame y una lista de columnas
        # para las cuales queremos crear filtros. La librería generará el widget adecuado
        # para cada tipo de dato (por ejemplo, un multiselect para columnas categóricas).
        dynamic_filters = DynamicFilters(dfBase, filters=['Director','Title', 'Genre','Year','Rating','Votes','Revenue (Millions)','Metascore'])
        
        # Este método renderiza los widgets de filtro en la aplicación.
        # location='columns': Coloca los filtros en columnas una al lado de la otra.
        # num_columns=2: Especifica que use 2 columnas para los filtros.
        # gap='large': Aumenta el espacio entre los filtros.
        dynamic_filters.display_filters(location='columns', num_columns=3, gap='large')
        
        # Este método aplica los filtros seleccionados por el usuario al DataFrame
        # y devuelve el nuevo DataFrame filtrado.
        dfDynamic = dynamic_filters.filter_df()
        
        with st.container(horizontal=True):
            st.metric("Filas", dfDynamic.shape[0], delta=dfDynamic.shape[0] - dfBase.shape[0])
            st.metric("Columnas", dfDynamic.shape[1])
        
        # Este es un método de conveniencia de la librería que muestra el DataFrame filtrado.
        # Es equivalente a usar st.dataframe(dfDynamic).
        dynamic_filters.display_df()
else:
    # Si no se ha subido ningún archivo, st.info() muestra un mensaje informativo con un ícono.
    st.info("Por favor, sube un archivo CSV para comenzar.")