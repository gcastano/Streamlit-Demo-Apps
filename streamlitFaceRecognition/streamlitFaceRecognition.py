import streamlit as st
import face_recognition #pip install face_recognition
import cv2 # pip install cv2
import numpy as np
from PIL import Image, ImageDraw # pip install PIL
import os

# Definimos los parámetros de configuración de la aplicación
st.set_page_config(
    page_title="Reconocimiento facial", #Título de la página
    page_icon="😊", # Ícono
    layout="wide", # Forma de layout ancho o compacto
    initial_sidebar_state="expanded" # Definimos si el sidebar aparece expandido o colapsado
)

def identificarRostro(imagen_buscada):
    """Compara la imagen entregada 

    Args:
        imagen_buscada (array): Imagen que se usará para comparar con los rostros conocidos
    """    
    # Recorre todos los archivos en el directorio
    directorioBase='Celebrity Faces Dataset/'
    encoding_a_buscar = face_recognition.face_encodings(imagen_buscada)[0]    
    
    st.subheader('Búsqueda')
    # Reemplace contenido con varios elememntos
    with st.empty():   
        for filename in os.listdir(directorioBase):        
            # Construye la ruta del archivo completo
            file_path = os.path.join(directorioBase, filename)        

            imagen_comparacion = face_recognition.load_image_file(file_path)
            encoding_comparacion = face_recognition.face_encodings(imagen_comparacion)[0]                      
            resultados = face_recognition.compare_faces([encoding_a_buscar], encoding_comparacion,tolerance=0.6)
            # Detenemos la búsqueda con la primera opción encontrada
            st.image(imagen_comparacion)
            # Paramos si el rostro coincide
            if resultados[0]==True:                
                break    
    if resultados[0]==True: # Si el rostro coincide lo mostramos
        st.success(f"Encontrado:{filename}" )        
        st.balloons()
    else:
        st.error(f"Celebridad no encontrada" )
                    
st.header('Qué celebridad es?')
st.subheader('Uso de [face_recognition](https://github.com/ageitgey/face_recognition)') 
# declaramos el control para cargar archivos
archivo_cargado = st.file_uploader("Elige un archivo",type='jpg')
# Si existe un archivo cargado ejecutamos el código
if archivo_cargado is not None:   
    # Cargamos el contenido del archivo
    bytes_data = archivo_cargado.getvalue()

    # Cargamos las columnas para mostrar las imágenes
    c1,c2,c3,c4 =st.columns([5,2,4,4])

    # Mostrar el nombre de archivo y la imagen
    with c1:
        st.subheader(f'Archivo: {archivo_cargado.name}')        
        st.image(bytes_data)        

    
    # Validamos que el archivo sea un array, sino lo convertimos
    if type(bytes_data) != np.ndarray:
        # Decodificamos los datos de la imagen con imdecode        
        imageBGR = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), 1)
        # Recodificamos los datos de la imagen con la escala de colores correcta
        image = cv2.cvtColor(imageBGR , cv2.COLOR_BGR2RGB)
    # Generamos el encoding de la imagen
    image_encoding = face_recognition.face_encodings(image)[0]
    # Obtenemos los landmarks del rostro
    face_landmarks_list = face_recognition.face_landmarks(image)
    # Obtenemos la ubicación del rostro
    face_locations = face_recognition.face_locations(image)
    
    
    for face_location in face_locations:        
        # Generamos la ubicación la cada en esta imagen
        top, right, bottom, left = face_location

        # Puedes acceder a la cara real así
        face_image = image[top:bottom, left:right]
        pil_image = Image.fromarray(face_image)
        with c2:
            st.subheader("Rostro detectado")
            st.image(pil_image)
    # Recorremos los puntos clave del rostro
    for face_landmarks in face_landmarks_list:        
        #convertir la imagen de la matriz numpy en el objeto de imagen PIL
        pil_image = Image.fromarray(image)        
        #convertir la imagen PIL para dibujar objeto
        d = ImageDraw.Draw(pil_image)        
        
        #Pintamos cada uno de los puntos de referencia
        d.line(face_landmarks['chin'],fill=(255,255,255), width=2)
        d.line(face_landmarks['left_eyebrow'],fill=(255,255,255), width=2)
        d.line(face_landmarks['right_eyebrow'],fill=(255,255,255), width=2)
        d.line(face_landmarks['nose_bridge'],fill=(255,255,255), width=2)
        d.line(face_landmarks['nose_tip'],fill=(255,255,255), width=2)
        d.line(face_landmarks['left_eye'],fill=(255,255,255), width=2)
        d.line(face_landmarks['right_eye'],fill=(255,255,255), width=2)
        d.line(face_landmarks['top_lip'],fill=(255,255,255), width=2)
        d.line(face_landmarks['bottom_lip'],fill=(255,255,255), width=2)
        # Dibujamos un rectángulo al rededor del rostro
        d.rectangle([(left,top),(right,bottom)],outline="yellow", width=2)
        with c3:
            tabimagen,tabencoding = st.tabs(["Imagen","Encoding"])
            with tabimagen:
                st.subheader("Puntos clave del rostro")
                st.write(", ".join(face_landmarks.keys()))
                st.image(pil_image)
            with tabencoding:
                st.code(image_encoding)
    with c4:
        # Ejecutamos la búsqueda de rostro
        identificarRostro(image)
