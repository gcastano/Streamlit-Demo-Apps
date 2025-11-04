# --- LIBRERÍAS Y DEPENDENCIAS ---
# A continuación, se importan las librerías necesarias para la aplicación.

# streamlit: Es el framework principal para construir la aplicación web de forma rápida y sencilla.
# Permite convertir scripts de datos en aplicaciones web interactivas en pocas líneas de código.
# Instalación: pip install streamlit
import streamlit as st

# streamlit_image_coordinates: Un componente personalizado de Streamlit que permite capturar
# las coordenadas (x, y) de los clics o de las selecciones de arrastre (rectángulos) en una imagen.
# https://discuss.streamlit.io/t/new-tiny-component-streamlit-image-coordinates/35150
# Instalación: pip install streamlit-image-coordinates
from streamlit_image_coordinates import streamlit_image_coordinates

# pandas: Una librería fundamental para la manipulación y análisis de datos en Python.
# La usamos aquí para almacenar y gestionar los datos de las zonas en una estructura de DataFrame.
# Instalación: pip install pandas
import pandas as pd

# PIL (Pillow): Es la librería de facto para el procesamiento de imágenes en Python.
# La utilizamos para abrir, redimensionar, recortar y dibujar sobre la imagen.
# Instalación: pip install Pillow
from PIL import Image, ImageDraw

# --- GESTIÓN DE ESTADO DE LA SESIÓN (SESSION STATE) ---
# st.session_state es un objeto de Streamlit que permite almacenar variables 
# y mantener su estado a través de las diferentes interacciones del usuario (reruns de la app).

# Verificamos si 'dfZonas' no existe en el estado de la sesión. Si es la primera vez que se ejecuta
# el script, se inicializa un DataFrame de pandas vacío con las columnas necesarias para las zonas.
if 'dfZonas' not in st.session_state:
    st.session_state.dfZonas = pd.DataFrame(columns=['x1', 'y1', 'x2', 'y2', 'Zona'])

# Verificamos si 'ultima_zona' no existe en el estado. Esta variable es un truco para evitar
# que la misma zona se añada múltiples veces si la app se recarga por otra interacción.
# Almacenará las coordenadas de la última zona creada.
if 'ultima_zona' not in st.session_state:
    st.session_state.ultima_zona = None

# Para facilitar el acceso, asignamos el DataFrame del estado de la sesión a una variable local.
# Cualquier cambio en 'dfZonas' deberá ser guardado de nuevo en 'st.session_state.dfZonas'.
dfZonas = st.session_state.dfZonas

# Configuración de la página de Streamlit para que use todo el ancho disponible.
st.set_page_config(layout="wide")

st.title("Demo de Zonas Interactivas en Imagen con Streamlit")
st.write("Esta aplicación permite definir zonas clicables en una imagen y probarlas.")
# --- CARGA Y PREPARACIÓN DE LA IMAGEN ---
# Abrimos la imagen desde un archivo local usando Pillow.
img = Image.open("factory.png")
# Redimensionamos la imagen a un ancho fijo de 900 píxeles, manteniendo la proporción original
# para evitar distorsiones.
img = img.resize((900, int(900 * img.height / img.width)))

# --- ESTRUCTURA DE LA APLICACIÓN CON PESTAÑAS ---
# Creamos tres pestañas para organizar la interfaz de usuario.
tabDemoBase, tabConfig, tabZonas = st.tabs(["Demo básico", "Configuración", "Probar Zonas"])

# --- PESTAÑA 1: DEMO BÁSICO ---
with tabDemoBase:    
    # Un checkbox para que el usuario elija el modo de interacción con la imagen.
    parHabilitarRectangulo = st.checkbox("Habilitar selección de rectángulo", value=False)
    
    # Dependiendo del estado del checkbox, se llama al componente de coordenadas de una forma u otra.
    if parHabilitarRectangulo:
        # Modo "arrastrar y soltar" para definir un rectángulo. click_and_drag=True
        value = streamlit_image_coordinates(img, width=900, click_and_drag=True, key="demo_rectangulo",cursor="crosshair")
    else:
        # Modo "clic simple" para obtener un solo punto.
        value = streamlit_image_coordinates(img, width=900, key="demo_clic",cursor="crosshair")
    
    # Mostramos el diccionario de coordenadas que devuelve el componente, útil para depuración.
    st.write(value)

# --- PESTAÑA 2: CONFIGURACIÓN DE ZONAS ---
with tabConfig:
    
    # Colocamos el componente de imagen para que el usuario dibuje rectángulos.
    # El resultado (un diccionario con x1, y1, x2, y2) se guarda en 'value'.
    value = streamlit_image_coordinates(img, width=900, click_and_drag=True,cursor="crosshair")

    # Este bloque se ejecuta solo si el usuario ha dibujado un rectángulo ('value' no es None).
    if value:
        
        # Comprobación para evitar duplicados. Solo se añade una nueva zona si las coordenadas
        # del rectángulo recién dibujado son diferentes a las de la 'ultima_zona' guardada.
        # Esto es clave porque Streamlit re-ejecuta el script en cada interacción.
        if st.session_state.ultima_zona is None or (value['x1'] != st.session_state.ultima_zona['x1'] and \
           value['y1'] != st.session_state.ultima_zona['y1'] and \
           value['x2'] != st.session_state.ultima_zona['x2'] and \
           value['y2'] != st.session_state.ultima_zona['y2']):
            
            # Creamos un diccionario con los datos de la nueva zona.
            dfZona = {'x1': value['x1'], 'y1': value['y1'], 'x2': value['x2'], 'y2': value['y2'], 'Zona': ""}
            
            # --- TRANSFORMACIÓN CON PANDAS: CONCATENACIÓN ---
            # pd.concat es una función de pandas para unir DataFrames.
            # Aquí, creamos un nuevo DataFrame de una sola fila a partir del diccionario 'dfZona'
            # y lo "pegamos" al final de nuestro DataFrame principal 'dfZonas'.
            # ignore_index=True recalcula el índice para que sea continuo (0, 1, 2...).
            dfZonas = pd.concat([dfZonas, pd.DataFrame([dfZona])], ignore_index=True)    
            
            # Actualizamos 'ultima_zona' en el estado de la sesión con la zona que acabamos de añadir.
            st.session_state.ultima_zona = dfZona
        

    # Iteramos sobre cada fila del DataFrame 'dfZonas' para mostrar y gestionar las zonas existentes.
    for index, row in dfZonas.iterrows():
        # Usamos un contenedor con borde para separar visualmente cada zona.
        with st.container(border=True):
            cols = st.columns([1, 3]) # Dividimos el espacio en dos columnas.
            
            with cols[0]: # Columna izquierda para la imagen recortada.
                # Definimos la tupla de coordenadas para el recorte.
                imagenzona = (row['x1'], row['y1'], row['x2'], row['y2'])
                # Usamos el método .crop() de Pillow para recortar la porción de la imagen.
                new_image = img.crop(imagenzona)    
                st.image(new_image) # Mostramos la miniatura de la zona.
            
            with cols[1]: # Columna derecha para el nombre y el botón de eliminar.
                # Creamos un campo de texto para que el usuario nombre la zona.
                zona_nombre = st.text_input(f"Nombre de la Zona {index+1}", value=row['Zona'], key=f"zona_{index}")
                
                # --- ACTUALIZACIÓN DE DATOS CON PANDAS ---
                # Usamos .at[] para acceder y modificar un valor específico en el DataFrame de forma eficiente.
                # Aquí, actualizamos el valor de la columna 'Zona' en la fila 'index'.
                dfZonas.at[index, 'Zona'] = zona_nombre            
                
                # --- ELIMINACIÓN DE DATOS CON PANDAS ---
                # Creamos un botón para eliminar la zona.
                # El parámetro on_click ejecuta una función lambda cuando se presiona.
                # La función lambda ejecuta dos operaciones de pandas en la misma línea:
                # 1. dfZonas.drop(idx, inplace=True): Elimina la fila con el índice 'idx'. inplace=True modifica el DataFrame original.
                # 2. dfZonas.reset_index(drop=True, inplace=True): Reorganiza el índice para que vuelva a ser secuencial.
                #    Es importante para evitar huecos en los índices después de borrar.
                st.button("Eliminar Zona", key=f"eliminar_{index}", on_click=lambda idx=index: dfZonas.drop(idx, inplace=True) or dfZonas.reset_index(drop=True, inplace=True))
            
    # Al final de todas las operaciones, guardamos el DataFrame modificado de vuelta en el estado de la sesión.
    # Esto es CRUCIAL para que los cambios persistan.
    st.session_state.dfZonas = dfZonas
    st.dataframe(dfZonas) # Mostramos el DataFrame actualizado.
# --- PESTAÑA 3: PROBAR ZONAS ---
with tabZonas:
    st.write("Haga clic en la imagen para probar las zonas definidas.")
    # Checkbox para decidir si se muestran visualmente las zonas sobre la imagen.
    parMostrarZonas = st.checkbox("Mostrar Zonas Definidas", value=True)
    
    img_a_mostrar = img # Por defecto, mostramos la imagen original.
    
    if parMostrarZonas:
        # Si el checkbox está activo, creamos una copia de la imagen para no modificar la original.
        overlay = img.copy()
        # Creamos un objeto 'Draw' de Pillow para poder dibujar sobre la imagen 'overlay'.
        draw = ImageDraw.Draw(overlay)
        # Iteramos sobre todas las zonas definidas.
        for index, row in dfZonas.iterrows():
            # Dibujamos un rectángulo rojo sobre la zona.
            draw.rectangle([row['x1'], row['y1'], row['x2'], row['y2']], outline="red", width=3)
            # Escribimos el nombre de la zona ligeramente por encima del rectángulo.
            draw.text((row['x1'], row['y1'] - 10), row['Zona'], fill="red")
        # La imagen que se mostrará ahora será la que tiene los dibujos.
        img_a_mostrar = overlay
        
    # Colocamos el componente de imagen en modo de "clic simple" para la prueba.
    value = streamlit_image_coordinates(img_a_mostrar, width=900, click_and_drag=False,cursor="pointer")

    # Si el usuario ha hecho clic en la imagen...
    if value:
        x_click = value['x']
        y_click = value['y']
        
        # --- FILTRADO DE DATOS CON PANDAS: QUERY ---
        # df.query() es un método muy potente y legible para filtrar un DataFrame.
        # Construimos una cadena de consulta que comprueba si las coordenadas del clic (x_click, y_click)
        # están dentro del rango [x1, x2] y [y1, y2] de alguna de las filas (zonas).
        # Esto nos devuelve un nuevo DataFrame con las filas que cumplen la condición.
        dfZona = dfZonas.query(f'x1 <= {x_click} <= x2 and y1 <= {y_click} <= y2', inplace=False)        
        
        # Comprobamos si el DataFrame resultante tiene alguna fila.
        if len(dfZona) > 0:
            # Si hay al menos una zona, tomamos el nombre de la primera que encontró.
            # .values convierte la columna 'Zona' en un array de numpy, y [0] coge el primer elemento.
            zona_encontrada = dfZona["Zona"].values[0]            
            st.success(f"Hiciste clic en la zona: {zona_encontrada}")            
        else:
            # Si el DataFrame filtrado está vacío, significa que el clic fue fuera de todas las zonas.
            st.warning("No se hizo clic en ninguna zona definida.")