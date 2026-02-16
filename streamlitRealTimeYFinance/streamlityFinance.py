import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# -----------------------------------------------------------------------------
# SECCIÓN DE LIBRERÍAS Y CONFIGURACIÓN
# -----------------------------------------------------------------------------
# Explicación de librerías utilizadas:
# 1. streamlit: Framework para crear aplicaciones web de datos rápidamente.
#    -> Instalación: pip install streamlit
# 2. yfinance: Librería para descargar datos financieros de Yahoo Finance.
#   https://ranaroussi.github.io/yfinance/
#    -> Instalación: pip install yfinance
# 3. pandas: Herramienta esencial para manipulación y análisis de datos estructurados.
#    -> Instalación: pip install pandas
# 4. plotly: Librería de gráficos interactivos.
#    -> Instalación: pip install plotly
# -----------------------------------------------------------------------------

# Configuración inicial de la página de la aplicación Streamlit
st.set_page_config(
    page_title="Monitor de precios de acciones en tiempo real",
    page_icon="📈",
    layout="wide",             # Utiliza todo el ancho de la pantalla
    initial_sidebar_state="expanded"
)

st.title("Precios de Acciones")

# Decorador @st.dialog: Crea una ventana modal (popup) cuando se llama a esta función.
# Documentación: https://docs.streamlit.io/develop/api-reference/execution-flow/st.dialog
@st.dialog("Detalle del Stock", width="large")
def verDetalleStock(ticker, period="1d", interval="1m"):
    """
    Muestra información detallada, descripción y gráfico interactivo de una acción específica.
    
    Args:
        ticker (str): Símbolo de la acción (ej. 'AAPL').
        period (str): Periodo de tiempo a descargar (ej. '1d', '5d', '1mo').
        interval (str): Intervalo de los datos (ej. '1m', '1h', '1d').
    """
    # Descarga de metadatos de la acción (sector, industria, descripción, etc.)
    dat = yf.Ticker(ticker).info
    
    st.title(f"{dat.get('longName', 'N/A')} ({ticker})")
    
    # Contenedor horizontal para mostrar métricas clave organizadas
    with st.container(horizontal=True, horizontal_alignment="center"):
        # Uso de .get() para evitar errores si la clave no existe en el diccionario
        st.write(f"**Sector:** {dat.get('sector', 'N/A')}")
        st.write(f"**Industria:** {dat.get('industry', 'N/A')}")
        st.write(f"**País:** {dat.get('country', 'N/A')}")
        # Formateo de números grandes con comas (:,)
        st.write(f"**Capitalización de mercado:** ${dat.get('marketCap', 0):,}")
        st.write(f"**Dividend Rate:** {dat.get('dividendRate', 'N/A')}")
    with st.expander("Ver descripción completa"):
        st.write(f"{dat.get('longBusinessSummary', 'N/A')}")
    with st.expander("Ver Noticias recientes"):
        news = yf.Ticker(ticker).news        
        for item in news:
            item=item["content"] # Accedemos al diccionario interno 'content' que contiene los detalles de cada noticia
            # st.json(item) # Muestra el diccionario completo de la noticia en formato JSON
            url=item['canonicalUrl']["url"]            
            st.write(f"**[{item['title']}]({url})**({item['pubDate']})  - *{item['provider']['displayName']}*")
            
    
    # -------------------------------------------------------------------------
    # TRANSFORMACIÓN DE DATOS CON PANDAS
    # -------------------------------------------------------------------------
    # multi_level_index=False simplifica las columnas (evita MultiIndex complejo).
    dfDatos = yf.download(ticker, period=period, interval=interval, multi_level_index=False)    
    
    # 2. Aseguramos que sea un DataFrame de pandas explícitamente
    dfDatos = pd.DataFrame(dfDatos)
    
    # 3. reset_index(): Mueve el índice actual (que suele ser la fecha) a una columna normal.
    # Esto es útil para manipular la fecha como una variable más antes de graficar.
    dfDatos.reset_index(inplace=True)
    
    # 4. Lógica condicional para establecer el índice correcto según el intervalo.
    # Si es intradiario (minutos 'm' o horas 'h'), usamos 'Datetime', si no, 'Date'.
    if interval.endswith("m") or interval.endswith("h"):
        dfDatos.set_index("Datetime", inplace=True)
    else:
        dfDatos.set_index("Date", inplace=True)
    
    # Creación del gráfico de línea con Plotly Express
    fig = px.line(
        dfDatos,
        x=dfDatos.index,   # Eje X: Índice (Fecha/Hora)
        y="Close",         # Eje Y: Precio de Cierre
        labels={"x": "Fecha", "Close": "Precio ($)"},        
        height=300,
        title=f"Precio de Cierre de {ticker} ({period} - {interval})"
    )
    fig.update_layout(
        xaxis_title=None, # or ""
        yaxis_title=None, # or ""
    )
    fig.update_layout( 
        hovermode="x unified",  # Muestra información de todos los puntos en la misma posición x        
    )
    # Cálculo de máximos y mínimos para resaltarlos en el gráfico
    highest_value = dfDatos['Close'].max()
    lowest_value = dfDatos['Close'].min()
    # idxmax() e idxmin() devuelven el índice (fecha) donde ocurre el valor máximo/mínimo
    highest_index = dfDatos['Close'].idxmax()
    lowest_index = dfDatos['Close'].idxmin()
    
    # Añadir marcador verde para el punto máximo
    fig.add_scatter(
        x=[highest_index],
        y=[highest_value],
        mode='markers',
        marker=dict(color='green', size=10),
        name='Máximo'
    )

    # Añadir marcador rojo para el punto mínimo
    fig.add_scatter(
        x=[lowest_index],
        y=[lowest_value],
        mode='markers',
        marker=dict(color='red', size=10),
        name='Mínimo'
    )
    
    
    
    # Visualización de métricas financieras actuales
    with st.container(horizontal=True, horizontal_alignment="center"):
        # [-1] accede al último dato (más reciente), [-2] al penúltimo.
        # Se calcula la variación porcentual (delta) manualmente.
        st.metric(label="Precio Actual", value=f"${dfDatos['Close'][-1]:.2f}", delta=f"{(dfDatos['Close'][-1]-dfDatos['Close'][-2])/dfDatos['Close'][-1]*100:.2f}%")
        st.metric(label="Volumen Actual", value=f"{dfDatos['Volume'][-1]:,}", delta=f"{(dfDatos['Volume'][-1]-dfDatos['Volume'][-2])/dfDatos['Volume'][-1]*100:.2f}%")
        st.metric(label="Precio Máximo", value=f"${dfDatos['High'][-1]:.2f}", delta=f"{(dfDatos['High'][-1]-dfDatos['High'][-2])/dfDatos['High'][-1]*100:.2f}%")
        st.metric(label="Precio Mínimo", value=f"${dfDatos['Low'][-1]:.2f}", delta=f"{(dfDatos['Low'][-1]-dfDatos['Low'][-2])/dfDatos['Low'][-1]*100:.2f}%")
        st.metric(label="Apertura", value=f"${dfDatos['Open'][-1]:.2f}", delta=f"{(dfDatos['Open'][-1]-dfDatos['Open'][-2])/dfDatos['Open'][-1]*100:.2f}%")
        st.metric(label="Cierre Anterior", value=f"${dfDatos['Close'][-2]:.2f}")
        # Cálculo del promedio de volumen de todo el periodo descargado
        st.metric(label="Volumen Promedio", value=f"{dfDatos['Volume'].mean():,.0f}")
        
    st.plotly_chart(fig, use_container_width=True)
    
# Decorador @st.fragment: Permite que esta función se re-ejecute independientemente del resto de la app.
# run_every=timedelta(seconds=60): Actualiza automáticamente este fragmento cada 60 segundos (auto-refresh).
@st.fragment(run_every=timedelta(seconds=60))
def generarTicker(ticker, period="1d", interval="1m"):    
    """
    Genera una tarjeta resumen (Card) para un ticker específico con un gráfico de área pequeño.
    
    Args:
        ticker (str): Símbolo de la acción.
        period (str): Periodo de datos.
        interval (str): Intervalo de datos.
    """
    
    # Descarga de datos
    dfDatos = yf.download(
        ticker,                    # Símbolo de la acción (ej. 'AAPL', 'GOOGL')
        period=period,             # Período de tiempo a descargar (ej. '1d', '1mo', '1y')
        interval=interval,         # Intervalo de los datos (ej. '1m', '1h', '1d')
        multi_level_index=False    # Simplifica las columnas evitando MultiIndex complejo
    )
    
    # Transformación: Reset del índice para verificar si llegaron datos
    dfDatos.reset_index(inplace=True)    
    
    # Validación: Si el DataFrame está vacío, mostramos advertencia y salimos
    if len(dfDatos) == 0:
        st.warning(f"No se encontraron datos para el ticker {ticker}. Pruebe con otra combinación de periodo e intervalo.")
        return
    
    # Descarga de metadatos para mostrar detalles de la acción en la tarjeta
    dat = yf.Ticker(ticker).info
    
    # Reasignación del índice (similar a la función anterior)
    # Algunas combinaciones de intervalo pueden generar columnas 'Datetime' o 'Date', por eso se verifica cuál existe.
    if "Datetime" in dfDatos.columns:
        dfDatos.set_index("Datetime", inplace=True)
    else:
        dfDatos.set_index("Date", inplace=True)
    
    # Creación de la tarjeta visual (Metric + Chart)
    with st.container(border=True, horizontal=True, horizontal_alignment="center"):    
        # st.metric tiene un parámetro 'chart_data' para mostrar mini-gráficos (sparklines)
        st.metric(
            label=f"**{ticker}** _{dat.get('longName', 'N/A')}_", 
            value=f"${dfDatos['Close'][-1]:.2f}", 
            delta=f"{(dfDatos['Close'][-1]-dfDatos['Close'][-2])/dfDatos['Close'][-1]*100:.2f}%",
            chart_data=dfDatos['Close'].tolist(), # Convertimos la serie de pandas a lista
            chart_type="area",
            width=300,
            height=200
        )        
        # Botón para abrir el diálogo de detalles
        st.button("Ver Detalles :material/open_in_new:", 
                  key=f"btn_{ticker}", 
                  on_click=verDetalleStock, 
                  args=(ticker,period,interval),
                  type="primary")

# Lista de acciones por defecto para cargar en la barra lateral
defaultStocks ="""AAPL
AMZN
GOOGL
MSFT
META
NVDA
TSLA"""

# -----------------------------------------------------------------------------
# INTERFAZ DE USUARIO (SIDEBAR Y GRID PRINCIPAL)
# -----------------------------------------------------------------------------
# Inputs en la barra lateral
parStock = st.sidebar.text_area("Ingrese los símbolos del ticker (por ejemplo, AAPL para Apple):", value=defaultStocks)
parPeriod = st.sidebar.selectbox("Seleccione el período de tiempo:", options=["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y"])
parInterval = st.sidebar.selectbox("Seleccione el intervalo de tiempo:", options=["1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"])

# Procesamiento de la entrada de tickers
if parStock:
    stocks = parStock.splitlines() # Convierte el texto multilinea en una lista
    cols = st.columns(5) # Crea 5 columnas para el layout tipo grid
    
    with st.container(horizontal=True, horizontal_alignment="center"):        
        for parStock in stocks:
            # Distribuye las acciones en las 5 columnas usando el operador módulo (%)
            # Ejemplo: índice 0 va a col 0, índice 5 va a col 0, índice 6 va a col 1...
            with cols[stocks.index(parStock) % 5]:
                generarTicker(parStock.upper(), period=parPeriod, interval=parInterval)