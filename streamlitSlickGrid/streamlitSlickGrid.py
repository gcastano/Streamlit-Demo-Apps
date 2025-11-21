# --- LIBRERÍAS ---
# A continuación, se importan todas las librerías necesarias para la aplicación.

# streamlit: Es el framework principal para construir la aplicación web interactiva.
# Permite convertir scripts de datos en aplicaciones web compartibles en minutos.
# Comando para instalar: pip install streamlit
import streamlit as st

# math: Es una librería estándar de Python que proporciona acceso a funciones matemáticas.
# En este caso, se usa para redondear valores hacia arriba (math.ceil).
# No requiere instalación (viene con Python).
import math

# plotly.express: Es una librería para crear gráficos interactivos de manera sencilla.
# Aquí se usa para generar un gráfico de líneas que muestra la tendencia de tierra arable.
# Comando para instalar: pip install plotly
import plotly.express as px

# pandas: Es una librería esencial para la manipulación y análisis de datos.
# Proporciona estructuras de datos como el DataFrame, que es fundamental en este script.
# Comando para instalar: pip install pandas
import pandas as pd

# json: Es una librería estándar de Python para trabajar con datos en formato JSON.
# No requiere instalación (viene con Python).
import json

# streamlit_slickgrid: Es un componente de Streamlit que permite mostrar y interactuar
# con tablas de datos avanzadas (grids) basadas en la librería de JavaScript SlickGrid.
# Ofrece funcionalidades como ordenamiento, filtrado, formato condicional, y vistas jerárquicas.
# Comando para instalar: pip install streamlit-slickgrid
# https://github.com/streamlit/streamlit-slickgrid
# Documentación: https://ghiscoding.gitbook.io/slickgrid-universal
# Ejemplos: https://ghiscoding.github.io/slickgrid-universal/#/example01
from streamlit_slickgrid import (
    add_tree_info,
    slickgrid,
    Formatters,
    Filters,
    FieldType,
    OperatorType,
    ExportServices,
    StreamlitSlickGridFormatters,
    StreamlitSlickGridSorters,
)

# --- CONFIGURACIÓN DE LA PÁGINA ---

# Configura la página de Streamlit para que use un diseño "wide" (ancho),
# aprovechando todo el ancho de la pantalla para mostrar la tabla.
st.set_page_config(
    layout="wide",
)

# --- FUNCIÓN PARA CARGAR GRÁFICO DE TENDENCIA ---
# Define una función que carga y muestra un gráfico de tendencia de tierra arable
# cuando se selecciona una fila en la tabla.
@st.dialog("Gráfico de Tendencia de Tierra Arable")
def cargarGraficoTendencia(df):
    # Obtiene el nombre del país desde el DataFrame.
    pais=df["Country"].values[0]    
    # Función para cargar y mostrar un gráfico de tendencia de tierra arable
    serie=json.loads(df["Arable Land (% of land area)"].values[0])    
    # Convierte la serie en un DataFrame de pandas para facilitar el manejo y graficación.
    serie=pd.DataFrame(serie,columns=["% tierra arable"])
    with st.container(horizontal=True, vertical_alignment="center"):
        st.image(f'https://flagsapi.com/{df["Two_Letter_Country_Code"].values[0]}/flat/64.png', width=32)
        st.markdown(f"### Tendencia de tierra arable para {pais}")
    # Crea un gráfico de líneas usando Plotly Express.    
    fig = px.area(serie,x=serie.index, y="% tierra arable")
    fig.update_xaxes(showticklabels=False)
    fig.update_layout(xaxis_title="")
    # Muestra el gráfico en la aplicación Streamlit.
    st.plotly_chart(fig, use_container_width=True)

# --- CARGA Y TRANSFORMACIÓN DE DATOS CON PANDAS ---

# 1. Carga de datos desde un archivo CSV a un DataFrame de pandas.
dfDatos = pd.read_csv("./dfDatosTierraArable.csv")

# 2. Ordena el DataFrame inicialmente por continente y luego por país.
# Esto es útil para la estructura jerárquica que se creará más adelante.
dfDatos=dfDatos.sort_values(by=['Continent_Name','Country'])


# 3. Inserta una columna 'id' en la primera posición (loc=0).
# El valor de la columna es el índice del DataFrame, asegurando un identificador único para cada fila.
dfDatos.insert(loc=0, column='id', value=dfDatos.index)

# 4. Crea una columna 'Flag' que contiene etiquetas HTML de imagen.
# Se utiliza el método 'apply' con una función lambda para procesar cada código de país ('Two_Letter_Country_Code').
# Para cada código (x), se genera una URL de la API de flagsapi.com para mostrar la bandera del país.
dfDatos["Flag"]=dfDatos["Two_Letter_Country_Code"].apply(lambda x: f'<img src="https://flagsapi.com/{x}/flat/64.png" height="16">')


# 5. Calcula valores máximos que se usarán para configurar los rangos de los filtros en la tabla.
maxHectares=dfDatos['Most_Recent_Year_hectares'].max()
maxHectares5yr=math.ceil(dfDatos['Hectares_Change_5yr'].max()) # Redondea hacia arriba el valor máximo.

# 6. Reordena el DataFrame para que los países con mayor porcentaje de tierra cultivable aparezcan primero dentro de cada continente.
dfDatos= dfDatos.sort_values(by=['Continent_Name','Arable_land_percent_recent'], ascending=[True, False])


# 7. Convierte el DataFrame de pandas a una lista de diccionarios.
# Cada diccionario en la lista representa una fila de la tabla. Este es el formato requerido por streamlit_slickgrid.
arrDatos = dfDatos.to_dict(orient="records")

# 8. Procesa la lista de datos para añadir información jerárquica (árbol).
# La función 'add_tree_info' agrupa los datos. Las filas con el mismo 'Continent_Name' se agruparán,
# y dentro de cada continente, se listarán los 'Country'.
# Añade claves especiales como '__parent' y '__depth' que SlickGrid usará para renderizar la vista de árbol.
arrDatos = add_tree_info(
    arrDatos,
    tree_fields=["Continent_Name", "Country"], # Campos que definen la jerarquía.
    join_fields_as="paises", # Nombre del nuevo campo que contendrá el texto jerárquico.
    id_field="id", # Campo que se usará como identificador único.
)

# --- DEFINICIÓN DE COLUMNAS PARA LA TABLA (SLICKGRID) ---
# Cada diccionario en esta lista define una columna en la tabla interactiva.

columns=[
    {
        "id": "paises", # Identificador único de la columna.
        "name": "Paises", # Título que se mostrará en la cabecera.
        "field": "paises", # Campo del diccionario de datos que se usará para esta columna.
        "sortable": True, # Permite ordenar por esta columna.
        "minWidth": 50,
        "type": FieldType.string, # Tipo de dato.
        "filterable": True, # Permite filtrar por esta columna.
        "formatter": Formatters.tree, # Formateador especial para mostrar la estructura de árbol (con iconos para expandir/colapsar).
        "exportCustomFormatter": Formatters.treeExport, # Formato para la exportación.
    },
    {
        "id": "Most_Recent_Year",
        "name": "Año más reciente",
        "field": "Most_Recent_Year",
        "sortable": True,        
    },
    {
        "id": "Most_Recent_Year_hectares",
        "name": "Tierra Arable (hectáreas) reciente",
        "field": "Most_Recent_Year_hectares",
        "sortable": True,
        "minWidth": 100,
        "type": FieldType.number,
        "cssClass": "text-right", # Alinea el texto a la derecha.
        "filterable": True,
        "filter": { # Configuración del filtro para esta columna.
            "model": Filters.numberRange, # Usa un filtro de rango numérico.
            "maxValue": maxHectares, # Establece el valor máximo del filtro.
            "operator": ">=", # El operador por defecto será 'mayor o igual que'.
        },
        "formatter": StreamlitSlickGridFormatters.numberFormatter, # Formatea el número.
        "params": { # Parámetros para el formateador.
            "minDecimal": 0,
            "maxDecimal": 2,
            "thousandSeparator":",", # Usa coma como separador de miles.
            "numberSuffix": " ha", # Añade un sufijo al número.
        },
    },    
    {
        "id": "Arable_land_percent_recent",
        "name": "% tierra arable reciente",
        "field": "Arable_land_percent_recent",
        "sortable": True,
        "sorter": StreamlitSlickGridSorters.numberArraySorter,
        "minWidth": 100,
        "type": FieldType.number,        
        "filterable": True,
        "filter": {
            "model": Filters.sliderRange, # Usa un filtro de tipo slider con rango.
            "maxValue": 100,
            "operator": OperatorType.rangeInclusive,
        },
        "formatter": StreamlitSlickGridFormatters.barFormatter, # Usa un formateador de barra de progreso.
        "params": { # Parámetros para la barra.
            "colors": [[20, "white", "red"], [100, "white", "green"]], # Colores condicionales: hasta 20% rojo, de ahí a 100% verde.
            "minDecimal": 0,
            "maxDecimal": 2,
            "numberSuffix": "%", # Añade el sufijo de porcentaje.
        },
    },
    {
        "id": "Hectares_Change_5yr",
        "name": "Cambio en Tierra Arable (hectáreas) en 5 años",
        "field": "Hectares_Change_5yr",
        "sortable": True,
        "minWidth": 100,
        "type": FieldType.number,
        "filterable": True,
        "cssClass": "text-right",
        "filter": {
            "model": Filters.slider, # Usa un filtro de tipo slider simple.
            "operator": ">=",
            "maxValue": maxHectares5yr,
        },
        "formatter": StreamlitSlickGridFormatters.numberFormatter,
        "params": {
            "colors": [ # Colores condicionales para el texto del número.
                [0, "red", None],  # Si el valor es menor o igual a 0, el texto es rojo.
                [None, "green"],   # Si es mayor que 0, es verde.
            ],
            "minDecimal": 0,
            "maxDecimal": 2,
            "thousandSeparator":",",
            "numberSuffix": " ha",
        },
    },
    {
        "id": "percent_change_5yr",
        "name": "% Cambio tierra arable 5 años",
        "field": "percent_change_5yr",
        "sortable": True,
        "minWidth": 100,
        "type": FieldType.number,
        "cssClass": "text-right",
        "filter": {
            "model": Filters.sliderRange,
            "maxValue": 1,
            "operator": OperatorType.rangeInclusive,
        },
        "formatter": Formatters.percent, # Formateador que muestra el valor como un porcentaje.
        "params": {
            "colors": [ # Colores condicionales.
                [0, "red", None],
                [None, "green"],                
            ],
            "minDecimal": 0,
            "maxDecimal": 2,
        },      
    },
]

# --- OPCIONES GENERALES DE LA TABLA (SLICKGRID) ---
# Este diccionario configura el comportamiento general de la tabla.
options = {
    "enableFiltering": True, # Activa la funcionalidad de filtros en las columnas.
    "enableTextExport": True, # Permite exportar los datos a CSV/TXT.
    "enableExcelExport": True, # Permite exportar los datos a Excel.
    "excelExportOptions": {"sanitizeDataExport": True},
    "textExportOptions": {"sanitizeDataExport": True},
    "externalResources": [ # Carga los servicios necesarios para la exportación.
        ExportServices.ExcelExportService,
        ExportServices.TextExportService,
    ],
    "frozenColumn": 0, # Fija la primera columna (índice 0) para que no se desplace horizontalmente.
    "autoResize": { # Permite que la tabla ajuste su tamaño automáticamente.
        "minHeight": 600,
    },
    "enableTreeData": True, # Habilita el modo de vista de árbol (jerárquico).
    "multiColumnSort": False,
    "treeDataOptions": { # Configuración específica para la vista de árbol.
        "columnId": "paises", # La columna que mostrará la estructura de árbol.
        "indentMarginLeft": 15, # Margen de indentación para cada nivel de la jerarquía.
        "initiallyCollapsed": True, # Comienza con todos los grupos colapsados.
        "parentPropName": "__parent", # Nombre de la propiedad que indica el ID del padre (añadido por add_tree_info).
        "levelPropName": "__depth", # Nombre de la propiedad que indica el nivel de profundidad (añadido por add_tree_info).
    },
}

# --- CÁLCULO DE TOTALES Y PREPARACIÓN FINAL DE DATOS ---

# 1. Agrupa los datos por continente y calcula los totales y promedios necesarios para las filas de resumen.
# - 'sum' para hectáreas totales y cambio en hectáreas.
# - 'mean' para los promedios de porcentajes.
dfDatosGrupo = dfDatos.groupby('Continent_Name').agg({'Most_Recent_Year_hectares':'sum',
                                                      'Arable_land_percent_recent':'mean',
                                                      'Hectares_Change_5yr':'sum',
                                                      'percent_change_5yr':'mean',"Country":"count"}).reset_index()
arrDatosTotales=[]
arrCamposAgregar=['Most_Recent_Year_hectares','Arable_land_percent_recent','Hectares_Change_5yr','percent_change_5yr']

# 2. Itera sobre los datos ya preparados para la jerarquía para insertar las filas de resumen (totales por continente).
for item in arrDatos:    
    # Si la profundidad (__depth) es 0, es una fila de nivel superior (continente).
    if item['__depth']==0:
        itemHead=item.copy() # Crea una copia para usarla como fila de resumen.
        # Rellena la fila de resumen con los datos agregados que calculamos previamente.
        for campo in arrCamposAgregar:
            itemHead[campo]=dfDatosGrupo.loc[dfDatosGrupo['Continent_Name']==item['Continent_Name'],campo].values[0]            
        cantPaises=dfDatosGrupo.loc[dfDatosGrupo['Continent_Name']==item['Continent_Name'],"Country"].values[0]
        itemHead['Country']=item['Continent_Name']
        itemHead['paises']=f"<b>{item['Continent_Name']}</b><i>({cantPaises} países) </i>" # Formatea el nombre del continente en negrita.
        itemHead['Most_Recent_Year']=None # Limpia campos que no aplican al resumen.
        
        # Crea un ID único para la fila de resumen del continente para que no colisione con los IDs existentes.
        parentId=itemHead["id"]+1000
        itemHead["id"]=parentId
        arrDatosTotales.append(itemHead) # Añade la fila de resumen a la lista final.
    
    # Asigna el ID del padre (la fila de resumen del continente) a cada país.
    # Esto crea la relación padre-hijo que SlickGrid necesita para la jerarquía.
    item["__parent"]=parentId
    
    # Formatea el nombre del país para incluir la bandera que creamos anteriormente.
    item["paises"]=f'{item["Flag"]} {item["Country"]}'
    
    # Añade la fila del país (ya con su padre asignado) a la lista final.
    arrDatosTotales.append(item)

st.title("Análisis de Tierra Arable por País y Continente")
st.subheader("Datos interactivos con Streamlit SlickGrid")

tabSlckgrid, tabInfo = st.tabs(["📊 Tabla Interactiva", "ℹ️ Información"])

with tabSlckgrid:
    # --- RENDERIZADO DE LA TABLA ---

    # Llama a la función 'slickgrid' para mostrar la tabla interactiva en la aplicación Streamlit.
    # Pasamos los datos finales (con resúmenes y jerarquía), la definición de las columnas y las opciones de configuración.
    resultado=slickgrid(arrDatosTotales, columns, options, key="mygrid2",on_click="rerun")
    if resultado is not None:
        row, col = resultado
        resultado
        st.write("Filas seleccionadas:")
        dfDatos.loc[[row]]
        cargarGraficoTendencia(dfDatos.loc[[row]])
with tabInfo:
    st.dataframe(dfDatos,hide_index=True)