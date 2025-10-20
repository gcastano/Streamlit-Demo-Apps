# --- LIBRERÍAS Y DEPENDENCIAS ---

# Librería: streamlit
# Propósito: Es el framework principal para construir la interfaz de usuario de nuestra aplicación web.
# Permite crear elementos interactivos como botones, áreas de texto y tablas con comandos simples de Python.
# Comando de instalación: pip install streamlit
import streamlit as st

# Librería: pandas
# Propósito: Es la librería estándar de facto en Python para la manipulación y análisis de datos.
# La usamos aquí para convertir nuestra lista de resultados en una tabla estructurada (DataFrame),
# ordenarla y prepararla para su visualización y descarga.
# Comando de instalación: pip install pandas
import pandas as pd

# Librería: googleAI (Módulo Local)
# Propósito: Este es el archivo .py que creamos anteriormente (googleAI.py) y que contiene nuestra función `generateData`.
# Al importarlo, podemos llamar a esa función para interactuar con la API de Gemini.
# Comando de instalación: (No requiere, es un archivo local de nuestro proyecto)
import googleAI

# Librería: stqdm
# Propósito: Una librería que integra la popular barra de progreso 'tqdm' con Streamlit.
# Nos permite mostrar visualmente el progreso del bucle que procesa los enlaces, mejorando la experiencia del usuario.
# Comando de instalación: pip install stqdm
from stqdm import stqdm

# Librería: time
# Propósito: Módulo estándar de Python para funciones relacionadas con el tiempo.
# Lo usamos específicamente para `time.sleep()`, que pausa la ejecución del programa durante unos segundos.
# Es útil para implementar una estrategia simple de reintento en caso de error de la API.
# Comando de instalación: (No requiere, es parte de la librería estándar de Python)
import time

# --- CONFIGURACIÓN DE LA PÁGINA DE STREAMLIT ---
# st.set_page_config se usa para configurar metadatos y la apariencia de la página.
# Debe ser el primer comando de Streamlit que se ejecuta.
st.set_page_config(
    page_title="Streamlit Monitor Precios",  # Título que aparece en la pestaña del navegador.
    page_icon="💲",                          # Icono que aparece en la pestaña del navegador.
    layout="wide"                            # Utiliza todo el ancho de la pantalla para la app.
)

# --- CONSTRUCCIÓN DE LA INTERFAZ DE USUARIO ---

# Muestra el título principal de la aplicación en la página.
st.title(":blue[:material/price_change:] Comparativo de Precios de Productos en Línea")
st.write("Utilizando Google Gemini para extracción de datos")
# Crea un diseño de dos columnas para organizar la interfaz.
# El array [2, 8] define la proporción de ancho entre las columnas (la segunda será 4 veces más ancha que la primera).
c1, c2 = st.columns([2, 8])

# 'with c1:' indica que todos los elementos indentados a continuación se colocarán en la primera columna.
with c1:
    st.subheader("Enlaces de Productos")
    # Crea un área de texto grande para que el usuario pegue los enlaces de los productos.
    parListaEnlaces = st.text_area("Ingrese un enlace por linea", height=400)
    
    # --- PROCESAMIENTO DE LA ENTRADA DEL USUARIO ---
    # Toma el texto completo del área de texto y lo divide en una lista de strings,
    # usando el salto de línea ("\n") como separador. Cada línea será un elemento en la lista.
    parListaEnlacesArray = parListaEnlaces.split("\n")
    st.caption(f"Se han ingresado {len(parListaEnlacesArray)} enlaces.")
    # Crea un botón principal. El código dentro del 'if' solo se ejecutará cuando el usuario haga clic en él.
    btnAnalizar = st.button(":material/frame_inspect: Analizar Enlaces", type="primary")

# 'with c2:' indica que los siguientes elementos se colocarán en la segunda columna.
with c2:
    st.subheader("Resultados")
    # Este bloque de código se ejecuta solo si se ha presionado el botón 'Analizar'.
    if btnAnalizar:
        # Inicializa una lista vacía para almacenar los diccionarios de datos de cada producto.
        listaDatosProductos = []
        
        # Crea un 'placeholder' o contenedor vacío. Este es un truco clave en Streamlit para
        # poder actualizar un elemento (como una tabla) dinámicamente dentro de un bucle.
        placeholder = st.empty()

        enlacesError = []  # Lista para almacenar enlaces que causan errores.
        # Itera sobre cada enlace ingresado por el usuario.
        # Envolvemos el iterable con stqdm() para mostrar una barra de progreso en la interfaz.        
        for enlace in stqdm(parListaEnlacesArray):
            productoRecuperado = False  # Bandera para controlar el bucle de reintentos.
            
            # Se asegura de no procesar líneas vacías. .strip() elimina espacios en blanco al inicio y al final.
            if enlace.strip() != "":
                # Inicia un bucle 'while' para reintentar la obtención de datos si falla la primera vez.
                while not productoRecuperado:
                    try:
                    # with st.container():
                        # Llama a la función del módulo googleAI para obtener los datos del producto.                        
                        datosProducto = googleAI.generateData(enlace.strip())
                        
                        # Agrega el diccionario de datos del producto a nuestra lista principal.
                        listaDatosProductos.append(datosProducto)
                        
                        # --- TRANSFORMACIÓN DE DATOS CON PANDAS (1) ---
                        # Convierte la lista de diccionarios en un DataFrame de pandas.
                        # Un DataFrame es una estructura de datos tabular (filas y columnas), similar a una hoja de cálculo.
                        df = pd.DataFrame(listaDatosProductos)
                        
                        # --- ACTUALIZACIÓN DINÁMICA DE LA INTERFAZ ---
                        # Usamos el 'placeholder' que creamos antes para mostrar y actualizar la tabla de datos.
                        # 'data_editor' muestra el DataFrame como una tabla interactiva.
                        # --- TRANSFORMACIÓN DE DATOS CON PANDAS (2) ---
                        # .sort_values(by="PrecioGramo") ordena el DataFrame para mostrar primero los productos
                        # con el menor precio por gramo, destacando así la mejor oferta.
                        placeholder.data_editor(
                            df.sort_values(by="PrecioGramo"),
                            column_config={
                                # Configura la columna "Enlace" para que se muestre como un enlace web clicable.
                                "Enlace": st.column_config.LinkColumn("Enlace"),
                            },
                            hide_index=True,          # Oculta el índice numérico de las filas de pandas.
                            use_container_width=True  # Hace que la tabla ocupe todo el ancho de la columna.
                        )
                        productoRecuperado = True  # Cambia la bandera para salir del bucle de reintento.
                    except Exception as e:
                        # Si ocurre cualquier error durante la llamada a la API, muestra una notificación.
                        st.toast(f"Error al procesar el enlace {enlace}: {e}")
                        if "quota" not in str(e).lower():                            
                            productoRecuperado = True  # Sale del bucle si es un error de cuota.
                            enlacesError.append(enlace)  # Agrega el enlace problemático a la lista de errores.
                        else:
                            # Pausa la ejecución por 20 segundos antes de reintentar. Esto evita bombardear la API.
                            time.sleep(20)
        if len(enlacesError) > 0:
            st.write(f"Se encontraron {len(enlacesError)} enlaces con error durante el procesamiento.")
            st.dataframe(enlacesError)
        # Después de que el bucle termina, comprueba si se recuperó algún dato.
        if listaDatosProductos:
            # --- TRANSFORMACIÓN DE DATOS CON PANDAS (3) ---
            # Convierte el DataFrame final a formato CSV (texto separado por comas).
            # index=False evita que se guarde el índice de pandas en el archivo.
            # .encode('utf-8') es importante para asegurar la compatibilidad con caracteres especiales.
            csv = df.to_csv(index=False).encode('utf-8')
            
            # Crea un botón que permite al usuario descargar los datos en el archivo CSV generado.
            st.download_button(
                label=":material/csv: Descargar datos como CSV",
                data=csv,
                file_name='datos_productos.csv',
                mime='text/csv',
                type="primary"
            )
        else:
            # Si la lista está vacía al final, informa al usuario.
            st.info("No se encontraron datos de productos para los enlaces proporcionados.")