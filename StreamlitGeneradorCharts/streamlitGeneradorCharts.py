# ==========================================
# INSTRUCCIONES DE INSTALACIÓN
# ==========================================
# Para ejecutar este proyecto, necesitas instalar las siguientes librerías
# ejecutando este comando en tu terminal:
# pip install mistralai streamlit pandas plotly streamlit_lottie

import json # JSON: Librería estándar para trabajar con datos en formato JSON (parsear y generar).
import pandas as pd  # Pandas: Librería estándar para manipulación y análisis de datos (DataFrames).
import streamlit as st  # Streamlit: Framework para crear aplicaciones web de data science rápidamente en Python.
from mistralai import Mistral  # MistralAI: Cliente oficial para interactuar con los modelos LLM de Mistral.
import plotly.express as px  # Plotly Express: Interfaz de alto nivel para crear gráficos interactivos fácilmente.
from streamlit_lottie import st_lottie  # Streamlit Lottie: Permite mostrar animaciones Lottie en Streamlit para mejorar la experiencia de usuario (UX).

# Configuración de la página de Streamlit
# layout="wide" permite aprovechar todo el ancho de la pantalla para mostrar los gráficos.
st.set_page_config(layout="wide", page_title="Generador de Gráficos con IA")

def generate(csv_data):
    """
    Envía un fragmento de los datos CSV al modelo de IA (Mistral) para solicitar
    la generación de código Python que cree gráficos con Plotly.

    Args:
        csv_data (str): Cadena de texto que contiene las primeras filas del CSV en formato raw.

    Returns:
        str: Una respuesta en formato texto (JSON string) que contiene una lista
             con el código de los gráficos y sus explicaciones.
    """
    
    # Por seguridad, las API keys no deben estar "hardcoded" (escritas directamente) en el código.
    # Streamlit maneja secretos de forma segura usando st.secrets o variables de entorno.
    client = Mistral(
        api_key=st.secrets["MISTRAL_API_KEY"]
    )

    # Definimos el modelo a utilizar. 'mistral-large-latest' es un modelo potente capaz de razonamiento complejo.
    model = "mistral-large-latest"
    
    # Instrucción del Sistema (Prompt Engineering):
    # Le damos un rol al modelo (Analista de datos) y definimos estrictamente el formato de salida (JSON).
    # Esto es crucial para poder procesar la respuesta programáticamente después.
    system_instruction = """

Eres un analista de datos experto en encontrar insights importantes de un set de datos. Recibirás un set de datos en CSV el cual analizarás y generarás 12 gráficas con código en python usando Plotly Express. 
En cada bloque de código solo generar la creación de gráficos con el nombre fig sin imports. Para los gráficos basados en una fecha vas a ordenar los datos primero por este campo.
Agrupa los datos por los campos categóricos y por la fecha cuando sea necesario. Para cada gráfico, también debes generar una breve explicación de los insights encontrados y por qué es relevante.
Retornarás un array del siguiente estilo:
[
{
chart:"código python para generar el gráfico de plotly Express",
explanation:"explicación de los insights encontrados en el gráfico y por qué es relevante"
}
]
No incluyas explicaciones ni texto adicional, solo el JSON.
"""
    
    # Mensaje del usuario: Le pasamos los datos reales para que trabaje sobre ellos.
    user_message = f"""Aquí están las primeras 10 filas del CSV:\n\n{csv_data}"""
    
    # Llamada a la API de Mistral
    # response_format={ "type": "json_object" } fuerza al modelo a devolver un JSON válido.
    response = client.chat.complete(
        model=model,
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_message},
        ],
    )

    # Retornamos solo el contenido del mensaje de la IA
    return response.choices[0].message.content


def main():
    """
    Función principal que controla el flujo de la aplicación Streamlit.
    1. Carga el archivo.
    2. Muestra los datos.
    3. Gestiona la llamada a la IA y la ejecución del código generado.
    """
    st.title(":material/robot_2: Creador de Gráficos con IA")
    
    # Widget de carga de archivos: permite al usuario subir su propio CSV.
    uploaded_file = st.file_uploader("Carga un archivo CSV", type=["csv"])
    
    if uploaded_file is not None:
        # Pandas lee el archivo CSV y lo convierte en un DataFrame (tabla manipulable).
        df = pd.read_csv(uploaded_file)
        

        
        # Preparamos un diccionario de variables globales para la función exec().
        # Esto permite que el código generado por la IA tenga acceso al dataframe 'df' y a la librería 'px'.
        input_globals = {'df': df, "px": px,"pd": pd}
        
        # Visualización de datos crudos para que el usuario verifique la carga.
        st.write("Primeras 10 filas del CSV:")
        with st.expander("Mostrar datos crudos"):
            st.dataframe(df.head(10))
        
        if st.button("Generar Gráficos"):
            # Optimización: Solo enviamos las primeras 10 filas al LLM para ahorrar tokens y dinero.
            # Convertimos el DataFrame a string CSV.
            csv_data = df.head(10).to_csv(index=False)
            animacion=st.empty()
            # Spinner visual mientras esperamos la respuesta de la API (UX).
            
            with st.spinner("Analizando datos..."):                                    
                with animacion.container():
                    st_lottie("https://lottie.host/cff9860c-cb60-420f-9874-3ffa82ce733f/fG2ox0LNjB.json", height=400)
                response = generate(csv_data)
            
            # Procesamiento de la respuesta
                # json.loads convierte el string JSON recibido de la IA en una lista de diccionarios de Python.
                charts = json.loads(response)
                # st.json(charts)  # Mostrar la estructura JSON para depuración (opcional)
                st.success("Gráficos generados exitosamente")
                
                # Creamos 3 columnas para organizar los gráficos en una cuadrícula (grid).
                cols = st.columns(3)
                
                # Iteramos sobre cada gráfico propuesto por la IA
                for i, chart_obj in enumerate(charts):
                    # Usamos módulo (%) para distribuir los gráficos en las 3 columnas cíclicamente.
                    with cols[i % 3]:
                        # Contenedor con altura fija para mantener uniformidad visual.
                        with st.container(height=400):                            
                            # Tabs para separar la visualización del código fuente
                            tabGraph, tabCode = st.tabs(["Gráfico", "Código y Explicación"])                                                    
                            try:
                                # Diccionario local para capturar las variables creadas por el código dinámico.
                                loc = {}
                                
                                # exec(): Ejecuta el string de código Python generado por la IA.
                                # PELIGRO: exec() ejecuta código arbitrario. En producción, esto debe usarse con extrema precaución.
                                exec(chart_obj["chart"], input_globals, loc)
                                
                                # Extraemos la figura 'fig' que la IA creó dentro del entorno 'loc'.
                                fig = loc.get("fig")                                
                                
                                # Mostramos el gráfico interactivo de Plotly.
                                tabGraph.plotly_chart(fig, use_container_width=True,height=300)
                            except Exception as e:
                                st.error(f"Error al generar el gráfico, por favor revisar el código ya que a veces se pueden presentar errores:\n{e}")
                            
                            # Mostramos el código y la explicación generada por la IA
                            tabCode.code(chart_obj["chart"], language="python")
                            tabCode.info(chart_obj["explanation"])

            animacion.empty()  # Limpiamos la animación después de mostrar los gráficos

if __name__ == "__main__":
    main()