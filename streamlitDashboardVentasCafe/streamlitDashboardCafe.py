# --- LIBRERÍAS ---
# Se importan todas las librerías necesarias para el proyecto.

# streamlit: Es el framework principal para construir la aplicación web interactiva.
# Comando de instalación: pip install streamlit
import streamlit as st

# pandas: Fundamental para la manipulación y análisis de datos. Se usa para leer el archivo Excel y transformar los datos.
# Comando de instalación: pip install pandas openpyxl
import pandas as pd

# plotly.express: Una librería de alto nivel para crear gráficos interactivos y estéticos de forma sencilla.
# Comando de instalación: pip install plotly
import plotly.express as px

# bumplot: Una librería específica para crear "bump charts", que son excelentes para visualizar cambios en el ranking a lo largo del tiempo.
# Comando de instalación: pip install bumplot
from bumplot import bumplot

# matplotlib: Una librería de visualización de datos muy potente. Aquí se usa como base para el bump chart.
# Comando de instalación: pip install matplotlib
from matplotlib import cm
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# --- CONFIGURACIÓN DE LA PÁGINA ---
# Configura el título de la pestaña del navegador y el layout de la página a "wide" para aprovechar todo el ancho.
st.set_page_config(page_title="Dashboard Tienda Café", layout="wide")

# Título principal del dashboard que se mostrará en la aplicación.
st.title(":material/coffee: Dashboard Tienda Café")
    
# --- ESTILOS PERSONALIZADOS ---
# Se obtienen los colores del tema actual de Streamlit para que los gráficos y estilos coincidan.
chartCategoricalColors = st.get_option("theme.chartCategoricalColors")
secondaryBackgroundColor = st.get_option("theme.secondaryBackgroundColor")
textColor = st.get_option("theme.textColor")

# Se define un bloque de CSS para personalizar el fondo de algunos componentes de Streamlit (métricas y gráficos).
# Esto se hace para que el diseño sea más cohesivo y atractivo.
st.write('<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">', unsafe_allow_html=True)
estilos = """
<style>
    div[class*='st-key-chart'],
    .stMetric, .stMetric svg{
        background-color: #FCF9F3!important
    }
    div.st-key-numeroproductos div[data-testid="stMetricValue"]>div::before {
        content: "\e541";
        font-family: 'Material Icons'; 
        vertical-align: -20%;
        color:#8B4513;
    }
    div.st-key-numerotiendas div[data-testid="stMetricValue"]>div::before {
        content: "\e8d1";
        font-family: 'Material Icons'; 
        vertical-align: -20%;   
        color:#8B4513;
    }
</style>
"""
# Se inyecta el CSS en la aplicación de Streamlit usando st.html.
st.html(estilos)

# --- FUNCIONES ---

@st.cache_data 
def cargarDatos():
    """
    Carga los datos de ventas desde un archivo Excel.
    
    Utiliza el decorador @st.cache_data de Streamlit para que los datos se carguen
    una sola vez y se mantengan en caché. Esto mejora significativamente el rendimiento
    de la aplicación, ya que no tiene que leer el archivo cada vez que el usuario
    interactúa con un widget.

    Returns:
        pd.DataFrame: Un DataFrame de pandas con los datos de ventas del café.
    """
    # Fuente del dataset original.
    # Fuente: https://www.kaggle.com/datasets/ahmedabbas757/coffee-sales
    dfDatosVentas = pd.read_excel("Coffee Shop Sales.xlsx")
    return dfDatosVentas


def generarMetrica(df, campo, titulo, grafica="linea", prefijo="$"):
    """
    Crea y muestra una métrica de Streamlit con su variación y un mini-gráfico.

    Args:
        df (pd.DataFrame): DataFrame que contiene los datos a lo largo del tiempo.
        campo (str): El nombre de la columna a analizar (ej. "Sales").
        titulo (str): El título que se mostrará sobre la métrica.
        grafica (str, optional): El tipo de mini-gráfico a mostrar ('linea' o 'barra'). Por defecto es 'linea'.
        prefijo (str, optional): Un prefijo para el valor (ej. "$"). Por defecto es "$".
    """
    # Se extrae el último dato de la columna para mostrarlo como valor principal.
    UltDato = df.iloc[-1][campo]
    # Se extrae el penúltimo dato para calcular la variación.
    AntDato = df.iloc[-2][campo]
    # Se calcula la variación porcentual entre el último y el penúltimo dato.
    variacion = (UltDato - AntDato) / AntDato
    # Se convierte la columna entera en una lista para usarla en el mini-gráfico.
    arrDatosVentas = df[campo].to_list()
    # Se utiliza el componente st.metric para mostrar la información formateada.
    st.metric(label=titulo, value=f"{prefijo}{UltDato:,.0f}", delta=f"{variacion:.2%}", chart_data=arrDatosVentas, delta_color="normal", chart_type=grafica, border=True, width=300)

def aplicarBackgroundChart(fig, color):
    """
    Aplica un color de fondo a un gráfico de Plotly para que coincida con el tema.

    Args:
        fig (plotly.graph_objects.Figure): La figura de Plotly a modificar.
        color (str): El color de fondo a aplicar.

    Returns:
        plotly.graph_objects.Figure: La figura de Plotly con el fondo actualizado.
    """
    # Actualiza el layout del gráfico para cambiar el color del área de trazado y el papel.
    return fig.update_layout({
        "plot_bgcolor": color,
        "paper_bgcolor": color,
    })

# --- CARGA Y TRANSFORMACIÓN DE DATOS ---

# Carga el DataFrame principal usando la función cacheada.
dfDatosVentas = cargarDatos()

# 1. Creación de nuevas columnas
# Se calcula la columna 'Sales' multiplicando la cantidad de la transacción por el precio unitario.
dfDatosVentas["Sales"] = dfDatosVentas["transaction_qty"] * dfDatosVentas["unit_price"]

# Se extraen componentes de la fecha para facilitar los agrupamientos posteriores.
# .dt es un accesor que permite usar métodos de fecha y hora en una Serie de pandas.
dfDatosVentas['Month_Name'] = dfDatosVentas['transaction_date'].dt.month_name(locale='es_ES') # Nombre del mes en español
dfDatosVentas['Month'] = dfDatosVentas['transaction_date'].dt.month # Número del mes
dfDatosVentas['Year'] = dfDatosVentas['transaction_date'].dt.year # Año
dfDatosVentas['Week'] = dfDatosVentas['transaction_date'].dt.isocalendar().week # Número de la semana del año

# --- FILTROS INTERACTIVOS ---
# Se crea un selectbox (menú desplegable) para que el usuario pueda filtrar por categoría de producto.
# Las opciones incluyen "Todas" más la lista de categorías únicas del DataFrame.
parTipoProducto = st.selectbox("Categoría de producto", options=["Todas"] + list(dfDatosVentas["product_category"].unique()))

# Si el usuario elige una categoría específica (diferente de "Todas"), se filtra el DataFrame principal.
if parTipoProducto != "Todas":
    dfDatosVentas = dfDatosVentas[dfDatosVentas["product_category"] == parTipoProducto]

# --- AGRUPACIONES DE DATOS (DATA WRANGLING) ---
# Se crean diferentes DataFrames agregados que servirán como fuente para los gráficos y métricas.
# El patrón .groupby().agg().reset_index() es muy común en pandas para resumir datos.

# Agrupa las ventas y cantidades por Año, Mes y Nombre del Mes.
dfVentasMes = dfDatosVentas.groupby(['Year', 'Month', 'Month_Name']).agg({"Sales": "sum", "transaction_qty": "sum"}).reset_index()

# Agrupa las ventas y cantidades por Mes y por Tienda.
dfVentasMesTienda = dfDatosVentas.groupby(['Year', 'Month', 'Month_Name', 'store_location']).agg({"Sales": "sum", "transaction_qty": "sum"}).reset_index()

# Agrupa las ventas y cantidades por Semana.
dfVentasSemana = dfDatosVentas.groupby(['Year', 'Week']).agg({"Sales": "sum", "transaction_qty": "sum"}).reset_index()

# Se decide dinámicamente si agrupar por tipo de producto o categoría general, basado en el filtro.
if parTipoProducto != "Todas":
    campoGrupo = "product_type"
else:
    campoGrupo = "product_category"

# Agrupa las ventas por Mes y por la categoría/tipo de producto seleccionado.
dfVentasProducto = dfDatosVentas.groupby(['Year', 'Month', 'Month_Name', campoGrupo]).agg({"Sales": "sum", "transaction_qty": "sum"}).reset_index()

# Se pivotea la tabla para tener las tiendas como columnas y los productos como filas.
dfVentasProductoTienda = dfDatosVentas.groupby(['store_location', campoGrupo]).agg({"Sales": "sum"}).reset_index()
dfVentasProductoTienda = dfVentasProductoTienda.pivot(index=campoGrupo, columns='store_location', values='Sales').fillna(0).reset_index()

# Se prepara el DataFrame para el Bump Chart. Se pivotea para tener los productos como columnas y los meses como filas.
dfVentasProductoBump = dfVentasProducto.pivot(index=['Month_Name', 'Month'], columns=campoGrupo, values='Sales').fillna(0).reset_index()
dfVentasProductoBump = dfVentasProductoBump.sort_values(by="Month") # Se asegura que los meses estén ordenados.

# --- CÁLCULOS PARA MÉTRICAS Y GRÁFICOS ---
# Se obtienen datos específicos del último y penúltimo mes/semana para las métricas y etiquetas.
dfMesAnt = dfVentasMes.iloc[-2]
dfMesUlt = dfVentasMes.iloc[-1]
MesUltNombre = dfMesUlt["Month_Name"]

# Se filtran los datos de ventas por producto para el último mes.
dfVentasProductoUlt = dfVentasProducto[(dfVentasProducto["Month"] == dfMesUlt["Month"]) & (dfVentasProducto["Year"] == dfMesUlt["Year"])]
# Se calcula el ranking de ventas de productos para el último mes.
dfVentasProductoUlt["Sales_Rank"] = dfVentasProductoUlt["Sales"].rank(ascending=False, method="min").astype(int)
dfVentasProductoUlt = dfVentasProductoUlt.sort_values(by="Sales_Rank")

dfSemanaAnt = dfVentasSemana.iloc[-2]
dfSemanaUlt = dfVentasSemana.iloc[-1]
SemanaUlt = dfSemanaUlt["Week"]

# Se calculan métricas generales.
numTiendas = dfDatosVentas["store_id"].nunique() # Cuenta el número de tiendas únicas.
numProductos = dfDatosVentas["product_id"].nunique() # Cuenta el número de productos únicos.

# --- RENDERIZADO DEL DASHBOARD ---

# Contenedor para las métricas principales (KPIs).
with st.container(horizontal=True, horizontal_alignment="center", key="metricas"):
    generarMetrica(dfVentasMes, "Sales", f"Ventas **{MesUltNombre}**", "line")
    generarMetrica(dfVentasMes, "transaction_qty", f"Unidades Mes **{MesUltNombre}**", "area", "")
    generarMetrica(dfVentasSemana, "Sales", f"Ventas semana **{SemanaUlt}**", "barra")
    generarMetrica(dfVentasSemana, "transaction_qty", f"Unidades semana **{SemanaUlt}**", "area", "")
    with st.container(gap='small',key="metricasAdicionales"):
        # st.write(":material/store:")
        with st.container(gap='small',key="numerotiendas"):
            st.metric(label="Número de tiendas", value=f"{numTiendas}", delta="", border=True, width=300)
        with st.container(gap='small',key="numeroproductos"):
            st.metric(label="Número de Productos", value=f"{numProductos}", delta="", border=True, width=300)
st.divider()
st.subheader(":material/store: Análisis por tiendas")
# Contenedor para los gráficos relacionados con las tiendas.
with st.container(horizontal=True, horizontal_alignment="center"):
    with st.container(border=True, key="chart-ventasTienda"):
        # Gráfico de barras agrupadas de ventas por tienda y mes.
        figVentasTienda = px.bar(dfVentasMesTienda, x='Month_Name', y='Sales', color='store_location', barmode='group', title="Ventas por tienda y mes", color_discrete_sequence=chartCategoricalColors)
        st.plotly_chart(aplicarBackgroundChart(figVentasTienda, secondaryBackgroundColor), use_container_width=True, theme=None)
    
    with st.container(border=True, key="chart-sunburstTienda"):
        # Gráfico Sunburst para ver la distribución de ventas jerárquicamente: Tienda -> Categoría -> Tipo.
        fig = px.sunburst(dfDatosVentas, path=['store_location', 'product_category', 'product_type'], values='Sales', title="Ventas por ubicación y categoría", color_discrete_sequence=chartCategoricalColors)
        st.plotly_chart(aplicarBackgroundChart(fig, secondaryBackgroundColor), use_container_width=True, theme=None)
    
    with st.container(border=True, key="chart-dataframe"):
        # Se muestra el DataFrame pivoteado como una tabla con un mapa de calor.
        columnas = dfVentasProductoTienda.columns[1:]
        # Se define un mapa de colores personalizado para el gradiente.
        colors = ["#8B0000", "#DAA520", "#228B22"]
        cmap_name = "my_custom_cmap"
        custom_cmap = LinearSegmentedColormap.from_list(cmap_name, colors, N=256)
        # Se aplica el estilo de gradiente al DataFrame y se formatea para que no tenga decimales.
        styled_df = dfVentasProductoTienda.style.background_gradient(subset=columnas, cmap=custom_cmap).format("{:,.0f}", subset=columnas)
        st.write("Ventas por producto y tienda")
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
st.divider()
st.subheader(":material/local_cafe: Análisis por Productos")
# Contenedor para los gráficos relacionados con los productos.
with st.container(horizontal=True, horizontal_alignment="center", gap="large"):
    # Se usan columnas para organizar mejor los gráficos en el espacio disponible.
    cols = st.columns([3, 3, 4])
    with cols[0]:
        with st.container(border=True, key="chart-ventasProducto"):
            # Gráfico de barras de ventas por categoría/tipo de producto y mes.
            figVentasProducto = px.bar(
                dfVentasProducto,
                x='Month_Name',
                y='Sales',
                color=campoGrupo,
                barmode='group',
                title="Ventas por categoría y mes" if parTipoProducto == "Todas" else f"Ventas por categoría {parTipoProducto} y mes",
                color_discrete_sequence=chartCategoricalColors
            )
            st.plotly_chart(aplicarBackgroundChart(figVentasProducto, secondaryBackgroundColor), use_container_width=True, border=True, theme=None)
    
    with cols[1]:
        with st.container(border=True, key="chart-sunburstProducto"):
            # Gráfico Sunburst para ver la jerarquía de productos.
            fig = px.sunburst(dfDatosVentas, path=['product_category', 'product_type', 'product_detail'], values='Sales', title="Ventas por categoría y detalle", color_discrete_sequence=chartCategoricalColors)
            st.plotly_chart(aplicarBackgroundChart(fig, secondaryBackgroundColor), use_container_width=True, theme=None)
    
    with cols[2]:
        # --- Creación del Bump Chart con Matplotlib y bumplot ---
        # Se extraen los nombres de las columnas que contienen las categorías/productos.
        camposCategorias = [x for x in dfVentasProductoBump.columns if "Month" not in x]
        categoriaProductos = dfVentasProductoUlt[campoGrupo].to_list()

        # Se crea la figura y los ejes de Matplotlib.
        fig, ax = plt.subplots(figsize=(8, 7))
        
        # Se llama a la función bumplot para generar el gráfico de ranking.
        bumplot(
            x="Month",
            y_columns=camposCategorias,
            data=dfVentasProductoBump,
            curve_force=0.5,
            plot_kwargs={"lw": 4},
            scatter_kwargs={"s": 150, "ec": "black", "lw": 2},
            colors=chartCategoricalColors,
        )
        
        # --- Personalización del gráfico de Matplotlib ---
        ax.set_title("Ranking de productos por mes" if parTipoProducto == "Todas" else f"Ranking de productos {parTipoProducto} por mes", fontsize=16)
        ax.set_facecolor(secondaryBackgroundColor)
        fig.patch.set_facecolor(secondaryBackgroundColor)
        
        ax.set_yticks(
            [i for i in range(1, len(categoriaProductos) + 1)],
        )
        
        # Se añaden etiquetas de texto al final de cada línea del bump chart.
        ultMes = dfVentasProductoBump["Month"].max()
        for i, categoria in enumerate(categoriaProductos):
            ax.text(
                x=ultMes + 0.2,
                y=i + 1,
                s=categoria,
                size=11,
                va="center",
                ha="left",
            )
        
        # Se establece la etiqueta del eje X como "Mes".
        ax.set_xlabel("Mes", fontsize=12)
        # Se ocultan los bordes (spines) superior, derecho, izquierdo y inferior del gráfico para un diseño más limpio.
        ax.spines[["top", "right", "left", "bottom"]].set_visible(False)
        # Se agrega una cuadrícula con transparencia para mejorar la legibilidad.
        ax.grid(alpha=0.4)
        
        # Se ajustan los colores del texto para que coincidan con el tema de Streamlit.
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_color(textColor)
        ax.title.set_color(textColor)
        ax.xaxis.label.set_color(textColor)
        
        # Se muestra el gráfico de Matplotlib en Streamlit.
        with st.container(border=True, key="chart-bumpProducto"):
            st.pyplot(fig, use_container_width=True)