# Importamos las librerías necesarias
import streamlit as st  # Librería para crear aplicaciones web interactivas. Instalación: pip install streamlit
import pandas as pd  # Librería para manipulación y análisis de datos. Instalación: pip install pandas
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode # Librería para crear tablas interactivas. Instalación: pip install streamlit-aggrid


# Definimos los parámetros de configuración de la aplicación
st.set_page_config(
    page_title="Ejemplos de AgGrid", # Título de la página
    page_icon="📊", # Icono de la página
    layout="wide", # Ajusta el diseño a ancho
    initial_sidebar_state="expanded" # Barra lateral expandida al inicio
)


# Carga de dataframe usando caché para optimizar el rendimiento
@st.cache_data # Decorador para guardar en caché la función y evitar recargas innecesarias
def cargarDatos():
    dfDatos = pd.read_csv('https://raw.githubusercontent.com/gcastano/datasets/main/datosTiendaTecnologiaLatam.csv') # Leemos el archivo CSV desde una URL
    return dfDatos

dfDatos=cargarDatos() # Llamamos a la función para cargar los datos

st.header('Ejemplos de AgGrid en Streamlit') # Título de la aplicación
c1,c2=st.columns([1,4]) # Creamos dos columnas
with c1: # Columna 1
    st.link_button("Documentación de streamlit-aggrid", "https://github.com/PablocFonseca/streamlit-aggrid") # Enlace a la documentación de AgGrid
with c2: # Columna 2
    st.link_button("Aplicación de ejemplo en Streamlit", "https://staggrid-examples.streamlit.app") # Enlace a la aplicación en Streamlit
# Creamos dos pestañas para mostrar diferentes configuraciones de AgGrid
tabBasico,tabGeneral,tabAgrupado = st.tabs(['AgGrid Básico','AgGrid Extendido','AgrGrid Agrupado']) # Creamos dos pestañas

# Configuraciones para la pestaña "AgGrid Básico"
with tabBasico:
    c1,c2 = st.columns(2) # Creamos dos columnas
    with c1: # Columna 1
        # Creamos la tabla AgGrid    
        AgGrid(dfDatos, # Dataframe a mostrar
            height=900, # Altura de la tabla
            width='100%', # Ancho de la tabla
            )
    with c2:
        st.dataframe(dfDatos,height=900,use_container_width=True) # Mostramos el dataframe en una tabla de Pandas

# Configuraciones para la pestaña "AgGrid General"
with tabGeneral:
    # Creamos un objeto GridOptionsBuilder a partir del dataframe
    gob = GridOptionsBuilder.from_dataframe(dfDatos)
    
    gob.configure_default_column(groupable=True, # Habilita la agrupación de columnas
                                value=True, # Habilita la visualización de valores
                                enableRowGroup=True,  # Habilita la agrupación por filas
                                aggFunc='sum', # Función de agregación para las columnas agrupadas (suma)
                                valueFormatter="parseFloat(value.toLocaleString()).toFixed(2)'", # Formato para los valores numéricos                             
                                )
    gob.configure_pagination(paginationAutoPageSize=True) # Habilita la paginación automática
    gob.configure_grid_options(suppressAggFuncInHeader = True, # Elimina el nombre de la función de agregación del encabezado
                                autoGroupColumnDef = {"cellRendererParams": {"suppressCount": True}}, # Desactiva el contador de filas en los grupos
                                pivotPanelShow= 'onlyWhenPivoting', # Muestra el panel de pivote solo cuando se realiza un pivote
            )
    
    gob.configure_selection(
        'multiple', # Permite la selección múltiple de filas
        use_checkbox=True, # Habilita las casillas de verificación para la selección
        groupSelectsChildren=True,  # Selecciona todos los elementos de un grupo al seleccionar el grupo
        groupSelectsFiltered=True # Selecciona los elementos filtrados de un grupo
    )
    gob.configure_side_bar() # Habilita la barra lateral
    

    # Configuraciones específicas para algunas columnas
    gob.configure_column("pais", header_name="País", filter=True) # Configura la columna "pais" con filtro habilitado
    gob.configure_column("categoría", header_name="Categoría", filter=True) # Configura la columna "categoría" con filtro habilitado
    gob.configure_column("producto", header_name="Producto", filter=True) # Configura la columna "producto" con filtro habilitado

    gob.configure_column(
        field="Total", # Nombre del campo
        header_name="Total Ventas",  # Nombre del encabezado
        type=["numericColumn"], # Tipo de columna (numérica)
        valueFormatter="parseFloat(value.toLocaleString()).toFixed(2)'", # Formato de los valores
        cellStyle= { "fontWeight": 'bold',"color":"blue" } # Estilo de la celda (negrita y color azul)
    )
    gob.configure_column(
        field="precio", # Nombre del campo
        header_name="Precio", # Nombre del encabezado
        type=["numericColumn"], # Tipo de columna
        aggFunc='avg',  # Función de agregación (promedio)
        valueFormatter="parseFloat(value.toLocaleString()).toFixed(2)'" # Formato de los valores
    )
    gridOptions = gob.build() # Construye las opciones de la grilla

    # Crea la tabla AgGrid
    seleccion = AgGrid(
        dfDatos, # Dataframe a mostrar
        gridOptions=gridOptions, # Opciones de la grilla
        height=900, # Altura de la tabla
        width='100%', # Ancho de la tabla
        theme='material',  # Tema de la tabla
        update_mode=GridUpdateMode.SELECTION_CHANGED # Modo de actualización
    )
    
    st.write(seleccion['selected_rows']) # Muestra las filas seleccionadas

# Configuraciones para la pestaña "AgGrid Agrupado"
with tabAgrupado:
    # Agrupamos los datos por país, categoría y producto
    dfDatosGrupos = dfDatos.groupby(['pais','categoría','producto']).agg({'Total':'sum','Cantidad':'sum'}).reset_index() 
    dfDatosGrupos = dfDatosGrupos.sort_values('Total',ascending=False) # Ordenamos los datos
    gob2 = GridOptionsBuilder.from_dataframe(dfDatosGrupos) # Creamos un nuevo objeto GridOptionsBuilder para la tabla agrupada
    
    gob2.configure_default_column(groupable=True, # Habilita la agrupación de columnas
                                value=True, # Habilita la visualización de valores
                                enableRowGroup=True,  # Habilita la agrupación por filas
                                aggFunc='sum', # Función de agregación para las columnas agrupadas (suma)
                                valueFormatter="parseFloat(value.toLocaleString()).toFixed(2)'", # Formato para los valores numéricos                             
                                )
    # Configuraciones para las columnas
    gob2.configure_column(
        field="pais", # Nombre del campo
        hide=True, # Oculta la columna
        header_name="País", # Nombre del encabezado
        width=150,  # Ancho de la columna
        rowGroup=True,  # Habilita la agrupación por filas para esta columna    
    )
    
    gob2.configure_column(
        field="categoría", # Nombre del campo
        hide=True, # Oculta la columna
        header_name="Categoría", # Nombre del encabezado
        width=150,  # Ancho de la columna
        rowGroup=True,   # Habilita la agrupación por filas para esta columna 
    )
    

    gob2.configure_grid_options(suppressAggFuncInHeader = True, # Elimina el nombre de la función de agregación del encabezado
                                autoGroupColumnDef = {"cellRendererParams": {"suppressCount": True}}, # Desactiva el contador de filas en los grupos                                
            )
    gridOptions = gob2.build() # Construye las opciones de la grilla
    AgGrid(
        dfDatosGrupos, # Dataframe a mostrar
        gridOptions=gridOptions, # Opciones de la grilla        
        height=900, # Altura de la tabla
        width='100%',  # Ancho de la tabla
        theme='streamlit',  # Tema de la tabla
        fit_columns_on_grid_load=True,  # Ajusta las columnas al cargar la grilla      
    )