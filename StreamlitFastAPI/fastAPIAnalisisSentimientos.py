# https://fastapi.tiangolo.com/
from fastapi import FastAPI, HTTPException # pip install fastapi uvicorn
from pydantic import BaseModel # pip install pydantic

# Instala la librería google-generativeai con el comando:
# pip install -q -U google-generativeai
import google.generativeai as genai 

# Librería para leer archivos de configuración
# Documentación: https://docs.python.org/3/library/configparser.html
# Instala con: pip install configparser
from configparser import ConfigParser 


descripcion = """

Utiliza el modelo generativo de Google para realizar el análisis de sentimiento.

#### evaluar_sentimiento
Esta API permite analizar el sentimiento de un texto proporcionado por el usuario. El usuario envía un comentario y la API responde si el sentimiento del comentario es POSITIVO, NEGATIVO o NEUTRAL.

#### generar_comentario_sentimiento
Esta API permite generar un comentario corto para un producto o servicio con el sentimiento entregado por el usuario.

"""

# Crea una instancia de la aplicación FastAPI
app = FastAPI(title="API de Análisis de Sentimientos",
              description=descripcion)

# Define el modelo de datos para la solicitud de sentimiento
class SentimientoRequest(BaseModel):
    texto: str    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "texto": "Este producto es justo lo que necesitaba. ¡Estoy muy feliz de haberlo encontrado!",                    
                }
            ]
        }
    }

# Define el modelo de datos para la respuesta de sentimiento
class SentimientoResponse(BaseModel):
    sentimiento: str
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "sentimiento": "POSITIVO",                    
                }
            ]
        }
    }

# Define el modelo de datos para la respuesta de comentario
class ComentarioResponse(BaseModel):
    comentario: str
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "comentario": "Este producto es justo lo que necesitaba. ¡Estoy muy feliz de haberlo encontrado!",                    
                }
            ]
        }
    }

descripcionMetodo ="""
Evalúa el sentimiento de un texto proporcionado por el usuario.
Retorna el sentimiento del texto como:
* POSITIVO
* NEGATIVO 
* NEUTRAL
"""

# Define la ruta para evaluar el sentimiento
@app.post("/evaluarSentimiento", response_model=SentimientoResponse,description=descripcionMetodo)
async def evaluar_sentimiento(request: SentimientoRequest):
    # Verifica si el texto está vacío
    if request.texto == "":
        raise HTTPException(status_code=400,detail="El texto no puede estar vacío")
    # Crea una instancia de ConfigParser para leer el archivo de configuración
    config = ConfigParser()
    # Leyendo el archivo de configuración seleccionado
    config.read("config.ini")
    # Obtiene la API KEY de Google desde el archivo de configuración
    GOOGLE_API_KEY = config["APIAccess"]["GOOGLE_API_KEY"]
    # Define el prompt del sistema para el modelo generativo
    systemPrompt="""
    Eres un experto analizando el sentimiento de textos entregados, 
    el usuario te va a entregar un comentario y 
    vas a responder si su sentimiento es POSITIVO, NEGATIVO o NEUTRAL 
    solo retornar el sentimiento, no generar markdown
    """
    # Configura la API KEY para la librería google-generativeai
    genai.configure(api_key = GOOGLE_API_KEY)
    # Define el prompt para el modelo
    prompt=[
            {
            "role": "user",
            "parts": [
                request.texto,
            ],
            }]
    # Carga el modelo generativo Gemini
    model = genai.GenerativeModel('gemini-1.5-pro-latest',system_instruction=systemPrompt)
    # Genera la respuesta del modelo
    response = model.generate_content(prompt)
    # Limpia la respuesta eliminando saltos de línea
    resultado = response.text.replace("\n","")
    # Retorna la respuesta como un objeto SentimientoResponse
    return SentimientoResponse(sentimiento=resultado)

# Define la ruta para generar un comentario con un sentimiento específico
@app.get("/comentario/{sentimiento}")
async def generar_comentario_sentimiento(sentimiento):
    # Valida que el sentimiento sea POSITIVO, NEGATIVO o NEUTRAL
    if  sentimiento.upper() not in ["POSITIVO","NEGATIVO","NEUTRAL"]:
        raise HTTPException(status_code=400,detail="Debe indicar un sentimiento POSITIVO, NEGATIVO o NEUTRAL")
    # Lee la configuración de la API KEY
    config = ConfigParser()
    config.read("config.ini")
    GOOGLE_API_KEY = config["APIAccess"]["GOOGLE_API_KEY"]
    # Define el prompt para el modelo
    systemPrompt="""
    Genera un ejemplo de comentario corto para un producto o servicio con el sentimiento entregado por el usuario
    """
    genai.configure(api_key = GOOGLE_API_KEY)
    prompt=[
            {
            "role": "user",
            "parts": [
                sentimiento,
            ],
            }]
    # Carga el modelo y genera el comentario.
    model = genai.GenerativeModel('gemini-1.5-pro-latest',system_instruction=systemPrompt)
    response = model.generate_content(prompt)
    resultado = response.text.replace("\n","")
    return ComentarioResponse(comentario=resultado)