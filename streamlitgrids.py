import streamlit as st
import pandas as pd
from matplotlib import colormaps
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

# Definimos los parámetros de configuración de la aplicación
st.set_page_config(
    page_title="Demo tablas con formato", #Título de la página
    page_icon="📊", # Ícono
    layout="wide", # Forma de layout ancho o compacto
    initial_sidebar_state="expanded" # Definimos si el sidebar aparece expandido o colapsado
)


# Código tomado de https://matplotlib.org/stable/users/explain/colors/colormaps.html
gradient = np.linspace(0, 1, 256)
gradient = np.vstack((gradient, gradient))

def plot_color_gradients(cmap_list):
    # Create figure and adjust figure height to number of colormaps
    nrows = len(cmap_list)
    figh = 0.35 + 0.15 + (nrows + (nrows - 1) * 0.1) * 0.22
    fig, axs = plt.subplots(nrows=nrows + 1, figsize=(6.4, figh))
    fig.subplots_adjust(top=1 - 0.35 / figh, bottom=0.15 / figh,
                        left=0.2, right=0.99)
    axs[0].set_title('Colormaps', fontsize=10)

    for ax, name in zip(axs, cmap_list):
        ax.imshow(gradient, aspect='auto', cmap=mpl.colormaps[name])
        ax.text(-0.01, 0.5, name, va='center', ha='right', fontsize=10,
                transform=ax.transAxes)

    # Turn off *all* ticks & spines, not just the ones with colormaps.
    for ax in axs:
        ax.set_axis_off()

    return fig

dfDatos = pd.read_csv('https://raw.githubusercontent.com/gcastano/datasets/main/datosTiendaTecnologiaLatam.csv')

dfProductosVentas =dfDatos.groupby('categoría').agg({'Total':'sum','orden':'count'}).reset_index()
dfProductosVentas['porcentaje_ventas']=dfProductosVentas['Total']/dfProductosVentas['Total'].sum()


st.subheader("Tabla sin formato")
c1,c2,c3=st.columns(3)
with c1:
    st.caption('st.table')
    st.table(dfProductosVentas)
with c2:
    st.caption('st.dataframe')
    st.dataframe(dfProductosVentas, use_container_width=True,hide_index=True)
with c3:
    st.caption('st.dataeditor')
    st.data_editor(dfProductosVentas, use_container_width=True,hide_index=True,disabled=True,key='de0')


dfFormato=dfProductosVentas.style.format({"Total": "$ {:,.2f}","orden": "{:.2f} órdenes",'porcentaje_ventas':"{:.2%}"})



st.subheader("Formato de números y porcentajes")
c1,c2,c3=st.columns(3)
with c1:
    st.caption('st.table')
    st.table(dfFormato)
with c2:
    st.caption('st.dataframe')
    st.dataframe(dfFormato, use_container_width=True,hide_index=True)
with c3:
    st.caption('st.dataeditor')
    st.data_editor(dfFormato, use_container_width=True,hide_index=True,disabled=True,key='de1')

parColorMap= st.selectbox('Matplotlib Colormaps',options= list(colormaps))
colormapsCant=len(list(colormaps))
st.write(f'Cantidad de paletas de colores:{colormapsCant}')

with st.expander('colormaps'):
    fig = plot_color_gradients(list(colormaps))
    st.write(fig)

dfFormato = dfProductosVentas.style.background_gradient(cmap =parColorMap,subset=['Total','porcentaje_ventas']).format({"Total": "$ {:,.2f}","orden": "{:.2f} órdenes","porcentaje_ventas":"{:.2%}"})
# dfFormato = dfProductosVentas.style.background_gradient(cmap =parColorMap).format({"Total": "$ {:,.2f}","orden": "{:.2f} órdenes","porcentaje_ventas":"{:.2%}"})
st.subheader("Formato heatmap combinado con formato de números")
c1,c2,c3=st.columns(3)
with c1:
    st.caption('st.table')
    st.table(dfFormato)
with c2:
    st.caption('st.dataframe')
    st.dataframe(dfFormato, use_container_width=True,hide_index=True)
with c3:
    st.caption('st.dataeditor')
    st.data_editor(dfFormato, use_container_width=True,hide_index=True,disabled=True,key='de2')

parResaltar=st.radio('Resaltar valores',options=['Máximos','Mínimos'],horizontal=True)
# dfFormato = dfProductosVentas.style.background_gradient(cmap =parColorMap,subset=['orden']).format({"Total": "$ {:,.2f}","orden": "{:.2f} órdenes","porcentaje_ventas":"{:.2%}"})
if parResaltar=='Máximos':
    dfFormato = dfProductosVentas.style.highlight_max(subset=['Total','porcentaje_ventas'],color='green')
else:
    dfFormato = dfProductosVentas.style.highlight_min(subset=['Total','porcentaje_ventas'],color='red')

st.subheader(f"Formato resaltar valores {parResaltar}")
c1,c2,c3=st.columns(3)
with c1:
    st.caption('st.table')
    st.table(dfFormato)
with c2:
    st.caption('st.dataframe')
    st.dataframe(dfFormato, use_container_width=True,hide_index=True)
with c3:
    st.caption('st.dataeditor')
    st.data_editor(dfFormato, use_container_width=True,hide_index=True,disabled=True,key='de3')

dfFormato = dfProductosVentas.style.bar(color='lightgray',height=90)
st.subheader("Formato barras en celdas")

c1,c2,c3=st.columns(3)
with c1:
    st.caption('st.table')
    st.table(dfFormato)
with c2:
    st.caption('st.dataframe')
    st.dataframe(dfFormato, use_container_width=True)
with c3:
    st.caption('st.dataeditor')
    st.data_editor(dfFormato, use_container_width=True,hide_index=True,disabled=True,key='de4')


st.subheader("Uso de formato en st.data_editor")
dfVentasPeriodo = dfDatos.groupby(['categoría','anio','mes'])['Total'].sum().reset_index()
maxVentas = dfDatos['Total'].max()
dfVentasPeriodo = dfVentasPeriodo.sort_values(by=['categoría']).groupby('categoría')['Total'].apply(list)
dfProductosVentas=dfProductosVentas.merge(dfVentasPeriodo,on='categoría').rename(columns={'Total_x':'Total','Total_y':'ventas'})
dfProductosVentas['porcentaje_ventas']=dfProductosVentas['porcentaje_ventas']*100

dfCantidadPeriodo = dfDatos.groupby(['categoría','anio','mes'])['Cantidad'].sum().reset_index()
maxCantidad = dfDatos['Cantidad'].max()
dfCantidadPeriodo = dfCantidadPeriodo.sort_values(by=['categoría']).groupby('categoría')['Cantidad'].apply(list)
dfProductosVentas=dfProductosVentas.merge(dfCantidadPeriodo,on='categoría')

st.data_editor(
    dfProductosVentas,
    column_config={
        "porcentaje_ventas": st.column_config.ProgressColumn(
            "Ventas",
            help="Porcentaje Ventas por Categoría",
            format="%.2f",
            min_value=0,
            max_value=100,
        ),
        "ventas": st.column_config.LineChartColumn(
            "Tendencia Ventas",
            width="medium",
            help="Ventas históricas",
            y_min=0,
            y_max=int(maxVentas),
         ),
         "Cantidad": st.column_config.BarChartColumn(
            "Unidades",
            width="medium",
            help="Unidades Vendidas",
            y_min=0,
            y_max=int(maxCantidad),
         ),
    },
    hide_index=True,
    disabled=True,
    use_container_width=True
)
