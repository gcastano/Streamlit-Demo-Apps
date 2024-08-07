from youtube_transcript_api import YouTubeTranscriptApi # https://github.com/jdepoix/youtube-transcript-api
from urllib.parse import urlparse, parse_qs
from groq import Groq # https://github.com/groq/groq-python
import requests
import streamlit as st
from io import BytesIO

st.set_page_config(
    page_title="Generador de resumen de videos", #Título de la página
    page_icon="🆕", # Ícono
    layout="wide",
    initial_sidebar_state="expanded" # Definimos si el sidebar aparece expandido o colapsado
)

def textToSpeechElevenLabs(text,APIKey):
    """Función que usa la API de Eleven Labs para tomar un texto y retornar un audio en bytes
       usando el método de Text to Speech
       https://elevenlabs.io/docs/api-reference/text-to-speech
    Args:
        text (str): Texto que se desea convertir a audio
        APIKey (str): API Key de la cuenta de Eleven Labs

    Returns:
        bytes: Audio en formato mpeg
    """    
    CHUNK_SIZE = 1024
    url = "https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgDQGcFmaJgB" 
    
    # El código pNInz6obpgDQGcFmaJgB corresponde a la voz a utilizar

    # Encabezado del request
    headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": APIKey
    }

    # Datos del request
    data = {
    "text": text,
    "model_id": "eleven_multilingual_v2",
    "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.5
    }
    }

    response = requests.post(url, json=data, headers=headers)
    
    # Crear un objeto BytesIO para contener los datos de audio en la memoria
    audio_stream = BytesIO()
    
    # Escribe cada parte de los datos de audio en la transmisión
    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
        if chunk:
            audio_stream.write(chunk)
    
    # Restablecer la posición de la transmisión al principio
    audio_stream.seek(0)
    
    # Devuelve la transmisión para un uso posterior
    return audio_stream

st.header('Generador de resúmenes de videos de :red[YouTube]')

# Pedimos la URL del video
with st.form('parametros'):
    parmVideo = st.text_input("URL del video de Youtube")
    # Solicitamos el modelo para generar el post
    modelos=['llama-3.1-70b-versatile','llama-3.1-8b-instant','llama3-groq-70b-8192-tool-use-preview','llama3-groq-8b-8192-tool-use-preview','llama3-70b-8192','llama3-8b-8192','mixtral-8x7b-32768','gemma-7b-it','gemma2-9b-it']
    parmModelo=st.selectbox('Modelo LLM',options=modelos)
    APIKeyElevenLabs=st.text_input(':blue-background[API Key] de Eleven Labs',type='password')
    btnGenerar =st.form_submit_button('Generar')
if btnGenerar:
    if parmModelo and parmVideo:
        urlVideo = parmVideo

        # Extraemos el id que está en la variable v del query string
        parsed_url = urlparse(urlVideo)
        parse_qs(parsed_url.query)

        video_id=parse_qs(parsed_url.query)['v'][0]

        # Obtenemos las transcripciones del video tanto en inglés como en español
        transcripcion = YouTubeTranscriptApi.get_transcript(video_id,languages=['en','es'])

        # Concatenamos la transcripción
        transcripcionTexto=''
        for frase in transcripcion:
            transcripcionTexto =transcripcionTexto + frase['text'] + " "

        # Cargamos la API de Groq
        apikey=st.secrets["GROQ_API"]

        # Cargamos el cliente de Groq
        client = Groq(api_key=apikey)
        completion = client.chat.completions.create(
            model=parmModelo,
            messages=[
                {
                    "role": "system",
                    "content": "Vas a ser un periodista experto en redacción para medios digitales, enfocado en ser concreto y consiso, cuando el usuario te envíe un texto llamado transcripción de video, vas a sacar un resumen en español de máximo 1500 caracteres, con las ideas, fechas, nombres y cifras más importantes"
                },
                {
                    "role": "user",
                    "content": transcripcionTexto
                }
            ],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )
        resumenVideo =''
        for chunk in completion:
            if chunk.choices[0].delta.content:
                resumenVideo= resumenVideo+ chunk.choices[0].delta.content
        cantPalabrasTranscr=len(transcripcionTexto.strip())
        cantPalabrasResumen=len(resumenVideo.strip())
        c1,c2=st.columns(2)
        with c1:
            st.metric('Palabras Transcripción',f'{cantPalabrasTranscr:,.0f}')
        with c2:
            st.metric('Palabras Resumen',f'{cantPalabrasResumen:,.0f}')
        st.markdown(resumenVideo)
        if APIKeyElevenLabs:        
            audio = textToSpeechElevenLabs(resumenVideo,APIKeyElevenLabs)
            if audio:
                st.audio(audio, format="audio/mpeg",autoplay=True) # El autoplay es para que se reproduzca apenas se cargue el audio
    else:
        st.warning("Ingrese la URL del video de YouTube y seleccione el modelo LLM para generar el resumen")