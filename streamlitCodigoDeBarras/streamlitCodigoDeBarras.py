# --------------------------------------------------------------------------
# LIBRERÍAS Y DEPENDENCIAS
# --------------------------------------------------------------------------
# A continuación, importamos todas las librerías necesarias para nuestro proyecto.

# io: Librería estándar de Python para manejar flujos de E/S (Entrada/Salida).
# Usamos BytesIO para crear un "archivo en memoria". Esto nos permite generar
# el código de barras en formato binario (bytes) sin tener que guardarlo en
# un archivo físico en el disco.
from io import BytesIO

# python-barcode: Una librería fantástica para generar códigos de barras en
# diversos formatos. Es fácil de usar y muy versátil.
# Comando para instalar: pip install python-barcode
# Documentación oficial: https://python-barcode.readthedocs.io/en/stable/
from barcode import Code128  # Específicamente, importamos el formato Code128, uno de los más comunes.
from barcode.writer import SVGWriter # Importamos el "escritor" que genera el código en formato SVG (Scalable Vector Graphics).
                                    # SVG es ideal para la web porque es un formato vectorial, lo que significa que
                                    # se puede escalar a cualquier tamaño sin perder calidad.

# streamlit: Es un framework de Python que permite crear aplicaciones web interactivas
# con muy poco código. Es perfecto para prototipos, dashboards y herramientas internas.
# Comando para instalar: pip install streamlit
import streamlit as st

# math: Librería estándar de Python para operaciones matemáticas.
# La usaremos para calcular el número de filas necesarias en nuestra cuadrícula de códigos.
import math

# --------------------------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA DE STREAMLIT
# --------------------------------------------------------------------------
# st.set_page_config() debe ser el primer comando de Streamlit en tu script.
# Sirve para configurar atributos globales de la página.
st.set_page_config(
    page_title="Generador de Códigos de Barras",  # Título que aparece en la pestaña del navegador.
    page_icon="🔳",  # Ícono que aparece en la pestaña del navegador (puede ser un emoji).
    layout="wide",  # "wide" utiliza todo el ancho de la pantalla, "centered" lo limita a un ancho fijo.
    initial_sidebar_state="expanded"  # "expanded" muestra la barra lateral por defecto, "collapsed" la oculta.
)

# Inyectamos un poco de CSS para mejorar la experiencia de impresión.
# La regla "@media print" se aplica solo cuando se intenta imprimir la página.
# "break-inside: avoid;" evita que un elemento (como un contenedor de código de barras)
# se divida entre dos páginas al imprimir.
st.html("""
    <style>
        @media print {
            div {
                break-inside: avoid;
            }
        }
    </style>
        """)

# --------------------------------------------------------------------------
# DEFINICIÓN DE FUNCIONES
# --------------------------------------------------------------------------

def generar_codigo_barras(codigo: str) -> str:
    """
    Genera un código de barras en formato Code128 y lo devuelve como una cadena de texto SVG.

    Args:
        codigo (str): El valor numérico o alfanumérico que se codificará en el código de barras.

    Returns:
        str: El contenido completo del archivo SVG del código de barras, como una cadena de texto decodificada en UTF-8.
    """
    # 1. Creamos un buffer de bytes en memoria. Imagina que es un archivo temporal que solo existe en la RAM.
    rv = BytesIO()
    
    # 2. Generamos el código de barras:
    #    - Code128(codigo, writer=SVGWriter()): Crea una instancia del código de barras con el valor proporcionado y
    #      le indica que debe usar el escritor SVG para renderizarlo.
    #    - .write(rv, {"text": codigo}): Escribe el SVG resultante en nuestro buffer en memoria (rv).
    #      La opción {"text": codigo} es importante porque le dice a la librería que incluya el texto legible
    #      por humanos debajo de las barras.
    # Opciones para personalizar el código de barras:
    options = {
        "text": codigo,           # Texto legible debajo del código de barras.
        "module_height": 5,      # Altura de las barras (en puntos).
        "font_size": 5,           # Tamaño de la fuente del texto.
        "quiet_zone": 1,          # Espacio en blanco alrededor del código de barras.
        "text_distance": 2        # Distancia entre las barras y el texto.
    }
    Code128(codigo, writer=SVGWriter()).write(rv, options)
    
    # 3. Obtenemos el contenido del buffer y lo devolvemos como texto:
    #    - rv.getvalue(): Extrae los bytes crudos del buffer.
    #    - .decode('utf-8'): Convierte esos bytes en una cadena de texto legible, que es el código fuente del SVG.
    return rv.getvalue().decode('utf-8')

# --------------------------------------------------------------------------
# LÓGICA PRINCIPAL DE LA APLICACIÓN
# --------------------------------------------------------------------------

# Inicializamos la variable que contendrá la lista de códigos.
listaCodigos=None

# La sección 'with st.sidebar:' agrupa todos los elementos que aparecerán en la barra lateral.
with st.sidebar:
    st.title("Generador de códigos de barras")
    st.markdown("Genera códigos de barras en formato SVG, listos para imprimir.")
    
    # st.text_area crea un campo de texto de múltiples líneas para la entrada del usuario.
    parCodigos = st.text_area("Códigos y Texto separados por comas (Uno por línea)", placeholder="Ejemplo:\n12345678,Producto A\n98765432,Producto B")
    
    # st.number_input crea un campo para introducir números, con controles para aumentar/disminuir.
    parColumnas = st.number_input("Número de columnas", min_value=1, max_value=10, value=5, step=1)
    
    # st.button crea un botón. El código dentro del 'if' solo se ejecutará cuando se haga clic.
    btnGenerar = st.button("Generar códigos de barras")

    # Si el botón ha sido presionado...
    if btnGenerar:
        # Transformación de datos principal:
        # 1. Tomamos el texto del 'text_area' (parCodigos).
        # 2. Usamos .split("\n") para dividir el texto en una lista, usando el salto de línea como separador.
        #    Cada línea del input se convierte en un elemento de la lista.
        listaCodigos = parCodigos.split("\n")
        
        # Guardamos la lista en el 'session_state' de Streamlit. Esto permite que los datos
        # persistan entre interacciones, como cambiar el número de columnas sin tener que
        # pegar los códigos de nuevo.
        st.session_state["listaCodigos"] = listaCodigos

# Este bloque se ejecuta si la variable 'listaCodigos' tiene contenido (es decir, si se presionó el botón).
if listaCodigos:
    # Calculamos cuántas filas necesitaremos para mostrar todos los códigos.
    # Usamos math.ceil() para redondear hacia arriba y asegurarnos de que todos los elementos tengan espacio.
    # Por ejemplo, con 12 códigos y 5 columnas, 12/5 = 2.4, que math.ceil() convierte en 3 filas.
    filas = math.ceil(len(listaCodigos) / parColumnas)
    
    # Inicializamos un contador para llevar la cuenta de qué código estamos mostrando.
    contador=0
    
    # Iteramos sobre el número de filas que calculamos.
    for fila in range(filas):
        # st.container es un bloque de diseño. Con 'horizontal=True', los elementos dentro se alinearán
        # uno al lado del otro. 'distribute' intenta espaciarlos uniformemente.
        with st.container(horizontal=True, vertical_alignment="bottom"):
            
            # Dentro de cada fila, iteramos sobre el número de columnas.
            for i in range(parColumnas):
                
                # Verificamos si ya hemos mostrado todos los códigos de la lista.
                if contador >= len(listaCodigos):
                    # Si ya no hay más códigos, creamos un contenedor vacío para mantener la estructura de la cuadrícula.
                    with st.container(border=False):
                        st.write(f"")                    
                else:
                    # Si todavía hay códigos por mostrar...
                    # Obtenemos el elemento actual de la lista (ej: "12345,Producto A").
                    item = listaCodigos[contador]
                    
                    # Transformación de datos secundaria:
                    # Separamos el código y el texto descriptivo usando la coma como delimitador.
                    codigo = item.split(",")[0]  # La primera parte es el código.
                    
                    # Para el texto, verificamos si existe una segunda parte después de la coma.
                    # Esto evita errores si el usuario solo introduce el código sin texto.
                    texto = item.split(",")[1] if len(item.split(",")) > 1 else ""
                    
                    # Llamamos a nuestra función para generar el SVG del código de barras.
                    svg_content = generar_codigo_barras(codigo)
                    
                    # Creamos un contenedor individual con borde para cada código de barras.
                    with st.container(border=True):
                        # st.caption muestra el texto descriptivo en un formato más pequeño.
                        st.markdown(f"###### {texto}")
                        # st.image puede mostrar imágenes desde un archivo, URL o, como en este caso,
                        # directamente desde una cadena de texto que contiene el código SVG.
                        # 'use_container_width=True' hace que la imagen se ajuste al ancho del contenedor.
                        st.image(svg_content, use_container_width=True)
                
                # Incrementamos el contador para pasar al siguiente código en la próxima iteración.
                contador += 1