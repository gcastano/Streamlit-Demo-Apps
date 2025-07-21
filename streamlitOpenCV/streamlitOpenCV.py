# =================================================================================
# EXPLICACIÓN DE LIBRERÍAS Y COMANDOS DE INSTALACIÓN
# =================================================================================

# streamlit: Una librería de Python que permite crear aplicaciones web interactivas
# y dashboards de datos de forma rápida y sencilla, directamente desde scripts de Python.
# Es ideal para prototipar y compartir proyectos de ciencia de datos y machine learning.
# Comando de instalación: pip install streamlit

# pandas: Una librería fundamental para la manipulación y análisis de datos en Python.
# Proporciona estructuras de datos como el DataFrame, que es esencial para trabajar
# con datos tabulares de forma eficiente. En este script, la usamos para organizar
# la información de los contornos detectados.
# Comando de instalación: pip install pandas

# cv2 (OpenCV-Python): Es una potente librería de visión por computadora y procesamiento de imágenes.
# Se utiliza para leer, manipular y analizar imágenes y videos.
# Comando de instalación: pip install opencv-python

# numpy: Fundamental para la computación científica en Python. Proporciona soporte para
# arrays y matrices multidimensionales, junto con una colección de funciones matemáticas
# para operar en estas estructuras. Es esencial para OpenCV, ya que las imágenes se representan como arrays de NumPy.
# Comando de instalación: pip install numpy

# PIL (Pillow): Es un fork amigable de la Python Imaging Library (PIL). Permite abrir,
# manipular y guardar muchos formatos de archivo de imagen diferentes. Streamlit la usa
# internamente para manejar las imágenes subidas por el usuario.
# Comando de instalación: pip install Pillow

# streamlit_image_zoom: Un componente personalizado para Streamlit que añade
# funcionalidades de zoom y panorámica a las imágenes mostradas en la app,
# mejorando la experiencia del usuario al inspeccionar detalles.
# Comando de instalación: pip install streamlit-image-zoom
# https://github.com/vgilabert94/streamlit-image-zoom
# =================================================================================


import streamlit as st
import cv2
import numpy as np
from PIL import Image
from streamlit_image_zoom import image_zoom
import pandas as pd

# --- Función de Procesamiento de OpenCV ---
def contar_objetos_imagen(image, blur_ksize, thresh_val,min_area = 100,clipLimit=2.0, tileGridSize=(8,8),ImagenNegativa=False):
    """
    Procesa una imagen para contar objetos utilizando una serie de técnicas de OpenCV.

    Esta función toma una imagen en formato PIL, la convierte para ser procesada con OpenCV,
    aplica mejoras de contraste, filtros, binarización y finalmente detecta y cuenta
    los contornos que superan un área mínima.

    Args:
        image (PIL.Image.Image): La imagen de entrada cargada con Pillow.
        blur_ksize (int): El tamaño del kernel para el desenfoque Gaussiano. Debe ser un número impar.
        thresh_val (int): El valor de umbral para la binarización. Píxeles por debajo de este valor se vuelven negros, y por encima blancos.
        min_area (int, optional): El área mínima en píxeles para que un contorno sea considerado un objeto válido. Defaults to 100.
        clipLimit (float, optional): Parámetro para CLAHE que limita la amplificación del contraste. Defaults to 2.0.
        tileGridSize (tuple, optional): Tamaño de la cuadrícula para CLAHE. Defaults to (8,8).
        ImagenNegativa (bool, optional): Si es True, invierte los colores de la imagen (negativo). Defaults to False.

    Returns:
        tuple: Una tupla conteniendo:
            - output_image_rgb (np.array): La imagen original con los contornos y números de los objetos detectados.
            - img_bgr (np.array): La imagen con contraste mejorado, convertida a RGB para visualización.
            - object_count (int): El número total de objetos contados.
            - img_gray (np.array): La imagen en escala de grises (paso intermedio).
            - img_blur (np.array): La imagen con el desenfoque aplicado (paso intermedio).
            - img_thresh (np.array): La imagen binarizada (paso intermedio).
            - dfContornos (pd.DataFrame): Un DataFrame de pandas con el número y área de cada contorno detectado.
    """
    # Pillow (PIL) carga las imágenes en formato RGB. OpenCV trabaja por defecto con BGR.
    # Primero, convertimos la imagen PIL a un array de NumPy.
    # Luego, cambiamos el espacio de color de RGB a BGR para que OpenCV pueda procesarla correctamente.
    img_bgr = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    img_bgr_base = img_bgr.copy() # Guardamos una copia de la imagen original para dibujar sobre ella al final.

    if ImagenNegativa:
        # La inversión de la imagen (negativo) puede ser útil cuando los objetos de interés
        # son oscuros y el fondo es claro. La binarización a menudo funciona mejor con objetos claros sobre fondo oscuro.
        img_bgr = cv2.bitwise_not(img_bgr)

    # --- Mejora de Contraste con CLAHE ---
    # CLAHE (Contrast Limited Adaptive Histogram Equalization) es una técnica avanzada
    # para mejorar el contraste local de una imagen. Funciona bien en imágenes con iluminación desigual.
    # Para no alterar los colores, aplicamos CLAHE solo al canal de luminosidad (L) del espacio de color LAB.
    # 1. Convertir la imagen de BGR a LAB.
    img_lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
    # 2. Separar los canales L (Luminosidad), a (componente verde-rojo), y b (componente azul-amarillo).
    l, a, b = cv2.split(img_lab)
    # 3. Crear el objeto CLAHE con los parámetros definidos por el usuario.
    clahe = cv2.createCLAHE(clipLimit=clipLimit, tileGridSize=tileGridSize)
    # 4. Aplicar CLAHE solo al canal L.
    l_clahe = clahe.apply(l)
    # 5. Volver a unir los canales con el canal L mejorado.
    img_lab_clahe = cv2.merge((l_clahe, a, b))
    # 6. Convertir la imagen de vuelta de LAB a BGR.
    img_bgr = cv2.cvtColor(img_lab_clahe, cv2.COLOR_LAB2BGR)

    # Convertir la imagen a escala de grises. El análisis de contornos se realiza sobre imágenes de un solo canal.
    img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # Aplicar un Desenfoque Gaussiano para suavizar la imagen y reducir el ruido.
    # Esto ayuda a evitar la detección de contornos falsos. El kernel debe ser de tamaño impar.
    blur_ksize = blur_ksize if blur_ksize % 2 == 1 else blur_ksize + 1
    img_blur = cv2.GaussianBlur(img_gray, (blur_ksize, blur_ksize), 0)

    # Binarización de la imagen. Todos los píxeles se convierten a blanco o negro según un valor de umbral.
    # THRESH_BINARY_INV invierte el resultado: los píxeles por encima del umbral se vuelven negros y por debajo blancos.
    # Esto es útil para obtener objetos blancos sobre un fondo negro, que es el formato estándar para findContours.
    _, img_thresh = cv2.threshold(img_blur, thresh_val, 255, cv2.THRESH_BINARY_INV)

    # --- Detección de Contornos ---
    # `findContours` busca las curvas continuas que forman los límites de los objetos en la imagen binarizada.
    # - img_thresh: La imagen de entrada (debe ser binaria).
    # - cv2.RETR_CCOMP: Recupera todos los contornos y los organiza en una jerarquía de dos niveles.
    # - cv2.CHAIN_APPROX_SIMPLE: Comprime los segmentos de contorno horizontales, verticales y diagonales, dejando solo sus puntos finales. Ahorra memoria.
    contours, _ = cv2.findContours(
        img_thresh,
        cv2.RETR_CCOMP,
        cv2.CHAIN_APPROX_SIMPLE
    )

    # Filtrar los contornos detectados para eliminar el ruido.
    # Se crea una nueva lista solo con los contornos cuya área es mayor que el mínimo definido por el usuario.
    valid_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]

    # --- Dibujar Resultados y Extraer Datos con Pandas ---
    # Dibujar los contornos válidos sobre la copia de la imagen original.
    output_image = img_bgr_base.copy()
    cv2.drawContours(output_image, valid_contours, -1, (0, 255, 0), 2) # Dibuja todos los contornos (-1) en color verde (0,255,0) con un grosor de 2 píxeles.

    # Convertir la imagen de salida de BGR a RGB para mostrarla correctamente en Streamlit.
    output_image_rgb = cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB)
    
    # [TRANSFORMACIÓN CON PANDAS] Se inicializa un DataFrame vacío con las columnas deseadas.
    # Este DataFrame almacenará los datos de cada objeto detectado.
    dfContornos = pd.DataFrame(columns=["Contorno", "Área"])

    # Iterar sobre cada contorno válido para numerarlo y extraer sus datos.
    for idx, contour in enumerate(valid_contours):
        # Calcular el área del contorno actual.
        area_contour = cv2.contourArea(contour)
        
        # Calcular los momentos del contorno para encontrar su centroide (centro de masa).
        M = cv2.moments(contour)
        # Asegurarse de no dividir por cero para calcular las coordenadas del centro (cX, cY).
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        else:
            # Si el momento m00 es cero, usar el primer punto del contorno como fallback.
            cX, cY = contour[0][0]

        # [TRANSFORMACIÓN CON PANDAS] Se crea un pequeño DataFrame para el contorno actual.
        dfContornoActual = pd.DataFrame({
            "Contorno": [idx + 1],  # Contador de objetos (empezando desde 1)
            "Área": [area_contour],  # Área del contorno
        })
        
        # [TRANSFORMACIÓN CON PANDAS] Se concatena (une) el DataFrame del contorno actual al DataFrame principal.
        # Esta es una forma eficiente de construir el DataFrame fila por fila.
        dfContornos = pd.concat([dfContornos, dfContornoActual])

        # Poner el número del objeto en la imagen.
        # Se usa un truco para crear un borde: primero se dibuja el texto en blanco y más grueso,
        # y luego encima el mismo texto en rojo y más fino. Esto mejora la visibilidad sobre cualquier fondo.
        texto = str(idx + 1)
        posicion = (cX, cY)
        fuente = cv2.FONT_HERSHEY_SIMPLEX
        escala_borde = 1.2
        color_borde = (255, 255, 255)
        grosor_borde = 8
        tipo_linea = cv2.LINE_AA

        # Dibuja el borde blanco del número
        cv2.putText(output_image_rgb, texto, posicion, fuente, escala_borde, color_borde, grosor_borde, tipo_linea)
        # Dibuja el número en rojo sobre el borde
        cv2.putText(output_image_rgb, texto, posicion, fuente, 1.2, (255, 0, 0), 2, tipo_linea)

    # Contar el número total de objetos válidos encontrados.
    object_count = len(valid_contours)
    
    # Convertir la imagen con contraste mejorado de BGR a RGB para mostrarla correctamente en el expander de Streamlit.
    img_bgr = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    
    return output_image_rgb,img_bgr, object_count, img_gray, img_blur, img_thresh, dfContornos

@st.dialog(title="Ver DataFrame de Contornos")
def verDataFrame(df):
    """
    Muestra un DataFrame de pandas dentro de un diálogo modal en Streamlit.
    
    Args:
        df (pd.DataFrame): El DataFrame a mostrar, que contiene la información de los contornos.
    """
    # Muestra el DataFrame, usando el ancho completo del contenedor y ocultando el índice por defecto de pandas.
    st.dataframe(df, use_container_width=True, hide_index=True)

# --- Interfaz de Usuario con Streamlit ---

# Configurar la página para que use un diseño ancho por defecto y tenga un título en la pestaña del navegador.
st.set_page_config(layout="wide", page_title="Contador de Objetos con OpenCV y Streamlit")
st.title("Contador de Objetos con OpenCV y Streamlit")

# Crear una barra lateral para los controles de configuración.
st.sidebar.header("Configuración")
# Widget para que el usuario suba un archivo de imagen.
uploaded_file = st.sidebar.file_uploader("Sube una imagen", type=["jpg", "jpeg", "png"])

# Sliders para ajustar los parámetros del procesamiento de imagen en tiempo real.
blur_kernel_size = st.sidebar.slider("Tamaño del Kernel de Desenfoque (impar)", 1, 100, 5, step=2)
threshold_value = st.sidebar.slider("Umbral de Binarización", 0, 255, 127)
min_area = st.sidebar.number_input("Área Mínima de Contorno",value=100, min_value=0, step=10, help="El área mínima en píxeles para que un contorno sea considerado un objeto válido.")
st.sidebar.markdown("#### Parámetros de Mejora de Contraste (CLAHE)")
clip_limit = st.sidebar.slider("Clip Limit", 1.0, 10.0, 2.0, step=0.1)
tile_grid_size = st.sidebar.slider("Tamaño de la Cuadrícula", 1, 32, 8, step=1)
# Checkbox para la opción de invertir la imagen.
imagenNegativa = st.sidebar.checkbox("Invertir Imagen (Negativo)", value=False)

# Este bloque de código se ejecuta solo si el usuario ha subido un archivo.
if uploaded_file is not None:
    # Abrir el archivo de imagen subido utilizando la librería Pillow.
    image = Image.open(uploaded_file)
    # Llamar a nuestra función principal de procesamiento con los parámetros de la sidebar.
    processed_image, img_bgr, count, gray, blur, thresh, dfContornos = contar_objetos_imagen(
        image, blur_kernel_size, threshold_value, min_area, clip_limit, (tile_grid_size, tile_grid_size), imagenNegativa
    )

    # Mostrar el resultado principal: el conteo de objetos.    
    st.metric(label="Número de Objetos", value=count)

    # Dividir el área de visualización en dos columnas para comparar la imagen original y la procesada.
    col1, col2 = st.columns([2, 8]) # La columna 2 (procesada) será 4 veces más ancha que la 1 (original).

    with col1:
        st.subheader("Imagen Original")
        st.image(image, use_container_width=True)

    with col2:
        st.subheader("Imagen Procesada (con zoom)")
        # Usar el componente `image_zoom` para permitir al usuario inspeccionar la imagen procesada de cerca.
        image_zoom(processed_image, keep_resolution=True, mode="dragmove", keep_aspect_ratio=True, zoom_factor=4.0, increment=0.2)
        # Botón que, al ser presionado, abre el diálogo para mostrar el DataFrame de pandas.
        if st.button("Ver Tabla de Datos de Contornos"):
            verDataFrame(dfContornos)

    # Crear una sección expandible para mostrar los pasos intermedios del procesamiento.
    # Esto es muy útil para entender cómo funciona el algoritmo y para depurar los parámetros.
    with st.expander("Ver Pasos Intermedios del Procesamiento"):
        st.write("Estos son los pasos que OpenCV sigue para identificar los objetos.")
        col_step0, col_step1, col_step2, col_step3 = st.columns(4)
        with col_step0:
            st.image(img_bgr, caption="1. Contraste Mejorado", use_container_width=True)
        with col_step1:
            st.image(gray, caption="2. Escala de Grises", use_container_width=True)
        with col_step2:
            st.image(blur, caption="3. Desenfoque Gaussiano", use_container_width=True)
        with col_step3:
            st.image(thresh, caption="4. Imagen Binarizada", use_container_width=True)
else:
    # Mensajes para guiar al usuario si no ha subido una imagen.
    st.info("Por favor, sube una imagen usando el panel de la izquierda para comenzar.")
    st.warning("Para mejores resultados, usa imágenes con objetos bien definidos sobre un fondo de color contrastante.")