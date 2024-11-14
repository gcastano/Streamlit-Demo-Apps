# Importamos las librerías necesarias
import streamlit as st  # Librería para crear aplicaciones web interactivas
from colorthief import ColorThief  # Librería para extraer paletas de colores de imágenes
import math
import random

# https://stackoverflow.com/questions/22603510/is-this-possible-to-detect-a-colour-is-a-light-or-dark-colour
def isLightOrDark(hexColor):
    # Convertimos el valor hexadecimal a RGB
    rgbColor=tuple(int(hexColor[i:i+2], 16) for i in (0, 2, 4))
    [r,g,b]=rgbColor
    # Cálculo del brillo percibido
    hsp = math.sqrt(0.299 * (r * r) + 0.587 * (g * g) + 0.114 * (b * b))
    if (hsp>127.5):
        return 'light'
    else:
        return 'dark'

def retornaColorTexto(hexColor):
    hexColor=hexColor.lstrip("#")
    if isLightOrDark(hexColor)=="dark":
        color= "#FFFFFF"
    else:
        color= "#000000"
    return color

# Definimos los parámetros de configuración de la aplicación
st.set_page_config(
    page_title="Extractor de paletas de colores",  # Título de la página
    page_icon="😊",  # Ícono de la página
    layout="wide",  # Layout ancho para aprovechar el espacio horizontal
    initial_sidebar_state="expanded"  # Barra lateral expandida al iniciar
)

# Encabezado de la aplicación
st.header('Generador de paletas de colores')

# Control para cargar un archivo de imagen
archivo_cargado = st.file_uploader("Elige un archivo", type=['jpg','png'])
par_cantColores= st.number_input("Cantidad de colores",value=20)
# Si se ha cargado un archivo
if archivo_cargado is not None:
    # Leemos el contenido del archivo cargado
    bytes_data = archivo_cargado

    # Creamos una instancia de ColorThief
    color_thief = ColorThief(archivo_cargado)
    # Obtenemos el color dominante de la imagen
    dominant_color = color_thief.get_color(quality=1)
    # Generamos una paleta de colores de la imagen
    palette = color_thief.get_palette(color_count=par_cantColores+1,quality=1)    
    # Creamos dos columnas para la visualización
    c1, c2 = st.columns([3, 7])

    # En la primera columna, mostramos el nombre del archivo y la imagen
    with c1:
        st.subheader(f'Archivo: {archivo_cargado.name}')
        st.image(bytes_data)

    # En la segunda columna, mostramos el color dominante y la paleta de colores
    with c2:
        # Formateamos el color dominante a formato hexadecimal
        colorDominante = '#%02x%02x%02x' % dominant_color

        # Creamos una lista para almacenar los colores de la paleta en formato hexadecimal
        colores = []
        for pal in palette:
            colores.append('#%02X%02X%02X' % pal)

        # Mostramos el color dominante
        st.write("#### Color dominante")
        colorTexto = retornaColorTexto(colorDominante)
        st.html(f'<div style="background-color:{colorDominante};width:100%;color:{colorTexto}">{colorDominante}</div>')
        st.divider()
        # Mostramos la paleta de colores
        c1,c2,c3,c4 = st.columns([4,3,3,10])
        c1.write("#### Paleta de colores")
        btnAleatorio = c2.button("Aleatorio",type="primary")
        btnResetear = c3.button("Reiniciar")
        # Creamos 4 columnas para mostrar los colores de la paleta
        cols = st.columns(4)
        i = 0
        # Si se quiere cambiar el orden de los colores se invoca el shuffle
        if btnAleatorio:
            random.shuffle(colores)
        
        for color in colores:
            # Mostramos cada color en una columna
            colorTexto = retornaColorTexto(color)
            cols[i % 4].html(f'{i}. <div style="background-color:{color};width:100%;color:{colorTexto};text-align:center">{color}</div>')
            i += 1
        st.divider()
        # Generamos un array de colores para Plotly
        listaColores = "'" + "','".join(colores) + "'"
        st.write("#### Paleta para Plotly")
        st.code(f"[{listaColores}]")

        # Generamos un array de colores para Vizzu
        listaColores = " ".join(colores)
        st.write("#### Paleta para Vizzu")
        st.code(f"{listaColores}")