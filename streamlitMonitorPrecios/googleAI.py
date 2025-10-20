# --- LIBRERÍAS Y DEPENDENCIAS ---
# Se importan las librerías necesarias para el proyecto.

# Librería: google-generativeai
# Propósito: Es el SDK oficial de Google para interactuar con sus modelos de IA generativa, como Gemini.
# Permite configurar y enviar prompts, y recibir las respuestas del modelo.
# Comando de instalación: pip install google-generativeai
from google import genai
from google.genai import types

# Librería: json
# Propósito: Viene incluida en la instalación estándar de Python. Es fundamental para trabajar con datos en formato JSON 
# (JavaScript Object Notation). Se usa aquí para convertir la respuesta de texto del modelo (que será un string JSON) 
# a un diccionario de Python.
# Comando de instalación: (No requiere, es parte de la librería estándar de Python)
import json

# Librería: streamlit
# Propósito: Framework para crear aplicaciones web interactivas de forma rápida y sencilla usando solo Python. 
# En este código, se utiliza específicamente 'st.secrets' para gestionar de forma segura las claves de API 
# cuando la aplicación se despliega en Streamlit Cloud.
# Comando de instalación: pip install streamlit
import streamlit as st
import re


def generateData(enlace):
    """
    Toma un enlace web de un producto, lo envía al modelo Gemini Pro de Google
    y le solicita que extraiga información específica en un formato JSON estructurado.

    Esta función configura una llamada a la API de Gemini con instrucciones muy precisas
    para forzar al modelo a devolver un JSON con un esquema definido, incluyendo
    el nombre del producto, la tienda, el precio, el peso y el precio por gramo.

    Args:
        enlace (str): Una cadena de texto que contiene la URL del producto a analizar.

    Returns:
        dict: Un diccionario de Python con la información extraída del producto,
              convertido desde la respuesta JSON del modelo.
    """
    
    # Inicializa el cliente de la API de Google GenAI.
    # Utiliza `st.secrets` para acceder de forma segura a la clave de la API (almacenada como "GEMINI_API")
    # cuando la aplicación está desplegada en un entorno como Streamlit Cloud.
    client = genai.Client(
        api_key=st.secrets["GEMINI_API"],
    )

    # Define el modelo de IA que se utilizará para la tarea. 
    # 'gemini-2.5-pro' es un modelo avanzado y potente. Se deja comentada la opción
    # 'gemini-flash-latest' como una alternativa que podría ser más rápida pero menos potente.
    model = "gemini-flash-latest"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f"""{enlace}"""),
            ],
        ),
    ]
    tools = [
        types.Tool(url_context=types.UrlContext()),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=0,
        response_schema=genai.types.Schema(
            type = genai.types.Type.OBJECT,
            required = ["Producto", "Tienda", "Precio", "Peso", "PrecioGramo", "Enlace"],
            properties = {
                "Producto": genai.types.Schema(
                    type = genai.types.Type.STRING,
                ),
                "Tienda": genai.types.Schema(
                    type = genai.types.Type.STRING,
                ),
                "Precio": genai.types.Schema(
                    type = genai.types.Type.NUMBER,
                ),
                "Peso": genai.types.Schema(
                    type = genai.types.Type.NUMBER,
                ),
                "PrecioGramo": genai.types.Schema(
                    type = genai.types.Type.NUMBER,
                ),
                "Enlace": genai.types.Schema(
                    type = genai.types.Type.STRING,
                ),
            },
        ),
        thinking_config = types.ThinkingConfig(
            thinking_budget=0,
        ),
        tools=tools,
        system_instruction=[
            types.Part.from_text(text="""**Situation**
Servicio de extracción de información de productos en línea para generar un formato JSON estructurado con detalles específicos.

**Task**
Analizar un enlace web de un producto y extraer de manera precisa la información solicitada.

**Objective**
Crear un JSON estandarizado con los datos fundamentales del producto para facilitar su identificación y comparación.

**Knowledge**
- El enlace será proporcionado directamente por el usuario
- La información debe ser extraída directamente de la página web del producto
- El JSON debe tener exactamente los 4 campos especificados
- La información debe ser lo más precisa posible

**Instrucciones Específicas**
El asistente debe:
1. Procesar el enlace web proporcionado si no puede retornar \"\"
2. Identificar con precisión el nombre del producto
3. Determinar el nombre de la tienda donde se encuentra el producto
4. Extraer el precio exacto mostrado en la página
5. Devolver la información en el formato JSON estructurado:
{
    \\\"Producto\\\": \\\"Nombre del producto\\\",
    \\\"Tienda\\\": \\\"Nombre de la tienda\\\", 
    \\\"Precio\\\": \\\"Precio que aparece en la página\\\",
    \\\"Peso\\\": \\\"Peso en gramos\\\",
    \\\"PrecioGramo\\\": \\\"Dividir el precio por el peso en gramos\\\",
    \\\"Enlace\\\": \\\"Enlace entregado para hacer la consulta\\\"
}"""),
        ],
    )
    
    # Variable para almacenar la respuesta completa.
    respuesta=""
    
    # Realiza la llamada a la API del modelo en modo 'streaming'.
    # Esto significa que la respuesta se recibe en fragmentos (chunks) a medida que el modelo la genera,
    # en lugar de esperar la respuesta completa al final.
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        # Concatena cada fragmento de texto recibido para reconstruir la respuesta JSON completa.
        if chunk.text:
            respuesta += chunk.text
        else:
            continue
    
    respuesta = respuesta.strip()
    # Usa una expresión regular para extraer el bloque JSON de la respuesta completa.
    codigo_json = re.search(r"{[\w\W]+?}", respuesta, re.DOTALL)    
    # Una vez recibida la respuesta completa en formato de texto JSON, `json.loads()` la convierte (parsea)
    # en un diccionario de Python, que es mucho más fácil de manejar en el resto del programa.
    return json.loads(codigo_json.group(0))