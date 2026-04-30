import streamlit as st # pip install streamlit
from google import genai # pip install google-generativeai
from google.genai import types
import pandas as pd # pip install pandas
import plotly.express as px # pip install plotly
import plotly.graph_objects as go # pip install plotly
import json # Librería estándar de Python para trabajar con JSON
import re # Librería estándar de Python para expresiones regulares
import traceback # Librería estándar de Python para imprimir trazas de error

# ─── Configuración de la Página ────────────────────────────────────────────────
# Configura las opciones de la página de Streamlit.
st.set_page_config(
    page_title="Decompilador de Charts · AI Analyzer", # Título que aparece en la pestaña del navegador
    page_icon="📊", # Ícono que aparece en la pestaña del navegador
    layout="wide", # Establece el diseño de la página en "wide" para ocupar todo el ancho disponible
)

# ─── Configuración de la Barra Lateral ──────────────────────────────────────────
@st.cache_data(show_spinner="Obteniendo modelos...")
def fetch_available_models(api_key: str):
    """
    Obtiene los modelos disponibles de la API de Gemini.

    Args:
        api_key (str): La clave de la API de Google Gemini.

    Returns:
        list: Una lista de nombres de modelos Gemini disponibles, o una lista predeterminada en caso de error.
    """
    try:
        # Inicializa el cliente de la API de Gemini con la clave proporcionada.
        client = genai.Client(api_key=api_key)
        models = []
        # Itera sobre todos los modelos disponibles.
        for model in client.models.list():
            # Filtra solo los modelos que contienen "gemini" en su nombre.
            if "gemini" in model.name:            
                name = model.name.replace("models/", "") # Elimina el prefijo "models/"
                models.append(name) # Añade el nombre del modelo a la lista
        return sorted(models) # Devuelve la lista de modelos ordenada alfabéticamente
    except Exception:
        # En caso de error, devuelve una lista predeterminada de modelos.
        return ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp"]

# Define el contenido de la barra lateral de Streamlit.
with st.sidebar:
    st.title("📊 Chart Vision") # Título de la aplicación en la barra lateral
    st.divider() # Un divisor visual
    st.caption("Chart Vision v1.2") # Versión de la aplicación
    st.info("Analizador de gráficas inteligente con Google Gemini.") # Mensaje informativo

# ─── Configuración de Gemini ────────────────────────────────────────────────────
# Intenta obtener la clave de la API de Gemini desde los secretos de Streamlit.
api_key = st.secrets.get("GEMINI_API_KEY", "")
# Si la clave de la API no está configurada, muestra un error y detiene la ejecución.
if not api_key:
    st.error("⚠️ Configura `GEMINI_API_KEY` en los Secrets de Streamlit.")
    st.stop()
# Almacena la clave de la API en el estado de la sesión de Streamlit.
st.session_state.gemini_api_key = api_key

def get_gemini_client() -> genai.Client:
    """
    Obtiene una instancia del cliente de la API de Gemini.

    Returns:
        genai.Client: Una instancia del cliente de Gemini.
    """
    # Retorna un nuevo cliente de Gemini usando la clave de API almacenada en el estado de la sesión.
    return genai.Client(api_key=st.session_state.gemini_api_key)

def _image_part(img_bytes: bytes) -> types.Part:
    """
    Crea una parte de imagen para la API de Gemini a partir de bytes de imagen.

    Args:
        img_bytes (bytes): Los bytes de la imagen.

    Returns:
        types.Part: Una parte de contenido de imagen con el tipo MIME detectado.
    """
    # Detecta el tipo MIME de la imagen basándose en los primeros bytes.
    if img_bytes[:4] == b'\x89PNG': mime = "image/png"
    elif img_bytes[:2] in (b'\xff\xd8',): mime = "image/jpeg"
    elif img_bytes[:4] == b'RIFF': mime = "image/webp"
    else: mime = "image/png" # Por defecto, si no se puede detectar, asume PNG.
    # Crea una parte de contenido a partir de los bytes de la imagen y el tipo MIME.
    return types.Part.from_bytes(data=img_bytes, mime_type=mime)

# ─── Funciones Auxiliares ───────────────────────────────────────────────────────
def extract_json(text: str) -> dict:
    """
    Extrae un objeto JSON de una cadena de texto.

    Args:
        text (str): La cadena de texto de la cual extraer el JSON.

    Returns:
        dict: El objeto JSON parseado.

    Raises:
        ValueError: Si no se encuentra un objeto JSON válido en la cadena.
    """
    # Busca el primer objeto JSON (delimitado por llaves {}) en la cadena.
    match = re.search(r'\{[\s\S]*\}', text)
    if not match: 
        raise ValueError("No se encontró JSON en la respuesta.") # Lanza un error si no se encuentra JSON.
    return json.loads(match.group()) # Parsea la cadena JSON encontrada a un diccionario Python.

def extract_code(text: str) -> str:
    """
    Extrae un bloque de código Python de una cadena de texto.

    Args:
        text (str): La cadena de texto de la cual extraer el código.

    Returns:
        str: El bloque de código Python extraído.
    """
    # Busca un bloque de código Python delimitado por "```python" o "```".
    match = re.search(r'```(?:python)?\n([\s\S]*?)```', text)
    if match: 
        return match.group(1).strip() # Retorna el contenido del bloque de código, eliminando espacios extra.
    return text.strip() # Si no se encuentra un bloque de código, retorna el texto original sin espacios.

# Mensaje unificado que se envía a Gemini para el análisis de la imagen.
UNIFIED_PROMPT = """
Analiza esta imagen de una gráfica/chart con detalle y responde ÚNICAMENTE con un objeto JSON válido (sin texto extra, sin markdown).

El JSON debe tener exactamente esta estructura:
{
  "chart_type": "tipo de gráfica en inglés",
  "title": "título de la gráfica",
  "x_label": "etiqueta eje X",
  "y_label": "etiqueta eje Y",
  "description": "descripción breve",
  "columns": [{"name": "Nombre", "type": "category|number|date"}],
  "sample_data": [{"Col1": val1}],
  "color_scheme": "descripción de colores y opacidad",
  "series": ["series"],
  "plotly_code": "Código Python con Plotly que reproduzca la gráfica fielmente. Usa pandas (variable `df` ya disponible), asigna el resultado a `fig`, usa rgba para transparencias si aplica, usa anotaciones si se requiere, adiciona el título si requieres con HMTL, emula el color de fondo y no llames a fig.show()."
}

Extrae los datos reales visibles para `sample_data`. El código debe ser completo y estar listo para ejecutarse con la variable `df`.
"""

def analyze_and_generate(client: genai.Client, img_bytes: bytes) -> dict:
    """
    Envía una imagen a Gemini para un análisis unificado y generación de código.

    Args:
        client (genai.Client): El cliente de la API de Gemini.
        img_bytes (bytes): Los bytes de la imagen a analizar.

    Returns:
        dict: El objeto JSON resultante del análisis de Gemini.
    """
    # Envía la imagen y el prompt unificado a Gemini para generar contenido.
    response = client.models.generate_content(
        model=st.session_state.selected_model, # Usa el modelo seleccionado por el usuario.
        contents=[
            types.Content(parts=[
                _image_part(img_bytes), # La imagen como parte del contenido.
                types.Part.from_text(text=UNIFIED_PROMPT), # El prompt de texto como parte del contenido.
            ])
        ],
    )
    return extract_json(response.text) # Extrae y retorna el JSON de la respuesta.

def build_default_df(analysis: dict) -> pd.DataFrame:
    """
    Construye un DataFrame de pandas a partir de los datos de muestra extraídos por Gemini.

    Args:
        analysis (dict): El diccionario de análisis devuelto por Gemini.

    Returns:
        pd.DataFrame: Un DataFrame de pandas con los datos de muestra, con tipos de columna ajustados.
    """
    sample = analysis.get("sample_data", []) # Obtiene los datos de muestra del análisis.
    if sample:
        df = pd.DataFrame(sample) # Crea un DataFrame a partir de los datos de muestra.
        # Itera sobre las columnas definidas en el análisis para ajustar sus tipos de datos.
        for col in analysis.get("columns", []):
            if col["name"] in df.columns:
                if col["type"] == "number": 
                    # Convierte la columna a tipo numérico, forzando errores a NaN.
                    df[col["name"]] = pd.to_numeric(df[col["name"]], errors="coerce")
                elif col["type"] == "date": 
                    # Convierte la columna a tipo fecha y hora, forzando errores a NaT.
                    df[col["name"]] = pd.to_datetime(df[col["name"]], errors="coerce")
        return df
    return pd.DataFrame() # Retorna un DataFrame vacío si no hay datos de muestra.

# ─── Interfaz de Usuario (UI) ──────────────────────────────────────────────────
st.title("Decompilador de Charts: :orange[:material/insert_chart:] :material/arrow_forward: :blue[:material/integration_instructions:]") # Título principal de la aplicación.
st.caption("✦ Powered by Google Gemini") # Subtítulo indicando la tecnología usada.
st.write("Sube una imagen de cualquier gráfica y la IA la analizará, extraerá sus datos y generará código Plotly para reproducirla.") # Descripción breve.

# Indicadores de pasos usando columnas y "cards".
cols = st.columns(4) # Crea 4 columnas para los pasos.
steps = [
    ("01 ─ CARGAR", "Cargar Imagen", "Sube PNG, JPG o WEBP",":material/upload:"),
    ("02 ─ ANALIZAR", "Análisis con IA", "Gemini extrae los datos",":material/psychology:"),
    ("03 ─ EDITAR", "Editar Datos", "Ajusta en el editor",":material/edit:"),
    ("04 ─ RENDERIZAR", "Generar Gráfica", "Visualiza con Plotly",":material/visibility:")
]
# Itera sobre los pasos para mostrarlos en las columnas.
for i, (num, title, desc, icon) in enumerate(steps):
    with cols[i]:
        with st.container(border=True): # Cada paso está dentro de un contenedor con borde.
            colscard = st.columns([1, 4],vertical_alignment="center") # Crea dos columnas dentro del contenedor para el número y el texto.
            with colscard[0]:
                st.write(f"## :blue[{icon}]") # Icono para cada paso.
            with colscard[1]:   
                st.write(f"**{num}**") # Número del paso.
                st.write(f"#### {title}") # Título del paso en negritas.
                st.caption(desc) # Descripción del paso.

st.divider() # Un divisor visual.

# ─── Paso 1: Carga de Imagen ────────────────────────────────────────────────────
st.header("01 · Imagen de la Gráfica", divider="blue") # Encabezado para el primer paso.

# Widget para subir archivos.
uploaded_file = st.file_uploader("Sube una imagen", type=["png", "jpg", "jpeg", "webp"], label_visibility="collapsed")

# Si se ha subido un archivo:
if uploaded_file:
    img_bytes = uploaded_file.read() # Lee los bytes de la imagen.
    c1, c2 = st.columns([1, 1]) # Crea dos columnas para la imagen y los controles.
    with c1:
        st.image(img_bytes, caption="Imagen cargada", use_container_width=True) # Muestra la imagen subida.
    with c2:
        with st.container(border=True):
            st.success("✓ Imagen lista para analizar", icon=":material/check_circle:") # Mensaje de éxito.
            st.write("La imagen será procesada para detectar el tipo de gráfica, ejes, etiquetas y datos visibles.")
            
            # Carga los modelos disponibles y permite al usuario seleccionar uno.
            model_options = fetch_available_models(st.session_state.gemini_api_key)
            st.session_state.selected_model = st.selectbox("Modelo de IA", options=model_options, index=0, key="model_sel")
            # Botón para iniciar el análisis con Gemini.
            analyze_btn = st.button("🔍 Analizar con Gemini", use_container_width=True, type="primary")

    # ─── Paso 2: Análisis ───────────────────────────────────────────────────────
    # Si se pulsa el botón de analizar o ya hay un análisis en el estado de la sesión:
    if analyze_btn or "analysis" in st.session_state:
        if analyze_btn:
            with st.spinner("Analizando y generando código..."): # Muestra un spinner mientras se analiza.
                try:
                    # Llama a la función de análisis y generación de código.
                    result = analyze_and_generate(get_gemini_client(), img_bytes)                    
                    st.session_state.analysis = result # Almacena el resultado del análisis.
                    st.session_state.img_bytes = img_bytes # Almacena los bytes de la imagen.
                    # Almacena el código generado.
                    code = result.get("plotly_code", "")
                    st.session_state.generated_code = code
                    # Actualiza el estado del área de texto para que coincida.
                    st.session_state.plotly_code_area = code
                except Exception as e:
                    st.error(f"Error: {e}") # Muestra un error si falla el análisis.
                    st.stop()

        analysis = st.session_state.analysis # Recupera el análisis del estado de la sesión.
        st.divider()
        st.header("02 · Resultado del Análisis", divider="blue") # Encabezado para el paso de resultados.
        
        with st.container(border=True):
            # Muestra el tipo de gráfica, título y descripción.
            st.badge(analysis.get("chart_type", "unknown").upper(), icon="📊")
            st.subheader(analysis.get("title", "Sin título"))
            st.write(analysis.get("description", ""))
            
            m1, m2, m3 = st.columns(3) # Muestra métricas clave.
            m1.metric("Eje X", analysis.get("x_label", "—"))
            m2.metric("Eje Y", analysis.get("y_label", "—"))
            m3.metric("Series", len(analysis.get("series", [])))

        # ─── Paso 3: Editor de Datos ───────────────────────────────────────────────
        st.divider()
        st.header("03 · Editor de Datos", divider="blue") # Encabezado para el editor de datos.
        # Si no hay un DataFrame editado o se acaba de realizar un nuevo análisis:
        if "df_edited" not in st.session_state or analyze_btn:
            # Construye el DataFrame por defecto a partir del análisis.
            st.session_state.df_edited = build_default_df(analysis)

        # Permite al usuario editar el DataFrame en Streamlit.
        st.session_state.df_edited = st.data_editor(st.session_state.df_edited, num_rows="dynamic", use_container_width=True)

        # ─── Paso 4: Generación de Código ──────────────────────────────────────────
        st.divider()
        st.header("04 · Código Generado", divider="blue") # Encabezado para el código generado.
        
        # Área de texto para mostrar y editar el código Plotly.
        st.text_area(
            "Edita el código si es necesario",
            height=300,
            key="plotly_code_area" # Clave para vincular al estado de la sesión.
        )
        # Sincroniza el código generado con el contenido del área de texto.
        st.session_state.generated_code = st.session_state.plotly_code_area


        # ─── Paso 5: Visualización ──────────────────────────────────────────────
        st.divider()
        st.header("05 · Visualización", divider="blue") # Encabezado para la visualización.
        # Botón para ejecutar el código y mostrar la gráfica.
        if st.button("▶ Ejecutar y Mostrar", use_container_width=True, type="primary"):
            try:
                df = st.session_state.df_edited # Obtiene el DataFrame editado.
                # Define las variables locales disponibles para el código a ejecutar.
                local_vars = {"df": df, "px": px, "go": go, "pd": pd}
                # Ejecuta el código Plotly generado o editado.
                exec(st.session_state.generated_code, local_vars)
                fig = local_vars.get("fig") # Intenta obtener la figura generada.
                if fig:
                    st.plotly_chart(fig, use_container_width=True) # Muestra la gráfica de Plotly.
                    st.divider()
                    st.subheader("Comparación") # Sección de comparación.
                    cc1, cc2 = st.columns(2)
                    cc1.image(img_bytes, caption="Original") # Muestra la imagen original.
                    cc2.plotly_chart(fig, use_container_width=True, key="comp") # Muestra la gráfica generada para comparación.
                else:
                    st.error("No se generó la variable `fig`.") # Error si no se generó la figura.
            except Exception as e:
                st.error(f"Error de ejecución: {e}") # Muestra errores de ejecución.
                with st.expander("Traceback"): st.code(traceback.format_exc()) # Expansor para ver la traza de error.

else:
    st.info("Sube una imagen para comenzar el análisis.", icon=":material/upload:") # Mensaje inicial si no hay imagen.