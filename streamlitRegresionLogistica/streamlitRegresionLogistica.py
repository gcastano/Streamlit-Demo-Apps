# ==============================================================================
# LIBRERÍAS Y DEPENDENCIAS
# ==============================================================================

# ------------------------------------------------------------------------------
# Streamlit: Una librería de Python que permite crear y compartir aplicaciones
# web interactivas para proyectos de Machine Learning y Ciencia de Datos de
# forma rápida y sencilla, sin necesidad de conocimientos de frontend.
#
# Para instalar Streamlit, ejecuta en tu terminal:
# pip install streamlit
# ------------------------------------------------------------------------------
import streamlit as st

# ------------------------------------------------------------------------------
# Pandas: Es una librería fundamental para la manipulación y análisis de datos en
# Python. Proporciona estructuras de datos como el DataFrame, que es esencial
# para trabajar con datos tabulares de manera eficiente.
#
# Para instalar Pandas, ejecuta en tu terminal:
# pip install pandas
# ------------------------------------------------------------------------------
import pandas as pd

# ------------------------------------------------------------------------------
# Pickle: Es un módulo de la librería estándar de Python utilizado para serializar
# y deserializar objetos de Python. "Serializar" significa convertir un objeto
# en un flujo de bytes que puede ser guardado en un archivo o transmitido por
# una red. Esto es muy común para guardar modelos de Machine Learning entrenados.
#
# No necesita instalación, ya que viene con Python.
# ------------------------------------------------------------------------------
import pickle

# ==============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ==============================================================================

# st.set_page_config() configura los metadatos y el layout de la aplicación web.
# - layout="wide": Hace que el contenido ocupe todo el ancho de la pantalla.
# - page_title: Establece el título que aparece en la pestaña del navegador.
st.set_page_config(layout="wide", page_title="Determinación de Churn en Clientes de Telecomunicaciones")

# ==============================================================================
# FUNCIONES
# ==============================================================================

def cargar_modelo():
    """
    Carga el modelo de Machine Learning desde un archivo .pkl.

    Esta función abre el archivo 'modeloChurn.pkl' en modo de lectura binaria ('rb')
    y utiliza la librería pickle para deserializar el objeto del modelo,
    cargándolo en memoria para su uso posterior en la aplicación.

    Returns:
        model: El objeto del modelo de Machine Learning cargado.
    """
    # Se abre el archivo en modo 'rb' (read binary), necesario para archivos pickle.
    with open("modeloChurn.pkl", 'rb') as file:
        # pickle.load() deserializa el archivo y lo convierte de nuevo en un objeto de Python.
        modelo = pickle.load(file)
    return modelo

# Se llama a la función para cargar el modelo al iniciar la aplicación.
# El modelo se guarda en la variable 'modelo' para ser reutilizado.
modelo = cargar_modelo()

def predecir_churn(modelo, datos_cliente, umbral=0.5):
    """
    Realiza una predicción de churn para un cliente dado utilizando el modelo cargado.

    Args:
        modelo (model): El modelo de Machine Learning entrenado.
        datos_cliente (dict): Un diccionario con los datos del cliente a evaluar.
        umbral (float): El umbral de probabilidad para clasificar a un cliente como "Churn".
                         Por defecto es 0.5 (50%).

    Returns:
        tuple: Una tupla conteniendo:
            - prediccion (int): El resultado de la predicción (1 para Churn, 0 para No Churn).
            - probabilidad (float): La probabilidad asociada a la predicción realizada.
            - prediction_probbase (array): Un array con las probabilidades para ambas clases [No Churn, Churn].
    """
    # Transformación de datos: Convierte el diccionario de Python con los datos del cliente
    # en un DataFrame de Pandas. Los modelos de Scikit-learn esperan recibir los datos de
    # entrada en este formato (o un array de NumPy).
    df_cliente = pd.DataFrame(datos_cliente)

    # El método .predict() devuelve la clase predicha (0 o 1) directamente.
    prediccion = modelo.predict(df_cliente)

    # El método .predict_proba() devuelve las probabilidades para cada clase.
    # El slicing [::,1] selecciona la probabilidad de la clase positiva (Churn, clase 1).
    prediction_probSi = modelo.predict_proba(df_cliente)[::,1]

    # Se obtienen las probabilidades base para ambas clases [P(No Churn), P(Churn)].
    prediction_probbase = modelo.predict_proba(df_cliente)

    # Se aplica el umbral de decisión personalizado.
    if prediction_probSi >= umbral:
        # Si la probabilidad de Churn supera el umbral, se confirma la predicción como 1.
        prediccion = 1
        probabilidad = prediction_probSi[0] # Se extrae el valor de la probabilidad.
    else:
        # Si no supera el umbral, la predicción es 0 (No Churn).
        prediccion = 0
        # La probabilidad mostrada será la de "No Churn", que es 1 menos la de "Churn".
        probabilidad = 1 - prediction_probSi[0]
        
    return prediccion, probabilidad, prediction_probbase

# ==============================================================================
# CONSTRUCCIÓN DE LA INTERFAZ DE USUARIO (UI) CON STREAMLIT
# ==============================================================================

# Título principal de la aplicación web.
st.title("Determinación de Churn en Clientes de Telecomunicaciones")

# Se crean dos columnas para organizar la interfaz: una más ancha para la entrada de datos (c1)
# y una más estrecha para mostrar los resultados (c2).
c1, c2 = st.columns([4, 2])

# Contenido de la primera columna (entrada de datos).
with c1:    
    st.header(":material/article_person: Ingrese los datos del cliente:")
    # Se dividen los campos de entrada en dos subcolumnas para un mejor diseño.
    cols = st.columns(2)
    with cols[0]:
        # Creación de widgets interactivos para que el usuario ingrese los datos del cliente.
        call_failure = st.number_input("Call Failure (Número de fallos en llamadas)", min_value=0, step=1)
        complaints = st.selectbox("Complaints (¿Ha presentado quejas?)", options=[0, 1], format_func=lambda x: "Sin queja" if x == 0 else "Con queja")
        subscription_length = st.number_input("Subscription Length (Meses totales de suscripción)", min_value=0, step=1)
        charge_amount = st.slider("Charge Amount (0: Monto más bajo, 9: Monto más alto)", min_value=0, max_value=9, step=1)
        seconds_of_use = st.number_input("Seconds of Use (Segundos totales de llamadas)", min_value=0, step=1)
        frequency_of_use = st.number_input("Frequency of use (Número total de llamadas)", min_value=0, step=1)
        frequency_of_sms = st.number_input("Frequency of SMS (Número total de mensajes de texto)", min_value=0, step=1)
    with cols[1]:
        distinct_called_numbers = st.number_input("Distinct Called Numbers (Números distintos llamados)", min_value=0, step=1)
        age_group = st.slider("Age Group (1: Más joven, 5: Más mayor)", min_value=1, max_value=5, step=1)
        tariff_plan = st.selectbox("Tariff Plan", options=[1, 2], format_func=lambda x: "Pago por uso" if x == 1 else "Contrato")
        status = st.selectbox("Status", options=[1, 2], format_func=lambda x: "Activo" if x == 1 else "Inactivo")
        age = st.number_input("Age (Edad del cliente)", min_value=0, step=1)
        customer_value = st.number_input("Customer Value (Valor calculado del cliente)", min_value=0.0, step=0.01)

    # Se recopilan todos los datos ingresados por el usuario en un diccionario de Python.
    # La estructura es {nombre_columna: [valor]}, ya que Pandas espera una lista de valores por cada clave.
    datos = {
        "Call  Failure": [call_failure],
        "Complains": [complaints],
        "Subscription  Length": [subscription_length],
        "Charge  Amount": [charge_amount],
        "Seconds of Use": [seconds_of_use],
        "Frequency of use": [frequency_of_use],
        "Frequency of SMS": [frequency_of_sms],
        "Distinct Called Numbers": [distinct_called_numbers],
        "Age Group": [age_group],
        "Tariff Plan": [tariff_plan],
        "Status": [status],
        "Age": [age],
        "Customer Value": [customer_value],
    }    

# Contenido de la segunda columna (resultados de la predicción).
with c2:
    # Se usa un contenedor con borde para agrupar visualmente los resultados.
    with st.container(border=True):
        st.header(":material/search_check_2: Resultado de la predicción:")

        # Slider para que el usuario ajuste el umbral de decisión dinámicamente.
        umbral = st.slider("Umbral de decisión para Churn", min_value=0.0, max_value=100.0, value=50.0, step=1.0, format="%0.1f %%")

        # Se llama a la función de predicción con los datos del usuario y el umbral seleccionado.
        # El umbral se divide por 100 para convertirlo a un valor entre 0 y 1.
        prediccion, probabilidad, prediction_prob = predecir_churn(modelo, datos, umbral / 100)

        # Se muestra un mensaje de error (rojo) o éxito (verde) según el resultado.
        if prediccion == 1:
            st.error("El cliente tiene alta probabilidad de dejar la compañía (Churn)", icon=":material/warning:")
        else:
            st.success("El cliente tiene baja probabilidad de dejar la compañía (No Churn)", icon=":material/check_circle:")
        
        # Muestra una barra de progreso para visualizar la probabilidad de la clase predicha.
        st.progress(probabilidad, text=f"Probabilidad: **{probabilidad:.2%}** de " + ("Churn" if prediccion == 1 else "No Churn"))

        # Transformación de datos: Se crea un DataFrame de Pandas para mostrar las probabilidades
        # de ambas clases ("No Churn" y "Churn") de forma clara y tabular.
        dfPrediccionProb = pd.DataFrame(prediction_prob, columns=["No Churn", "Churn"])
        
        # Transformación de datos: Se aplica la función .applymap() para formatear cada celda del
        # DataFrame como un porcentaje con dos decimales.
        dfPrediccionProb = dfPrediccionProb.applymap(lambda x: f"{x:.2%}")
        
        # Se muestra el DataFrame en la aplicación.
        # - use_container_width=True: El DataFrame ocupa todo el ancho de su columna.
        # - hide_index=True: Oculta el índice numérico del DataFrame para una vista más limpia.
        st.dataframe(dfPrediccionProb, use_container_width=True, hide_index=True)