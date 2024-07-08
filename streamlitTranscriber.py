import streamlit as st
from streamlit_mic_recorder import mic_recorder # pip install streamlit-mic-recorder
from streamlit_mic_recorder import speech_to_text # pip install streamlit-mic-recorder
from streamlit_lottie import st_lottie # pip install streamlit-lottie https://github.com/andfanilo/streamlit-lottie
from st_audiorec import st_audiorec # pip install streamlit-audiorec
import requests
from io import BytesIO

st.set_page_config(
    page_title="Prueba de manejo de audios con Streamlit", #Título de la página
    page_icon="🎙️", # Ícono
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
    

st.header('Controles de Audio en :red-background[Streamlit]')

c1,c2 =  st.columns([2,8])
with c1:
    st_lottie('https://lottie.host/d71ebc94-ead6-4aca-8dc8-0062336fde1f/X8PGsPl8vF.json')
with c2:
    st.subheader('Grabación de Audio con :blue[streamlit_mic_recorder]')
    st.code("from streamlit_mic_recorder import mic_recorder")
    st.markdown("[https://github.com/B4PT0R/streamlit-mic-recorder](https://github.com/B4PT0R/streamlit-mic-recorder)")
    audio = mic_recorder(
        start_prompt="Iniciar grabación",
        stop_prompt="Detener grabación",
        just_once=False,
        use_container_width=False,
        format="wav",
        callback=None,
        args=(),
        kwargs={},
        key='recorder'
    )

    if audio:
        st.audio(audio['bytes'], format='audio/wav') #El formato debe coincidir con el del control de grabación

    st.subheader('Grabación de Audio con :blue[st_audiorec]')
    st.code("from st_audiorec import st_audiorec")
    wav_audio_data = st_audiorec()

    if wav_audio_data is not None:
        st.code('st.audio(data, format="audio/wav", start_time=0, *, sample_rate=None, end_time=None, loop=False, autoplay=False)')
        st.markdown("Documentación [https://docs.streamlit.io/develop/api-reference/media/st.audio](https://docs.streamlit.io/develop/api-reference/media/st.audio)")        
        st.audio(wav_audio_data, format='audio/wav')
st.divider()
c1,c2 =  st.columns([2,8])
with c1:
    st_lottie('https://lottie.host/ae0dbd3e-cc51-4872-a683-972232ba2e55/zzDvaHgUVx.json')
with c2:
    st.subheader('Transcripción de Audio con :blue[speech_to_text]')
    st.code("from streamlit_mic_recorder import speech_to_text")
    st.markdown("[https://github.com/B4PT0R/streamlit-mic-recorder](https://github.com/B4PT0R/streamlit-mic-recorder)")

    text = speech_to_text(
        language='es',
        start_prompt="Iniciar grabación",
        stop_prompt="Detener grabación",
        just_once=False,
        use_container_width=False,
        callback=None,
        args=(),
        kwargs={},
        key='Transcriber'
    )
    st.write(text)

    st.subheader('Convertir la transcripción de Audio a otra voz con :blue[API de Eleven Labs]')
    st.markdown("[https://elevenlabs.io/docs/api-reference/text-to-speech](https://elevenlabs.io/docs/api-reference/text-to-speech)")
    APIKey=st.text_input(':blue-background[API Key] de Eleven Labs',type='password')
    if APIKey:
        parTexto=st.text_area('Texto a convertir',value=text,placeholder="Ingrese un texto a convertir o haga una transcripción de su voz")
        if parTexto:
            audio = textToSpeechElevenLabs(parTexto,APIKey)
            if audio:
                st.audio(audio, format="audio/mpeg",autoplay=True) # El autoplay es para que se reproduzca apenas se cargue el audio
