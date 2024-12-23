# Importamos las librerías necesarias
import streamlit as st  # Librería para crear aplicaciones web interactivas
import pandas as pd  # Librería para manipulación y análisis de datos
import plotly.express as px  # Librería para crear gráficos interactivos
import requests  # Librería para hacer solicitudes HTTP
import json  # Librería para trabajar con datos en formato JSON

# Definimos los parámetros de configuración de la aplicación
st.set_page_config(
    page_title="Monitoreo de Metricas", #Título de la página
    page_icon="📊", # Ícono
    layout="wide", # Forma de layout ancho o compacto
    initial_sidebar_state="expanded" # Definimos si el sidebar aparece expandido o colapsado
)

# Función para enviar un mensaje de WhatsApp usando la API de 2Chat
def enviarMensajeWhatsApp(mensaje):
    """
    Envía un mensaje de WhatsApp utilizando la API de 2Chat.
    Args:
        mensaje (str): El contenido del mensaje a enviar.
    Returns:
        None
    """
    url = "https://api.p.2chat.io/open/whatsapp/send-message"

    payload = json.dumps({
      "to_number": st.secrets["telefonoMonitoreo"], # Número de teléfono de destino
      "from_number": st.secrets["telefonoOrigen"], # Número de teléfono de origen
      "text": mensaje,      
    })
    headers = {
      'X-User-API-Key': st.secrets["2ChatAPIKey"], # API Key para autenticación
      'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)    

# Función para generar una alerta si el valor de la medida está fuera del rango
def generarAlerta(valorMedida, parMinMonitoreo, parMaxMonitoreo):
    """
    Genera una alerta si el valor de la medida está fuera de los parámetros de monitoreo y envía un mensaje de WhatsApp.

    Args:
        valorMedida (float): El valor de la medida a evaluar.
        parMinMonitoreo (float): El valor mínimo permitido para la medida.
        parMaxMonitoreo (float): El valor máximo permitido para la medida.

    Returns:
        None
    """
    if valorMedida < parMinMonitoreo:
        mensaje = f"🔴 *ALERTA:* El valor de la medida es {valorMedida} y es menor que el valor mínimo de {parMinMonitoreo}"
    elif valorMedida > parMaxMonitoreo:
        mensaje = f"🔴 *ALERTA:* El valor de la medida es {valorMedida} y es mayor al valor máximo de {parMaxMonitoreo}"        
    enviarMensajeWhatsApp(mensaje)

# Configuración de los parámetros en la barra lateral
with st.sidebar:
    parMinMonitoreo = st.number_input("Rango Minimo", value=15)
    parMaxMonitoreo = st.number_input("Rango Maximo", value=27)
    parVentanaDatos = st.number_input("Ventana de Datos", value=15)
    parSegundosActualizacion = st.number_input("Segundos de Actualización", value=5)

st.header("Monitoreo de Métricas")  # Título de la aplicación

# Inicialización del estado de la sesión
if "ultimaFecha" not in st.session_state:
    st.session_state.ultimaFecha = None
if "ultimoValorEnAlerta" not in st.session_state:
    st.session_state.ultimoValorEnAlerta = False

# Función para actualizar los datos periódicamente
@st.fragment(run_every=parSegundosActualizacion)
def ActualizarDatos(parMinMonitoreo, parMaxMonitoreo, parVentanaDatos):
    gsheetid = '10bSRhhhD4ZibrRjUZyIWu-Uo2f5dH6ZeL8RrlKHKbQ8'
    sheetid = '0'
    url = f'https://docs.google.com/spreadsheets/d/{gsheetid}/export?format=csv&gid={sheetid}&format'
    try:
        dfDatos = pd.read_csv(url).tail(parVentanaDatos) # Cargar los datos de la hoja de cálculo
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return

    
    # Crear una gráfica de línea con los datos
    fig = px.line(dfDatos, x='FechaHora', y='Medida', markers=True)  # Crear la gráfica de línea con marcadores
    fig.add_hrect(y0=parMinMonitoreo, y1=parMaxMonitoreo, fillcolor="#DAFFFB", line_color="rgba(0,0,0,0)", opacity=0.5)  # Añadir una banda horizontal para el rango permitido
    fig.add_hline(y=parMinMonitoreo, line_dash="dot", annotation_text="Minimo", annotation_position="bottom right")  # Añadir una línea horizontal para el valor mínimo
    fig.add_hline(y=parMaxMonitoreo, line_dash="dot", annotation_text="Maximo", annotation_position="bottom right")  # Añadir una línea horizontal para el valor máximo
    fig.update_yaxes(rangemode="tozero")  # Asegurar que el eje y comience en cero
    st.plotly_chart(fig, use_container_width=True)  # Mostrar la gráfica en la aplicación Streamlit

    # Obtener el último valor de la medida y la última fecha
    valorMedida = dfDatos['Medida'].iloc[-1]
    ultimaFecha = dfDatos['FechaHora'].iloc[-1]

    # Verificar si hay una nueva medida y generar una alerta si está fuera del rango
    # Validamos que la última fecha sea diferente a la última fecha almacenada en el estado de la sesión
    if ultimaFecha != st.session_state.ultimaFecha:
        st.session_state.ultimaFecha = ultimaFecha  # Actualizar la última fecha en el estado de la sesión
        
        # Verificar si el valor de la medida está fuera del rango permitido
        if valorMedida < parMinMonitoreo or valorMedida > parMaxMonitoreo:
            st.session_state.ultimoValorEnAlerta = True  # Marcar que hay una alerta activa
            generarAlerta(valorMedida, parMinMonitoreo, parMaxMonitoreo)  # Generar la alerta y enviar el mensaje de WhatsApp
        
        # Si el valor de la medida vuelve al rango normal y había una alerta activa, enviar mensaje de resolución
        else:
            if st.session_state.ultimoValorEnAlerta:
                st.session_state.ultimoValorEnAlerta = False  # Marcar que la alerta ha sido resuelta
                mensaje = f"✅ *ALERTA RESUELTA:* El valor de la medida ha vuelto al rango normal."
                enviarMensajeWhatsApp(mensaje)  # Enviar el mensaje de resolución de alerta
    
# Llamar a la función para actualizar los datos
ActualizarDatos(parMinMonitoreo, parMaxMonitoreo, parVentanaDatos)
