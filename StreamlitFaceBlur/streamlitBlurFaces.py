# ==========================================
# LIBRERÍAS Y COMANDOS DE INSTALACIÓN
# ==========================================
# 1. Streamlit: Para crear la interfaz web interactiva.
#    -> pip install streamlit
# 2. OpenCV (cv2): Para el procesamiento de imágenes y visión por computadora.
#    -> pip install opencv-python
# 3. NumPy: Para manejo eficiente de matrices y arrays (las imágenes son arrays).
#    -> pip install numpy
# 4. FFmpeg-python: Wrapper para manejar la codificación de video (necesario para ver videos en web).
#    -> pip install ffmpeg-python
#    Nota: También necesitas tener FFmpeg instalado en tu sistema operativo.

import streamlit as st
import cv2
import numpy as np
import os
import ffmpeg

# Configuración inicial de la página de Streamlit
st.set_page_config(layout="wide", page_title="Difuminar Rostros en Imágenes y Videos", page_icon=":mask:")

def anonimizar_imagen(image_path, cascade_path):
    """
    Detecta rostros en una imagen estática y aplica un efecto de difuminado (blur).

    Args:
        image_path (str): Ruta del archivo de imagen original.
        cascade_path (str): Ruta del archivo XML del clasificador Haar Cascade.

    Returns:
        numpy.ndarray: La imagen procesada con los rostros difuminados.
    """
    # Cargar la imagen usando OpenCV
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: No se pudo cargar la imagen en {image_path}")
        return
    
    # Transformación: Convertir a escala de grises
    # Los clasificadores Haar funcionan mejor en monocromo (intensidad de luz)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Cargar el clasificador pre-entrenado para detección de rostros frontales
    face_cascade = cv2.CascadeClassifier(cascade_path)
    if face_cascade.empty():
        print(f"Error: No se pudo cargar el cascade en {cascade_path}")
        return

    # Detección: Busca rostros en la imagen en escala de grises
    # scaleFactor=1.1: Reduce la imagen un 10% en cada escala
    # minNeighbors=4: Cuántos vecinos debe tener cada candidato a rectángulo para conservarlo
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(30, 30))

    # Iterar sobre cada rostro detectado (coordenadas x, y, ancho w, alto h)
    for (x, y, w, h) in faces:
        # Selección de ROI (Region of Interest): Extraemos solo la parte de la cara
        face_roi = img[y:y+h, x:x+w]
        
        # Transformación: Aplicar desenfoque Gaussiano
        # (29, 29) es el tamaño del kernel (debe ser impar). A mayor número, más borroso.
        blurred_face = cv2.GaussianBlur(face_roi, (29, 29), 0)
        
        # Reemplazar la región original de la cara con la versión difuminada
        img[y:y+h, x:x+w] = blurred_face

    # Limpieza de ventanas de OpenCV (buena práctica aunque Streamlit maneja la visualización)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    return img

def anonimizar_video(cascade_path, video_source):
    """
    Procesa un archivo de video frame por frame para detectar y difuminar rostros.

    Args:
        cascade_path (str): Ruta del clasificador Haar Cascade.
        video_source (str): Ruta del archivo de video de entrada.

    Returns:
        str: El nombre del archivo de video procesado (guardado temporalmente).
    """
    face_cascade = cv2.CascadeClassifier(cascade_path)
    if face_cascade.empty():
        print(f"Error: No se pudo cargar el cascade en {cascade_path}")
        return

    # Inicializar captura de video
    cap = cv2.VideoCapture(video_source)
    
    # Definir el códec y crear el objeto VideoWriter
    # 'mp4v' es un códec común, pero a veces requiere conversión posterior para web
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    filename = video_source.split("temp\\")[-1]    
    videoFilenamePath = f"blurred_{filename}"
    
    # Construir ruta de salida segura
    videoPath = os.path.join(os.path.dirname(__file__), "temp", videoFilenamePath)
    
    # Configurar el escritor de video: ruta, códec, FPS, y tamaño (ancho, alto)
    out = cv2.VideoWriter(videoPath, fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))

    # Bucle principal: Leer frame -> Procesar -> Guardar
    while True:
        ret, frame = cap.read() # Leer un frame
        if not ret:
            break # Fin del video

        # Convertir frame actual a escala de grises para detección
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, # Imagen en escala de grises
                                              scaleFactor=1.1, # Escala de reducción
                                              minNeighbors=4, # Vecinos para retener
                                              minSize=(30, 30) # Tamaño mínimo del rostro
                                              )

        for (x, y, w, h) in faces:
            # Difuminar la región de la cara
            frame[y:y+h, x:x+w] = cv2.GaussianBlur(frame[y:y+h, x:x+w], (25, 25), 0)
            # Dibujar un rectángulo negro alrededor de la cara difuminada
            # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 0), 2)
        
        # Escribir el frame modificado en el archivo de salida
        out.write(frame)
        
        # Permitir salir del bucle si se presiona 'q' (útil en ejecución local)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    # Liberar recursos del sistema
    out.release()
    cap.release()
    cv2.destroyAllWindows()
    
    return videoFilenamePath

def main():
    """
    Función principal de la aplicación Streamlit.
    Maneja la carga de archivos, lógica de UI y llamadas a funciones de procesamiento.
    """
    st.title("Anonimizador de Imágenes y Videos")

    # Widget de carga de archivos (soporta imágenes y videos)
    uploaded_file = st.file_uploader("Elige una imagen o video...", type=["jpg", "jpeg", "png","mp4", "avi", "mov"])
    
    if uploaded_file is not None:
        # Determinar tipo de archivo basado en extensión
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        if file_extension in [".jpg", ".jpeg", ".png"]:
            uploaded_image = uploaded_file            
            uploaded_video = None
        elif file_extension in [".mp4", ".avi", ".mov"]:
            uploaded_video = uploaded_file
            uploaded_image = None
        else:
            st.error("Formato de archivo no soportado.")
            return

        # Guardar el archivo subido en una carpeta temporal local para que OpenCV pueda leerlo
        if uploaded_image or uploaded_video:
            # Crear ruta absoluta
            save_path = os.path.join(os.path.dirname(__file__), "temp", uploaded_file.name)
            
            # Asegurar que el directorio temp exista (opcional pero recomendado)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            # Escribir el buffer del archivo en disco
            with open(save_path, mode='wb') as f:
                f.write(uploaded_file.getbuffer())

        # Lógica para Imágenes
        if uploaded_image is not None:
            c1,c2 = st.columns(2)
            with c1:
                st.subheader("Imagen Original")
                # Decodificar imagen para mostrarla en Streamlit
                image = cv2.imdecode(np.frombuffer(uploaded_image.read(), np.uint8), cv2.IMREAD_COLOR)
                st.image(image, channels="BGR", caption="Imagen Cargada")
            with c2:
                st.subheader("Imagen con Rostros Difuminados")
                # Procesar imagen
                # NOTA: Asegúrate de tener el archivo .xml en la carpeta 'modelo'
                imageBlurred = anonimizar_imagen(save_path, os.path.join(os.path.dirname(__file__), "modelo/haarcascade_frontalface_default.xml"))
                st.image(imageBlurred, channels="BGR", caption="Imagen con Rostros Difuminados")
        
        # Lógica para Videos
        if uploaded_video is not None:
            c1,c2 = st.columns(2)
            with c1:
                st.subheader("Video Original")
                st.video(uploaded_video)
            with c2:
                st.subheader("Video con Rostros Difuminados")
                # Procesar video
                videoPath = anonimizar_video(os.path.join(os.path.dirname(__file__), "modelo/haarcascade_frontalface_default.xml"), save_path)                                            
                
                # Transcodificación con FFmpeg
                # OpenCV genera archivos que a veces los navegadores no reproducen bien.
                # Usamos ffmpeg para recomprimir a H.264 (x264) y AAC, estándar para web.
                input_video = os.path.join(os.path.dirname(os.path.realpath(__file__)), "temp", videoPath)
                output_video = input_video.replace(".mp4", "_encoded.mp4")
                
                # Ejecutar comando de ffmpeg
                ffmpeg.input(input_video).output(output_video, vcodec='libx264', acodec='aac').run(overwrite_output=True)
                
                videoPath = os.path.basename(output_video)
                st.video(os.path.join(os.path.dirname(os.path.realpath(__file__)),"temp", videoPath))
                with st.columns(1)[0]:
                    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "temp", videoPath), "rb") as file:
                        st.download_button(
                            label="Descargar Video Procesado",
                            data=file,
                            file_name=videoPath,
                            mime="video/mp4"
                        )
# Punto de entrada del script
if __name__ == "__main__":
    main()