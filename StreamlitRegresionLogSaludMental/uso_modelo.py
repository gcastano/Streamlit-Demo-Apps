import streamlit as st
import pandas as pd
import joblib

# 1. Configuración de la página
st.set_page_config(page_title="Predicción de Salud Mental", page_icon="🧠", layout="wide")

# 2. Cargar el modelo en caché
# @st.cache_resource es un decorador vital en Streamlit.
# Evita que el modelo se vuelva a cargar desde el disco cada vez que el usuario hace clic en algo,
# mejorando drásticamente la velocidad de la app.
@st.cache_resource
def cargar_modelo():
    """
    Carga el modelo entrenado desde el archivo .pkl.
    Returns:
        Pipeline: Objeto scikit-learn entrenado.
    """
    return joblib.load('modelo_salud_mental.pkl')

modelo = cargar_modelo()

# 3. Título y descripción
st.title("🧠 Evaluación de Riesgo de Salud Mental")
st.write("""
Ingrese los datos de estilo de vida y demográficos del paciente en el panel a continuación. 
El sistema calculará la probabilidad de riesgo para **Depresión, Ansiedad, Bipolaridad y PTSD**.
""")
st.caption("Fuente: [Mental Health Dataset](https://www.kaggle.com/datasets/atharvasoundankar/mental-health-and-lifestyle-habits-2019-2024)")

# 4. Crear el formulario de entrada usando columnas
col1, col2 = st.columns(2)

with col1:
    st.subheader("Datos Personales")
    country = st.selectbox("País", ["Brazil", "Australia", "Japan", "Germany", "India", "Canada", "USA"])
    age = st.number_input("Edad", min_value=15, max_value=100, value=30)
    gender = st.selectbox("Género", ["Male", "Female", "Other"])
    
    st.subheader("Hábitos Diarios")
    diet = st.selectbox("Tipo de Dieta", ["Vegetarian", "Vegan", "Balanced", "Junk Food", "Keto"])
    exercise = st.selectbox("Nivel de Ejercicio", ["Low", "Moderate", "High"])

with col2:
    st.subheader("Métricas de Bienestar")
    stress = st.selectbox("Nivel de Estrés", ["Low", "Moderate", "High"])
    sleep = st.slider("Horas de Sueño al día", min_value=0.0, max_value=24.0, value=7.0, step=0.5)
    work_hours = st.slider("Horas de Trabajo por semana", min_value=0, max_value=120, value=40)
    screen_time = st.slider("Horas de Pantalla al día", min_value=0.0, max_value=24.0, value=5.0, step=0.5)
    social_score = st.slider("Interacción Social (0-10)", min_value=0.0, max_value=10.0, value=5.0, step=0.1)
    happiness = st.slider("Puntaje de Felicidad (0-10)", min_value=0.0, max_value=10.0, value=5.0, step=0.1)

st.write("---")

# 5. Botón para predecir
if st.button("Evaluar Riesgo", type="primary", use_container_width=True):
    
    # PANDAS: Creación de DataFrame manual
    # Empaquetamos los inputs del usuario en un diccionario y luego en un DataFrame.
    # Es crucial que los nombres de las columnas coincidan EXACTAMENTE con las usadas en el entrenamiento.
    datos_entrada = pd.DataFrame([{
        'Country': country,
        'Age': age,
        'Gender': gender,
        'Exercise Level': exercise,
        'Diet Type': diet,
        'Sleep Hours': sleep,
        'Stress Level': stress,
        'Work Hours per Week': work_hours,
        'Screen Time per Day (Hours)': screen_time,
        'Social Interaction Score': social_score,
        'Happiness Score': happiness
    }])
    
    # Hacer la predicción de probabilidades
    # .predict_proba() devuelve un array con la probabilidad (0 a 1) para cada clase posible.
    probabilidades = modelo.predict_proba(datos_entrada)[0]
    clases_modelo = modelo.classes_
    
    # Unimos las clases con sus probabilidades en un diccionario
    riesgos = dict(zip(clases_modelo, probabilidades))
    
    # Ordenamos el diccionario de mayor a menor probabilidad
    riesgos = dict(sorted(riesgos.items(), key=lambda item: item[1], reverse=True))

    st.subheader("📊 Probabilidad de Riesgos")

    res_cols = st.columns(5)
    
    # Iteramos sobre los resultados para mostrarlos dinámicamente
    for i, enfermedad in enumerate(riesgos):
        porcentaje = riesgos[enfermedad] * 100
        with res_cols[i]:
            color = "green" if enfermedad == 'Healthy' else "red"
            # Visualización métrica con color condicional
            st.metric(label=f":{color}[**{enfermedad}**]", value=f"{porcentaje:.1f}%")
            st.progress(int(porcentaje) / 100)
            
    # Mostrar la condición más probable
    # .predict() devuelve la clase ganadora directamente
    prediccion_final = modelo.predict(datos_entrada)[0]
    
    if prediccion_final == 'Healthy':
        st.success(f"Diagnóstico principal pronosticado: **Sin Condición (Healthy)**")
    else:
        st.error(f"Diagnóstico principal pronosticado: **{prediccion_final}**")