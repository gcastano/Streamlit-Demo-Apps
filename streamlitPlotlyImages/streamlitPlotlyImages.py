# --- LIBRERÍAS ---
# Streamlit: Permite crear y compartir aplicaciones web para ciencia de datos de forma rápida y sencilla.
# Para instalar: pip install streamlit
import streamlit as st

# Pandas: Librería fundamental para la manipulación y análisis de datos en Python. Ofrece estructuras de datos como los DataFrames.
# Para instalar: pip install pandas
import pandas as pd

# Plotly Express: Una interfaz de alto nivel para Plotly, que permite crear figuras y gráficos interactivos con muy poco código.
# Para instalar: pip install plotly
import plotly.express as px

# Python Imaging Library (Pillow): Proporciona capacidades para abrir, manipular y guardar muchos formatos de archivo de imagen diferentes.
# Para instalar: pip install Pillow
from PIL import Image

# Requests: Permite enviar solicitudes HTTP de manera sencilla. La usaremos para descargar las imágenes de las banderas desde una URL.
# Para instalar: pip install requests
import requests


# --- CONFIGURACIÓN DE LA PÁGINA DE STREAMLIT ---
# st.set_page_config() configura los metadatos y el layout de la aplicación web.
st.set_page_config(
    page_title="Gráficos con imágenes", # Título que aparece en la pestaña del navegador.
    page_icon="📊", # Ícono que aparece en la pestaña del navegador.
    layout="wide", # Usa todo el ancho de la pantalla para la app.
    initial_sidebar_state="expanded" # Mantiene la barra lateral abierta por defecto.
)

# --- FUNCIONES AUXILIARES PARA GRÁFICOS ---

def aplicarFormatoChart(fig,bgcolor='#FFFFFF',verleyenda=False,margin = dict(l=20, r=20,b=100,t=100),colorGridY="silver",verLineaX=False,verLineaY=False,ejeXVisible=True,ejeYVisible=True,verXgrid=False,verYgrid=True,verTituloX=True,verTituloY=True,Xtickmode="auto",Ytickmode="auto",verSpikesX=False,verSpikesY=False):
    """Aplica un formato estético predefinido a los gráficos de Plotly para darles una apariencia profesional y limpia.

    Args:
        fig (plotly.graph_objects.Figure): Objeto de figura de Plotly al que se aplicará el formato.
        bgcolor (str, optional): Color de fondo del gráfico. Por defecto '#FFFFFF'.
        verleyenda (bool, optional): Booleano para mostrar u ocultar la leyenda. Por defecto False.
        margin (dict, optional): Diccionario que define los márgenes del gráfico (izquierda, derecha, abajo, arriba).
        colorGridY (str, optional): Color de las líneas de la cuadrícula. Por defecto "silver".
        verLineaX (bool, optional): Booleano para mostrar la línea base del eje X. Por defecto False.
        verLineaY (bool, optional): Booleano para mostrar la línea base del eje Y. Por defecto False.
        ejeXVisible (bool, optional): Booleano para mostrar u ocultar el eje X completo. Por defecto True.
        ejeYVisible (bool, optional): Booleano para mostrar u ocultar el eje Y completo. Por defecto True.
        verXgrid (bool, optional): Booleano para mostrar u ocultar la cuadrícula del eje X. Por defecto False.
        verYgrid (bool, optional): Booleano para mostrar u ocultar la cuadrícula del eje Y. Por defecto True.
        verTituloX (bool, optional): Booleano para mostrar el título del eje X. Por defecto True.
        verTituloY (bool, optional): Booleano para mostrar el título del eje Y. Por defecto True.
        Xtickmode (str, optional): Modo de los 'ticks' (marcas) en el eje X ('auto', 'linear', 'array'). Por defecto "auto".
        Ytickmode (str, optional): Modo de los 'ticks' (marcas) en el eje Y. Por defecto "auto".
        verSpikesX (bool, optional): Muestra una línea que cruza el gráfico al pasar el ratón sobre el eje X. Por defecto False.
        verSpikesY (bool, optional): Muestra una línea que cruza el gráfico al pasar el ratón sobre el eje Y. Por defecto False.

    Returns:
        plotly.graph_objects.Figure: El objeto de figura de Plotly con el formato ya aplicado.
    """
    # Actualiza el layout general del gráfico con colores, márgenes y modos de los ejes.
    fig.update_layout(paper_bgcolor=bgcolor, 
                      plot_bgcolor=bgcolor, 
                      margin=margin,                       
                      xaxis=dict(tickmode=Xtickmode), 
                      yaxis=dict(tickmode=Ytickmode))
    # Configura las propiedades visuales del eje X (líneas, visibilidad, color, etc.).
    fig.update_xaxes(showline=verLineaX,
                    linewidth=2,
                    linecolor=colorGridY,
                    visible=ejeXVisible,
                    showgrid=verXgrid,
                    tickfont=dict(color='white'),
                    title_font=dict(color='white'))
    # Configura las propiedades visuales del eje Y.
    fig.update_yaxes(showline=verLineaY,
                    linewidth=2,
                    linecolor=colorGridY,
                    visible=ejeYVisible,
                    showgrid=verYgrid,
                    tickfont=dict(color='white'),
                    title_font=dict(color='white'))
    # Actualiza la visibilidad de la leyenda y el color de la cuadrícula.
    fig.update_layout(showlegend=verleyenda)
    fig.update_yaxes(gridcolor=colorGridY)
    fig.update_xaxes(gridcolor=colorGridY)
    # Configura el tamaño de la fuente de las etiquetas de los ejes.
    fig.update_xaxes(tickfont_size=17)
    fig.update_yaxes(tickfont_size=17)
    # Habilita los 'spikes' para una mejor visualización interactiva.
    fig.update_xaxes(showspikes=verSpikesX)
    fig.update_yaxes(showspikes=verSpikesY)
    # Añade un padding (relleno) al título para separarlo del área del gráfico.
    fig.update_layout(title=dict(pad=dict(l=20)))
    # Configura la apariencia de los 'ticks' para que apunten hacia afuera.
    fig.update_layout(xaxis=dict(ticks='outside',
                    ticklen=10,
                    tickcolor=colorGridY)
                    )
    fig.update_layout(yaxis=dict(ticks='outside',
                    ticklen=10,
                    tickcolor=colorGridY)
                      )
    # Oculta los títulos de los ejes si el parámetro correspondiente es False.
    if not verTituloX:  fig.update_xaxes(title_text='')
    if not verTituloY:  fig.update_yaxes(title_text='')
    return fig


def generarTitulo(titulo,subtitulo,colorTitulo="black",colorSubtitulo="grey"):
    """Crea un título formateado con HTML para permitir múltiples líneas y colores diferentes en el título y subtítulo.

    Args:
        titulo (str): El texto del título principal.
        subtitulo (str): El texto del subtítulo.
        colorTitulo (str, optional): Color del título principal. Por defecto "black".
        colorSubtitulo (str, optional): Color del subtítulo. Por defecto "grey".

    Returns:
        str: Una cadena de texto con formato HTML lista para ser usada como título en un gráfico de Plotly.
    """
    # Combina el título y subtítulo usando etiquetas HTML para controlar el estilo (tamaño de fuente, color, negrita).
    titulo_html = f"""<b><span style='font-size:25px;color:{colorTitulo}'>{titulo}</span></b></br></br><span style='color:{colorSubtitulo}'>{subtitulo}</span>"""
    return titulo_html

def adicionarImagen(fig,rutaImagen,valorY=1.05):
    """Añade una imagen al layout de un gráfico de Plotly, pensada para gráficos de barras horizontales (imágenes en el eje Y).

    Args:
        fig (plotly.graph_objects.Figure): Objeto de figura de Plotly.
        rutaImagen (str): URL de la imagen a añadir.
        valorY (float, optional): Posición vertical de la imagen en el dominio del gráfico.

    Returns:
        plotly.graph_objects.Figure: El objeto de figura con la imagen añadida.
    """
    # Añade una imagen al layout del gráfico.
    return fig.add_layout_image(
        dict(
            source=Image.open(requests.get(rutaImagen, stream=True).raw), # Descarga y abre la imagen desde la URL.
            xref="x domain", # Referencia de coordenadas.
            yref="y domain",
            x=-0.04, y=valorY, # Posición de la imagen.
            sizex=1, sizey=1, # Tamaño relativo (se ajustará después).
            xanchor="left", # Anclaje horizontal.
            yanchor="bottom", # Anclaje vertical.
            layer="above" # La imagen se dibuja por encima de las barras del gráfico.
        )
    )

def adicionarImagenH(fig,rutaImagen,valorX=1.05):
    """Añade una imagen al layout de un gráfico de Plotly, pensada para gráficos de barras verticales (imágenes en el eje X).

    Args:
        fig (plotly.graph_objects.Figure): Objeto de figura de Plotly.
        rutaImagen (str): URL de la imagen a añadir.
        valorX (float, optional): Posición horizontal de la imagen en el dominio del gráfico.

    Returns:
        plotly.graph_objects.Figure: El objeto de figura con la imagen añadida.
    """
    # Añade una imagen al layout del gráfico.
    return fig.add_layout_image(
        dict(
            source=Image.open(requests.get(rutaImagen, stream=True).raw), # Descarga y abre la imagen desde la URL.
            xref="x domain",
            yref="y domain",
            x=valorX, y=0.01, # Posición de la imagen.
            sizex=1, sizey=1,
            xanchor="left",
            yanchor="bottom",
            layer="above"
        )
    )

# --- LÓGICA PRINCIPAL DE LA APLICACIÓN ---

# Título principal que se muestra en la aplicación de Streamlit.
st.header("Gráficos mejorados para publicaciones")

# Carga de datos desde un archivo CSV a un DataFrame de Pandas.
dfDatos =  pd.read_csv("./table.csv")

# Creación de una nueva columna 'bandera'.
# Se utiliza el método .apply() con una función lambda para procesar cada fila.
# Para cada 'Country Code', se construye una URL que apunta a la imagen de la bandera correspondiente en la API de flagsapi.com.
dfDatos["bandera"]=dfDatos["Country Code"].apply(lambda x: f"https://flagsapi.com/{x}/flat/64.png")

# Genera el título y subtítulo del gráfico utilizando la función auxiliar.
titulo=generarTitulo(titulo="Países que más emisiones de CO2 han emitido a la fecha",subtitulo="Emisiones de CO2 acumuladas por país desde 1751 hasta 2023",colorTitulo="#FDF5AA",colorSubtitulo="white")

# Crea un widget de radio en Streamlit para que el usuario elija la orientación del gráfico.
parOrientacion = st.radio("¿Cómo quieres que se muestre el gráfico?", ("Vertical", "Horizontal"),horizontal=True)

# Lógica condicional basada en la selección del usuario.
if parOrientacion == "Vertical":
    # Ordena el DataFrame de forma ascendente para que en el gráfico horizontal el valor más alto quede arriba.
    dfDatos=dfDatos.sort_values(by='Share of Global Cumulative CO2 Emissions (%)', ascending=True)
    # Crea un gráfico de barras horizontal con Plotly Express.
    fig = px.bar(data_frame= dfDatos,
                  x='Share of Global Cumulative CO2 Emissions (%)',
                  y="Country",
                  text='Share of Global Cumulative CO2 Emissions (%)',
                  title=titulo,
                  height=800,
                  color_discrete_sequence=["#58A0C8"]
                  )
    # Aplica el formato estético a la figura.
    fig = aplicarFormatoChart(fig, bgcolor="#113F67", verLineaX=True, verXgrid=False, verYgrid=False, ejeYVisible=True, verTituloX=False, Xtickmode="linear", ejeXVisible=False)
else:
    # Ordena el DataFrame de forma descendente para el gráfico vertical.
    dfDatos=dfDatos.sort_values(by='Share of Global Cumulative CO2 Emissions (%)', ascending=False)
    # Crea un gráfico de barras vertical.
    fig = px.bar(data_frame= dfDatos,
                x="Country",
                y='Share of Global Cumulative CO2 Emissions (%)',
                text='Share of Global Cumulative CO2 Emissions (%)',
                title=titulo,
                height=800,
                color_discrete_sequence=["#58A0C8"]
                )
    # Aplica el formato estético a la figura.
    fig = aplicarFormatoChart(fig, bgcolor="#113F67", verLineaX=True, verXgrid=False, verYgrid=False, ejeYVisible=False, verTituloX=False, Xtickmode="linear", ejeXVisible=True)

# Actualiza las trazas del gráfico para formatear el texto que aparece sobre (o fuera de) las barras.
fig.update_traces(
    texttemplate='<b>%{text:.2s} %</b>', # Formato del texto: negrita, dos dígitos significativos y el símbolo '%'.
    textposition='outside', # Posición del texto fuera de la barra.
    textfont_size=20, # Tamaño de la fuente.
    textfont_color='#FCF8DD' # Color de la fuente.
)

# Calcula un factor de desplazamiento para posicionar las imágenes de las banderas de manera uniforme.
factorDesplazamiento = 1/len(dfDatos)

# Itera sobre cada fila del DataFrame para añadir la bandera correspondiente.
# .iterrows() devuelve el índice y la fila (como una Serie de Pandas) en cada iteración.
for index, fila in dfDatos.iterrows():    
    bandera=fila["bandera"] # Obtiene la URL de la bandera de la fila actual.
    
    # Añade la imagen de la bandera al gráfico dependiendo de la orientación elegida.
    if parOrientacion == "Vertical":    
        fig.update_layout(margin_pad=70) # Añade un padding extra para que las imágenes no se corten.
        # Calcula la posición Y de la imagen. Se invierte para que corresponda con el orden del gráfico.
        valorPosicion = (1 - (index * factorDesplazamiento))
        fig = adicionarImagen(fig, bandera, valorY=valorPosicion)
    else:
        fig.update_layout(margin_pad=50) # Padding para el gráfico horizontal.
        # Calcula la posición X de la imagen.
        valorPosicion = (index * factorDesplazamiento)+0.01
        fig = adicionarImagenH(fig, bandera, valorX=valorPosicion)
    
# Actualiza las propiedades de TODAS las imágenes añadidas al layout.
# Esto es más eficiente que configurar estas propiedades en cada iteración del bucle.
fig.update_layout_images(dict(
        xref="x domain",
        yref="y domain",
        sizex=0.1, # Tamaño relativo de la imagen.
        sizey=0.1,
        xanchor="left",
        yanchor="top"
))
# Asegura que el color de las etiquetas de los ejes sea el correcto después de todas las modificaciones.
fig.update_xaxes(tickfont=dict(color='white'))
fig.update_yaxes(tickfont=dict(color='white'))

# Muestra el gráfico final en la aplicación de Streamlit.
# use_container_width=True hace que el gráfico ocupe todo el ancho del contenedor.
st.plotly_chart(fig,use_container_width=True,key="chart1")