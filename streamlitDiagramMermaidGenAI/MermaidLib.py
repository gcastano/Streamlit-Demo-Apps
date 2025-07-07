# -*- coding: utf-8 -*-

# ------------------- LIBRERÍAS -------------------
# A continuación, se importan todas las librerías necesarias para la función.

# --- base64: Librería estándar de Python ---
# Se utiliza para la codificación y decodificación de datos en Base64.
# Específicamente, `urlsafe_b64encode` se usa para asegurar que el texto codificado
# no contenga caracteres ('+' y '/') que puedan causar problemas en las URLs.
# No requiere instalación (es parte de la librería estándar de Python).
import base64

# --- io y requests: Para manejo de datos en memoria y peticiones HTTP ---
# io: Proporciona herramientas para trabajar con flujos de E/S. `io.BytesIO` permite
#     tratar un bloque de bytes (como una imagen descargada) como si fuera un archivo en memoria.
# requests: Es la librería estándar de facto para realizar peticiones HTTP en Python.
#           La usaremos para comunicarnos con la API de mermaid.ink.
# Comando para instalar requests: pip install requests
import io, requests

# --- IPython.display: Para mostrar contenido enriquecido en Notebooks ---
# Estas funciones están diseñadas para renderizar objetos como imágenes directamente
# en entornos como Jupyter Notebook o Google Colab. No son esenciales si el código
# se ejecuta en un script normal.
# Comando para instalar: pip install ipython
from IPython.display import Image, display

# --- Pillow (PIL): Para manipulación de imágenes ---
# Es una poderosa librería para abrir, manipular y guardar múltiples formatos de imagen.
# Aquí la usamos para abrir la imagen PNG recibida desde la API.
# Se importa como `im` por convención.
# Comando para instalar: pip install Pillow
from PIL import Image as im

# --- Matplotlib: Para visualización de datos ---
# Es una librería de gráficos muy popular en Python. En este script, las líneas que la
# usan están comentadas, probablemente eran para pruebas o debugging en un entorno local.
# Comando para instalar: pip install matplotlib
import matplotlib.pyplot as plt

# --- urllib.parse: Librería estándar para manipulación de URLs ---
# Proporciona funciones para manipular y analizar URLs. `urllib.parse.quote` se usa
# para codificar texto de forma que sea seguro incluirlo en una URL (por ejemplo,
# reemplazando espacios con '%20').
# No requiere instalación.
import urllib.parse

def generarGraficoMermaid(graph: str, formato: str = 'PNG') -> tuple:
    """
    Genera una imagen de un diagrama a partir de código Mermaid llamando a la API de mermaid.ink.

    Esta función toma una cadena de texto con sintaxis de Mermaid, la codifica en Base64
    URL-safe y la envía a la API pública de mermaid.ink para renderizarla. Puede devolver
    la imagen en formato PNG, SVG o PDF.

    Args:
        graph (str): La cadena de texto que contiene el código del diagrama Mermaid.
        formato (str, optional): El formato de salida deseado. Puede ser 'PNG', 'SVG', o 'PDF'.
                                 Por defecto es 'PNG'.

    Returns:
        tuple: Una tupla que contiene:
               - img (bytes or PIL.Image.Image or None): Los datos de la imagen generada.
                 Es un objeto de imagen de Pillow para PNG, y bytes para SVG y PDF.
                 Es None si ocurre un error.
               - error (str or None): Un mensaje de error si la generación falla, de lo contrario es None.
    """
    # 1. Codificación del código Mermaid para la URL
    # El texto del diagrama se codifica primero a bytes en formato UTF-8.
    graphbytes = graph.encode("utf8")
    # Esos bytes se codifican a Base64 URL-safe. Esto transforma el código en una cadena de
    # texto segura para ser parte de una URL, un requisito de la API de mermaid.ink.
    base64_bytes = base64.urlsafe_b64encode(graphbytes)
    # Finalmente, los bytes Base64 se decodifican a una cadena de texto ASCII.
    base64_string = base64_bytes.decode("ascii")

    # 2. Inicialización de variables de retorno
    img = None
    error = None
    urlEdit = None # Esta variable no se utiliza en el retorno, pero podría ser para una futura funcionalidad.

    # 3. Petición a la API de mermaid.ink
    # Documentación de la API: https://mermaid.ink/
    try:
        # Se construye la URL de la API dependiendo del formato solicitado.
        if formato == 'PDF':
            # Para PDF, se pide el recurso y se obtiene el contenido binario (`.content`).
            img = requests.get('https://mermaid.ink/pdf/' + base64_string).content
        elif formato == 'SVG':
            # Para SVG, también se obtiene el contenido binario (`.content`), que es el XML del SVG.
            img = requests.get('https://mermaid.ink/svg/' + base64_string).content
        else:  # Por defecto, el formato es PNG
            # Se realiza la petición a la API para obtener una imagen PNG.
            response = requests.get('https://mermaid.ink/img/' + base64_string + '?type=png')
            # El contenido de la respuesta (los bytes de la imagen) se envuelve en un objeto BytesIO
            # para que la librería Pillow pueda leerlo como si fuera un archivo.
            img = im.open(io.BytesIO(response.content))

    except Exception as e:
        # Si algo falla durante la petición (problema de red, error de la API, etc.),
        # se captura la excepción y se formatea un mensaje de error.
        error = f"Error al generar el gráfico Mermaid: {e}"

    # Estas líneas están comentadas, pero si se activaran, usarían Matplotlib para
    # mostrar la imagen generada en una ventana o guardarla en un archivo local.
    # plt.imshow(img)
    # plt.axis('off') # Permite ocultar los ejes del gráfico
    # plt.savefig('image.png', dpi=1200) # Guarda la imagen con alta resolución

    # La función devuelve la imagen generada y la variable de error.
    return img, error