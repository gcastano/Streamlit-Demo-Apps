# Fuente de las imágenes:
# https://data.caltech.edu/records/mzrjq-6wc02

# Importando las bibliotecas necesarias

import streamlit as st  # pip install streamlit --upgrade
# Streamlit es un framework para crear aplicaciones web interactivas para machine learning y ciencia de datos.

import google.generativeai as genai # pip install -q -U google-generativeai
# La biblioteca Google Generative AI proporciona acceso a los modelos Gemini de Google.

import pandas as pd  # pip install pandas --upgrade
# Pandas es una biblioteca para la manipulación y análisis de datos.

import glob  # Biblioteca estándar de Python, no requiere instalación
# Glob se utiliza para buscar archivos basándose en patrones.

from streamlit_card import card  # pip install streamlit-card --upgrade
# streamlit-card permite crear tarjetas interactivas en Streamlit.

import base64  # Biblioteca estándar de Python, no requiere instalación
# Base64 se utiliza para codificar y decodificar datos.


# Configurando la página de Streamlit
st.set_page_config(
    page_title="Clasificación de imágenes con Google Gemini",  # Establece el título de la página
    page_icon="😊",  # Establece el icono de la página
    layout="wide",  # Establece el diseño en modo ancho
    initial_sidebar_state="expanded"  # Establece el estado inicial de la barra lateral
)


def upload_to_gemini(path, mime_type=None):
    """Sube el archivo dado a Gemini.

    Ver https://ai.google.dev/gemini-api/docs/prompting_with_media
    """
    file = genai.upload_file(path, mime_type=mime_type)
    
    return file


def clasificarConGemini(archivo, categorias):
    """Clasifica una imagen usando Google Gemini."""
    
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])  # Configura la clave API de Gemini

    # Crea la configuración del modelo
    generation_config = {
        "temperature": 1,  # Controla la aleatoriedad del texto generado
        "top_p": 0.95,  # Controla la diversidad del texto generado
        "top_k": 40,  # Controla el número de tokens considerados para la generación
        "max_output_tokens": 8192,  # Establece el número máximo de tokens en la respuesta
        "response_mime_type": "text/plain",  # Establece el formato de respuesta
    }
    estructuraRespuesta = "categoria|descripcion"  # Define la estructura de la respuesta
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",  # Especifica el modelo Gemini a utilizar
        generation_config=generation_config,
        system_instruction=f"Tu tarea es recibir una imagen, analizarla y clasificarla en las siguientes categorías: {categorias}. Solo retornarás el nombre de la categoría adecuada, si no encuentras retornas sin clasificar. Retornarás además una descripción de menos de 15 palabras de la imagen y todo en un texto de tipo {estructuraRespuesta}",
    )
    files = [
        upload_to_gemini(archivo, mime_type="image/jpeg"),  # Sube la imagen a Gemini
    ]
    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [
                    files[0],
                ],
            },

        ]
    )
    try:
        response = chat_session.send_message("INSERT_INPUT_HERE")  # Envía la imagen al modelo
        respuesta = response.text  # Obtiene el texto de la respuesta
    except:
        respuesta = "Sin clasificar|Error en Gemini"  # Maneja posibles errores
    return respuesta


def clasificarImagenes():
    """Clasifica todas las imágenes en la carpeta 'imagenes'."""
    dfClasificacion = pd.DataFrame()
    
    archivos = glob.glob("./imagenes/*.jpg")  # Obtiene una lista de todos los archivos JPG en la carpeta
    textoBarra="Iniciando clasificación de imágenes"
    barraProgreso = st.progress(0, text=textoBarra)
    cantArchivos= len(archivos)
    i=1
    for archivo in archivos:  # Itera a través de cada archivo de imagen
        textoBarra=f"Clasificando {i} de {cantArchivos}"
        barraProgreso.progress(i/cantArchivos,text=textoBarra)
        # Se obtiene la clasificación en formato categoria|descripcion
        clasificacion = clasificarConGemini(archivo, par_categorias)
        clasificacion = clasificacion.split("|")
        # Se arma el dataframe con los datos recuperados
        Elemento = {"imagen": [archivo],
                    "categoria": [clasificacion[0].upper()],
                    "descripcion": [clasificacion[1]]}
        dfElemento = pd.DataFrame(Elemento)
        dfClasificacion = pd.concat([dfClasificacion, dfElemento])
        i+=1
    dfClasificacion.to_csv("ImagenesClasificadas.csv", index=False)  # Guarda los resultados de la clasificación
    # Ocultamos la barra de progreso
    barraProgreso.empty()
    st.session_state["dfImagenes"] = dfClasificacion
    return dfClasificacion


def generarImagenCard(rutaImagen):
    """Genera una imagen codificada en base64 para la tarjeta."""
    with open(rutaImagen, "rb") as f:
        data = f.read()
        encoded = base64.b64encode(data)
    return "data:image/png;base64," + encoded.decode("utf-8")


# --- Aplicación principal de Streamlit ---

st.header("Clasificador de imágenes con :blue[Google Gemini]")
# Pedimos las categorías
par_categorias = st.text_input("Ingresar las categorías separadas por coma")
# Invocamos la clasificación de imágenes
btnIniciar = st.button("Clasificar Imágenes")

if glob.glob("ImagenesClasificadas.csv"):
    st.session_state["dfImagenes"] = pd.read_csv("ImagenesClasificadas.csv")

if btnIniciar or "dfImagenes" in st.session_state:    
    if btnIniciar:
        dfImagenes=clasificarImagenes()

    if "dfImagenes" in st.session_state:
        dfImagenes = st.session_state["dfImagenes"]  


    c1, c2 = st.columns([2, 8])
    c1.dataframe(dfImagenes.groupby("categoria")["imagen"].count().reset_index())
    with c2:
        opcionesCategoria = dfImagenes["categoria"].unique()
        par_categoria = st.segmented_control(
            "Categorías", opcionesCategoria
        )

        if par_categoria:
            dfImagenes = dfImagenes[dfImagenes["categoria"] == par_categoria]
        i = 0
        cols = st.columns(3)
        for index, fila in dfImagenes.iterrows():
            rutaImagen = fila["imagen"]
            with cols[i % 3]:
                card(
                    title=fila["categoria"],
                    text=fila["descripcion"],
                    image=generarImagenCard(rutaImagen),
                    styles={
                        "card": {
                            "width": "100%",
                            "height": "500px"
                        }
                    }
                )
            i += 1