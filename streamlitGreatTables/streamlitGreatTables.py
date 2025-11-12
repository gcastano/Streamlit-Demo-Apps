# ==============================================================================
# LIBRERÍAS Y SU INSTALACIÓN
# ==============================================================================
# A continuación, se importan todas las librerías necesarias para este script.
# Para instalarlas, puedes usar pip desde tu terminal:
#
# great-tables: Una librería para crear tablas de calidad de publicación de forma declarativa.
# Comando: pip install great-tables
# https://posit-dev.github.io/great-tables/articles/intro.html
# 
# gt-extras: Extensiones y utilidades adicionales para great-tables.
# Comando: pip install gt-extras
#
# polars: Una librería de DataFrames increíblemente rápida, escrita en Rust, que ofrece una API moderna y eficiente.
# Se usa aquí en conjunto con great-tables para algunas operaciones de alto rendimiento.
# Comando: pip install polars
#
# streamlit: Un framework para crear aplicaciones web interactivas para ciencia de datos y machine learning con Python puro.
# Comando: pip install streamlit
#
# pandas: La librería fundamental para la manipulación y análisis de datos en Python.
# Comando: pip install pandas
# ==============================================================================

from great_tables import GT, html,md,style,loc,vals
from great_tables.data import sza
import polars as pl
import streamlit as st
import pandas as pd
import gt_extras as gte

# --- Configuración de la página de Streamlit ---
# st.set_page_config() configura los metadatos y el layout de la aplicación web.
# layout="wide" hace que el contenido ocupe todo el ancho de la pantalla.
# page_title y page_icon definen el título en la pestaña del navegador y el ícono.
st.set_page_config(layout="wide", page_title="Great Tables Demo", page_icon=":earth_americas:")

# ==============================================================================
# CARGA Y TRANSFORMACIÓN DE DATOS (DATA WRANGLING)
# ==============================================================================

# --- Carga de datos de Tierra Cultivable (Porcentaje) ---
# Se carga el archivo CSV del Banco Mundial.
# skiprows=4 se utiliza para omitir las primeras 4 filas que contienen metadatos y no datos tabulares.
dfDatos = pd.read_csv('ArableLand_worldbank.csv',skiprows=4)

# --- Carga y transformación de datos de Tierra Cultivable (Hectáreas) ---
# 1. Cargar el segundo dataset que contiene los datos en hectáreas.
# 2. .drop() elimina columnas que no son necesarias para el análisis.
dfDatosHectares = pd.read_csv('arable_land_hectares.csv').drop(columns=['Series Name','Series Code',"Country Code"])

# 3. .melt() transforma el DataFrame de un formato "ancho" a "largo".
#    Las columnas de años (ej: '1990', '1991') se convierten en filas,
#    creando dos nuevas columnas: 'Year' (para el año) y 'Arable Land (hectares)' (para el valor).
#    'Country Name' se mantiene como identificador de cada fila (id_vars).
dfDatosHectares= dfDatosHectares.melt(id_vars=['Country Name'],var_name='Year',value_name='Arable Land (hectares)')

# 4. Limpieza de la columna 'Year': Los nombres de columna originales tenían formato como "2018 [YR2018]".
#    .str[0:4] extrae solo los primeros 4 caracteres, que corresponden al año.
dfDatosHectares["Year"]=dfDatosHectares['Year'].str[0:4]

# 5. Filtrado de datos: Se eliminan filas donde el valor es '..', que representa datos faltantes en este dataset.
dfDatosHectares=dfDatosHectares[dfDatosHectares['Arable Land (hectares)']!='..']

# 6. Conversión de tipo: La columna de hectáreas se convierte a tipo numérico (float) para poder realizar cálculos.
dfDatosHectares['Arable Land (hectares)']=dfDatosHectares['Arable Land (hectares)'].astype(float)

# --- Cálculo del cambio en 5 años en Hectáreas ---
# 7. Encontrar el año más reciente con datos para cada país.
#    .groupby('Country Name')['Year'].max() agrupa por país y encuentra el máximo año.
#    .reset_index() convierte el resultado de groupby de nuevo en un DataFrame.
#    .rename() cambia el nombre de la columna para mayor claridad.
dfDatosHectaresRecent=dfDatosHectares.groupby('Country Name')['Year'].max().reset_index().rename(columns={'Year':'Most_Recent_Year'})

# 8. Unir (merge) el año más reciente con el DataFrame original.
#    Esto añade la columna 'Most_Recent_Year' a cada fila del país correspondiente.
dfDatosHectaresRecent['Most_Recent_Year']=dfDatosHectaresRecent['Most_Recent_Year'].astype(int)
dfDatosHectaresRecent=pd.merge(dfDatosHectares,dfDatosHectaresRecent,on=['Country Name'],how='inner')
dfDatosHectaresRecent["Year"]=dfDatosHectaresRecent['Year'].astype(int)

# 9. Filtrar para mantener solo dos registros por país: el del año más reciente y el de 5 años antes.
dfDatosHectaresRecent=dfDatosHectaresRecent[(dfDatosHectaresRecent['Year']==dfDatosHectaresRecent['Most_Recent_Year']) | (dfDatosHectaresRecent['Year']==dfDatosHectaresRecent['Most_Recent_Year']-5)]

# 10. Crear una columna para etiquetar cada una de las dos filas por país.
#     .apply() con una función lambda permite crear una lógica condicional para etiquetar las filas.
dfDatosHectaresRecent["year_type"]= dfDatosHectaresRecent.apply(lambda x: 'Most_Recent_Year_hectares' if x['Year']==x['Most_Recent_Year'] else ('5_Years_Prior' if x['Year']==x['Most_Recent_Year']-5 else 'Other'),axis=1)
dfDatosHectaresRecent=dfDatosHectaresRecent.drop(columns=['Most_Recent_Year','Year'])

# 11. .pivot() transforma el DataFrame de formato "largo" a "ancho".
#     Ahora, en lugar de tener dos filas por país, tendremos una sola con dos columnas:
#     'Most_Recent_Year_hectares' y '5_Years_Prior'. Esto facilita el cálculo de la diferencia.
dfDatosHectaresRecent= dfDatosHectaresRecent.pivot(index='Country Name',columns='year_type',values='Arable Land (hectares)').reset_index()

# 12. Calcular el cambio absoluto y porcentual en los últimos 5 años.
dfDatosHectaresRecent["Hectares_Change_5yr"]= dfDatosHectaresRecent["Most_Recent_Year_hectares"] - dfDatosHectaresRecent["5_Years_Prior"]
dfDatosHectaresRecent["percent_change_5yr"]= (dfDatosHectaresRecent["Hectares_Change_5yr"]/dfDatosHectaresRecent["5_Years_Prior"])

# --- Combinación y Limpieza Final de Datos ---
# Cargar datos de mapeo de países a continentes.
dfPaises= pd.read_csv('country-and-continent.csv',sep=';')

# Unir (merge) los datos principales con la información del continente.
dfDatos=dfDatos.merge(dfPaises[['Country Name','Continent_Name','Two_Letter_Country_Code']],on='Country Name',how='left')

# Filtrar códigos de país que representan agregaciones regionales (ej. 'AFE' para Africa Eastern and Southern), no países individuales.
# El símbolo ~ (tilde) invierte la selección, quedándonos con los que NO están en la lista.
dfDatos= dfDatos[~dfDatos['Country Code'].isin(['AFE','AFW','ARB','CEB','EAS','EAP','TEA','EMU','ECS','ECA','TEC','EUU','HPC','HIC','IBT','IDB','IDX','IDA','LCN','LAC','TLA','LDC','LMY','LIC','LMC','MEA','MNA','TMN','MIC','NAC','PST','PRE','SAS','TSA','SSF','SSA','TSS','UMC','WLD'])]
dfDatos=dfDatos.drop(columns=['Country Code','Indicator Name','Indicator Code','Unnamed: 69'])

# Realizar la transformación .melt() también en este DataFrame para tener un formato largo por año.
dfDatos= dfDatos.melt(id_vars=['Country Name','Continent_Name','Two_Letter_Country_Code'],var_name='Year',value_name='Arable Land (% of land area)')
dfDatos=dfDatos.rename(columns={'Country Name':'Country'})

# Asegurar tipos de datos correctos y eliminar filas con valores nulos.
dfDatos['Year']=dfDatos['Year'].astype(int)
dfDatos['Arable Land (% of land area)']=dfDatos['Arable Land (% of land area)'].astype(float)
dfDatos=dfDatos.dropna()

# Obtener el dato porcentual más reciente para cada país.
dfDatosAnio=dfDatos.groupby('Country')['Year'].max().reset_index()
dfDatosRecientes=pd.merge(dfDatos,dfDatosAnio,on=['Country','Year'],how='inner')
dfDatosRecientes.rename(columns={'Year':'Most_Recent_Year','Arable Land (% of land area)':'Arable_land_percent_recent'},inplace=True)

# Unir este dato reciente al DataFrame principal.
dfDatos=pd.merge(dfDatos,dfDatosRecientes,on=['Country'],how='inner',suffixes=('','_y'))
dfDatos=dfDatos.sort_values(by=['Country','Year'])

# --- Preparación del DataFrame Final para la Tabla ---
# Agrupar por país y agregar todos los valores porcentuales anuales en una lista.
# Esta lista será utilizada por great-tables para crear un mini-gráfico (nanoplot) dentro de la tabla.
dfDatosTabla = dfDatos.groupby(['Two_Letter_Country_Code','Country','Continent_Name','Most_Recent_Year','Arable_land_percent_recent'])["Arable Land (% of land area)"].apply(list).reset_index()

# Convertir el porcentaje a formato decimal para los cálculos.
# dfDatosTabla["Arable_land_percent_recent"]=dfDatosTabla["Arable_land_percent_recent"]/100

# Unir finalmente el DataFrame de porcentajes con el DataFrame de cambio en hectáreas.
dfDatosTabla =dfDatosTabla.merge(dfDatosHectaresRecent,left_on='Country',right_on='Country Name',how='left').drop(columns=['Country Name','5_Years_Prior'])

# ==============================================================================
# CREACIÓN DE LA INTERFAZ DE USUARIO CON STREAMLIT
# ==============================================================================
st.title(
    " Visualización de Datos de Tierra Cultivable con Great Tables",
    help="Consulta la documentación de `great_tables` para más información."
)

# Widget multiselect para que el usuario filtre por continente.
# .unique().tolist() obtiene una lista de continentes únicos para las opciones.
# 'default' establece las opciones seleccionadas por defecto.
parContinente = st.multiselect(
    "Selecciona el/los continente(s) a mostrar",
    dfDatosTabla['Continent_Name'].unique().tolist(),
    default=dfDatosTabla['Continent_Name'].unique().tolist()
)

# Widget selectbox para que el usuario elija la columna por la cual ordenar la tabla.
parOrdenarPor = st.selectbox(
    "Ordenar tabla por columna",
    options=["Arable_land_percent_recent","Most_Recent_Year_hectares","Hectares_Change_5yr","percent_change_5yr"],
    format_func=lambda x: str(x).replace("_"," ").capitalize(), # Mejora la legibilidad de las opciones
    index=0
)

# Filtrar el DataFrame basado en la selección del usuario.
if parContinente:
    dfDatosTabla = dfDatosTabla[dfDatosTabla['Continent_Name'].isin(parContinente)]    

dfDatosTabla["Flag"]=dfDatosTabla["Two_Letter_Country_Code"].apply(lambda x: f"https://flagsapi.com/{x}/flat/64.png")
dfDatosTabla["Country_Flag"]=dfDatosTabla.apply(lambda x: gte.add_text_img(
    text=x['Country'],
    img_url=x['Flag'],
    left=True,
),axis=1)
# ==============================================================================
# GENERACIÓN DE LA TABLA CON GREAT TABLES
# ==============================================================================
# La tabla se construye encadenando métodos de forma declarativa.

table = (
    # 1. Iniciar el objeto GT.
    #    - Se convierte el DataFrame de pandas a polars para compatibilidad y rendimiento.
    #    - Se ordena el DataFrame según la selección del usuario.
    #    - rowname_col: Columna que actúa como etiqueta de fila (código de país).
    #    - groupname_col: Columna usada para agrupar las filas (continente).
    GT(pl.from_pandas(dfDatosTabla.sort_values(parOrdenarPor,ascending=False)),rowname_col="Country_Flag", groupname_col="Continent_Name")
    .cols_hide(["Two_Letter_Country_Code","Country","Flag"])  # Ocultar columna de código de país.
    # 2. Añadir un encabezado principal y un subtítulo a la tabla.
    .tab_header(
        title=html("Porcentaje de <b>Tierra Cultivable</b> a lo Largo de los Años"),
        subtitle=html("Tendencias en el porcentaje de tierra cultivable <b>para varios países.</b>"),
    )
    
    # 3. Formatear una columna como un "nanoplot" (un mini-gráfico de línea).
    #    Usa la lista de valores que creamos anteriormente.
    .fmt_nanoplot("Arable Land (% of land area)")
    
    # 4. Formatear columnas numéricas para que tengan 1 decimal.
    .fmt_number(
        columns=["Most_Recent_Year_hectares","Hectares_Change_5yr"],
        decimals=1,        
    )
    
    # 5. Formatear una columna para mostrar imágenes.
    #    - `file_pattern` crea una URL dinámica usando el valor de la columna (código de país).
    .fmt_image(
        columns="Two_Letter_Country_Code",
        file_pattern="https://flagsapi.com/{}/flat/64.png",
        height="30px"
    )
    
    # 6. Crear "spanners" o encabezados que agrupan varias columnas.
    .tab_spanner(
        label="Datos Más Recientes",        
        columns=["Most_Recent_Year", "Arable_land_percent_recent","Most_Recent_Year_hectares"]
    )
    .tab_spanner(
        label="Cambio en 5 Años",
        columns=["percent_change_5yr","Hectares_Change_5yr"]
    )
    
    # 7. Renombrar las etiquetas de las columnas para que sean más legibles.
    .cols_label(
        Most_Recent_Year = "Año",
        Arable_land_percent_recent = "Tierra Cultivable (%)",
        Most_Recent_Year_hectares = "Tierra Cultivable (hectáreas)",
        percent_change_5yr = "Cambio Porcentual",
        Hectares_Change_5yr= "Cambio en Hectáreas"        
    )
    
    # 8. Aplicar estilos condicionales.
    #    - Si el cambio porcentual es negativo, el texto se colorea de rojo.
    .tab_style(
        style=style.text(color="red"),
        locations=loc.body(columns=["percent_change_5yr","Hectares_Change_5yr"],rows=pl.col("percent_change_5yr") < 0),
    )
    #    - Si el cambio porcentual es positivo o cero, el texto se colorea de verde.
    .tab_style(
        style=style.text(color="green"),
        locations=loc.body(columns=["percent_change_5yr","Hectares_Change_5yr"],rows=pl.col("percent_change_5yr") > 0),
    )
    .tab_style(
        style=style.text(color="silver"),
        locations=loc.body(columns=["percent_change_5yr","Hectares_Change_5yr"],rows=pl.col("percent_change_5yr") == 0),
    )
    
    # 9. Aplicar otros estilos para mejorar la legibilidad.
    .tab_style(style=[style.text(weight="bold"),style.fill(color="#F0F0F0")], locations=loc.body(columns="Country_Flag"))
    .tab_style(style=style.text(weight="bold"), locations=loc.spanner_labels(ids=["Datos Más Recientes","Cambio en 5 Años"]))
    .tab_style(style=[style.text(weight="bold"),style.fill(color="#D9E9CF")], locations=loc.row_groups()) # Estilo para los nombres de los grupos (continentes)
    
    # 10. Formatear columnas como porcentajes con 2 decimales.
    .fmt_percent(columns=["Arable_land_percent_recent","percent_change_5yr"], decimals=2)
    
    
    # 11. Aplicar una escala de colores (heatmap) a una columna para visualizar la magnitud de los valores.
    .data_color(
        columns=['Most_Recent_Year_hectares'],
        palette=["#F7A4A4", "#F7D060","#B6E2A1"], # Paleta de colores de bajo a alto
    )
    # Aplicar un gráfico de barras dentro de las celdas para otra columna.
    .pipe(
        gte.gt_plt_bar_pct,
        column=["Arable_land_percent_recent"],
        autoscale=False,
        labels=True,
        fill="#84994F",
        
    )
    # 12. Añadir filas de resumen general al final de la tabla (mínimo, máximo, promedio).
    .grand_summary_rows(
        fns={
            "Mínimo": pl.min("Most_Recent_Year_hectares", "Arable_land_percent_recent"),
            "Máximo": pl.col("Most_Recent_Year_hectares", "Arable_land_percent_recent").max(),
            "Promedio": pl.col("Most_Recent_Year_hectares", "Arable_land_percent_recent").mean(),
        },
        fmt=vals.fmt_number,
    )   
    # 13. Añadir notas al pie de la tabla para citar las fuentes.
    .tab_source_note(source_note="Fuente: Archivos electrónicos y sitio web de la FAO, Organización de las Naciones Unidas para la Alimentación y la Agricultura.")
    .tab_source_note(source_note="Publicado por: Organización de las Naciones Unidas para la Alimentación y la Agricultura (FAO)")
    .tab_source_note(md("Tabla original: [worldbank.org](https://data.worldbank.org/indicator/AG.LND.ARBL.ZS?end=2023&start=1961&view=chart)"))
    
    # 14. Convertir el objeto de la tabla a HTML crudo para poder mostrarlo en Streamlit.
    .as_raw_html()
)


tabTabla,tabDatos = st.tabs(["Tabla de Tierra Cultivable","Datos Fuente"])
with tabTabla:
    # --- Renderizar la tabla en la aplicación Streamlit ---
    # st.write() muestra contenido en la app.
    # unsafe_allow_html=True es necesario para que Streamlit renderice el HTML generado por great_tables.
    st.write(table, unsafe_allow_html=True)    
    
with tabDatos:
    st.subheader("Datos Fuente - Tierra Cultivable (% del área terrestre)")
    st.dataframe(dfDatosTabla)
    