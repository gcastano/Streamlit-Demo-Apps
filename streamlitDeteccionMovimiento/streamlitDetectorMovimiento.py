# ==============================================================================
# LIBRERÍAS Y COMANDOS DE INSTALACIÓN
# ==============================================================================
# streamlit: Una librería de Python para crear y compartir aplicaciones web para
#            ciencia de datos y machine learning de forma rápida y sencilla.
#            Instalación: pip install streamlit
#
# opencv-python: Conocida como OpenCV, es una librería de visión por computadora
#                y procesamiento de imágenes de código abierto.
#                Instalación: pip install opencv-python
#
# tempfile: Es una librería nativa de Python (no requiere instalación) que se
#           usa para crear archivos y directorios temporales.
#
# datetime: Librería nativa de Python para trabajar con fechas y horas.
# ==============================================================================

import streamlit as st                # Importa la librería Streamlit para crear la interfaz web
import cv2                            # Importa OpenCV para procesamiento de video e imágenes
import tempfile                       # Importa tempfile para crear archivos temporales
from datetime import timedelta        # De la librería datetime, importa timedelta para manejar duraciones de tiempo

# Configura la página de Streamlit para que tenga un título y ocupe todo el ancho
st.set_page_config(page_title="Detector de Movimiento en Video", layout="wide")

@st.fragment
def MostrarVideo(video_path, segundosMovimiento):
    """
    Muestra el video analizado y permite al usuario navegar a los momentos
    específicos donde se detectó movimiento.

    Args:
        video_path (str): La ruta al archivo de video que se va a mostrar.
        segundosMovimiento (list): Una lista de enteros que representan los segundos
                                  en los que se detectó movimiento.

    Returns:
        None: No devuelve ningún valor, renderiza componentes en la interfaz de Streamlit.
    """
    st.success("Análisis de movimiento completado.")  # Muestra un mensaje de éxito al finalizar el análisis
    
    # Crea un control segmentado para que el usuario elija un segundo específico
    parMoviminto = st.segmented_control(
                                            "Segundos de movimiento",
                                            options=segundosMovimiento,
                                            default=segundosMovimiento[0] if segundosMovimiento else 0
                                        )
    
    # Muestra el componente de video de Streamlit, comenzando la reproducción en el segundo seleccionado
    st.video(video_path, start_time=timedelta(seconds=parMoviminto))

# Título principal de la aplicación web
st.title("Detector de Movimiento en Video")

# Componente de Streamlit para que el usuario suba un archivo de video
uploaded_file = st.file_uploader("Carga un video", type=["mp4", "avi", "mov"])

# Verifica si el usuario ha subido un archivo
if uploaded_file is not None:
    # Crea un archivo temporal para guardar el video subido.
    # OpenCV necesita una ruta de archivo en el disco para abrir el video.
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read()) # Escribe los bytes del video subido al archivo temporal
    video_path = tfile.name           # Obtiene la ruta del archivo temporal
    # st.write(video_path)
    # Abre el video usando OpenCV
    cap = cv2.VideoCapture(video_path)
    # Crea un contenedor vacío en Streamlit que se actualizará dinámicamente con los fotogramas
    stframe = st.empty()
    
    # Lee los dos primeros fotogramas para iniciar la comparación
    ret, frame1 = cap.read()
    ret, frame2 = cap.read()
    
    # Inicializa una lista para almacenar los segundos en los que se detecta movimiento
    segundosMovimiento = []
    
    # Bucle principal: se ejecuta mientras haya fotogramas disponibles en el video
    while ret and frame2 is not None:
        
        # --- PASOS DE PROCESAMIENTO DE IMAGEN PARA DETECTAR MOVIMIENTO ---

        # 1. Diferencia Absoluta: Calcula la diferencia pixel a pixel entre dos fotogramas.
        #    Las áreas que no cambian resultan en negro, y las que cambian, en color.
        diff = cv2.absdiff(frame1, frame2)
        
        # 2. Escala de Grises: Convierte la imagen de diferencia a escala de grises.
        #    Simplifica el análisis al trabajar con una sola dimensión de intensidad.
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        
        # 3. Desenfoque Gaussiano: Aplica un filtro de desenfoque para suavizar la imagen
        #    y eliminar el ruido de alta frecuencia (pequeñas variaciones irrelevantes).
        blur = cv2.GaussianBlur(gray, (5,5), 0)
        
        # 4. Umbral (Thresholding): Crea una imagen binaria (blanco y negro).
        #    Píxeles con intensidad mayor a 20 se convierten en blanco (movimiento)
        #    y los demás en negro (sin movimiento).
        _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
        
        # 5. Dilatación: "Engorda" las áreas blancas para rellenar pequeños agujeros y
        #    conectar regiones de movimiento cercanas, creando contornos más sólidos.
        dilated = cv2.dilate(thresh, None, iterations=3)
        
        # 6. Encontrar Contornos: Detecta los bordes de las formas blancas (áreas de movimiento)
        #    en la imagen dilatada.
        # cv2.findContours: Encuentra los contornos en la imagen binaria dilatada.
        # Parámetros:
        #   - dilated: Imagen binaria donde buscar los contornos.
        #   - cv2.RETR_TREE: Modo de recuperación de contornos, recupera todos los contornos y construye una jerarquía completa de contornos anidados.
        #   - cv2.CHAIN_APPROX_SIMPLE: Método de aproximación de contornos, comprime los segmentos horizontales, verticales y diagonales dejando solo sus puntos extremos.
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Itera sobre cada contorno encontrado
        for contour in contours:
            # Filtra los contornos pequeños que probablemente son ruido
            if cv2.contourArea(contour) < 500:
                continue
            
            # Obtiene el rectángulo delimitador que encierra el contorno
            (x, y, w, h) = cv2.boundingRect(contour)
            # Dibuja el rectángulo verde sobre el fotograma original para visualizar el movimiento
            cv2.rectangle(
                frame1,           # Imagen sobre la que se dibuja el rectángulo (el fotograma original)
                (x, y),           # Coordenada superior izquierda del rectángulo (esquina inicial)
                (x+w, y+h),       # Coordenada inferior derecha del rectángulo (esquina final)
                (0,255,0),        # Color del rectángulo en formato BGR (verde)
                2                 # Grosor del borde del rectángulo en píxeles
            )
            
            # Obtiene el tiempo actual del video en milisegundos, lo convierte a segundos
            # y lo añade a la lista de momentos con movimiento.
            segundosMovimiento.append(int(cap.get(cv2.CAP_PROP_POS_MSEC)/1000))

        # Muestra los resultados en la interfaz de Streamlit
        with stframe.container():
            # Crea un diseño de 2 columnas para una mejor visualización
            c1, c2 = st.columns([7, 3])
            # En la columna ancha, muestra el video con los rectángulos de movimiento
            c1.image(frame1, channels="BGR", caption="Video con Detección de Movimiento")
            # En la columna estrecha, muestra las diferentes etapas del procesamiento
            with c2.container(horizontal=True,horizontal_alignment ="left"):
                st.image(diff, caption="1. Diferencia", width=200)
                st.image(gray, caption="2. Escala de Grises", width=200)
                st.image(blur, caption="3. Desenfoque", width=200)
                st.image(dilated, caption="4. Dilatación", width=200)
            
        # Actualiza los fotogramas para la siguiente iteración
        frame1 = frame2          # El fotograma 2 se convierte en el fotograma 1
        ret, frame2 = cap.read() # Lee un nuevo fotograma para ser el fotograma 2
    
    # Procesa la lista de segundos para eliminar duplicados y ordenarla
    # set() elimina duplicados, list() lo convierte a lista, sorted() la ordena.
    segundosMovimiento = sorted(list(set(segundosMovimiento)))
    
    # Libera el objeto de captura de video para cerrar el archivo y liberar recursos
    cap.release()
    
    # Llama a la función para mostrar el video final y los controles de navegación
    MostrarVideo(video_path, segundosMovimiento)