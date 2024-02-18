import streamlit as st
import pandas as pd
import plotly.express as px


# Definimos los parámetros de configuración de la aplicación
st.set_page_config(
    page_title="Dashboard Ventas Tienda Tech", #Título de la página
    page_icon="📊", # Ícono
    layout="wide", # Forma de layout ancho o compacto
    initial_sidebar_state="expanded" # Definimos si el sidebar aparece expandido o colapsado
)

# Cargamos el dataframe desde un CSV
dfDatos = pd.read_csv('https://raw.githubusercontent.com/gcastano/datasets/main/datosTiendaTecnologiaLatam.csv')

# Declaramos los parámetros en la barra lateral
with st.sidebar:
    # Filtro de años
    parAno=st.selectbox('Año',options=dfDatos['anio'].unique(),index=0)
    # Filtro de Mes    
    parMes = st.selectbox('Mes',options=dfDatos['mes'].unique(),index=0)
    # Filtro de País
    parPais = st.multiselect('País',options=dfDatos['pais'].unique())

# Si hay parametros seleccionados aplicamos los filtros
if parAno:
    dfDatos=dfDatos[dfDatos['anio']==parAno]

if parMes:
    dfDatos=dfDatos[dfDatos['mes']<=parMes]
if len(parPais)>0:
    dfDatos=dfDatos[dfDatos['pais'].isin(parPais)]

# Obtenemos los datos del mes seleccionado
dfMesActual = dfDatos[dfDatos['mes']==parMes]
# Obtenemos los datos del año anterior
if parMes:
    if parMes>1:
        dfMesAnterior = dfDatos[dfDatos['mes']==parMes-1]
    else:
        dfMesAnterior = dfDatos[dfDatos['mes']==parMes]

st.header('Tablero de control de ventas - Tienda Tech')

# Mostramos las métricas
# Declaramos 5 columnas de igual tamaño
c1,c2,c3,c4,c5 = st.columns(5)
with c1:
    productosAct= dfMesActual['Cantidad'].sum()
    productosAnt= dfMesAnterior['Cantidad'].sum()
    variacion=productosAnt-productosAct
    st.metric(f"Productos vendidos",f'{productosAct:,.0f} unidades', f'{variacion:,.0f}')
with c2:
    ordenesAct= dfMesActual['orden'].count()
    ordenesAnt= dfMesAnterior['orden'].count()
    variacion=ordenesAct-ordenesAnt
    st.metric(f"Ventas realizadas",f'{ordenesAct:.0f}', f'{variacion:.1f}')
with c3:
    ventasAct= dfMesActual['Total'].sum()
    ventasAnt= dfMesAnterior['Total'].sum()
    variacion=ventasAct-ventasAnt
    st.metric(f"Ventas totales",f'US$ {ventasAct:,.0f}', f'{variacion:,.0f}')
with c4:
    utilidadAct= dfMesActual['utilidad'].sum()
    utilidadAnt= dfMesAnterior['utilidad'].sum()
    variacion=utilidadAct-utilidadAnt
    st.metric(f"Utilidades",f'US$ {utilidadAct:,.0f}', f'{variacion:,.0f}')
with c5:
    utilPercentAct= (utilidadAct/ventasAct)*100
    utilPercentAnt= (utilidadAnt/ventasAnt)*100
    variacion=utilPercentAnt-utilPercentAct
    st.metric(f"Utilidad porcentual",f'{utilPercentAct:,.2f} %.', f'{variacion:,.0f} %')

# Declaramos 2 columnas en una proporción de 60% y 40%
c1,c2 = st.columns([60,40])
with c1:
    dfVentasMes = dfDatos.groupby('mes').agg({'Total':'sum'}).reset_index()
    fig = px.line(dfVentasMes,x='mes',y='Total', title='Ventas por mes')    
    st.plotly_chart(fig,use_container_width=True)
with c2:
    dfVentasPais = dfMesActual.groupby('pais').agg({'Total':'sum'}).reset_index().sort_values(by='Total',ascending=False)
    fig = px.bar(dfVentasPais,x='pais',y='Total', title=f'Ventas por categoría Mes: {parMes}', color='pais',text_auto=',.0f')
    fig.update_layout(showlegend=False) #Determina si se muestra o no la leyenda
    st.plotly_chart(fig,use_container_width=True)

# Declaramos 2 columnas en una proporción de 60% y 40%
c1,c2 = st.columns([60,40])
with c1:
    dfVentasCategoria = dfDatos.groupby(['mes','categoría']).agg({'Total':'sum'}).reset_index()
    fig = px.line(dfVentasCategoria,x='mes',y='Total', title='Ventas por mes y categoría',color='categoría')
    
    st.plotly_chart(fig,use_container_width=True)
with c2:
    dfVentasCategoria = dfMesActual.groupby('categoría').agg({'Total':'sum'}).reset_index().sort_values(by='Total',ascending=False)
    fig = px.bar(dfVentasCategoria,x='categoría',y='Total', title=f'Ventas por categoría Mes: {parMes}', color='categoría',text_auto=',.0f')
    fig.update_layout(showlegend=False) #Determina si se muestra o no la leyenda
    st.plotly_chart(fig,use_container_width=True)

# Consolidamos los datos para el comparativo de ventas por categoría y país
dfVentasPais =dfMesActual.groupby(['categoría','pais']).agg(cantidad=('orden','count')).reset_index()
# Creamos el gráfico en Plotly, el facet_col determina por qué campo se hace la separación de los gráficos
fig = px.pie(dfVentasPais,color='categoría',values='cantidad',facet_col='pais', facet_col_wrap=4, height=800,title='Ventas por categoría y país')
st.plotly_chart(fig,use_container_width=True)

# Mostramos las tablas de top de productos
c1,c2= st.columns(2)
dfProductosVentas =dfMesActual.groupby(['categoría','producto']).agg({'Total':'sum','orden':'count'}).reset_index()
with c1:    
    st.subheader('Top 10 productos más vendidos')
    st.table(dfProductosVentas.sort_values(by='orden',ascending=False).head(10)[['categoría','producto','Total','orden']])
with c2:    
    st.subheader('Top 10 productos menos vendidos')    
    st.table(dfProductosVentas.sort_values(by='orden').head(10)[['categoría','producto','Total','orden']])