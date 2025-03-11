# Importar las librerías necesarias
import streamlit as st  # Para crear la aplicación web. Instalar con: pip install streamlit
import pandas as pd  # Para manipulación de datos. Instalar con: pip install pandas
import plotly.express as px  # Para crear gráficos interactivos. Instalar con: pip install plotly

# Configurar el título y el diseño de la página
st.set_page_config(layout="wide", page_title="Ejemplo drill down con Streamlit y Plotly")
st.title("Ejemplo drill down con Streamlit y Plotly")

# Cargar los datos desde un archivo CSV en línea
dfSales = pd.read_csv("https://raw.githubusercontent.com/gcastano/datasets/refs/heads/main/datosTiendaTecnologiaLatam.csv", parse_dates=["fecha"])

# Definir una paleta de colores para los gráficos
paletacolor = px.colors.qualitative.Plotly

# Función para generar agrupaciones de fechas (trimestre, mes, año)
def generarGruposFecha(df, columnaFecha):
    df["Trimestre"] = df[columnaFecha].dt.to_period('Q').astype(str).str.replace("Q", "T")
    df["Mes"] = df[columnaFecha].dt.to_period('M').astype(str)
    df["Año"] = df[columnaFecha].dt.to_period('Y').astype(str)
    return df

# Aplicar la función para generar las agrupaciones de fecha
dfSales = generarGruposFecha(dfSales, "fecha")

# Función para generar datos para un gráfico dado un grupo (ej. ventas por mes)
def generarDatosPorGrupo(grupo, df):    
    # return arg list to set x, y and chart title    
    dfGrupo = df.groupby(grupo)["Total"].sum().reset_index()
    titulo = f"Ventas por {grupo}"
    return [{'x': [dfGrupo[grupo]], 'y': [dfSales["Total"]]}, {'title': titulo}]

# Crear un gráfico de barras para las ventas por día
figxFecha = px.bar(dfSales.groupby("fecha")["Total"].sum().reset_index(), x="fecha", y="Total", title="Ventas por día", text="Total")
# Agregar botones para cambiar la granularidad del gráfico (día, mes, trimestre)
figxFecha.update_layout(
    updatemenus=[
        dict(
            type="buttons",
            direction="left",
            buttons=list([
                dict(
                    args=generarDatosPorGrupo("fecha", dfSales),
                    label="Día",
                    method="update"
                ),
                dict(
                    args=generarDatosPorGrupo("Mes", dfSales),
                    label="Mes",
                    method="update"
                ),
                dict(
                    args=generarDatosPorGrupo("Trimestre", dfSales),
                    label="Trimestre",
                    method="update"
                )
            ]),
            showactive=True,
            x=0.8,
            xanchor="left",
            y=1.2,
            yanchor="top"
        ),
    ]
)

# Función para generar datos para un gráfico de productos por grupo (categoría o producto)
def generarDatosPorGrupoProducto(grupo, df):    
    dfGrupo = df.groupby(grupo)["Cantidad"].sum().reset_index()
    return [{'x': [dfGrupo[grupo]], 'y': [dfGrupo["Cantidad"]], 'text': [dfGrupo["Cantidad"]]}, {'title': f"Ventas por {grupo}"}]

# Crear un gráfico de barras para las ventas por categoría
figxProducto = px.bar(dfSales.groupby(["categoría"])["Cantidad"].sum().reset_index(), x="categoría", y="Cantidad", title="Ventas por categoría", text="Cantidad")
# Agregar botones para cambiar la granularidad (categoría, producto)
figxProducto.update_layout(
    updatemenus=[
        dict(
            type="buttons",
            direction="left",
            buttons=list([
                dict(
                    args=generarDatosPorGrupoProducto("categoría", dfSales),
                    label="Categoría",
                    method="update"
                ),
                dict(
                    args=generarDatosPorGrupoProducto("producto", dfSales),
                    label="Producto",
                    method="update"
                )
            ]),
            showactive=True,
            x=0.8,
            xanchor="left",
            y=1.2,
            yanchor="top"
        ),
    ]
)

# Dividir la página en dos columnas
c1, c2 = st.columns(2)
# Mostrar el gráfico de ventas por fecha en la primera columna
with c1:
    with st.container(border=True):
        st.plotly_chart(figxFecha)
# Mostrar el gráfico de ventas por producto en la segunda columna
with c2:
    with st.container(border=True):
        st.plotly_chart(figxProducto)

# Función para generar un gráfico drill-down para las fechas usando st.segmented_control
@st.fragment
def generarDrillDownFecha():
    parNivel = st.segmented_control("Nivel de detalle", ["Día", "Mes", "Trimestre"], default="Día")
    if parNivel == "Día":
        fig = px.bar(dfSales.groupby("fecha")["Total"].sum().reset_index(), x="fecha", y="Total", title="Ventas por día")
    elif parNivel == "Mes":
        fig = px.bar(dfSales.groupby("Mes")["Total"].sum().reset_index(), x="Mes", y="Total", title="Ventas por mes")
    else:
        fig = px.bar(dfSales.groupby("Trimestre")["Total"].sum().reset_index(), x="Trimestre", y="Total", title="Ventas por trimestre")
    with st.container(border=True):
        st.plotly_chart(fig)


# Función para generar un gráfico drill-down para productos usando st.segmented_control (Comentado en el código original)
@st.fragment    
def generarDrillDownProducto():
    parNivel = st.segmented_control("Nivel de detalle", ["Categoría", "Producto"], default="Categoría")
    if parNivel == "Categoría":
        fig = px.bar(dfSales.groupby("categoría")["Cantidad"].sum().reset_index(), x="categoría", y="Cantidad", title="Ventas por categoría")
    else:
        fig = px.bar(dfSales.groupby("producto")["Cantidad"].sum().reset_index(), x="producto", y="Cantidad", title="Ventas por producto")
    with st.container(border=True):
        st.plotly_chart(fig)

# Dividir la página en dos columnas
c1, c2 = st.columns(2)
# Mostrar el drill-down de fechas en la primera columna
with c1:
    generarDrillDownFecha()
# Mostrar el drill-down de productos en la segunda columna (Comentado en el código original)
with c2:
    generarDrillDownProducto()


#  Gráfico drill-down interactivo usando plotly y variables de sesión
if "categoriaSeleccionada" not in st.session_state:
    st.session_state.categoriaSeleccionada = None

@st.fragment    
def generarDrillDownStreamlit():
    placeholder = st.empty()
    with placeholder:
        with st.container(border=True):
            # Si se ha seleccionado una categoría, mostrar las ventas por producto de esa categoría
            if st.session_state.categoriaSeleccionada is not None:
                # Filtrar los datos por la categoría seleccionada
                dfProducto = dfSales[dfSales["categoría"] == st.session_state.categoriaSeleccionada]
                # Crear un gráfico de barras con las ventas por producto
                parDrillUp = st.button(":material/arrow_upward: Regresar")
                figDrillDown = px.bar(
                    dfProducto.groupby("producto")["Cantidad"].sum().reset_index(),
                    x="producto",
                    y="Cantidad",
                    title=f"Ventas por producto de la categoría {st.session_state.categoriaSeleccionada}",
                    color_discrete_sequence=[st.session_state.colorProducto]
                )
                if parDrillUp:
                    # Limpiar la variable de sesión y volver a ejecutar el fragmento
                    # para regresar al nivel anterior
                    st.session_state.categoriaSeleccionada = None
            # Si no se ha seleccionado una categoría, mostrar las ventas por categoría
            else:
                dfSalesCategory = dfSales.groupby("categoría")["Cantidad"].sum().reset_index()
                figDrillDown = px.bar(
                    dfSalesCategory,
                    x="categoría",
                    y="Cantidad",
                    title="Ventas por categoría",
                    color="categoría",
                    color_discrete_sequence=paletacolor
                )

            # Mostrar el gráfico y capturar los eventos de selección
            eventos = st.plotly_chart(figDrillDown, use_container_width=True, on_select="rerun")
            # Si se selecciona una categoría, guardarla en la variable de sesión y volver a ejecutar el fragmento
            if len(eventos.selection.points) > 0:
                st.session_state.categoriaSeleccionada = eventos.selection.points[0]["label"]
                #Obtenemos la lista de categorías
                colorProducto = dfSalesCategory["categoría"].unique()                
                #Obtenemos el color de la categoría seleccionada
                st.session_state.colorProducto = paletacolor[colorProducto.tolist().index(st.session_state.categoriaSeleccionada)]
                #Volvemos a ejecutar el fragmento
                st.rerun(scope="fragment")
            # Si no se selecciona ninguna categoría, limpiar la variable de sesión
            else:
                st.session_state.categoriaSeleccionada = None

# Ejecutar la función para generar el drill-down interactivo
generarDrillDownStreamlit()