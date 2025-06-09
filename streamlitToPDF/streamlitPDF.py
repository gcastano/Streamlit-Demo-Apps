# Importamos la librería Streamlit, que es un framework para crear aplicaciones web interactivas y dashboards en Python de forma rápida.
# Comando para instalar: pip install streamlit
import streamlit as st

# Importamos la librería Pandas, fundamental para la manipulación y análisis de datos en Python, especialmente con estructuras tipo DataFrame.
# Comando para instalar: pip install pandas
import pandas as pd

# Importamos la función pisa de la librería xhtml2pdf, utilizada para convertir contenido HTML y CSS a formato PDF.
# Comando para instalar: pip install xhtml2pdf
# https://xhtml2pdf.readthedocs.io/en/latest/index.html
from xhtml2pdf import pisa

# Importamos el módulo io, que proporciona herramientas para trabajar con diversos tipos de flujos de E/S (entrada/salida), como buffers en memoria.
# Es parte de la librería estándar de Python, no requiere instalación adicional.
import io

# Importamos el módulo base64, que se utiliza para codificar datos binarios en formato de texto ASCII (Base64) y viceversa.
# Es útil para embeber imágenes en HTML o transferir datos binarios en formatos de texto.
# Es parte de la librería estándar de Python, no requiere instalación adicional.
import base64

# Importamos Plotly Express como px, una interfaz de alto nivel para Plotly, que permite crear figuras interactivas y de calidad de publicación fácilmente.
# Comando para instalar: pip install plotly
import plotly.express as px

# Importamos plotly.io como pio, que contiene funciones para la entrada/salida de figuras de Plotly, incluyendo la exportación a imágenes.
# Se instala junto con Plotly: pip install plotly
import plotly.io as pio


# Definimos los parámetros de configuración de la aplicación Streamlit
st.set_page_config(
    page_title="Dashboard Ventas Tienda Tech", # Título que aparecerá en la pestaña del navegador.
    page_icon="📊", # Ícono que aparecerá en la pestaña del navegador (puede ser un emoji o una URL de imagen).
    layout="wide", # Define el layout de la página. "wide" utiliza todo el ancho disponible, "centered" lo centra con márgenes.
    initial_sidebar_state="expanded" # Define el estado inicial de la barra lateral. "expanded" la muestra abierta, "collapsed" la oculta.
)


def plotly_chart_to_base64(fig):
    """
    Convierte un gráfico de Plotly a una imagen PNG en formato base64 a color.

    Esta función toma una figura de Plotly, la convierte en una imagen PNG en bytes
    utilizando plotly.io.to_image, y luego codifica estos bytes en una cadena
    base64 para poder ser embebida, por ejemplo, en un documento HTML.

    Args:
        fig (plotly.graph_objects.Figure): La figura de Plotly que se va a convertir.

    Returns:
        str: Una cadena de texto que representa la imagen PNG codificada en base64.
    """
    # Convierte la figura de Plotly a bytes en formato PNG.
    # 'scale=2' aumenta la resolución de la imagen para mejor calidad.
    img_bytes = pio.to_image(fig, format="png", scale=2)
    # Codifica los bytes de la imagen a base64 y luego decodifica el resultado a una cadena UTF-8.
    fig_base64 = base64.b64encode(img_bytes).decode("utf-8")
    return fig_base64

def generarImagenBase64(fig):
    """
    Genera una imagen en formato base64 a partir de una figura de Plotly.

    Esta función convierte una figura de Plotly directamente a una imagen PNG en bytes
    y luego la codifica en base64. Es similar a plotly_chart_to_base64 pero
    usa directamente el método to_image de la figura.

    Args:
        fig (plotly.graph_objects.Figure): La figura de Plotly a convertir.

    Returns:
        str: Cadena de texto con la imagen PNG codificada en base64.
    """
    # Convierte la figura de Plotly a bytes en formato PNG.
    # 'scale=2' se utiliza para obtener una imagen de mayor resolución.
    img_bytes = fig.to_image(format="png", scale=2)
    # Codifica los bytes de la imagen a base64.
    # .decode("utf-8") convierte los bytes codificados en base64 a una cadena de texto.
    fig_base64 = base64.b64encode(img_bytes).decode("utf-8")
    return fig_base64

# Cargamos el dataframe desde un archivo CSV alojado en una URL de GitHub.
# pd.read_csv es una función de Pandas que lee datos tabulares de un archivo CSV y los carga en un DataFrame.
dfDatos = pd.read_csv('https://raw.githubusercontent.com/gcastano/datasets/main/datosTiendaTecnologiaLatam.csv')

# Declaramos los parámetros o filtros en la barra lateral (sidebar) de la aplicación Streamlit.
# 'with st.sidebar:' agrupa todos los elementos que se mostrarán en la barra lateral.
with st.sidebar:
    # Filtro de años: Crea un widget de selección (selectbox) para que el usuario elija un año.
    # 'options' se llena con los valores únicos de la columna 'anio' del DataFrame.
    # 'index=0' establece el primer valor de la lista como la opción seleccionada por defecto.
    parAno=st.selectbox('Año',options=dfDatos['anio'].unique(),index=0)
    
    # Filtro de Mes: Similar al filtro de año, pero para la columna 'mes'.
    parMes = st.selectbox('Mes',options=dfDatos['mes'].unique(),index=0)
    
    # Filtro de País: Crea un widget de selección múltiple (multiselect) para países.
    # El usuario puede seleccionar uno, varios o ningún país.
    # 'options' se llena con los valores únicos de la columna 'pais'.
    parPais = st.multiselect('País',options=dfDatos['pais'].unique())
    
    # Filtro Plantilla: Permite al usuario seleccionar una plantilla HTML para el reporte PDF.
    parPlantilla = st.selectbox('Plantilla',options=['plantilla.html','plantilla1.html'],index=0)

# Aplicamos los filtros al DataFrame si el usuario ha seleccionado algún valor.
# Si parAno tiene un valor (es decir, el usuario seleccionó un año):
if parAno:
    # Filtramos el DataFrame 'dfDatos' para mantener solo las filas donde la columna 'anio' coincide con el año seleccionado.
    dfDatos=dfDatos[dfDatos['anio']==parAno]

# Si parMes tiene un valor:
if parMes:
    # Filtramos el DataFrame para incluir filas donde el mes es menor o igual al mes seleccionado (acumulativo hasta el mes).
    dfDatos=dfDatos[dfDatos['mes']<=parMes]

# Si la lista parPais contiene elementos (es decir, el usuario seleccionó al menos un país):
if len(parPais)>0:
    # Filtramos el DataFrame para mantener solo las filas donde la columna 'pais' está en la lista de países seleccionados.
    # '.isin(parPais)' comprueba si el valor de la columna 'pais' se encuentra dentro de la lista 'parPais'.
    dfDatos=dfDatos[dfDatos['pais'].isin(parPais)]

# Obtenemos los datos del mes seleccionado actualmente por el usuario.
# Filtramos el DataFrame 'dfDatos' (ya filtrado por año y país si aplica) para el mes exacto seleccionado.
dfMesActual = dfDatos[dfDatos['mes']==parMes]

# Obtenemos los datos del mes anterior al seleccionado para comparaciones.
if parMes: # Aseguramos que se haya seleccionado un mes.
    if parMes>1: # Si el mes seleccionado no es Enero (mes 1).
        # Filtramos el DataFrame para el mes inmediatamente anterior.
        dfMesAnterior = dfDatos[dfDatos['mes']==parMes-1]
    else: # Si el mes seleccionado es Enero (mes 1).
        # Para Enero, el "mes anterior" se considera el mismo Enero para evitar errores o datos vacíos si no hay datos de Diciembre del año anterior.
        # (Nota: una lógica más completa podría buscar Diciembre del año anterior si estuviera disponible y fuera el objetivo).
        dfMesAnterior = dfDatos[dfDatos['mes']==parMes]

# Muestra un encabezado principal en la página de la aplicación Streamlit.
st.header('Tablero de control de ventas - Tienda Tech')

# Mostramos las métricas clave de rendimiento (KPIs).
# Declaramos 5 columnas de igual tamaño para distribuir las métricas horizontalmente.
c1,c2,c3,c4,c5 = st.columns(5)

# En la primera columna (c1):
with c1:
    # Calculamos el total de productos vendidos en el mes actual sumando la columna 'Cantidad'.
    productosAct= dfMesActual['Cantidad'].sum()
    # Calculamos el total de productos vendidos en el mes anterior.
    productosAnt= dfMesAnterior['Cantidad'].sum()
    # Calculamos la variación respecto al mes anterior.
    variacion=productosAnt-productosAct # Una variación positiva aquí significaría que el mes anterior fue mejor.
    # Mostramos la métrica usando st.metric.
    # f'{productosAct:,.0f}' formatea el número con comas como separadores de miles y sin decimales.
    st.metric(f"Productos vendidos",f'{productosAct:,.0f} unidades', f'{variacion:,.0f}')

# En la segunda columna (c2):
with c2:
    # Contamos el número de órdenes (ventas) en el mes actual contando las filas de la columna 'orden'.
    ordenesAct= dfMesActual['orden'].count()
    # Contamos el número de órdenes en el mes anterior.
    ordenesAnt= dfMesAnterior['orden'].count()
    # Calculamos la variación.
    variacion=ordenesAct-ordenesAnt
    st.metric(f"Ventas realizadas",f'{ordenesAct:.0f}', f'{variacion:.1f}')

# En la tercera columna (c3):
with c3:
    # Calculamos el total de ventas (ingresos) en el mes actual sumando la columna 'Total'.
    ventasAct= dfMesActual['Total'].sum()
    # Calculamos el total de ventas en el mes anterior.
    ventasAnt= dfMesAnterior['Total'].sum()
    # Calculamos la variación.
    variacion=ventasAct-ventasAnt
    st.metric(f"Ventas totales",f'US$ {ventasAct:,.0f}', f'{variacion:,.0f}')

# En la cuarta columna (c4):
with c4:
    # Calculamos la utilidad total en el mes actual sumando la columna 'utilidad'.
    utilidadAct= dfMesActual['utilidad'].sum()
    # Calculamos la utilidad total en el mes anterior.
    utilidadAnt= dfMesAnterior['utilidad'].sum()
    # Calculamos la variación.
    variacion=utilidadAct-utilidadAnt
    st.metric(f"Utilidades",f'US$ {utilidadAct:,.0f}', f'{variacion:,.0f}')

# En la quinta columna (c5):
with c5:
    # Calculamos el porcentaje de utilidad del mes actual.
    utilPercentAct= (utilidadAct/ventasAct)*100 if ventasAct != 0 else 0 # Evitar división por cero
    # Calculamos el porcentaje de utilidad del mes anterior.
    utilPercentAnt= (utilidadAnt/ventasAnt)*100 if ventasAnt != 0 else 0 # Evitar división por cero
    # Calculamos la variación porcentual.
    variacion=utilPercentAnt-utilPercentAct # Una variación positiva aquí significaría que el mes anterior tuvo mejor % de utilidad.
    st.metric(f"Utilidad porcentual",f'{utilPercentAct:,.2f} %.', f'{variacion:,.0f} %')

# Declaramos 2 columnas con una proporción de tamaño de 60% para la primera y 40% para la segunda.
c1,c2 = st.columns([0.6,0.4]) # Streamlit ajustará esto a [60,40] o proporciones equivalentes

# En la primera columna (c1, más ancha):
with c1:
    # Agrupamos los datos del DataFrame 'dfDatos' (filtrado por año) por 'mes'.
    # '.agg({'Total':'sum'})' calcula la suma de la columna 'Total' para cada mes.
    # '.reset_index()' convierte el resultado agrupado de nuevo en un DataFrame con 'mes' como columna.
    dfVentasMes = dfDatos.groupby('mes').agg({'Total':'sum'}).reset_index()
    # Creamos un gráfico de líneas con Plotly Express.
    # 'x' es el mes, 'y' es el total de ventas.
    # 'color_discrete_sequence' define la paleta de colores a usar.
    fig1 = px.line(dfVentasMes,x='mes',y='Total', title='Ventas por mes',color_discrete_sequence=px.colors.qualitative.Plotly)    
    # Mostramos el gráfico de Plotly en la aplicación Streamlit.
    # 'use_container_width=True' hace que el gráfico ocupe todo el ancho de la columna.
    st.plotly_chart(fig1,use_container_width=True)

# En la segunda columna (c2, más estrecha):
with c2:
    # Agrupamos los datos del 'dfMesActual' (datos del mes seleccionado) por 'pais'.
    # Calculamos la suma del 'Total' de ventas para cada país.
    # '.sort_values(by='Total',ascending=False)' ordena los países por total de ventas de mayor a menor.
    dfVentasPais = dfMesActual.groupby('pais').agg({'Total':'sum'}).reset_index().sort_values(by='Total',ascending=False)
    # Creamos un gráfico de barras con Plotly Express.
    # 'x' es el país, 'y' es el total de ventas.
    # 'color='pais'' asigna un color diferente a cada barra de país.
    # 'text_auto=',.0f'' muestra el valor de la barra formateado.
    fig2 = px.bar(dfVentasPais,x='pais',y='Total', title=f'Ventas por País Mes: {parMes}', color='pais',text_auto=',.0f', color_discrete_sequence=px.colors.qualitative.Plotly)
    # 'fig2.update_layout(showlegend=False)' oculta la leyenda del gráfico, ya que el color está en las etiquetas del eje x.
    fig2.update_layout(showlegend=False)
    st.plotly_chart(fig2,use_container_width=True)

# Declaramos otras 2 columnas con la misma proporción 60/40.
c1,c2 = st.columns([0.6,0.4])

# En la primera de estas nuevas columnas (c1):
with c1:
    # Agrupamos los datos de 'dfDatos' (filtrado por año) por 'mes' y 'categoría'.
    # Calculamos la suma del 'Total' de ventas para cada combinación de mes y categoría.
    dfVentasCategoria = dfDatos.groupby(['mes','categoría']).agg({'Total':'sum'}).reset_index()
    # Creamos un gráfico de líneas múltiples, donde cada línea representa una categoría.
    # 'color='categoría'' diferencia las líneas por categoría.
    fig3 = px.line(dfVentasCategoria,x='mes',y='Total', title='Ventas por mes y categoría',color='categoría',color_discrete_sequence=px.colors.qualitative.Plotly)
    st.plotly_chart(fig3,use_container_width=True)

# En la segunda de estas nuevas columnas (c2):
with c2:
    # Agrupamos los datos de 'dfMesActual' (datos del mes seleccionado) por 'categoría'.
    # Calculamos la suma del 'Total' de ventas para cada categoría en el mes actual.
    # Ordenamos las categorías por total de ventas de mayor a menor.
    dfVentasCategoria = dfMesActual.groupby('categoría').agg({'Total':'sum'}).reset_index().sort_values(by='Total',ascending=False)
    # Creamos un gráfico de barras para las ventas por categoría en el mes seleccionado.
    fig4 = px.bar(dfVentasCategoria,x='categoría',y='Total', title=f'Ventas por categoría Mes: {parMes}', color='categoría',text_auto=',.0f',color_discrete_sequence=px.colors.qualitative.Plotly)
    fig4.update_layout(showlegend=False) # Ocultamos la leyenda.
    st.plotly_chart(fig4,use_container_width=True)

# --- Sección para Exportar a PDF ---

# Cargar la plantilla HTML desde un archivo.
# El nombre del archivo de plantilla se toma del selector 'parPlantilla'.
# 'encoding="utf-8"' asegura la correcta interpretación de caracteres especiales.
with open(parPlantilla, "r", encoding="utf-8") as file:
    template = file.read()

# Renderizar la plantilla HTML reemplazando los marcadores de posición con los datos calculados.
# Usamos el método .replace() de las cadenas para sustituir los placeholders.
# Los valores numéricos se formatean para una mejor presentación.
html_content = template.replace("[unidades]", f'{productosAct:,.0f} unidades')
html_content = html_content.replace("[ventas]", f'{ordenesAct:.0f}')
html_content = html_content.replace("[ventastotales]", f'US$ {ventasAct:,.0f}')
html_content = html_content.replace("[utilidades]", f'US$ {utilidadAct:,.0f}')
html_content = html_content.replace("[porcentual]", f'{utilPercentAct:,.2f} %')

# Convertimos los gráficos de Plotly a imágenes en formato base64 para embeberlos en el HTML.
# Llamamos a la función 'generarImagenBase64' para cada figura.
html_content = html_content.replace("[GRAFICA1]", generarImagenBase64(fig1))
html_content = html_content.replace("[GRAFICA2]", generarImagenBase64(fig2))
html_content = html_content.replace("[GRAFICA3]", generarImagenBase64(fig3))
html_content = html_content.replace("[GRAFICA4]", generarImagenBase64(fig4))

# Creamos un buffer en memoria para almacenar el PDF generado.
# io.BytesIO() crea un flujo de bytes en memoria, similar a un archivo temporal pero sin escribir en disco.
buffer = io.BytesIO()

# Generamos el PDF a partir del contenido HTML usando xhtml2pdf.
# 'html_content' es la cadena HTML con los datos y gráficos.
# 'dest=buffer' indica que el PDF se escribirá en el buffer en memoria.
# 'encoding='utf-8'' asegura la correcta codificación de caracteres en el PDF.
pisa_status = pisa.CreatePDF(html_content, dest=buffer, encoding='utf-8')

# Guardar el contenido HTML renderizado en un archivo .html (opcional, para depuración o visualización).
with open("reporte.html", "w", encoding="utf-8") as html_file:
    html_file.write(html_content)

# Añadimos un botón de descarga en la barra lateral para el PDF generado.
st.sidebar.download_button(
    label=":material/picture_as_pdf: Descargar reporte en PDF", # Texto del botón.
    data=buffer.getvalue(), # Los datos del PDF (contenido del buffer).
    file_name="reporte_ventas.pdf", # Nombre del archivo que se descargará.
    mime="application/pdf", # Tipo MIME del archivo, indica que es un PDF.
    type="primary" # Estilo del botón (opcional).
)