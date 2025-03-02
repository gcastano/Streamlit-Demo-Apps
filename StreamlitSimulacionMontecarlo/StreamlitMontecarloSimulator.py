# Importa las librerías necesarias
import streamlit as st  # Para crear la interfaz web. Instalar con: pip install streamlit
import pandas as pd  # Para manipular datos en formato tabular. Instalar con: pip install pandas
import numpy as np  # Para realizar cálculos numéricos. Instalar con: pip install numpy
import plotly.express as px  # Para crear gráficos interactivos. Instalar con: pip install plotly
import montecarlo as mc # Para las funciones de la simulación.
from code_editor import code_editor # Para editar el código en la app. Instalar con: pip install streamlit-code-editor
import utils as ut  # Para funciones de utilidad personalizadas. Asegúrate de tener el archivo utils.py en el mismo directorio.

# Ejemplo {{ventas}} * ({{precio}}-({{precio}}*0.1*{{descuento}}))

# Configura la página de Streamlit
st.set_page_config(page_title="Simulador de Montecarlo", layout="wide")
# Aplica estilos CSS personalizados
ut.local_css("estilos.css") # Asegúrate de tener el archivo estilos.css en el mismo directorio.

# Título principal de la aplicación
st.title(':material/analytics: Simulador de Montecarlo')

# Contenedor para los parámetros de la simulación
with st.container(border=True, key="panel-parametros"):
    # Subtítulo para la sección de parámetros
    st.subheader(':blue[:material/function: Parámetros de la simulación]')
    # Crea dos columnas para organizar los elementos
    c1, c2 = st.columns([2, 8], vertical_alignment="center")
    # Columna 1: Input para el nombre de la variable resultado
    with c1:
        parVariableResultado = st.text_input('Variable resultado', 'Resultado')
    # Columna 2: Editor de código para la fórmula de simulación
    with c2:
        st.write('##### Fórmula de la simulación')
        parformula = code_editor('', lang='python', 
                                 response_mode='blur',
                                 )  # Editor de código
    # Muestra un mensaje informativo sobre cómo ingresar la fórmula
    st.info('Ingrese la fórmula de la simulación. Utilice las variables entre llaves dobles. Por ejemplo, si la fórmula es `X1+X2`, debe ingresar `{{X1}}+{{X2}}`', icon=":material/info:")

    # Input para el número de simulaciones
    parNumSimulaciones = st.number_input('Número de simulaciones', min_value=1, value=1000)
    # Si se ha ingresado una fórmula
    if parformula:
        # Genera las variables a partir de la fórmula ingresada
        formulaSimulacion, listaNombreVariables = mc.generarVariables(parformula["text"])
        
        # Verifica si se encontraron variables en la fórmula
        if len(listaNombreVariables) == 0:
            st.error("No se encontraron variables en la fórmula. Todas las variables deben tener el formato {{variable}}", icon=":material/warning:")
            st.stop() # Detiene la ejecución si no hay variables
        # Crea un DataFrame para las variables
        dfBase = pd.DataFrame({'Variable': listaNombreVariables, "Distribucion": "Normal", "Tipo Datos": "Decimales", "Param 1": 0.0000, "Param 2": 0.000,"Param 3": 0.000})
        # Crea dos columnas para la edición de variables y la información de distribuciones
        columns = st.columns(2)
        with columns[0]:
            # Data editor para configurar las variables
            dfVariables = st.data_editor(dfBase,
                                        column_config={
                                            "Variable": st.column_config.TextColumn(
                                                "Variable",                                                
                                                disabled=True,
                                            ),
                                            "Distribucion": st.column_config.SelectboxColumn(
                                                "Distribución",
                                                help="Distribución de probabilidad de la simulación",
                                                width="medium",
                                                options=[
                                                    "Normal",
                                                    "Uniforme",
                                                    "Binomial",
                                                    "Triangular",
                                                ],
                                                required=True,
                                            ),
                                            "Tipo Datos": st.column_config.SelectboxColumn(
                                                "Tipo de Datos",
                                                help="Tipo de datos de la variable",
                                                width="medium",
                                                options=[
                                                    "Entero",
                                                    "Decimales",
                                                ],
                                                required=True,
                                            )
                                        },
                                        hide_index=True, use_container_width=True)
            # Botón para iniciar la simulación
            btnSimular = st.button('Simular', type="primary")
            # Calcula el valor mínimo de los parámetros
            minValorParametros = dfVariables.apply(lambda x: x["Param 1"] + x["Param 2"]+ x["Param 3"], axis=1).min()
            # Muestra un mensaje de error si los parámetros son cero
            if minValorParametros == 0:
                st.error("Algunas de las variables tienen los Param 1, Param 2 y Param 3 en cero", icon=":material/warning:")
        with columns[1]:
            # Texto informativo sobre las distribuciones
            textoDistribuciones = """### Distribuciones
**Normal** Distribución en forma de campana, valores cerca de la media.
* *Param 1:* Media de la distribución.
* *Param 2:* Desviación estándar de la distribución.	
* **Casos de uso:** Estadísticas, control de calidad, finanzas.

**Distribución Uniforme:** Todos los resultados en un rango tienen igual probabilidad.
* *Param 1:* Valor mínimo del rango.
* *Param 2:* Valor máximo del rango.
* **Casos de uso:** Números aleatorios, tiempos de espera, juegos de azar.

**Distribución Binomial:** Número de éxitos en ensayos con dos resultados posibles.
* *Param 1:* Número de ensayos.
* *Param 2:* Probabilidad de éxito.
* **Casos de uso:** Encuestas, control de calidad, biología.

**Distribución Triangular:** Valores más probables en un rango.
* *Param 1:* Valor mínimo del rango.
* *Param 2:* Valor más probable.
* *Param 3:* Valor máximo del rango.
* **Casos de uso:** Estimaciones, riesgos, incertidumbre.
            """
            with st.container(height=300):
                st.info(textoDistribuciones)
        # Inicializa el estado de la sesión para el resultado
        if 'resultado' not in st.session_state:
            st.session_state.resultado = pd.DataFrame()

# Contenedor para los resultados de la simulación
with st.container(border=True, key="panel-analisis"):    
    # Si se ha presionado el botón Simular o hay resultados en la sesión    
    if btnSimular or len(st.session_state.resultado) > 0:
        
        # Detiene si los parámetros son cero
        if minValorParametros == 0:
            st.stop()
        # Si no hay resultados en la sesión o se ha presionado el botón Simular
        if len(st.session_state.resultado) == 0 or btnSimular:
            # Subtítulo para la sección de resultados            
            # Declaramos un diccionario para almacenar las variables
            variables = dict()
            # Itera sobre las variables y genera valores aleatorios según la distribución seleccionada
            for index, fila in dfVariables.iterrows():
                if fila["Distribucion"] == "Normal":
                    variables[fila["Variable"]] = np.random.normal(fila["Param 1"], fila["Param 2"], parNumSimulaciones)
                if fila["Distribucion"] == "Uniforme":
                    variables[fila["Variable"]] = np.random.uniform(fila["Param 1"], fila["Param 2"], parNumSimulaciones)
                if fila["Distribucion"] == "Binomial":
                    variables[fila["Variable"]] = np.random.binomial(fila["Param 1"], fila["Param 2"], parNumSimulaciones)
                if fila["Distribucion"] == "Triangular":
                    variables[fila["Variable"]] = np.random.triangular(fila["Param 1"], (fila["Param 2"] , fila["Param 3"], parNumSimulaciones))
                if fila["Tipo Datos"] == "Entero":
                    variables[fila["Variable"]] = variables[fila["Variable"]].astype(int)

            # Evalúa la fórmula de simulación
            variables[parVariableResultado] = eval(formulaSimulacion)
            
            # Crea un DataFrame con los resultados
            dfResultado = pd.DataFrame(variables)
            # Guarda el DataFrame en el estado de la sesión
            st.session_state.resultado = dfResultado
        else:
            # Si ya hay resultados en la sesión, los carga
            dfResultado = st.session_state.resultado
        # Subtítulo para la sección de resultados
        st.subheader(':green[:material/insights: Resultados de la simulación]')
        # Crea dos pestañas para mostrar los resultados: Análisis y Datos
        tabAnalisis, tabDatos = st.tabs(["Análisis", "Datos"])

        with tabDatos:
            # Crea dos columnas para mostrar la tabla de datos y los histogramas
            c1, c2 = st.columns([4, 6])
            with c1:
                st.dataframe(dfResultado, use_container_width=True)
            with c2:
                columns = st.columns(3)
                contador = 0
                # Crea histogramas para cada variable
                for variable in listaNombreVariables:
                    col = contador % 3
                    fig = px.histogram(dfResultado, x=variable, title=variable)
                    fig.update_layout(bargap=0.03)
                    columns[col].plotly_chart(ut.aplicarFormatoChart(fig), use_container_width=True, key=f"chart-{variable}")
                    contador += 1
        with tabAnalisis:
            c1, c2 = st.columns([8, 2])
            with c1:
                # Calcula el histograma para la variable resultado
                count, division = np.histogram(dfResultado[parVariableResultado], bins=100)
                dfHistograma = pd.DataFrame({"count": count, "division": division[:100]})
                # Crea un slider para seleccionar el rango de probabilidad
                rangoPercentiles = [2.5, 5, 25, 50, 75, 95, 97.5]
                percentiles = np.percentile(dfResultado[parVariableResultado], rangoPercentiles)
                dfPercentiles = pd.DataFrame({"Percentil": [str(i) + " %" for i in rangoPercentiles], "Valor": percentiles})
                parMontoProbabilidad = st.slider('Monto para calcular probabilidad', float(dfResultado[parVariableResultado].min()),
                                                 float(dfResultado[parVariableResultado].max()),
                                                 (float(percentiles[0]), float(percentiles[-1])))
                # Calcula la probabilidad, el promedio y la mediana para el rango seleccionado
                dfRango = dfResultado[(dfResultado[parVariableResultado] >= parMontoProbabilidad[0]) & (
                            dfResultado[parVariableResultado] <= parMontoProbabilidad[1])]
                probabilidadMonto = dfRango[parVariableResultado].count() / parNumSimulaciones
                promedioGeneral = dfResultado[parVariableResultado].mean()
                medianaGeneral = dfResultado[parVariableResultado].median()
                promedio = dfRango[parVariableResultado].mean()
                mediana = dfRango[parVariableResultado].median()
                columns = st.columns(3)
                columns[0].metric(label="Probabilidad", value=f"{probabilidadMonto:,.2%}", delta_color="normal")
                columns[1].metric(label="Promedio", value=f"{promedio:,.2f}", delta_color="normal")
                columns[2].metric(label="Mediana", value=f"{mediana:,.2f}", delta_color="normal")
                # Muestra la interpretación de los resultados
                interpretacion = f""" Con una probabilidad de **{probabilidadMonto:,.2%}**, el monto de **{parVariableResultado}** se encuentra entre **{parMontoProbabilidad[0]:,.2f}** y **{parMontoProbabilidad[1]:,.2f}**.
                """
                st.success(interpretacion, icon=":material/emoji_objects:")
                # Crea un histograma para la variable resultado con el rango seleccionado
                fig = px.histogram(dfResultado, x=parVariableResultado, title=parVariableResultado)
                fig.update_layout(bargap=0.03)
                fig.add_vrect(x0=parMontoProbabilidad[0], x1=parMontoProbabilidad[1], fillcolor="green", opacity=0.25,
                              line_width=0)
                fig.add_vline(x=promedioGeneral, line_dash="dash", line_color="blue", line_width=1)
                fig.add_vline(x=medianaGeneral, line_dash="dash", line_color="red", line_width=1)
                st.plotly_chart(ut.aplicarFormatoChart(fig), use_container_width=True, key="chart-histograma")
            with c2:
                # Muestra métricas adicionales
                st.metric(label="Simulaciones", value=parNumSimulaciones, delta_color="normal")
                st.metric(label=":blue[:material/crop_square: Promedio General]", value=f"{promedioGeneral:,.2f}",
                          delta_color="normal")
                st.metric(label=":red[:material/crop_square: Mediana General]", value=f"{medianaGeneral:,.2f}",
                          delta_color="normal")
                st.table(dfPercentiles)
                st.info("Los percentiles son los valores que dividen una muestra de datos en 100 partes iguales. Por ejemplo, el percentil 50 es la mediana de los datos.")