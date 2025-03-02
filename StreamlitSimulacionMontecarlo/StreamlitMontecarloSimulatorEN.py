# Imports the necessary libraries
import streamlit as st  # To create the web interface. Install with: pip install streamlit
import pandas as pd  # To manipulate data in tabular format. Install with: pip install pandas
import numpy as np  # To perform numerical calculations. Install with: pip install numpy
import plotly.express as px  # To create interactive graphs. Install with: pip install plotly
import montecarlo as mc # For the simulation functions.
from code_editor import code_editor # To edit the code in the app. Install with: pip install streamlit-code-editor
import utils as ut  # For custom utility functions. Make sure you have the utils.py file in the same directory.

# Example {{sales}} * ({{price}}-({{price}}*0.1*{{discount}}))

# Configure the Streamlit page
st.set_page_config(page_title="Monte Carlo Simulator", layout="wide")
# Apply custom CSS styles
ut.local_css("estilos.css") # Make sure you have the estilos.css file in the same directory.

# Main title of the application
st.title(':material/analytics: Monte Carlo Simulator')

# Container for the simulation parameters
with st.container(border=True, key="panel-parametros"):
    # Subtitle for the parameters section
    st.subheader(':blue[:material/function: Simulation parameters]')
    # Create two columns to organize the elements
    c1, c2 = st.columns([2, 8], vertical_alignment="center")
    # Column 1: Input for the name of the result variable
    with c1:
        parVariableResultado = st.text_input('Result variable', 'Result')
    # Column 2: Code editor for the simulation formula
    with c2:
        st.write('##### Simulation formula')
        parformula = code_editor('', lang='python', 
                                 response_mode='blur',
                                 )  # Code editor
    # Displays an informative message about how to enter the formula
    st.info('Enter the simulation formula. Use variables between double braces. For example, if the formula is `X1+X2`, you should enter `{{X1}}+{{X2}}`', icon=":material/info:")

    # Input for the number of simulations
    parNumSimulaciones = st.number_input('Number of simulations', min_value=1, value=1000)
    # If a formula has been entered
    if parformula:
        # Generates the variables from the entered formula
        formulaSimulacion, listaNombreVariables = mc.generarVariables(parformula["text"])
        
        # Checks if variables were found in the formula
        if len(listaNombreVariables) == 0:
            st.error("No variables were found in the formula. All variables must be in the format {{variable}}", icon=":material/warning:")
            st.stop() # Stops execution if there are no variables
        # Creates a DataFrame for the variables
        dfBase = pd.DataFrame({'Variable': listaNombreVariables, "Distribucion": "Normal", "Tipo Datos": "Decimales", "Param 1": 0.0000, "Param 2": 0.000,"Param 3": 0.000})
        # Creates two columns for variable editing and distribution information
        columns = st.columns(2)
        with columns[0]:
            # Data editor to configure the variables
            dfVariables = st.data_editor(dfBase,
                                        column_config={
                                            "Variable": st.column_config.TextColumn(
                                                "Variable",                                                
                                                disabled=True,
                                            ),
                                            "Distribucion": st.column_config.SelectboxColumn(
                                                "Distribution",
                                                help="Probability distribution of the simulation",
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
                                                "Data Type",
                                                help="Data type of the variable",
                                                width="medium",
                                                options=[
                                                    "Entero",
                                                    "Decimales",
                                                ],
                                                required=True,
                                            )
                                        },
                                        hide_index=True, use_container_width=True)
            # Button to start the simulation
            btnSimular = st.button('Simulate', type="primary")
            # Calculates the minimum value of the parameters
            minValorParametros = dfVariables.apply(lambda x: x["Param 1"] + x["Param 2"]+ x["Param 3"], axis=1).min()
            # Displays an error message if the parameters are zero
            if minValorParametros == 0:
                st.error("Some of the variables have Param 1, Param 2 and Param 3 at zero", icon=":material/warning:")
        with columns[1]:
            # Informative text about distributions
            textoDistribuciones = """### Distributions
**Normal** Bell-shaped distribution, values close to the mean.
* *Param 1:* Mean of the distribution.
* *Param 2:* Standard deviation of the distribution.
* **Use cases:** Statistics, quality control, finance.

**Uniform Distribution:** All outcomes in a range have equal probability.
* *Param 1:* Minimum value of the range.
* *Param 2:* Maximum value of the range.
* **Use cases:** Random numbers, wait times, gambling.

**Binomial Distribution:** Number of successes in trials with two possible outcomes.
* *Param 1:* Number of trials.
* *Param 2:* Probability of success.
* **Use cases:** Surveys, quality control, biology.

**Triangular Distribution:** Most likely values in a range.
* *Param 1:* Minimum value of the range.
* *Param 2:* Most likely value.
* *Param 3:* Maximum value of the range.
* **Use cases:** Estimates, risks, uncertainty.
            """
            with st.container(height=300):
                st.info(textoDistribuciones)
        # Initializes the session state for the result
        if 'resultado' not in st.session_state:
            st.session_state.resultado = pd.DataFrame()

# Container for the simulation results
with st.container(border=True, key="panel-analisis"):    
    # If the Simulate button has been pressed or there are results in the session
    if btnSimular or len(st.session_state.resultado) > 0:
        
        # Stops if the parameters are zero
        if minValorParametros == 0:
            st.stop()
        # If there are no results in the session or the Simulate button has been pressed
        if len(st.session_state.resultado) == 0 or btnSimular:
            # Subtitle for the results section
            # Declare a dictionary to store the variables
            variables = dict()
            # Iterates over the variables and generates random values according to the selected distribution
            for index, row in dfVariables.iterrows():
                if row["Distribucion"] == "Normal":
                    variables[row["Variable"]] = np.random.normal(row["Param 1"], row["Param 2"], parNumSimulaciones)
                if row["Distribucion"] == "Uniforme":
                    variables[row["Variable"]] = np.random.uniform(row["Param 1"], row["Param 2"], parNumSimulaciones)
                if row["Distribucion"] == "Binomial":
                    variables[row["Variable"]] = np.random.binomial(row["Param 1"], row["Param 2"], parNumSimulaciones)
                if row["Distribucion"] == "Triangular":
                    variables[row["Variable"]] = np.random.triangular(row["Param 1"], (row["Param 2"] , row["Param 3"], parNumSimulaciones))
                if row["Tipo Datos"] == "Entero":
                    variables[row["Variable"]] = variables[row["Variable"]].astype(int)

            # Evaluates the simulation formula
            variables[parVariableResultado] = eval(formulaSimulacion)
            
            # Creates a DataFrame with the results
            dfResultado = pd.DataFrame(variables)
            # Saves the DataFrame to the session state
            st.session_state.resultado = dfResultado
        else:
            # If there are already results in the session, loads them
            dfResultado = st.session_state.resultado
        # Subtitle for the results section
        st.subheader(':green[:material/insights: Simulation results]')
        # Creates two tabs to display the results: Analysis and Data
        tabAnalisis, tabDatos = st.tabs(["Analysis", "Data"])

        with tabDatos:
            # Creates two columns to display the data table and histograms
            c1, c2 = st.columns([4, 6])
            with c1:
                st.dataframe(dfResultado, use_container_width=True)
            with c2:
                columns = st.columns(3)
                contador = 0
                # Creates histograms for each variable
                for variable in listaNombreVariables:
                    col = contador % 3
                    fig = px.histogram(dfResultado, x=variable, title=variable)
                    fig.update_layout(bargap=0.03)
                    columns[col].plotly_chart(ut.aplicarFormatoChart(fig), use_container_width=True, key=f"chart-{variable}")
                    contador += 1
        with tabAnalisis:
            c1, c2 = st.columns([8, 2])
            with c1:
                # Calculates the histogram for the result variable
                count, division = np.histogram(dfResultado[parVariableResultado], bins=100)
                pd.DataFrame({"count": count, "division": division[:100]})
                # Creates a slider to select the probability range
                rangoPercentiles = [2.5, 5, 25, 50, 75, 95, 97.5]
                percentiles = np.percentile(dfResultado[parVariableResultado], rangoPercentiles)
                dfPercentiles = pd.DataFrame({"Percentil": [str(i) + " %" for i in rangoPercentiles], "Valor": percentiles})
                parMontoProbabilidad = st.slider('Amount to calculate probability', float(dfResultado[parVariableResultado].min()),
                                                 float(dfResultado[parVariableResultado].max()),
                                                 (float(percentiles[0]), float(percentiles[-1])))
                # Calculates the probability, average and median for the selected range
                dfRango = dfResultado[(dfResultado[parVariableResultado] >= parMontoProbabilidad[0]) & (
                            dfResultado[parVariableResultado] <= parMontoProbabilidad[1])]
                probabilidadMonto = dfRango[parVariableResultado].count() / parNumSimulaciones
                promedioGeneral = dfResultado[parVariableResultado].mean()
                medianaGeneral = dfResultado[parVariableResultado].median()
                promedio = dfRango[parVariableResultado].mean()
                mediana = dfRango[parVariableResultado].median()
                columns = st.columns(3)
                columns[0].metric(label="Probability", value=f"{probabilidadMonto:,.2%}", delta_color="normal")
                columns[1].metric(label="Average", value=f"{promedio:,.2f}", delta_color="normal")
                columns[2].metric(label="Median", value=f"{mediana:,.2f}", delta_color="normal")
                # Displays the interpretation of the results
                interpretacion = f""" With a probability of **{probabilidadMonto:,.2%}**, the amount of **{parVariableResultado}** is between **{parMontoProbabilidad[0]:,.2f}** and **{parMontoProbabilidad[1]:,.2f}**.
                """
                st.success(interpretacion, icon=":material/emoji_objects:")
                # Creates a histogram for the result variable with the selected range
                fig = px.histogram(dfResultado, x=parVariableResultado, title=parVariableResultado)
                fig.update_layout(bargap=0.03)
                fig.add_vrect(x0=parMontoProbabilidad[0], x1=parMontoProbabilidad[1], fillcolor="green", opacity=0.25,
                              line_width=0)
                fig.add_vline(x=promedioGeneral, line_dash="dash", line_color="blue", line_width=1)
                fig.add_vline(x=medianaGeneral, line_dash="dash", line_color="red", line_width=1)
                st.plotly_chart(ut.aplicarFormatoChart(fig), use_container_width=True, key="chart-histograma")
            with c2:
                # Displays additional metrics
                st.metric(label="Simulations", value=parNumSimulaciones, delta_color="normal")
                st.metric(label=":blue[:material/crop_square: General Average]", value=f"{promedioGeneral:,.2f}",
                          delta_color="normal")
                st.metric(label=":red[:material/crop_square: General Median]", value=f"{medianaGeneral:,.2f}",
                          delta_color="normal")
                st.table(dfPercentiles)
                st.info("Percentiles are the values that divide a data sample into 100 equal parts. For example, the 50th percentile is the median of the data.")