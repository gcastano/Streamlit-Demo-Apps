import pandas as pd  # Librería para manipulación de datos
# Instalar con: pip install pandas
import streamlit as st  # Librería para crear aplicaciones web interactivas
# Instalar con: pip install streamlit
import plotly.graph_objects as gp  # Librería para crear gráficos interactivos
# Instalar con: pip install plotly
import plotly.express as px  # Librería para crear gráficos más fácilmente
# Instalar con: pip install plotly
import utils # Archivo con funciones personalizadas
import numpy as np # Librería para operaciones numéricas
# Instalar con: pip install numpy

# Configura la página de Streamlit
st.set_page_config(layout="wide", page_title="Dashboard de Población", page_icon="🌍")

# Obtiene los colores de fondo y texto del tema actual de streamlit
backgroundColor = st.get_option('theme.secondaryBackgroundColor')
textColor = st.get_option('theme.textColor')
# Aplica estilos CSS personalizados desde el archivo "estilos.css"
utils.local_css("estilos.css", backgroundColor)

# Define una paleta de colores para los gráficos
paleta = ['#1077ff', '#ee8052', '#599ada', '#eee852', '#7ddc65', '#ed5855', '#79848f',"#ed5855"]

def aplicarRangosEdad(dfDatosRango):
    """
    Categoriza la edad en rangos predefinidos.

    Args:
        dfDatosRango (pd.DataFrame): DataFrame con una columna 'AgeEnd' que representa la edad.

    Returns:
        pd.DataFrame: DataFrame con una nueva columna 'rango' que contiene la categoría de edad.
    """
    # Definir los bins (límites de los rangos de edad)
    bins = [0, 18, 45, 60, 75, 90, float('inf')]

    # Definir las etiquetas para cada rango
    labels = [
    'Menor de edad (0-17)', 
    'Adulto joven (18-44)', 
    'Adulto medio (45-59)', 
    'Adulto mayor (60-74)', 
    'Anciano (75-89)', 
    'Anciano longevo (90+)'
    ]

    # Crear una nueva columna con los rangos de edad usando pd.cut
    # pd.cut divide los datos en intervalos (bins) y les asigna una etiqueta (labels)
    dfDatosRango['rango'] = pd.cut(dfDatosRango['AgeEnd'], bins=bins, labels=labels)
    return dfDatosRango

def generarPiramidePoblacional(data,anio,pais):
    """
    Genera una pirámide poblacional interactiva usando Plotly.

    Args:
        data (pd.DataFrame): DataFrame con datos de población por edad y sexo.
        anio (int): Año para el que se genera la pirámide.
        pais (str): País para el que se genera la pirámide.

    Returns:
        plotly.graph_objects.Figure: Figura de Plotly que representa la pirámide poblacional.
    """
    y_age = list(range(0, 100, 10)) #data['rango']    
    if pais == "Todos":
        pais = "el Mundo"
    rango=data['rango'].unique()
    x_M = data[data["Sex"]=="Male"]["Value"]
    x_F = (data[data["Sex"]=="Female"]["Value"] * -1)
    # Creating instance of the figure 
    fig = gp.Figure() 
    
    # Adding Male data to the figure 
    fig.add_trace(gp.Bar(y= y_age, x = x_M,  
                        name = 'Male',  
                        orientation = 'h',
                        text=x_M,
                        customdata=rango,
                        marker_color ="#1077ff",
                        texttemplate='%{text:,.0f}',
                        hoverinfo='text',
                        hovertemplate='%{text:,.0f} persona %{customdata} años') 
        )
    
    # Adding Female data to the figure 
    fig.add_trace(gp.Bar(y = y_age, x = x_F, 
                        name = 'Female', orientation = 'h',
                        text=x_F*-1,
                        customdata=rango,
                        texttemplate='%{text:,.0f}',
                        hoverinfo='text',
                        marker_color="#FDB7EA",
                        hovertemplate='%{text:,.0f} persona %{customdata} años') 
                )
    
    # Updating the layout for our graph 
    fig.update_layout(title = f'Pirámide de Población para {pais} en el año {anio}', 
                    title_font_size = 22, barmode = 'relative', 
                    bargap = 0.1, bargroupgap = 0, 
                    xaxis = dict(title = 'Población', 
                                title_font_size = 14),
                    yaxis = dict(title = 'Rango de edad',
                                title_font_size = 14,
                                tickvals = y_age,
                                ticktext = rango),
                    )
    return fig

# Lee los datos del archivo CSV
dfDatos = pd.read_csv("unpopulation_dataportal_20250331213650.csv")
# dfDatos.to_excel("dfDatos.xlsx",index=False)
dfDatosBase=dfDatos.copy() # Crea una copia del DataFrame original
st.header(":material/travel_explore: Dashboard de Análisis de Población")
st.info("Este dashboard permite analizar la población mundial y de diferentes países a lo largo del tiempo. Se pueden observar las tendencias de la población por rango de edad y género, así como la distribución porcentual de la población en diferentes rangos de edad. Los datos utilizados provienen de la base de datos de la ONU y están disponibles en el siguiente [enlace](https://population.un.org/dataportal/home/).")
c1,c2= st.columns([7,3]) # Divide la página en dos columnas
with c1: # Trabaja con la primera columna
    with st.container(key="container-filtros"): # Crea un contenedor para los filtros
        subcols= st.columns(2) # Divide el contenedor en dos columnas
        with subcols[0]: # Trabaja con la primera subcolumna
            parPais = st.selectbox("Selecciona un país",options=["Todos"]+ list(dfDatos["Location"].unique())) # Crea un selectbox para seleccionar el país
        with subcols[1]: # Trabaja con la segunda subcolumna
            parAnio= st.slider("Selecciona un año", min_value=dfDatos["Time"].min(), max_value=dfDatos["Time"].max(), value=2024, step=1, key="par-anio") # Crea un slider para seleccionar el año
        if parPais != "Todos": # Filtra los datos por país si se selecciona un país
                dfDatos = dfDatos[dfDatos["Location"] == parPais] # Filtra el DataFrame por país
            
        dfDatosPiramide = dfDatos[dfDatos["Time"] == parAnio] # Filtra los datos por año

with c2:  # Trabaja con la segunda columna  
    totalPoblacion = dfDatosPiramide["Value"].sum() # Calcula la población total
    if parPais == "Todos": # Define el título del métrico
        parPaisTitulo = f"Población total {parAnio}"
    else: # Define el título del métrico
        parPaisTitulo = f"Población total {parAnio} en {parPais}"
    st.metric(label=parPaisTitulo, value=f"{totalPoblacion:,.0f} personas") # Muestra la población total en un métrico
c1,c2= st.columns(2) # Divide la página en dos columnas
with c1: # Trabaja con la primera columna       
    dfDatosRango = dfDatosPiramide.groupby(["AgeEnd","Sex"]).agg({"Value": "sum"}).reset_index().sort_values(by="AgeEnd") # Agrupa los datos por edad y sexo
    # Crea rangos de edad usando pd.cut
    dfDatosRango["rango"] = pd.cut(dfDatosRango["AgeEnd"], bins=range(0, 120, 10), labels=["0-9", "10-19", "20-29", "30-39", "40-49", "50-59", "60-69", "70-79", "80-89", "90-99","100+"])
    dfDatosAnioSexo = dfDatosRango.groupby(["rango","Sex"]).agg({"Value": "sum"}).reset_index() # Agrupa los datos por rango de edad y sexo
    # st.dataframe(dfDatosAnioSexo)
    # dfDatosPiramide.to_excel("dfDatosAnioSexo.xlsx", index=False)
    fig =generarPiramidePoblacional(dfDatosAnioSexo,parAnio,parPais) # Genera la pirámide poblacional   
    st.plotly_chart(utils.aplicarFormatoChart(fig,backgroundColor=backgroundColor,legend=True), use_container_width=True,key="chart-piramide") # Muestra la pirámide poblacional
with c2:  # Trabaja con la segunda columna
    dfDatosRango=aplicarRangosEdad(dfDatosRango) # Aplica los rangos de edad
    dfDatosRango = dfDatosRango.groupby(["rango"]).agg({"Value": "sum"}).reset_index() # Agrupa por rango de edad
    dfDatosRango["porcentaje"]=dfDatosAnioSexo["Value"]/ dfDatosAnioSexo['Value'].sum() # Calcula el porcentaje de cada rango
    if parPais == "Todos":  # Define el título del gráfico
        parPaisTitulo = "el Mundo"
    else:  # Define el título del gráfico
        parPaisTitulo = parPais
    fig = px.pie(  # Crea un gráfico de pastel
        dfDatosRango, 
        values='Value', 
        names='rango', 
        title=f"Distribución de la población por rango de edad para el {parAnio} en {parPaisTitulo}", 
        labels={"Value": "Población"},         
        color_discrete_sequence=paleta
    )
    fig.update_traces(  # Actualiza la información que se muestra al pasar el mouse
        hovertemplate='<b>Rango de edad: %{label}</b><br>Población: %{value:,.0f}<br>Porcentaje: %{percent:.2%}',
        textinfo='percent+label',
        textfont_size=14,
        textposition='outside',
    )
    fig.update_layout(showlegend=False,title_font_size = 22) # Actualiza el diseño del gráfico
    
    st.plotly_chart(utils.aplicarFormatoChart(fig,backgroundColor=backgroundColor), use_container_width=True,key="chart-piramide2")  # Muestra el gráfico de pastel
st.subheader("Tendencia de la población por rango de edad")
c1,c2= st.columns(2)  # Divide la página en dos columnas
with c1:  # Trabaja con la primera columna
    dfDatosRango = dfDatos.groupby(["AgeEnd","Time"]).agg({"Value": "sum"}).reset_index().sort_values(by="AgeEnd") # Agrupa por edad y tiempo    
        
    dfDatosRango["rango"] = pd.cut(dfDatosRango["AgeEnd"], bins=range(0, 120, 10), labels=["0-9", "10-19", "20-29", "30-39", "40-49", "50-59", "60-69", "70-79", "80-89", "90-99","100+"]) # Crea rangos de edad usando pd.cut
    # Convertir la columna 'rango' en una columna categórica ordenada
    categorias_ordenadas = ["0-9", "10-19", "20-29", "30-39", "40-49", "50-59", "60-69", "70-79", "80-89", "90-99", "100+"]
    dfDatosRango["rango"] = pd.Categorical(dfDatosRango["rango"], categories=categorias_ordenadas, ordered=True)
    dfDatosAnioSexo = dfDatosRango.groupby(["rango","Time"]).agg({"Value": "sum"}).reset_index() # Agrupa por rango y tiempo
    dfDatosAnioSexo["porcentaje"]=dfDatosAnioSexo["Value"]/ dfDatosAnioSexo.groupby('Time')['Value'].transform('sum') # Calcula el porcentaje
        
    figTendencia=px.area(dfDatosAnioSexo.sort_values(["Time","rango"]),x="Time",y="Value", color="rango",custom_data=["rango"], title="Tendencia de la población por rango de edad", labels={"Value":"Población"}, color_discrete_sequence=paleta) # Crea un gráfico de área

    figTendencia.update_traces(
        hovertemplate='<b>Rango de edad: %{customdata[0]} años</b><br>Año: %{x}<br>Población: %{y:,.0f}',        
        # mode='lines+markers',
    )
    figTendencia.update_layout(title_font_size = 22)
    st.plotly_chart(utils.aplicarFormatoChart(figTendencia, backgroundColor=backgroundColor,legend=True), use_container_width=True,key="chart-tendencia2")  # Muestra el gráfico de área
with c2:  # Trabaja con la segunda columna
    dfDatosAnioSexo=aplicarRangosEdad(dfDatosRango) # Aplica rangos de edad   
    dfDatosAnioSexo = dfDatosRango.groupby(["rango","Time"]).agg({"Value": "sum"}).reset_index()  # Agrupa por rango de edad y tiempo
    dfDatosAnioSexo["porcentaje"]=dfDatosAnioSexo["Value"]/ dfDatosAnioSexo.groupby('Time')['Value'].transform('sum') # Calcula el porcentaje
    figTendencia=px.area(dfDatosAnioSexo,x="Time",y="porcentaje", color="rango",custom_data=["rango"], title="Tendencia de la población por rango de edad", labels={"Value":"Población"}, color_discrete_sequence=paleta) # Crea un gráfico de área
    figTendencia.update_layout(
        yaxis_tickformat=".0%",
        yaxis_title="Porcentaje"
    )
    figTendencia.update_layout(title_font_size = 22)
    figTendencia.update_traces(  # Actualiza la información que se muestra al pasar el mouse
        hovertemplate='<b>Rango de edad: %{customdata[0]} años</b><br>Año: %{x}<br>Población: %{y:,.2%}',        
        # mode='lines+markers',
    )    
    st.plotly_chart(utils.aplicarFormatoChart(figTendencia,backgroundColor=backgroundColor,legend=True), use_container_width=True, key="chart-tendencia") # Muestra el gráfico de área


st.subheader("Analisis de variación de la población por rango de edad")
with st.container(key="container-rango"):  # Crea un contenedor para el rango   
    parRango=st.slider("Selecciona un rango de edad", min_value=dfDatos["Time"].min(), max_value=dfDatos["Time"].max(), value=(dfDatos["Time"].min(), dfDatos["Time"].max()), step=1, key="par-rango") # Crea un slider para el rango de tiempo
    c1,c2= st.columns(2) # Divide la página en dos columnas   
    with c1:  # Trabaja con la primera columna
        dfDatosPiramide = dfDatos[dfDatos["Time"].isin([parRango[0],parRango[1]])] # Filtra el DataFrame por el rango de tiempo       
        dfDatosRango = dfDatosPiramide.copy().groupby(["AgeEnd","Time"]).agg({"Value": "sum"}).reset_index().sort_values(by="AgeEnd") # Agrupa por edad y tiempo
        dfDatosRango["rango"] = pd.cut(dfDatosRango["AgeEnd"], bins=range(0, 120, 10), labels=["0-9", "10-19", "20-29", "30-39", "40-49", "50-59", "60-69", "70-79", "80-89", "90-99","100+"]) # Crea rangos de edad
        dfDatosAnio = dfDatosRango.groupby(["rango","Time"]).agg({"Value": "sum"}).reset_index()  # Agrupa por edad, rango y tiempo
        dfDatosAnio =dfDatosAnio.pivot(index=["rango"], columns="Time", values="Value").reset_index() # Pivotea la tabla
        
        dfDatosAnio["porcentaje1"]=dfDatosAnio[parRango[0]]/ dfDatosAnio[parRango[0]].sum() # Calcula el porcentaje para el primer año
        dfDatosAnio["porcentaje2"]=dfDatosAnio[parRango[1]]/ dfDatosAnio[parRango[1]].sum() # Calcula el porcentaje para el segundo año
        dfDatosAnio["diferencia"]=dfDatosAnio["porcentaje2"]-dfDatosAnio["porcentaje1"] # Calcula la diferencia
        dfDatosAnio["color"] = np.where(dfDatosAnio["diferencia"]<0, 'negativo', 'positivo') # Crea una columna para el color

        
        fig=px.bar(
            dfDatosAnio.sort_values("rango"),
            x="diferencia",
            y="rango",
            color="color",
            title=f"Distribución de la población por rango de edad en {parRango[0]} y {parRango[1]}",
            labels={"Value": "Población"},
            color_discrete_map={"positivo": "#7ddc65", "negativo": "#ed5855"},
            text=dfDatosAnio["diferencia"].apply(lambda x: f"{x:.2%}"),
        )
        fig.update_layout(
            xaxis_tickformat=".0%",
            xaxis_title="Diferencia porcentual"
        )
        
        st.plotly_chart(utils.aplicarFormatoChart(fig,backgroundColor=backgroundColor), use_container_width=True) # Muestra el gráfico de barras
    with c2:  # Trabaja con la segunda columna
        dfDatosRango = dfDatosPiramide.groupby(["AgeEnd","Time"]).agg({"Value": "sum"}).reset_index().sort_values(by="AgeEnd") # Agrupa por edad y tiempo
        dfDatosRango=aplicarRangosEdad(dfDatosRango) # Aplica rangos de edad
        dfDatosAnio = dfDatosRango.groupby(["rango","Time"]).agg({"Value": "sum"}).reset_index()  # Agrupa por rango de edad y tiempo
        dfDatosAnio =dfDatosAnio.pivot(index="rango", columns="Time", values="Value").reset_index()  # Pivotea la tabla
        dfDatosAnio["porcentaje1"]=dfDatosAnio[parRango[0]]/ dfDatosAnio[parRango[0]].sum() # Calcula el porcentaje para el primer año
        dfDatosAnio["porcentaje2"]=dfDatosAnio[parRango[1]]/ dfDatosAnio[parRango[1]].sum()  # Calcula el porcentaje para el segundo año
        dfDatosAnio["diferencia"]=dfDatosAnio["porcentaje2"]-dfDatosAnio["porcentaje1"] # Calcula la diferencia
        dfDatosAnio["color"] = np.where(dfDatosAnio["diferencia"]<0, 'negativo', 'positivo')  # Crea una columna para el color
        fig = px.bar(  # Crea un gráfico de barras
            dfDatosAnio,
            x="diferencia",
            y="rango",
            color="color",
            title=f"Distribución de la población por categoría de edad en {parRango[0]} y {parRango[1]}",
            labels={"Value": "Población"},
            color_discrete_map={"positivo": "#7ddc65", "negativo": "#ed5855"},
            text=dfDatosAnio["diferencia"].apply(lambda x: f"{x:.2%}"),
        )
        fig.update_layout(  # Actualiza el diseño del gráfico
            xaxis_tickformat=".0%",
            xaxis_title="Diferencia porcentual"
        )
        st.plotly_chart(utils.aplicarFormatoChart(fig,backgroundColor=backgroundColor), use_container_width=True)  # Muestra el gráfico de barras