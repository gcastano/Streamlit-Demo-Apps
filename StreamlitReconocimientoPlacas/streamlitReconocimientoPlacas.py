# Importar las librerías necesarias

# Streamlit: framework para crear aplicaciones web de manera sencilla con Python.
# Instalación: pip install streamlit
import streamlit as st

# OpenCV (cv2): librería para visión artificial y procesamiento de imágenes.
# Instalación: pip install opencv-python
import cv2 

# NumPy: librería para trabajar con matrices y vectores multidimensionales.
# Instalación: pip install numpy
import numpy as np

# EasyOCR: librería para reconocimiento óptico de caracteres (OCR).
# Instalación: pip install easyocr
# https://github.com/JaidedAI/EasyOCR
import easyocr

# imutils: librería con funciones de utilidad para procesamiento de imágenes con OpenCV.
# Instalación: pip install imutils
import imutils

# rembg: librería para eliminar el fondo de una imagen.
# Instalación: pip install rembg
# https://github.com/danielgatis/rembg
import rembg

# NumPy: librería para trabajar con matrices y vectores multidimensionales.
# Instalación: pip install numpy
import numpy as np

# PIL (Pillow): librería para abrir, manipular y guardar imágenes.
# Instalación: pip install Pillow
from PIL import Image

# Definimos los parámetros de configuración de la aplicación
st.set_page_config(
    page_title="Reconocimiento de placas de vehículos", # Título de la página
    page_icon="🚘", # Ícono de la página
    layout="wide", # Formato de diseño: ancho o compacto
    initial_sidebar_state="expanded" # Define si la barra lateral aparece expandida o contraída
)


def obtenerPlaca(location,img,gray):
    """Obtiene la placa de una imagen de un vehículo

    Args:
        location (array): coordenadas donde se detecta que puede estar la placa
        img (imagen): imagen del vehículo
        gray (imagen): imagen del vehículo en escala de grises

    Returns:
        placa(str): placa detectada
        imagenplaca(imagen): imagen de la placa detectada
        imagenContornos(imagen): imagen de los contornos procesados
    """    
    # Crear una imagen en blanco con las mismas dimensiones que la imagen original
    mask = np.zeros(gray.shape, np.uint8) 
    # Dibujar los contornos en la imagen de máscara
    new_image = cv2.drawContours(mask, [location], 0,255, -1) 
    # Realizar una operación AND bit a bit entre la imagen original y la imagen de máscara
    new_image = cv2.bitwise_and(img, img, mask=mask) 

    # Convertir la imagen a RGB para mostrarla
    imagenContornos =cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB) 

    # Encontrar las coordenadas de las cuatro esquinas del documento
    (x,y) = np.where(mask==255) 
    # Encontrar la esquina superior izquierda
    (x1, y1) = (np.min(x), np.min(y)) 
    # Encontrar la esquina inferior derecha
    (x2, y2) = (np.max(x), np.max(y)) 
    # Recortar la imagen usando las coordenadas
    cropped_image = gray[x1:x2+1, y1:y2+1] 

    # Convertir la imagen a RGB para mostrarla
    imagenplaca=cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB) 

    # Crear un objeto lector easyocr con español como idioma
    reader = easyocr.Reader(['es']) 
    # Leer el texto de la imagen recortada
    result = reader.readtext(cropped_image) 
    
    placa=None

    if result:
        # Extraer el texto del resultado
        placa = result[0][-2] 
    
    return placa,imagenplaca,imagenContornos

# Define el encabezado de la aplicación
st.header('Reconocimiento de placas de Vehículos')
# Define el subtítulo de la aplicación y muestra un enlace al artículo original
st.subheader('Adaptación del artículo [Automatic Number Plate Recognition System using EasyOCR](https://www.geeksforgeeks.org/automatic-license-number-plate-recognition-system/)') 
st.warning("Se debe cargar una foto de un vehículo donde se vea la placa claramente",icon=":material/warning:")
# Crea un widget para cargar archivos
archivo_cargado = st.file_uploader("Elige un archivo con la imagen de un vehículo",type=['jpg','png'])
# Si se carga un archivo, ejecuta el siguiente código
if archivo_cargado is not None:   
    # Divide el área de visualización en dos columnas
    c1,c2= st.columns(2)
    
    # Carga el contenido del archivo
    bytes_data = archivo_cargado.getvalue()
    img=bytes_data    
    # img = cv2.imread("./carro1.jpg") # Lee la imagen
    if type(bytes_data) != np.ndarray:
        # Decodifica los datos de la imagen con imdecode        
        imageBGR = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), 1)
        img= imageBGR    
    
    # Aplicar la eliminación de fondo utilizando REMBG esto puede 
    # Esto puede tomar un tiempo al ejecutarse la primera vez ya que debe descargar el modelo
    output_array = rembg.remove(img)
    
    # Crear una imagen PIL a partir de la matriz de salida
    output_image = Image.fromarray(output_array)

    
    # Muestra un subtítulo en la columna 1
    c1.subheader("Proceso")  
    # Muestra un subtítulo en la columna 2        
    c2.subheader("Resultado")
    
    with c1:
        c3,c4= st.columns(2)
        c3.write("Imagen cargada")  
        # Muestra la imagen en la columna 1 interna
        c3.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))            
        c4.write("Imagen con fondo eliminado")  
        # Imagen con el fondo eliminado
        c4.image(cv2.cvtColor(output_array, cv2.COLOR_BGR2RGB))
        # Convierte la imagen a escala de grises
        gray = cv2.cvtColor(output_array, cv2.COLOR_BGR2GRAY) 
        # Aplica un filtro bilateral para reducir el ruido
        bfilter = cv2.bilateralFilter(gray, 11, 17, 17)         
        c3.write("Imagen escala de grises")  
        # Muestra la imagen en la columna 1 interna
        c3.image(cv2.cvtColor(bfilter, cv2.COLOR_BGR2RGB)) 
    
        # Crea un objeto lector easyocr con español como idioma
        # Esto puede tomar un tiempo al ejecutarse la primera vez ya que debe descargar el modelo
        reader = easyocr.Reader(['es'])     
        # Lee el texto de la imagen en escala de grises
        result = reader.readtext(gray)    
        resultadosOCR=[x[1] for x in result if len(x[1])>4]
        # Detecta los bordes de la imagen
        edged = cv2.Canny(bfilter, 30, 200)         
        c4.write("Imagen con solo bordes")  
        # Muestra la imagen en la columna 2 interna
        c4.image(cv2.cvtColor(edged, cv2.COLOR_BGR2RGB))

    # Encuentra los contornos de la imagen
    keypoints = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) 
    # Obtiene los contornos
    contours = imutils.grab_contours(keypoints) 
    # Ordena los contornos por área en orden descendente y toma los 10 primeros
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10] 

    # Itera sobre los contornos para encontrar el mejor contorno aproximado de los 10 contornos
    location = None
    placa=None
    for contour in contours:
        # Aproxima el contorno a un polígono
        approx = cv2.approxPolyDP(contour, 10, True)    
        # Si el polígono tiene 4 lados, se considera un candidato a placa
        if len(approx) == 4:            
            location = approx            
            # Obtiene la placa, la imagen de la placa y la imagen con la placa resaltada
            placa,imagenplaca,imagenContornos=obtenerPlaca(location,img,gray)
            if placa:
                # Si la longitud de la placa es mayor a 5 caracteres, se considera válida
                if len(placa)>5:
                    break
    if placa:                
        c1.write("Imagen con solo placa detectada")  
        # Muestra la imagen con la placa resaltada en la columna 1
        c1.image(imagenContornos) 
        
        with c2:
            c3,c4= st.columns([5,2])            
            c4.write("Placa procesada")  
            # Muestra la imagen de la placa en la columna 4 interna
            c4.image(imagenplaca) 
            # Extrae el texto de la placa
            text = placa 
            # Dibuja un rectángulo alrededor del texto de la placa en la imagen original
            res = cv2.rectangle(img, tuple(location[0][0]), tuple(location[2][0]), (0,255,0),3)             
            c4.write("Placa detectada")  
            # Muestra la placa detectada en un formato métrico
            c4.metric("Placa",text)
            # Muestra la imagen original con la placa resaltada en la columna 1 interna
            c3.image(cv2.cvtColor(res, cv2.COLOR_BGR2RGB))
        c2.write("Textos detectados con OCR")  
        # Muestra una tabla con los textos detectados con más de 4 caracteres
        c2.dataframe(resultadosOCR,use_container_width=True)       
        
    else:
        # Muestra un mensaje de error si no se encuentra ninguna placa
        c2.error("No se ha encontrado placas de vehículos en la imagen")         
        c2.write("Textos detectados con OCR")  
        # Muestra una tabla con los textos detectados con más de 4 caracteres
        c2.dataframe(resultadosOCR,use_container_width=True)       