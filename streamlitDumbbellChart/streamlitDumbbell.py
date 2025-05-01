
# Script para crear una aplicación web interactiva con Streamlit
# que visualiza la tasa de fertilidad a lo largo del tiempo usando gráficos Dumbbell con Plotly.
# Los datos se obtienen de Our World In Data.
# El gráfico permite comparar la tasa de fertilidad entre dos años seleccionados
# y filtrar por países o grupos de países.

# Importar la librería Streamlit para crear la aplicación web interactiva.
# Comando para instalar: pip install streamlit
import streamlit as st

# Importar la librería Pandas para la manipulación y análisis de datos.
# Es fundamental para cargar, limpiar y transformar los datos.
# Comando para instalar: pip install pandas
import pandas as pd

# Importar Plotly Graph Objects para crear figuras y gráficos interactivos.
# Permite un control detallado sobre los elementos del gráfico.
# Comando para instalar: pip install plotly
import plotly.graph_objects as go

# Importar el módulo 'data' de Plotly (aunque no se usa directamente aquí,
# a veces se usa para cargar datasets de ejemplo de Plotly).
# from plotly import data # Comentado ya que no se utiliza explícitamente en este código.

# URL de referencia para gráficos Dumbbell en Plotly (útil para consulta)
# https://plotly.com/python/dumbbell-plots/

# --- Configuración de la Página de Streamlit ---
# Establece la configuración inicial de la página web.
st.set_page_config(
    page_title="Gráficos Dumbbell | Tasa de Fertilidad", # Título que aparece en la pestaña del navegador.
    layout="wide" # Utiliza el ancho completo de la página para la disposición de elementos.
)

# --- Título Principal de la Aplicación ---
# Muestra el título principal en la página web.
st.title("Gráficos Dumbbell: Evolución de la Tasa de Fertilidad")

# --- Carga de Datos ---
# Lee los datos desde una URL de Our World In Data en formato CSV.
# 'storage_options' se usa para pasar cabeceras HTTP, como 'User-Agent',
# lo cual a veces es necesario para que algunos servidores permitan la descarga.
@st.cache_data # Cachea los datos para no tener que descargarlos cada vez que se interactúa con la app
def cargar_datos():
    """
    Carga los datos de la tasa de fertilidad desde Our World In Data.

    Returns:
        pandas.DataFrame: DataFrame con los datos cargados.
    """
    url = "https://ourworldindata.org/grapher/children-born-per-woman.csv?v=1&csvType=full&useColumnShortNames=true"
    
    try:
        df = pd.read_csv(url, storage_options={"User-Agent": "Mozilla/5.0"})
        # Renombrar columnas para mayor claridad si es necesario (ejemplo opcional)
        # df = df.rename(columns={'fertility_rate_hist': 'Tasa_Fertilidad'})
        return df
    except Exception as e:
        st.error(f"Error al cargar los datos: {e}")
        return pd.DataFrame() # Devuelve un DataFrame vacío en caso de error

df_original = cargar_datos()

# Copia del dataframe para evitar modificar el original cacheado directamente
df = df_original.copy()

# --- Controles de Usuario (Widgets de Streamlit) ---
# Se definen columnas para organizar los widgets de control.
# Las proporciones [6, 2, 2] definen el ancho relativo de cada columna.
c1, c2, c3 = st.columns([6, 2, 2])

# Dentro de la primera columna (c1): Slider para seleccionar el rango de años.
with c1:
    # st.slider crea un control deslizante.
    # "Años": Etiqueta del slider.
    # min_value, max_value: Límites del slider.
    # value: Valor inicial (un tuple para un rango).
    # step: Incremento del slider.
    parAnos = st.slider(
        "Selecciona el rango de años a comparar:",
        min_value=1950, # Usa el mínimo del df si está disponible
        max_value=2023, # Usa el máximo del df si está disponible
        value=(1950, 2023), # Valor por defecto
        step=1
    )
    # Filtrar el DataFrame principal (df) para incluir solo los años seleccionados en el slider.
    # .isin() comprueba si los valores de la columna 'Year' están en la lista [año_inicio, año_fin].
    if not df.empty:
        df = df[df["Year"].isin([parAnos[0], parAnos[1]])]

# Dentro de la segunda columna (c2): Selectbox para elegir categoría (Países o Grupos).
with c2:
    # st.selectbox crea una lista desplegable.
    # "Categoría": Etiqueta del selectbox.
    # options: Lista de opciones disponibles.
    # index: Índice de la opción seleccionada por defecto (0 = "Países").
    parCategoria = st.selectbox(
        "Filtrar por:",
        options=["Países", "Grupos"],
        index=0
    )
    # Filtrar el DataFrame basado en la categoría seleccionada.
    # Los países tienen un valor en la columna "Code", los grupos tienen NaN (Not a Number).
    if not df.empty:
        if parCategoria == "Países":
            # ~df["Code"].isna() selecciona filas donde 'Code' NO es NaN (son países).
            df = df[~df["Code"].isna()]
        else:
            # df["Code"].isna() selecciona filas donde 'Code' ES NaN (son grupos/regiones).
            df = df[df["Code"].isna()]

# Dentro de la tercera columna (c3): Multiselect para elegir entidades específicas.
with c3:
    # Obtiene las entidades únicas disponibles después de los filtros anteriores.
    opciones_entidades = df["Entity"].unique() if not df.empty else []
    # st.multiselect permite seleccionar múltiples opciones de una lista.
    # "Entidades": Etiqueta del multiselect.
    # options: Lista de entidades únicas disponibles.
    parEntidades = st.multiselect(
        "Selecciona entidades específicas (opcional):",
        options=opciones_entidades
    )
    # Si el usuario ha seleccionado al menos una entidad, filtrar el DataFrame.
    if len(parEntidades) > 0 and not df.empty:
        # .isin() filtra para mantener solo las filas cuya 'Entity' está en la lista de seleccionadas.
        df = df[df["Entity"].isin(parEntidades)]

# Checkbox para decidir si mostrar flechas en los marcadores de línea.
parFlecha = st.checkbox("Mostrar flechas indicando dirección del cambio", value=False)

# --- Preparación de Datos para Plotly ---

# Diccionario de configuración para el marcador de flecha (si se activa).
# Define el símbolo, color, tamaño y orientación del marcador.
dictMarker = dict(
    symbol="arrow",       # Tipo de símbolo.
    color="#AAAAAA",      # Color gris claro.
    size=15,              # Tamaño del símbolo.
    angleref="previous",  # La flecha apunta desde el punto anterior al actual.
    standoff=8            # Distancia entre el punto y el inicio de la flecha.
)

# Crear una estructura de datos organizada para Plotly.
# Primero, obtener una lista ordenada de las entidades únicas presentes en el DataFrame filtrado.
# Se ordena por la tasa de fertilidad del primer año seleccionado para una mejor visualización.
# Es importante manejar el caso de que el dataframe esté vacío después de filtrar.
if not df.empty and parAnos[0] in df['Year'].values:
    # Ordenamos las entidades según el valor del primer año seleccionado
    Entidades = (
        df[df['Year'] == parAnos[1]]
        .sort_values(by=["fertility_rate_hist"], ascending=True)["Entity"]
        .unique()
    )
else:
     # Si no hay datos para el primer año (o df está vacío), usamos las entidades del segundo año o una lista vacía
    if not df.empty and parAnos[1] in df['Year'].values:
         Entidades = (
            df[df['Year'] == parAnos[1]]
            .sort_values(by=["fertility_rate_hist"], ascending=True)["Entity"]
            .unique()
         )
    else:
        Entidades = [] # Lista vacía si no hay datos válidos


# Diccionario para almacenar los datos formateados para las trazas de Plotly.
# 'line_x', 'line_y': Coordenadas para las líneas horizontales del dumbbell.
# parAnos[0], parAnos[1]: Listas con los valores de fertilidad para cada año (para los puntos).
data = {"line_x": [], "line_y": [], parAnos[0]: [], parAnos[1]: []}

# Iterar sobre cada entidad única ordenada.
for entidad in Entidades:
    # Obtener el valor de la tasa de fertilidad para el primer año seleccionado.
    # .loc[...] selecciona filas basadas en condiciones.
    # .values[0] extrae el primer valor encontrado (asumiendo que hay uno único por entidad/año).
    # Se añade manejo de errores por si falta algún dato.
    try:
        valor_ano1 = df.loc[(df.Year == parAnos[0]) & (df.Entity == entidad), "fertility_rate_hist"].values[0]
    except IndexError:
        valor_ano1 = None # O manejar como prefieras (ej. 0, np.nan)

    # Obtener el valor de la tasa de fertilidad para el segundo año seleccionado.
    try:
        valor_ano2 = df.loc[(df.Year == parAnos[1]) & (df.Entity == entidad), "fertility_rate_hist"].values[0]
    except IndexError:
        valor_ano2 = None

    # Solo procesar si tenemos datos válidos para ambos años
    if valor_ano1 is not None and valor_ano2 is not None:
        # Añadir los valores a las listas correspondientes en el diccionario 'data'.
        data[parAnos[0]].append(valor_ano1)
        data[parAnos[1]].append(valor_ano2)

        # Añadir las coordenadas para la línea que conecta los dos puntos.
        # Se añade 'None' después de cada par de puntos (x, y) para indicar a Plotly
        # que debe detener la línea actual y empezar una nueva para la siguiente entidad.
        data["line_x"].extend([valor_ano1, valor_ano2, None])
        data["line_y"].extend([entidad, entidad, None])
    else:
        # Si falta algún dato, podríamos optar por omitir la entidad o representarla de otra forma.
        # Aquí simplemente la omitimos para las líneas y puntos.
        # Podríamos añadirla a las listas de años con None si quisiéramos mostrarla de alguna manera.
        # data[parAnos[0]].append(valor_ano1) # Añadiría None si falta
        # data[parAnos[1]].append(valor_ano2) # Añadiría None si falta
        pass # Omitir entidad si faltan datos


# Opcional: Mostrar la estructura de datos preparada para Plotly (útil para depuración).
# st.json(data)

# --- Creación del Gráfico Dumbbell con Plotly ---
if Entidades.size > 0 and len(data[parAnos[0]]) > 0: # Comprobar si hay datos para graficar
    # Crear la figura principal de Plotly.
    fig = go.Figure(
        data=[
            # 1. Traza para las líneas y (opcionalmente) las flechas conectoras.
            go.Scatter(
                x=data["line_x"],       # Coordenadas X (valores de fertilidad).
                y=data["line_y"],       # Coordenadas Y (nombres de entidades).
                mode="lines" if not parFlecha else "lines+markers", # Modo: solo líneas o líneas y marcadores (flechas).
                showlegend=False,       # No mostrar esta traza en la leyenda.
                line=dict(              # Estilo de la línea.
                    color="#DBDBDB",    # Color gris claro.
                    width=3,            # Ancho de la línea.
                    dash="solid"        # Estilo de línea sólido.
                ),
                # Aplicar el diccionario de marcador de flecha solo si parFlecha es True.
                marker=dictMarker if parFlecha else None,
            ),
            # 2. Traza para los puntos (marcadores) y texto del primer año seleccionado.
            go.Scatter(
                x=data[parAnos[0]],     # Coordenadas X (valores de fertilidad del primer año).
                y=Entidades,            # Coordenadas Y (nombres de entidades).
                mode="markers+text",    # Modo: mostrar marcadores y texto asociado.
                name=str(parAnos[0]),   # Nombre de la traza para la leyenda (el año).
                marker=dict(            # Estilo del marcador.
                    color="#9FB3DF",    # Color azul claro.
                    size=15             # Tamaño del marcador.
                ),
                text=data[parAnos[0]], # Texto a mostrar (valor formateado a 1 decimal).
                textposition="middle right", # Posición del texto relativo al marcador.
                textfont=dict(size=15), # Tamaño de la fuente del texto
                texttemplate="%{text:.2f} hijos" # Plantilla para formatear el texto (opcional, si 'text' ya está formateado)
            ),
            # 3. Traza para los puntos (marcadores) y texto del segundo año seleccionado.
            go.Scatter(
                x=data[parAnos[1]],     # Coordenadas X (valores de fertilidad del segundo año).
                y=Entidades,            # Coordenadas Y (nombres de entidades).
                mode="markers+text",    # Modo: mostrar marcadores y texto asociado.
                name=str(parAnos[1]),   # Nombre de la traza para la leyenda (el año).
                marker=dict(            # Estilo del marcador.
                    color="#DDA853",    # Color naranja/dorado.
                    size=15             # Tamaño del marcador.
                ),
                text=data[parAnos[1]], # Texto a mostrar.
                textposition="middle left", # Posición del texto relativo al marcador.
                textfont=dict(size=15), # Tamaño de la fuente del texto
                texttemplate="%{text:.2f} hijos" # Plantilla para formatear el texto (opcional)
            ),
        ]
    )

    # --- Ajustes del Layout del Gráfico ---

    # Calcular la altura del gráfico dinámicamente basada en el número de entidades.
    # Se establece un mínimo y un máximo para la altura.
    alto = len(Entidades) * 25 # Ajustar el multiplicador para cambiar el espaciado vertical
    if alto > 6000:
        alto = 6000 # Altura máxima
    if alto < 400:
        alto = 400 # Altura mínima

    # Añadir una línea vertical roja para marcar la tasa de reemplazo (2.1 hijos por mujer).
    fig.add_vline(
        x=2.1,                  # Posición X de la línea.
        line_width=2,           # Ancho de la línea.
        line_dash="dash",       # Estilo de línea punteada.
        line_color="red",       # Color de la línea.
        annotation_text="Tasa de reemplazo (2.1)", # Texto de la anotación.
        annotation_position="top right", # Posición de la anotación.
        annotation_font_size=15,         # Tamaño de fuente de la anotación.
        annotation_font_color="red"      # Color de fuente de la anotación.
    )

    # Actualizar las propiedades del eje X.
    fig.update_xaxes(
        title_text="Tasa de fertilidad (promedio de hijos por mujer)", # Título del eje X.
        title_font=dict(size=20), # Tamaño de fuente del título.
        tickfont=dict(size=15)    # Tamaño de fuente de las etiquetas del eje.
    )

    # Actualizar las propiedades del eje Y.
    fig.update_yaxes(
        title_text=parCategoria,  # Título del eje Y (será "Países" o "Grupos").
        title_font=dict(size=20), # Tamaño de fuente del título.
        tickfont=dict(size=15)    # Tamaño de fuente de las etiquetas del eje (nombres de entidades).
    )

    # Actualizar el layout general de la figura.
    fig.update_layout(
        # Configuración del título del gráfico.
        title=dict(
            text=f"Evolución de la Tasa de Fertilidad: {parAnos[0]} vs {parAnos[1]}",
            font=dict(size=20) # Tamaño de fuente del título.
        ),
        height=alto, # Aplicar la altura calculada dinámicamente.
        legend_title_text="Año", # Título de la leyenda.
        # Opcional: Margen del gráfico (útil para ajustar el espaciado).
        margin=dict(l=0, r=0, t=50, b=50), # Ajustar l (left) si los nombres de entidades son largos.
        # Opcional: Estilo de fuente global.
        # font=dict(family="Arial", size=12, color="black")
    )

    # --- Mostrar el Gráfico en Streamlit ---
    # Renderiza la figura de Plotly en la aplicación Streamlit.
    # use_container_width=True hace que el gráfico se ajuste al ancho del contenedor.
    st.plotly_chart(fig, use_container_width=True)

else:
    # Mensaje si no hay datos para mostrar después de aplicar los filtros.
    st.warning(f"No se encontraron datos para las selecciones realizadas ({parCategoria}, Años: {parAnos[0]}-{parAnos[1]}, Entidades: {parEntidades if parEntidades else 'Todas'}). Por favor, ajusta los filtros.")

# Añadir una nota sobre la fuente de datos
st.markdown("---")
st.markdown("Fuente de datos: [Our World in Data](https://ourworldindata.org/grapher/children-born-per-woman)")