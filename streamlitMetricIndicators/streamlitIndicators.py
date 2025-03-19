# Importa las bibliotecas necesarias.
import streamlit as st  # Para crear la aplicación web. Comando de instalación: pip install streamlit
import plotly.graph_objects as go  # Para crear gráficos interactivos. Comando de instalación: pip install plotly
import pandas as pd  # Para manipular datos. Comando de instalación: pip install pandas
import uuid # Para generar id unicos para los gráficos de plotly en streamlit. Comando de instalación: pip install uuid
from plotly.subplots import make_subplots # Para crear subplots en plotly. Comando de instalación: pip install plotly

# Configura el título de la página y el diseño.
st.set_page_config(layout="wide", page_title='Streamlit Metricas e Indicadores')

# Define una función para generar un indicador con gráfico vertical usando Streamlit.
def generarIndicadorStreamlitChartV(df, colvalue, colPosicion, texto='', relativo=False, tipo='l', orientacion="v"):
    """Genera un indicador con un gráfico vertical usando Streamlit.

    Args:
        df (pd.DataFrame): El DataFrame que contiene los datos.
        colvalue (str): El nombre de la columna que contiene el valor del indicador.
        colPosicion (str): El nombre de la columna que contiene la posición (eje x).
        texto (str, optional): Texto adicional para la etiqueta. Defaults to ''.
        relativo (bool, optional): Si True, muestra el delta como porcentaje. Defaults to False.
        tipo (str, optional): El tipo de gráfico ('l' para línea, 'b' para barras, 'a' para área). Defaults to 'l'.
        orientacion (str, optional): La orientación del gráfico ('v' para vertical, 'h' para horizontal). Defaults to 'v'.
    """
    # Crea una figura de Plotly.
    fig = go.Figure()    
    # Obtiene el último y penúltimo valor de la columna de valor.
    ultimo = df[colvalue].iloc[-1]
    penultimo = df[colvalue].iloc[-2]        
    # Obtiene la etiqueta de la columna de posición.
    etiqueta = df[colPosicion].iloc[-1]
    # Crea un contenedor con borde.
    with st.container(border=True):
        # Muestra la métrica con el delta (cambio) relativo o absoluto.
        if relativo:
            st.metric(label=f"{colvalue} {etiqueta} {texto}", value=ultimo, delta=f"{(ultimo-penultimo)/penultimo:,.3%}")
        else:
            st.metric(label=f"{colvalue} {etiqueta} {texto}", value=ultimo, delta=f"{ultimo-penultimo:,.3f}")
        
        # Agrega el gráfico especificado.
        if tipo == 'l': # Gráfico de líneas.
            fig.add_trace(go.Scatter(y=df[colvalue], mode='lines', x=df[colPosicion]))            
        if tipo == 'b': # Gráfico de barras.
            fig.add_trace(go.Bar(y=df[colvalue], x=df[colPosicion]))
        if tipo == 'a': # Gráfico de área.
            fig.add_trace(go.Scatter(y=df[colvalue], fill='tozeroy', x=df[colPosicion]))
        # Oculta y bloquea los ejes.
        fig.update_xaxes(visible=False, fixedrange=True)
        fig.update_yaxes(visible=False, fixedrange=True)
        fig.update_layout(height=100) # Ajusta la altura del gráfico.
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0)) # Elimina los márgenes.
        clave = uuid.uuid4() # genera un id para el gráfico para evitar que streamlit los redibuje.
        st.plotly_chart(fig, use_container_width=True, key=clave)      

# Define una función para generar un indicador con gráfico horizontal usando Streamlit.
def generarIndicadorStreamlitChartH(df, colvalue, colPosicion, texto='', relativo=False, tipo='l'):
    """Genera un indicador con un gráfico horizontal usando Streamlit.

    Args:
        df (pd.DataFrame): El DataFrame que contiene los datos.
        colvalue (str): El nombre de la columna que contiene el valor del indicador.
        colPosicion (str): El nombre de la columna que contiene la posición (eje x).
        texto (str, optional): Texto adicional para la etiqueta. Defaults to ''.
        relativo (bool, optional): Si True, muestra el delta como porcentaje. Defaults to False.
        tipo (str, optional): El tipo de gráfico ('l' para línea, 'b' para barras, 'a' para área). Defaults to 'l'.
    """
    # Crea una figura de Plotly.
    fig = go.Figure()    
    ultimo = df[colvalue].iloc[-1]
    penultimo = df[colvalue].iloc[-2]        
    etiqueta = df[colPosicion].iloc[-1]

    with st.container(border=True):        
        cols = st.columns([2, 8]) # Divide el contenedor en dos columnas.
        if relativo:
            cols[0].metric(label=f"{colvalue} {etiqueta} {texto}", value=ultimo, delta=f"{(ultimo - penultimo) / penultimo:,.3%}")
        else:
            cols[0].metric(label=f"{colvalue} {etiqueta} {texto}", value=ultimo, delta=f"{ultimo - penultimo:,.3f}")
        if tipo == 'l':
            fig.add_trace(go.Scatter(y=df[colvalue], mode='lines', x=df[colPosicion]))            
        if tipo == 'b':
            fig.add_trace(go.Bar(y=df[colvalue], x=df[colPosicion]))
        if tipo == 'a':
            fig.add_trace(go.Scatter(y=df[colvalue], fill='tozeroy', x=df[colPosicion]))
        fig.update_xaxes(visible=False, fixedrange=True)
        fig.update_yaxes(visible=False, fixedrange=True)
        fig.update_layout(height=100)
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
        clave = uuid.uuid4() # genera un id para el gráfico para evitar que streamlit los redibuje.
        cols[1].plotly_chart(fig, use_container_width=True, key=clave)

# Define una función para generar un indicador básico con Plotly.
def generarIndicadorPlotly(df,colvalue,colPosicion,texto='',relativo=False):
    """Genera un indicador básico con Plotly.

    Args:
        df (pd.DataFrame): El DataFrame que contiene los datos.
        colvalue (str): El nombre de la columna que contiene el valor del indicador.
        colPosicion (str): El nombre de la columna que contiene la posición (eje x).
        texto (str, optional): Texto adicional para la etiqueta. Defaults to ''.
        relativo (bool, optional): Si True, muestra el delta como porcentaje. Defaults to False.

    Returns:
        go.Figure: La figura de Plotly.
    """
    ultimo=df[colvalue].iloc[-1]
    penultimo=df[colvalue].iloc[-2]        
    etiqueta=df[colPosicion].iloc[-1]
    fig = go.Figure(go.Indicator(
        mode = "number+delta",    
        value = ultimo,
        delta = {'reference': penultimo,'relative': relativo},
        title = {'text': f"<b>{colvalue}</b> {etiqueta} {texto}"},
        domain = {'x': [0, 1], 'y': [0, 1]},
        
    ))
    return fig

# Define una función para generar un indicador de tipo gauge con Plotly.
def generarIndicadorPlotlyGauge(df, colvalue, colPosicion, texto='', relativo=False, rangos=True):
    """Genera un indicador de tipo gauge con Plotly.

    Args:
        df (pd.DataFrame): El DataFrame que contiene los datos.
        colvalue (str): El nombre de la columna que contiene el valor del indicador.
        colPosicion (str): El nombre de la columna que contiene la posición (eje x).
        texto (str, optional): Texto adicional para la etiqueta. Defaults to ''.
        relativo (bool, optional): Si True, muestra el delta como porcentaje. Defaults to False.
        rangos (bool, optional): Si True, muestra rangos de colores. Defaults to True.

    Returns:
        go.Figure: La figura de Plotly.
    """
    ultimo = df[colvalue].iloc[-1]
    penultimo = df[colvalue].iloc[-2]        
    etiqueta = df[colPosicion].iloc[-1]
    maximo = df[colvalue].max()
    if relativo:
        formato = '.3%'
    else:
        formato = ',.3f'
    if rangos: # Si se deben mostrar rangos de colores.
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",    
            value=ultimo,
            delta={'reference': penultimo, 'relative': relativo,'valueformat': formato},
            gauge={'axis': {'range': [None, maximo]},
                   'bar': {'color': "grey"},
                   'steps': [
                       {'range': [0, 1.9], 'color': '#FF8F8F'}, # Rango rojo.
                       {'range': [1.9, 2.1], 'color': '#EEF296'}, # Rango amarillo.
                       {'range': [2.1, maximo], 'color': '#9ADE7B'}], # Rango verde.
                   'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 2}},
            title={'text': f"<b>{colvalue}</b> {etiqueta} {texto}"},
            domain={'x': [0, 1], 'y': [0, 1]},
        ))
    else: # Si no se deben mostrar rangos.
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",    
            value=ultimo,
            delta={'reference': penultimo, 'relative': relativo},            
            title={'text': f"<b>{colvalue}</b> {etiqueta} {texto}"},
            domain={'x': [0, 1], 'y': [0, 1]},
        ))
    return fig

# Define una función para generar un indicador numérico con un gráfico.
def generarIndicadorPlotlyNumberChart(df, colvalue, colPosicion, texto='', relativo=False, tipo='l'):
    """Genera un indicador numérico con un gráfico.

    Args:
        df (pd.DataFrame): El DataFrame que contiene los datos.
        colvalue (str): El nombre de la columna que contiene el valor del indicador.
        colPosicion (str): El nombre de la columna que contiene la posición (eje x).
        texto (str, optional): Texto adicional para la etiqueta. Defaults to ''.
        relativo (bool, optional): Si True, muestra el delta como porcentaje. Defaults to False.
        tipo (str, optional): El tipo de gráfico ('l' para línea, 'b' para barras, 'a' para área). Defaults to 'l'.

    Returns:
        go.Figure: La figura de Plotly.
    """
    ultimo = df[colvalue].iloc[-1]
    penultimo = df[colvalue].iloc[-2]        
    etiqueta = df[colPosicion].iloc[-1]
    if relativo:
        formato = '.3%'
    else:
        formato = ',.3f'
    fig = go.Figure(go.Indicator(
        mode="number+delta",    
        value=ultimo,
        delta={'reference': penultimo, 'relative': relativo, 'valueformat': formato},
        title={'text': f"<b>{colvalue}</b> {etiqueta} {texto}"},
        domain={'x': [0, 1], 'y': [0, 1]},
    ))
    if tipo == 'l':
        fig.add_trace(go.Scatter(y=df[colvalue], mode='lines', x=df[colPosicion]))
    if tipo == 'b':
        fig.add_trace(go.Bar(y=df[colvalue], x=df[colPosicion]))
    if tipo == 'a':
        fig.add_trace(go.Scatter(y=df[colvalue], fill='tozeroy', x=df[colPosicion]))
    fig.update_xaxes(visible=False, fixedrange=True)
    fig.update_yaxes(visible=False, fixedrange=True)
    return fig

# Define una función para generar un indicador numérico con un gráfico Vertical.
def generarIndicadorPlotlyNumberChartSubplotV(df, colvalue, colPosicion, texto='', relativo=False, tipo='l'):
    """Genera un indicador numérico con un gráfico vertical en un subplot.

    Args:
        df (pd.DataFrame): El DataFrame que contiene los datos.
        colvalue (str): El nombre de la columna que contiene el valor del indicador.
        colPosicion (str): El nombre de la columna que contiene la posición (eje x).
        texto (str, optional): Texto adicional para la etiqueta. Defaults to ''.
        relativo (bool, optional): Si True, muestra el delta como porcentaje. Defaults to False.
        tipo (str, optional): El tipo de gráfico ('l' para línea, 'b' para barras, 'a' para área). Defaults to 'l'.

    Returns:
        go.Figure: La figura de Plotly.
    """
    ultimo = df[colvalue].iloc[-1]
    penultimo = df[colvalue].iloc[-2]        
    etiqueta = df[colPosicion].iloc[-1]
    if relativo:
        formato = '.3%'
    else:
        formato = ',.3f'
    fig = make_subplots(
            rows=2, cols=1,
            vertical_spacing=0.03,
            specs=[[{"type": "indicator"}], [{"type": "scatter"}]],
            row_heights=[0.5, 0.5] # Ajusta la altura de cada subplot.
        )
    fig.add_trace(go.Indicator(
        mode="number+delta",    
        value=ultimo,
        delta={'reference': penultimo, 'relative': relativo, 'valueformat': formato},
        title={'text': f"<b>{colvalue}</b> {etiqueta} {texto}"},
        domain={'x': [0, 1], 'y': [0, 1]},
    ), row=1, col=1)
    if tipo == 'l':
        fig.add_trace(go.Scatter(y=df[colvalue], mode='lines', x=df[colPosicion]),row=2, col=1)
    if tipo == 'b':
        fig.add_trace(go.Bar(y=df[colvalue], x=df[colPosicion]),row=2, col=1)
    if tipo == 'a':
        fig.add_trace(go.Scatter(y=df[colvalue], fill='tozeroy', x=df[colPosicion]),row=2, col=1)
    fig.update_xaxes(visible=False, fixedrange=True)
    fig.update_yaxes(visible=False, fixedrange=True)
    return fig


def generarIndicadorPlotlyNumberChartSubplotH(df, colvalue, colPosicion, texto='', relativo=False, tipo='l'):    
    """Genera un indicador numérico con un gráfico horizontal en un subplot.

    Args:
        df (pd.DataFrame): El DataFrame que contiene los datos.
        colvalue (str): El nombre de la columna que contiene el valor del indicador.
        colPosicion (str): El nombre de la columna que contiene la posición (eje x).
        texto (str, optional): Texto adicional para la etiqueta. Defaults to ''.
        relativo (bool, optional): Si True, muestra el delta como porcentaje. Defaults to False.
        tipo (str, optional): El tipo de gráfico ('l' para línea, 'b' para barras, 'a' para área). Defaults to 'l'.

    Returns:
        go.Figure: La figura de Plotly.
    """
    ultimo = df[colvalue].iloc[-1]
    penultimo = df[colvalue].iloc[-2]        
    etiqueta = df[colPosicion].iloc[-1]
    if relativo:
        formato = '.3%'
    else:
        formato = ',.3f'
    fig = make_subplots(
            rows=1, cols=2,
            horizontal_spacing=0.01,
            specs=[[{"type": "indicator"},{"type": "scatter"}]],
            column_widths=[0.3, 0.7] # Ajusta el ancho de cada subplot
        )
    fig.add_trace(go.Indicator(
        mode="number+delta",    
        value=ultimo,
        delta={'reference': penultimo, 'relative': relativo, 'valueformat': formato},
        title={'text': f"<b>{colvalue}</b> {etiqueta} {texto}"},
        domain={'x': [0, 1], 'y': [0, 1]}
    ), row=1, col=1)
    if tipo == 'l':
        fig.add_trace(go.Scatter(y=df[colvalue], mode='lines', x=df[colPosicion]),row=1, col=2)
    if tipo == 'b':
        fig.add_trace(go.Bar(y=df[colvalue], x=df[colPosicion]),row=1, col=2)
    if tipo == 'a':
        fig.add_trace(go.Scatter(y=df[colvalue], fill='tozeroy', x=df[colPosicion]),row=1, col=2)
    fig.update_xaxes(visible=False, fixedrange=True)
    fig.update_yaxes(visible=False, fixedrange=True)
    return fig

# Carga los datos desde un archivo CSV.
# El conjunto de datos contiene la tasa de fertilidad total por país y año.
dfNatality = pd.read_csv("./API_SP.DYN.TFRT.IN_DS2_EN_csv_v2_2145.csv", encoding='latin1')
# Elimina las columnas innecesarias
dfNatality = dfNatality.drop(columns=['Country Code', 'Indicator Name', 'Indicator Code'])
# Transforma los datos de formato ancho a formato largo.
dfNatality = dfNatality.melt(id_vars=['Country Name'], var_name='Year', value_name='Fertility Rate')
# Renombra la columna 'Country Name' a 'Country'.
dfNatality = dfNatality.rename(columns={'Country Name': 'Country'})
# Elimina las filas con valores faltantes.
dfNatality = dfNatality.dropna()
# Convierte la columna 'Year' a tipo entero.
dfNatality['Year'] = dfNatality['Year'].astype(int)
# Ordena los datos por país y año.
dfNatality = dfNatality.sort_values(by=['Country', 'Year'])
# Convierte la columna 'Fertility Rate' a tipo flotante.
dfNatality['Fertility Rate'] = dfNatality['Fertility Rate'].astype(float)

# Crea un encabezado para la aplicación.
st.header('Ejemplos indicadores')

# Crea un widget selectbox para seleccionar un país.
parPais = st.selectbox('Seleccione un país', dfNatality['Country'].unique())
# Crea dos columnas para mostrar los indicadores.
cols = st.columns(2)

# Si se selecciona un país.
if parPais:
    dfNatalityPais = dfNatality[dfNatality['Country'] == parPais]
    cols = st.columns(2)
    with cols[0]:
        fig = generarIndicadorPlotly(dfNatalityPais, 'Fertility Rate', 'Year', parPais)
        st.plotly_chart(fig, use_container_width=True)
    with cols[1]:
        fig = generarIndicadorPlotlyGauge(dfNatalityPais, 'Fertility Rate', 'Year', parPais, True)
        st.plotly_chart(fig, use_container_width=True)
    cols = st.columns(2)
    with cols[0]:
        fig = generarIndicadorPlotlyGauge(dfNatalityPais, 'Fertility Rate', 'Year', parPais, True, False)
        st.plotly_chart(fig, use_container_width=True)
    with cols[1]:
        parTipoGraficoPlotly = st.selectbox('Seleccione un tipo de gráfico', ['Lineal', 'Barras', 'Area'], key='parTipoGraficoPlotly')
        parTipoGraficoPlotly = parTipoGraficoPlotly[0].lower()
        fig = generarIndicadorPlotlyNumberChart(dfNatalityPais, 'Fertility Rate', 'Year', parPais, tipo=parTipoGraficoPlotly)
        st.plotly_chart(fig, use_container_width=True)        
    cols = st.columns(2)
    with cols[0]:        
        clave = uuid.uuid4()
        fig = generarIndicadorPlotlyNumberChartSubplotV(dfNatalityPais, 'Fertility Rate', 'Year', parPais, tipo=parTipoGraficoPlotly)
        st.plotly_chart(fig, use_container_width=True, key=clave)
    with cols[1]:
        fig = generarIndicadorPlotlyNumberChartSubplotH(dfNatalityPais, 'Fertility Rate', 'Year', parPais, tipo=parTipoGraficoPlotly)
        clave = uuid.uuid4()
        st.plotly_chart(fig, use_container_width=True, key=clave)
    cols = st.columns(2)
    with cols[0]:
        parTipoGraficoStreamlit = st.selectbox('Seleccione un tipo de gráfico', ['Lineal', 'Barras', 'Area'], key='parTipoGraficoStreamlit')
        parTipoGraficoStreamlit = parTipoGraficoStreamlit[0].lower()
        parRelativo = st.checkbox('Mostrar en porcentaje')
        generarIndicadorStreamlitChartV(dfNatalityPais, 'Fertility Rate', 'Year', parPais, parRelativo, tipo=parTipoGraficoStreamlit)
    with cols[1]:
        generarIndicadorStreamlitChartH(dfNatalityPais, 'Fertility Rate', 'Year', parPais, parRelativo, tipo=parTipoGraficoStreamlit)