import streamlit as st
import pandas as pd
import plotly.express as px

# https://docs.streamlit.io/develop/quick-reference/changelog
# https://docs.streamlit.io/develop/api-reference/data/st.dataframe
# https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart
# https://chart-selections-demo.streamlit.app/

# Definimos los parámetros de configuración de la aplicación
st.set_page_config(
    page_title="Ejemplos de Tablero Interactivo",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

color_discrete_sequence=px.colors.carto.Safe

# Carga de dataframe
@st.cache_data
def cargarDatos():
    dfDatos = pd.read_csv('https://raw.githubusercontent.com/gcastano/datasets/main/datosTiendaTecnologiaLatam.csv')
    return dfDatos

dfDatos=cargarDatos()

textoFiltros=''
# Columnas:
#'orden', 'anio', 'mes', 'dia', 'fecha', 'pais', 'ciudad', 'categoría',
# 'producto', 'precio', 'util_porcent', 'Cantidad', 'Total', 'utilidad'

st.header('Tablero Interactivo Streamlit')
dfDatosPivot = dfDatos.pivot_table(columns='pais',index='categoría',values='Cantidad',aggfunc='sum').reset_index()

parDataFrame = st.dataframe(dfDatosPivot,
                            on_select="rerun", # Cada clic vuelve a ejecutar la app
                            selection_mode=["multi-row", "multi-column"], # Tipo de selección
                            use_container_width=True)

# Mostramos la estructura retornada
with st.expander('Datos Dataframe'):
    st.write(parDataFrame)

# Usamos iloc para filtrar los datos con los parámetros y cargamos la columna 0 que es la de categoría
categoria = dfDatosPivot.iloc[parDataFrame.selection.rows,0].unique()

# Cargamos la lista de columnas seleccionadas que en nuestro caso son países
pais = parDataFrame.selection.columns

# Validamos si hay datos seleccionamos y aplicamos el filtro
if len(categoria)>0:
    dfDatos=dfDatos[dfDatos['categoría'].isin(categoria)]
    textoCategorias = ','.join(categoria)
    textoFiltros = f'**Categoría:** {textoCategorias}'
if len(pais)>0:
    dfDatos=dfDatos[dfDatos['pais'].isin(pais)]
    textoPaises = ','.join(pais)
    textoFiltros = textoFiltros + ' ' + f'**Países:** {textoPaises}'

# Agrupamos los datos
dfDatosCantidad = dfDatos.groupby('mes')['Cantidad'].sum().reset_index()
dfDatosCiudad = dfDatos.groupby('ciudad')['Cantidad'].sum().reset_index()
textoCategorias=''
textoPaises=''

st.divider()
st.markdown(f'{textoFiltros}')
c1,c2,c3 = st.columns(3)
with c1:
    # Gráfico de unidades vendidas por mes
    figMes = px.bar(dfDatosCantidad,x='mes',y='Cantidad',title='Unidades por Mes',color_discrete_sequence=color_discrete_sequence)
    # on_select="rerun" hace que por cada clic reinicia la app
    parMes = st.plotly_chart(figMes,on_select="rerun")
    with st.expander('Puntos Mes'):
        st.write(parMes)
with c2:
    # Gráfico de unidades vendidas por ciudad
    figCiudad = px.bar(dfDatosCiudad,x='ciudad',y='Cantidad',color='ciudad',title='Unidades por Ciudad',color_discrete_sequence=color_discrete_sequence)
    parCiudad = st.plotly_chart(figCiudad,on_select="rerun")
    with st.expander('Puntos Ciudad'):
        st.write(parCiudad)
with c3:
    # Gráfico scatter de porcentaje de utilidad vs precio
    figScatter = px.scatter(dfDatos,x='util_porcent',y='precio',color='producto',title='Precio vs Utilidad %',color_discrete_sequence=color_discrete_sequence)
    # Indicamos que el eje X es en porcentaje
    figScatter.layout.xaxis.tickformat = ',.1%'    
    parScatter = st.plotly_chart(figScatter,on_select="rerun")
    with st.expander('Puntos Productos utilidad'):
        st.write(parScatter)

# Analizamos los datos retornados de los clic en los gráficos y aplicamos los filtros
if len(parMes.selection.points)>0:
    meses = [x['x'] for x in parMes.selection.points]
    dfDatos=dfDatos[dfDatos['mes'].isin(meses)]
    meses = [str(x['x']) for x in parMes.selection.points] # Se convierten los meses a string para poder concatenar
    meses = ','.join(meses)    
    textoFiltros = f'**Meses**:{meses}'

if len(parCiudad.selection.points)>0:
    ciudades = [x['x'] for x in parCiudad.selection.points]
    dfDatos=dfDatos[dfDatos['ciudad'].isin(ciudades)]
    ciudades = ','.join(ciudades)
    textoFiltros = textoFiltros + ' / ' +  f'**Ciudades**: {ciudades}'

if len(parScatter.selection.points)>0:
    productos = set([x['legendgroup'] for x in parScatter.selection.points])    
    dfDatos=dfDatos[dfDatos['producto'].isin(productos)]
    productos=','.join(productos)
    textoFiltros = textoFiltros + ' / ' +  f'**Productos**: {productos}'


st.divider()
# Mostramos la gráfica dependiendo de las selecciones de los charts
with st.container():
    st.write(textoFiltros)
    if len(parMes.selection.points)>1 or len(parMes.selection.points)==0:
        if len(parScatter.selection.points)>0:
            dfDatosGrupo=dfDatos.groupby(['mes','ciudad','producto'])['Cantidad'].sum().reset_index()
            altoChart=len(parScatter.selection.points)*2
            figVentas=px.line(dfDatosGrupo,x='mes',y='Cantidad',color='producto',facet_row='ciudad',color_discrete_sequence=color_discrete_sequence,facet_row_spacing =0.04) 
        else:
            dfDatosGrupo=dfDatos.groupby(['mes','ciudad'])['Cantidad'].sum().reset_index()
            figVentas=px.line(dfDatosGrupo,x='mes',y='Cantidad',color='ciudad',color_discrete_sequence=color_discrete_sequence)     
    else:
        if len(parScatter.selection.points)>0:
            dfDatosGrupo=dfDatos.groupby(['mes','ciudad','producto'])['Cantidad'].sum().reset_index()
            altoChart=len(parScatter.selection.points)*2
            figVentas=px.bar(dfDatosGrupo,x='mes',y='Cantidad',color='producto',facet_row='ciudad',color_discrete_sequence=color_discrete_sequence,facet_row_spacing =0.04,barmode='group') 
        else:
            dfDatosGrupo=dfDatos.groupby(['mes','ciudad'])['Cantidad'].sum().reset_index()
            figVentas=px.bar(dfDatosGrupo,x='mes',y='Cantidad',color='ciudad',color_discrete_sequence=color_discrete_sequence,barmode='group')             
    st.plotly_chart(figVentas,use_container_width=True)

