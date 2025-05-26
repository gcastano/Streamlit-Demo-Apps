# Librería: streamlit
# Propósito: Streamlit es un framework de Python de código abierto que permite crear aplicaciones web interactivas para proyectos de machine learning y ciencia de datos con muy poco código.
# Comando para instalar: pip install streamlit
import streamlit as st

# Librería: pandas
# Propósito: Pandas es una librería fundamental para la manipulación y análisis de datos en Python. Proporciona estructuras de datos como DataFrames, que son ideales para trabajar con datos tabulares.
# Comando para instalar: pip install pandas
import pandas as pd

# Librería: numpy
# Propósito: NumPy (Numerical Python) es esencial para la computación científica en Python. Ofrece soporte para arrays y matrices multidimensionales, junto con una colección de funciones matemáticas para operar con ellos.
# Comando para instalar: pip install numpy
import numpy as np

# Librería: plotly
# Propósito: Plotly es una librería de graficación interactiva. plotly.graph_objects es un módulo específico que permite crear figuras complejas y personalizadas.
# Comando para instalar: pip install plotly
import plotly.graph_objects as go

# Librería: matplotlib
# Propósito: Matplotlib es una librería de graficación 2D muy popular en Python. Aunque en este código la visualización principal se hace con Plotly, Matplotlib es una dependencia común en el ecosistema de ciencia de datos y podría ser útil para otras tareas o personalizaciones.
# Comando para instalar: pip install matplotlib
import matplotlib.pyplot as plt

# Configuración de la página de Streamlit
# st.set_page_config se utiliza para establecer atributos de la página como el título que aparece en la pestaña del navegador y el layout (ancho).
st.set_page_config(
    page_title="Validación Ley de Benford", # Título de la página en la pestaña del navegador
    layout="wide" # Utiliza todo el ancho disponible de la página
)

def color_diferencia(val):
    """
    Aplica un color rojo al texto si el valor absoluto de la diferencia porcentual supera un umbral.

    Esta función se usa para el estilizado condicional de celdas en un DataFrame de Pandas.

    Args:
        val (str): Un valor de cadena que representa un porcentaje (ej. '5.25%').

    Returns:
        str: Una cadena de estilo CSS ('color: red') si la condición se cumple, sino una cadena vacía.
    """
    try:
        # Intenta convertir el valor (quitando el '%' y espacios) a un número flotante y dividir por 100 para obtener la proporción.
        num = float(val.strip('%')) / 100
        # Comprueba si el valor absoluto del número es mayor que el umbral global 'parUmbral'.
        if abs(num) >= parUmbral:
            return 'color: red' # Devuelve el estilo CSS para texto rojo
    except:
        # Si ocurre algún error durante la conversión (ej. el valor no es un porcentaje válido), no hace nada.
        pass
    return '' # Devuelve una cadena vacía si no se cumple la condición o hay error.

def generar_distribucion_benford():
    """
    Calcula la distribución teórica de los primeros dígitos según la Ley de Benford.

    La Ley de Benford establece que en muchas colecciones de números que ocurren naturalmente,
    el primer dígito 'd' (1-9) aparece con una probabilidad P(d) = log10(1 + 1/d).

    Returns:
        numpy.ndarray: Un array con las probabilidades teóricas para los dígitos del 1 al 9.
    """
    # np.arange(1, 10) crea un array [1, 2, 3, 4, 5, 6, 7, 8, 9].
    # La fórmula np.log10(1 + 1/d) se aplica a cada elemento 'd' del array.
    return np.log10(1 + 1 / np.arange(1, 10))

def obtener_primer_digito(numeros):
    """
    Extrae el primer dígito significativo de una lista de números.

    Args:
        numeros (list): Una lista de números (enteros o flotantes).

    Returns:
        list: Una lista de cadenas, donde cada cadena es el primer dígito significativo
              del número correspondiente. Los números cero son ignorados.
    """
    # Se utiliza una comprensión de listas para procesar cada número.
    # str(abs(int(num)))[0]:
    #   1. int(num): Convierte el número a entero (trunca decimales).
    #   2. abs(...): Toma el valor absoluto para manejar números negativos.
    #   3. str(...): Convierte el entero a cadena.
    #   4. [0]: Extrae el primer carácter de la cadena (el primer dígito).
    #   La condición `if int(num) != 0` asegura que no se procesen números que sean cero.
    return [str(str(abs(int(num)))[0]) for num in numeros if int(num) != 0]

def detect_anomalies(observed, expected, threshold=0.05):
    """
    Detecta los dígitos cuya frecuencia observada se desvía de la frecuencia esperada
    (Ley de Benford) más allá de un umbral especificado.

    Args:
        observed (numpy.ndarray): Array de frecuencias observadas para los dígitos 1-9.
        expected (numpy.ndarray): Array de frecuencias esperadas (Benford) para los dígitos 1-9.
        threshold (float, optional): El umbral de desviación para considerar una anomalía.
                                     Por defecto es 0.05 (5%).

    Returns:
        tuple:
            - list: Una lista de los dígitos (1-9) que se consideran anómalos.
            - pandas.DataFrame: Un DataFrame con los dígitos, sus frecuencias observadas,
                                esperadas y la diferencia absoluta.
    """
    anomalies = [] # Lista para almacenar los dígitos anómalos.
    # Calcula la diferencia absoluta entre las frecuencias observadas y esperadas.
    differences = np.abs(observed - expected)
    # Itera sobre las frecuencias observadas y esperadas.
    for i, (obs, exp) in enumerate(zip(observed, expected)):
        # Si la diferencia absoluta entre la frecuencia observada y esperada es mayor que el umbral.
        if abs(obs - exp) >= threshold:
            anomalies.append(i + 1) # Añade el dígito (i+1 porque i es 0-8) a la lista de anomalías.

    # Creación de un DataFrame de Pandas para mostrar la comparación detallada.
    # Esta es una transformación de datos importante con Pandas.
    dfComparacion = pd.DataFrame({
        'Dígito': list(range(1, 10)),      # Columna 'Dígito' con los números del 1 al 9.
        'Frecuencia Observada': observed,  # Columna con las frecuencias observadas.
        'Frecuencia Esperada': expected,   # Columna con las frecuencias esperadas (Benford).
        'Diferencia': differences          # Columna con las diferencias absolutas calculadas.
    })
    return anomalies, dfComparacion

# Título principal de la aplicación Streamlit.
st.title("Validación de la Ley de Benford")

# Creación de pestañas en la interfaz de Streamlit para diferentes métodos de entrada de datos.
tab = st.segmented_control(
    "Origen de los datos",
    options=[":material/description: Carga Archivo", ":material/numbers: Carga Texto"],
    default=":material/description: Carga Archivo", # Pestaña por defecto al cargar la aplicación.
    selection_mode="single",
)
numeros=None
# Contenido de la pestaña "Carga Archivo".
with st.container(border=True): # Utiliza un contenedor para agrupar widgets y contenido.
    if tab == ":material/description: Carga Archivo":
        st.write("""
        Carga un archvio con el listado de números (uno por línea o en CSV/Excel) para analizar.
        """)

        # Widget de Streamlit para cargar archivos. Permite tipos CSV, XLSX, TXT.
        archivo_cargado = st.file_uploader("Carga un archivo (CSV, Excel, TXT)", type=["csv", "xlsx", "txt"])
        numeros = [] # Inicializa la lista para almacenar los números extraídos.

        if archivo_cargado: # Si se ha cargado un archivo:
            if archivo_cargado.name.endswith('.csv'):
                # Procesamiento de archivos CSV.
                # pd.read_csv(): Lee el archivo CSV en un DataFrame de Pandas.
                df = pd.read_csv(archivo_cargado)
                # Extracción de números:
                # 1. df.select_dtypes(include=[np.number]): Selecciona solo las columnas numéricas del DataFrame. (Transformación Pandas)
                # 2. .stack(): Apila las columnas del DataFrame en una Serie, útil si hay múltiples columnas numéricas. (Transformación Pandas)
                # 3. pd.to_numeric(..., errors='coerce'): Convierte los valores a numéricos. Si un valor no puede ser convertido, se reemplaza por NaT/NaN (Not a Time/Not a Number). (Transformación Pandas)
                # 4. .dropna(): Elimina las filas/valores que son NaT/NaN. (Transformación Pandas)
                # 5. .tolist(): Convierte la Serie resultante a una lista de Python.
                numeros = pd.to_numeric(df.select_dtypes(include=[np.number]).stack(), errors='coerce').dropna().tolist()
            elif archivo_cargado.name.endswith('.xlsx'):
                # Procesamiento de archivos Excel (XLSX).
                # pd.read_excel(): Lee el archivo Excel en un DataFrame de Pandas.
                df = pd.read_excel(archivo_cargado)
                # La extracción de números sigue la misma lógica que para los archivos CSV. (Transformaciones Pandas)
                numeros = pd.to_numeric(df.select_dtypes(include=[np.number]).stack(), errors='coerce').dropna().tolist()
            elif archivo_cargado.name.endswith('.txt'):
                # Procesamiento de archivos de texto (TXT).
                # archivo_cargado.read().decode('utf-8'): Lee el contenido del archivo y lo decodifica como UTF-8.
                content = archivo_cargado.read().decode('utf-8')
                # Se procesa cada línea del archivo:
                # line.strip(): Elimina espacios en blanco al inicio y final de la línea.
                # line.strip().replace('.', '', 1).replace('-', '', 1).isdigit(): Verifica si la línea (después de quitar un punto decimal y un signo negativo) consiste solo en dígitos.
                # float(...): Convierte la línea a un número flotante.
                numeros = [float(line.strip()) for line in content.splitlines() if line.strip().replace('.', '', 1).replace('-', '', 1).isdigit()]

    # Contenido de la pestaña "Carga Texto".
    else:
        # Widget de Streamlit para entrada de texto multilínea.
        text_input = st.text_area("Pega los números aquí (uno por línea):")
        if text_input: # Si se ha ingresado texto:
            # La extracción de números sigue una lógica similar a la de los archivos TXT.
            numeros = [float(line.strip()) for line in text_input.splitlines() if line.strip().replace('.', '', 1).replace('-', '', 1).isdigit()]

    # Widget de Streamlit para ingresar el umbral de desviación como un número.
    # El valor se ingresa como porcentaje (0-100) y luego se convierte a proporción (0-1).
    parUmbral = st.number_input("Umbral de desviación para detectar anomalías (%)", min_value=0.0, max_value=100.0, value=5.0, step=1.0)
    parUmbral = parUmbral / 100 # Convierte el porcentaje a una proporción.

if numeros: # Si la lista 'numeros' contiene datos:
    # Extrae los primeros dígitos de los números.
    digits = obtener_primer_digito(numeros)
    # Cuenta la frecuencia de cada primer dígito (1-9).
    digit_counts = {str(d): digits.count(str(d)) for d in range(1, 10)}
    
    # Creación de un DataFrame de Pandas para almacenar las frecuencias de los dígitos. (Transformación Pandas)
    dfDatos = pd.DataFrame(list(digit_counts.items()), columns=['Dígito', 'Frecuencia'])
    # Cálculo del porcentaje de cada dígito. (Transformación Pandas: creación de nueva columna basada en otras)
    dfDatos['Porcentaje'] = (dfDatos['Frecuencia'] / dfDatos['Frecuencia'].sum())
    
    # Obtiene las frecuencias observadas como un array NumPy desde el DataFrame.
    observed_freq = dfDatos['Porcentaje'].values
    # Obtiene las frecuencias esperadas según la Ley de Benford.
    expected_freq = generar_distribucion_benford()

    # Detecta anomalías comparando las frecuencias observadas y esperadas con el umbral.
    anomalies, dfDiferencias = detect_anomalies(observed_freq, expected_freq, parUmbral)

    st.subheader("Distribución de dígitos iniciales") # Subtítulo para la sección de resultados.
    fig = go.Figure() # Inicializa una figura de Plotly.

    # Añade las barras de frecuencia observada al gráfico.
    fig.add_trace(go.Bar(
        x=list(range(1, 10)), # Eje X: Dígitos del 1 al 9.
        y=observed_freq,      # Eje Y: Frecuencias observadas.
        name='Observado',     # Nombre de esta traza para la leyenda.
        # Color condicional: rojo si el dígito está en la lista de anomalías, azul por defecto.
        marker_color=['#C62E2E' if (d+1) in anomalies else '#1f77b4' for d in range(9)],
        opacity=0.7,          # Opacidad de las barras.
        text=observed_freq,   # Texto que se mostrará en las barras (frecuencia observada).
        texttemplate="%{text:.2%}", # Formato del texto como porcentaje con 2 decimales.
    ))

    # Añade la línea de la Ley de Benford (frecuencia esperada) al gráfico.
    fig.add_trace(go.Scatter(
        x=list(range(1, 10)), # Eje X: Dígitos del 1 al 9.
        y=expected_freq,      # Eje Y: Frecuencias esperadas (Benford).
        mode='lines+markers', # Modo de la traza: líneas, marcadores y texto.
        name='Benford',       # Nombre de esta traza para la leyenda.
        line=dict(color='orange', width=3), # Estilo de la línea.
        marker=dict(symbol='circle', size=8, color='orange'), # Estilo de los marcadores.        
    ))

    # Configuración del layout del gráfico Plotly.
    fig.update_layout(
        xaxis=dict(title='Dígito inicial', tickmode='array', tickvals=list(range(1, 10))), # Configuración del eje X.
        yaxis=dict(title='Frecuencia'), # Título del eje Y (antes de formatear a porcentaje).
        bargap=0.2, # Espacio entre barras.
        title="Distribución de dígitos iniciales" # Título del gráfico.
    )
    # Formatea las etiquetas del eje Y como porcentajes.
    fig.update_yaxes(tickformat=".2%", title="Porcentaje")
    
    # Divide la interfaz en dos columnas para mostrar el gráfico y la tabla de diferencias.
    c1, c2 = st.columns([6,4]) # La primera columna es más ancha que la segunda.
    with c1: # Contenido de la primera columna.
        # Muestra el gráfico Plotly.
        st.plotly_chart(fig, use_container_width=True)
    with c2: # Contenido de la segunda columna.
        # Formateo de columnas del DataFrame 'dfDiferencias' para mostrar como porcentajes.
        # .applymap(lambda x: f"{x:.2%}"): Aplica una función lambda a cada celda de las columnas seleccionadas para formatearlas como string de porcentaje. (Transformación Pandas)
        dfDiferencias[['Frecuencia Observada', 'Frecuencia Esperada', 'Diferencia']] = dfDiferencias[['Frecuencia Observada', 'Frecuencia Esperada', 'Diferencia']].applymap(lambda x: f"{x:.2%}")

        # Aplicación de estilo condicional al DataFrame para colorear las diferencias anómalas.
        # .style.applymap(): Aplica la función 'color_diferencia' a la columna 'Diferencia'. (Estilización Pandas)
        dfDiferencias_styled = dfDiferencias.style.applymap(color_diferencia, subset=['Diferencia'])
        # Muestra el DataFrame estilizado en Streamlit.
        st.dataframe(dfDiferencias_styled, use_container_width=True, hide_index=True)

        # Muestra un mensaje de advertencia si se detectan anomalías.
        if anomalies:
            st.warning(f"¡Anomalía detectada en los dígitos: {', '.join(map(str, anomalies))}!")
        else: # Muestra un mensaje de éxito si no se detectan anomalías.
            st.success("No se detectaron anomalías significativas según la Ley de Benford.")
else: # Si no se han cargado o ingresado números.
    st.info("Por favor, carga o ingresa un listado de números para analizar.")