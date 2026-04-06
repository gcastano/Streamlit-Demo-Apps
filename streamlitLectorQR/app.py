# ==========================================
# 📦 COMANDOS DE INSTALACIÓN (PIP INSTALL)
# Ejecuta este comando en tu terminal antes de correr el script:
# pip install streamlit opencv-python numpy pillow pyzbar streamlit-paste-button pandas
# ==========================================

# ==========================================
# 📚 EXPLICACIÓN DE LIBRERÍAS UTILIZADAS
# ==========================================
import streamlit as st
# streamlit: Framework principal para crear interfaces web interactivas y paneles de datos en Python de forma rápida.
import cv2
# cv2 (OpenCV): Librería líder en visión artificial. Se usa aquí para acceder a la webcam, leer fotogramas y detectar QRs.
import numpy as np
# numpy: Fundamental para cálculos numéricos. En procesamiento de imágenes, transforma y manipula los datos como matrices de píxeles.
from PIL import Image
# PIL (Pillow): Librería estándar de Python para abrir, manipular y guardar imágenes estáticas (como las que se suben).
from pyzbar.pyzbar import decode
# pyzbar: Motor decodificador que lee los datos del código QR y los convierte de un formato visual a texto plano.
from streamlit_paste_button import paste_image_button
# streamlit_paste_button: Componente de terceros para Streamlit que permite leer datos directamente del portapapeles del sistema.
# pip install streamlit-paste-button

# ==========================================
# 🐼 NOTA SOBRE TRANSFORMACIÓN DE DATOS CON PANDAS:
# En este script específico, las "transformaciones de datos" suceden a nivel de matrices numéricas (NumPy y OpenCV) 
# al convertir y manipular píxeles. Sin embargo, en un proyecto real para producción, utilizarías `pandas` para 
# almacenar y transformar el historial de QRs detectados. 
# Ejemplo de transformación con Pandas que podrías agregar:
#   import pandas as pd
#   df_historial = pd.DataFrame(st.session_state.historial_qrs, columns=["Fecha", "Contenido_QR"])
#   df_historial["Dominio"] = df_historial["Contenido_QR"].str.extract(r'(https?://[^/]+)') # Transformación de texto
#   st.dataframe(df_historial)
# ==========================================

# Configuración inicial de la página
st.set_page_config(page_title="Lector QR Todo-en-Uno", page_icon="🔴", layout="centered")

st.title(":material/qr_code_scanner: Lector de Código QR")
st.write("Carga un archivo, pega desde tu portapapeles o usa el escáner automático con tu cámara.")

# --- Inicialización de variables de sesión para la cámara ---
# Almacenamos el estado para no perder los datos cuando la app de Streamlit se recarga
if "qr_detectado" not in st.session_state:
    st.session_state.qr_detectado = None
if "imagen_capturada" not in st.session_state:
    st.session_state.imagen_capturada = None

# --- Funciones Auxiliares ---
def leer_qr_estatico(imagen):
    """
    Decodifica códigos QR presentes en imágenes estáticas (archivos subidos o capturas).
    
    Esta función utiliza la librería pyzbar para buscar patrones de códigos QR 
    en el arreglo de datos de la imagen y extraer la información a texto plano.
    
    Parámetros:
    ----------
    imagen : PIL.Image o numpy.ndarray
        La imagen de entrada que contiene el código QR a decodificar.
        
    Retorna:
    -------
    list of str or None:
        Una lista de cadenas de texto con los datos decodificados en formato UTF-8 
        si se encuentra al menos un QR. Retorna None si no hay detecciones.
    """
    try:
        # Transformación de los datos de la imagen a un objeto decodificado
        objetos_decodificados = decode(imagen)
        if not objetos_decodificados:
            return None
        # Transformación de formato de byte a string UTF-8 mediante list comprehension
        return[obj.data.decode('utf-8') for obj in objetos_decodificados]
    except Exception as e:
        st.error(f"Error al procesar la imagen: {e}")
        return None

def mostrar_resultados(resultados):
    """
    Renderiza en la interfaz gráfica los resultados de la decodificación.
    
    Aplica componentes visuales de Streamlit dependiendo de si la lectura 
    fue exitosa o no, mostrando alertas e imprimiendo el código.
    
    Parámetros:
    ----------
    resultados : list of str or None
        Lista de textos decodificados previamente por la función `leer_qr_estatico`.
    """
    if resultados:
        st.success("¡Código QR detectado con éxito!")
        for res in resultados:
            st.code(res, language="text")
    else:
        st.warning("No se detectó ningún código QR. Intenta con una imagen más nítida.")

# --- Definición de Pestañas ---
tab1, tab2, tab3 = st.tabs([":material/file_upload: Cargar Archivo", ":material/content_paste: Pegar (Portapapeles)", ":material/camera_alt: Escáner OpenCV"])

# ---------------------------------------------------------
# PESTAÑA 1: Cargar Archivo Local
# ---------------------------------------------------------
with tab1:
    archivo_subido = st.file_uploader("Sube tu imagen con el código QR", type=['png', 'jpg', 'jpeg', 'webp'])
    
    if archivo_subido is not None:
        # Convertimos el archivo binario subido en un objeto de imagen manejable
        imagen = Image.open(archivo_subido)
        st.image(imagen, caption="Imagen cargada", width=300)
        
        with st.spinner("Analizando código QR..."):
            resultados = leer_qr_estatico(imagen)
        mostrar_resultados(resultados)

# ---------------------------------------------------------
# PESTAÑA 2: Pegar desde el Portapapeles
# ---------------------------------------------------------
with tab2:
    st.info("💡 Haz una captura de pantalla de un QR y presiona el botón de abajo para pegarlo.")
    
    # Botón personalizado de streamlit-paste-button
    resultado_pegado = paste_image_button(
        label="📋 Pegar imagen desde el Portapapeles",
        text_color="#ffffff",
        background_color="#FF4B4B",
        hover_background_color="#FF6363",
        errors="ignore"
    )
    
    if resultado_pegado.image_data is not None:
        imagen_pegada = resultado_pegado.image_data
        st.image(imagen_pegada, caption="Imagen pegada", width=300)
        
        with st.spinner("Analizando código QR de la captura..."):
            resultados = leer_qr_estatico(imagen_pegada)
        mostrar_resultados(resultados)

# ---------------------------------------------------------
# PESTAÑA 3: Escáner Automático con OpenCV
# ---------------------------------------------------------
with tab3:
    st.write("Enciende tu cámara web. El sistema tomará la foto automáticamente al detectar un QR.")
    
    col1, col2 = st.columns(2)
    iniciar = col1.button(":green[:material/camera_alt: Iniciar Escáner Automático]", use_container_width=True)
    detener = col2.button(":red[:material/stop: Detener / Limpiar]", use_container_width=True)

    # Limpiar resultados anteriores en el estado de la sesión
    if detener:
        st.session_state.qr_detectado = None
        st.session_state.imagen_capturada = None

    # Mostrar resultado guardado en memoria
    if st.session_state.qr_detectado:
        st.success("¡Código QR capturado automáticamente!")
        st.code(st.session_state.qr_detectado, language="text")
        st.image(st.session_state.imagen_capturada, caption="Momento exacto de la detección", channels="RGB", width=400)

    # Iniciar el bucle de la cámara
    if iniciar:
        st.session_state.qr_detectado = None
        st.session_state.imagen_capturada = None
        
        marco_video = st.empty() # Contenedor dinámico para mostrar el video en vivo
        
        cap = cv2.VideoCapture(0) # Acceso a la cámara web (índice 0)
        detector_qr = cv2.QRCodeDetector() # Inicializa el detector de OpenCV
        
        if not cap.isOpened():
            st.error("No se pudo acceder a la cámara web. Asegúrate de que no esté en uso por otra app.")
        else:
            detectado = False
            st.toast("Cámara activada. Enfoca un código QR...", icon="🎥")
            
            while not detectado:
                ret, frame = cap.read() # Lectura del fotograma (como matriz NumPy)
                if not ret:
                    st.error("Error al leer la cámara.")
                    break
                
                # Extraer la información del QR usando el fotograma
                data, bbox, _ = detector_qr.detectAndDecode(frame)
                
                # Transformación visual de datos: dibujar recuadros usando coordenadas matriciales
                if bbox is not None:
                    n_lines = len(bbox[0])
                    for i in range(n_lines):
                        pt1 = tuple(map(int, bbox[0][i]))
                        pt2 = tuple(map(int, bbox[0][(i+1) % n_lines]))
                        # Se dibuja la línea directamente sobre la matriz 'frame'
                        cv2.line(frame, pt1, pt2, color=(0, 255, 0), thickness=3)
                
                # TRANSFORMACIÓN DE DATOS (Espacios de Color):
                # OpenCV lee imágenes en formato BGR por defecto. 
                # Streamlit (y los navegadores web) requieren el espacio de color RGB.
                # Transformamos la matriz del fotograma para que los colores sean precisos.
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                marco_video.image(frame_rgb, channels="RGB")
                
                # Lógica para detener el bucle cuando se realiza la extracción de datos con éxito
                if data:
                    st.session_state.qr_detectado = data
                    st.session_state.imagen_capturada = frame_rgb
                    detectado = True
                    break
            
            cap.release() # Liberar el hardware de la cámara
            
            # Forzar recarga de Streamlit para renderizar el resultado final fuera del bucle de video
            if detectado:
                st.rerun()