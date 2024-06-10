import streamlit as st
import pandas as pd
import requests
import json
import time

# Definimos los parámetros de configuración de la aplicación
st.set_page_config(
    page_title="Validación de emails", #Título de la página
    page_icon="📨", # Ícono
)

API_KEY = st.secrets['API_KEY']
headers = {
    'Authorization': f'Bearer {API_KEY}',
}

def validarEmail(email):
    """Función para validar emails usando un servicio de https://testmail.top/

    Args:
        email (str): email que se desea validar

    Returns:
        respuesta(json): Respuesta del servicio que determina si el correo es válido
    """    

    response = requests.get(f'https://api.testmail.top/domain/check?data={email}', headers=headers)    
    respuesta = json.loads(response.content)        
    return respuesta


st.header('📨 Validación de email')
tab1,tab2=st.tabs(['Consulta simple','Consulta Múltiple'])
with tab1:
    email=st.text_input('Email')
    btnValidar=st.button('Validar',key='btnValidar',type='primary')
    if btnValidar:
        respuesta=validarEmail(email)
        st.code(respuesta)
        mensaje=respuesta['message']
        if respuesta['result']:
            st.success(mensaje)
        else:
            st.error(mensaje)
with tab2:

    dfEmails = st.data_editor(pd.DataFrame({'email': ['']}),num_rows='dynamic',use_container_width=True)
    btnValidarMasivo=st.button('Validar',key='btnValidarMasivo',type='primary')
    if btnValidarMasivo:
        progress_text = "Validando emails"
        barraProgreso = st.progress(0, text=progress_text)
        maxFilas =len(dfEmails.dropna())
        
        for index,fila in dfEmails.dropna().iterrows():
            progress_text = f"Validando: {fila['email']}"
            porcentaje=index/maxFilas
            barraProgreso.progress(porcentaje, text=progress_text)
            respuesta = validarEmail(fila['email'])
            mensaje=respuesta['message']
            if respuesta['result']:
                estado='Ok'
            else:
                estado='Error'
            dfEmails.loc[index,'Estado']=estado
            dfEmails.loc[index,'Mensaje']=mensaje
        time.sleep(2)            
        barraProgreso.empty()
        st.dataframe(dfEmails,hide_index=True)
