# """
# ================================================================================
# TUTORIAL: CLONADOR DE GRÁFICAS CON IA (PYTHON, STREAMLIT, GEMINI Y PANDAS)
# ================================================================================

# LIBRERÍAS UTILIZADAS Y CÓMO INSTALARLAS:
# Comando de instalación:
# pip install streamlit google-genai pandas plotly pillow

# Explicación de librerías:
# - streamlit: Framework para crear aplicaciones web interactivas con Python de forma rápida.
# - google.genai: SDK oficial para interactuar con la API de Google Gemini (modelos de IA).
# - pandas: Librería fundamental para manipulación y análisis de datos en tablas (DataFrames).
# - plotly.express / graph_objects: Librerías para crear gráficas interactivas de alta calidad.
# - json: Librería estándar de Python para procesar datos en formato JSON.
# - re: Librería estándar para usar Expresiones Regulares (búsqueda de patrones en texto).
# - traceback: Librería estándar para extraer y mostrar errores detallados de ejecución.
# """

import streamlit as st
from google import genai
from google.genai import types
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import re
import traceback


# ─── Configuración de la Página ────────────────────────────────────────────────
st.set_page_config(
    page_title="Chart Vision · AI Analyzer",
    page_icon="📊",
    layout="wide",
)

# ─── Configuración de la Barra Lateral (Sidebar) ────────────────────────────────
# Utilizamos @st.cache_data para que la petición de modelos no se haga cada vez 
# que interactuamos con la aplicación, ahorrando tiempo y recursos.
@st.cache_data(show_spinner="Obteniendo modelos...")
def fetch_available_models(api_key: str):
    """
    Obtiene la lista de modelos disponibles en la API de Google Gemini.
    
    Args:
        api_key (str): La clave de acceso para la API de Google Gemini.
        
    Returns:
        list: Una lista ordenada alfabéticamente con los nombres de los modelos.
              Si falla, devuelve una lista por defecto con modelos conocidos.
    """
    try:
        client = genai.Client(api_key=api_key)
        models = []
        for model in client.models.list():
            if "gemini" in model.name:            
                name = model.name.replace("models/", "")
                models.append(name)
        return sorted(models)
    except Exception:
        return ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp"]

with st.sidebar:
    st.title("📊 Chart Vision")
    st.divider()
    st.caption("Chart Vision v1.2")
    st.info("Analizador de gráficas inteligente con Google Gemini.")

# ─── Configuración de Gemini ────────────────────────────────────────────────────
# Obtenemos la clave de API desde los secretos de Streamlit (.streamlit/secrets.toml)
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    st.error("⚠️ Configura `GEMINI_API_KEY` en los Secrets de Streamlit.")
    st.stop()
st.session_state.gemini_api_key = api_key

def get_gemini_client() -> genai.Client:
    """
    Inicializa y devuelve el cliente de Gemini usando la API key de la sesión.
    
    Returns:
        genai.Client: Cliente instanciado para hacer peticiones a la IA.
    """
    return genai.Client(api_key=st.session_state.gemini_api_key)

def _image_part(img_bytes: bytes) -> types.Part:
    """
    Convierte los bytes de una imagen al formato requerido por la API de Gemini (types.Part).
    Detecta automáticamente el tipo MIME (png, jpeg, webp) leyendo los primeros bytes (Magic Numbers).
    
    Args:
        img_bytes (bytes): Los datos binarios de la imagen cargada.
        
    Returns:
        types.Part: Objeto de imagen formateado para Gemini.
    """
    if img_bytes[:4] == b'\x89PNG': mime = "image/png"
    elif img_bytes[:2] in (b'\xff\xd8',): mime = "image/jpeg"
    elif img_bytes[:4] == b'RIFF': mime = "image/webp"
    else: mime = "image/png"
    return types.Part.from_bytes(data=img_bytes, mime_type=mime)

# ─── Funciones Auxiliares ───────────────────────────────────────────────────────
def extract_json(text: str) -> dict:
    """
    Extrae un bloque JSON válido de una cadena de texto devolviendo un diccionario de Python.
    Utiliza expresiones regulares para encontrar el contenido entre las llaves {}.
    
    Args:
        text (str): Texto sin procesar devuelto por la IA.
        
    Returns:
        dict: Diccionario de Python parseado desde el JSON.
    """
    match = re.search(r'\{[\s\S]*\}', text)
    if not match: raise ValueError("No se encontró JSON en la respuesta.")
    return json.loads(match.group())

def extract_code(text: str) -> str:
    """
    Extrae código Python de un bloque de texto formateado con Markdown (```python ... ```).
    
    Args:
        text (str): Texto sin procesar.
        
    Returns:
        str: Código Python limpio.
    """
    match = re.search(r'```(?:python)?\n([\s\S]*?)```', text)
    if match: return match.group(1).strip()
    return text.strip()

# Prompt unificado con instrucciones precisas para que la IA entienda su tarea.
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
    Envía la imagen y el prompt unificado a Gemini para análisis y generación de código.
    
    Args:
        client (genai.Client): El cliente de la API de Gemini.
        img_bytes (bytes): Los bytes de la imagen a analizar.
        
    Returns:
        dict: Diccionario que contiene los datos extraídos y el código Plotly generado.
    """
    response = client.models.generate_content(
        model=st.session_state.selected_model,
        contents=[
            types.Content(parts=[
                _image_part(img_bytes),
                types.Part.from_text(text=UNIFIED_PROMPT),
            ])
        ],
    )
    return extract_json(response.text)

def build_default_df(analysis: dict) -> pd.DataFrame:
    """
    Transforma los datos extraídos por la IA (sample_data) en un DataFrame de pandas.
    Realiza transformaciones de tipos de datos basándose en el análisis de columnas.
    
    TUTORIAL PANDAS:
    - pd.DataFrame(): Convierte una lista de diccionarios en una tabla.
    - pd.to_numeric(): Convierte texto a números. El argumento errors="coerce" 
      reemplaza valores no convertibles con NaN (valores nulos de pandas).
    - pd.to_datetime(): Convierte texto a formato de fecha/hora.
    
    Args:
        analysis (dict): Diccionario generado por Gemini.
        
    Returns:
        pd.DataFrame: Un DataFrame listo para ser usado y modificado en la interfaz.
    """
    sample = analysis.get("sample_data", [])
    if sample:
        df = pd.DataFrame(sample)
        # Bucle para corregir los tipos de datos de cada columna según la IA
        for col in analysis.get("columns", []):
            if col["name"] in df.columns:
                if col["type"] == "number": 
                    # Transformación: Casting a valores numéricos
                    df[col["name"]] = pd.to_numeric(df[col["name"]], errors="coerce")
                elif col["type"] == "date": 
                    # Transformación: Casting a fechas
                    df[col["name"]] = pd.to_datetime(df[col["name"]], errors="coerce")
        return df
    return pd.DataFrame()

# ─── Interfaz de Usuario (UI) ───────────────────────────────────────────────────
st.title("Chart Vision")
st.caption("✦ Powered by Google Gemini")
st.write("Sube una imagen de cualquier gráfica y la IA la analizará, extraerá sus datos y generará código Plotly para reproducirla.")

# Tarjetas indicadoras de los pasos del proceso utilizando columnas de Streamlit
cols = st.columns(4)
steps = [
    ("01 ─ UPLOAD", "Cargar Imagen", "Sube PNG, JPG o WEBP"),
    ("02 ─ ANALYZE", "Análisis con IA", "Gemini extrae los datos"),
    ("03 ─ EDIT", "Editar Datos", "Ajusta en el editor"),
    ("04 ─ RENDER", "Generar Gráfica", "Visualiza con Plotly")
]
for i, (num, title, desc) in enumerate(steps):
    with cols[i]:
        with st.container(border=True):
            st.caption(num)
            st.write(f"**{title}**")
            st.write(desc)

st.divider()

# ─── Paso 1: Carga de Imagen ────────────────────────────────────────────────────
st.header("01 · Imagen de la Gráfica", divider="blue")

uploaded_file = st.file_uploader("Sube una imagen", type=["png", "jpg", "jpeg", "webp"], label_visibility="collapsed")

if uploaded_file:
    img_bytes = uploaded_file.read()
    c1, c2 = st.columns([1, 1])
    with c1:
        st.image(img_bytes, caption="Imagen cargada", use_container_width=True)
    with c2:
        with st.container(border=True):
            st.success("✓ Imagen lista para analizar", icon=":material/check_circle:")
            st.write("La imagen será procesada para detectar el tipo de gráfica, ejes, etiquetas y datos visibles.")
            
            # Selección de modelo dinámico
            model_options = fetch_available_models(st.session_state.gemini_api_key)
            st.session_state.selected_model = st.selectbox("Modelo de IA", options=model_options, index=0, key="model_sel")
            analyze_btn = st.button("🔍 Analizar con Gemini", use_container_width=True, type="primary")

    # ─── Paso 2: Análisis ────────────────────────────────────────────────────────
    # Guardamos los resultados en st.session_state para que no se pierdan al recargar la página
    if analyze_btn or "analysis" in st.session_state:
        if analyze_btn:
            with st.spinner("Analizando y generando código..."):
                try:
                    result = analyze_and_generate(get_gemini_client(), img_bytes)                    
                    st.session_state.analysis = result
                    st.session_state.img_bytes = img_bytes
                    # Guardar código generado desde el análisis
                    code = result.get("plotly_code", "")
                    st.session_state.generated_code = code
                    # Actualizar explícitamente el estado del área de texto
                    st.session_state.plotly_code_area = code
                except Exception as e:
                    st.error(f"Error: {e}")
                    st.stop()

        analysis = st.session_state.analysis
        st.divider()
        st.header("02 · Resultado del Análisis", divider="blue")
        
        with st.container(border=True):
            st.badge(analysis.get("chart_type", "unknown").upper(), icon="📊")
            st.subheader(analysis.get("title", "Sin título"))
            st.write(analysis.get("description", ""))
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Eje X", analysis.get("x_label", "—"))
            m2.metric("Eje Y", analysis.get("y_label", "—"))
            m3.metric("Series", len(analysis.get("series", [])))

        # ─── Paso 3: Editor de Datos (Pandas en acción) ───────────────────────────
        st.divider()
        st.header("03 · Editor de Datos", divider="blue")
        # Si no existe el DataFrame en sesión o si pulsamos el botón analizar, construimos uno nuevo
        if "df_edited" not in st.session_state or analyze_btn:
            st.session_state.df_edited = build_default_df(analysis)

        # st.data_editor nos permite interactuar y modificar el DataFrame de Pandas directamente en la UI
        st.session_state.df_edited = st.data_editor(st.session_state.df_edited, num_rows="dynamic", use_container_width=True)

        # ─── Paso 4: Generación de Código ─────────────────────────────────────────
        st.divider()
        st.header("04 · Código Generado", divider="blue")
        
        # Área de texto vinculada a la sesión para editar el código generado por Gemini
        st.text_area(
            "Edita el código si es necesario",
            height=300,
            key="plotly_code_area"
        )
        # Mantenemos sincronizado el generated_code para el Paso 5
        st.session_state.generated_code = st.session_state.plotly_code_area


        # ─── Paso 5: Renderización de la Gráfica ─────────────────────────────────
        st.divider()
        st.header("05 · Visualización", divider="blue")
        if st.button("▶ Ejecutar y Mostrar", use_container_width=True, type="primary"):
            try:
                # Recuperamos el DataFrame modificado
                df = st.session_state.df_edited
                # Creamos un entorno virtual (diccionario local_vars) pasando el DataFrame 
                # y las librerías necesarias para que la función exec() pueda ejecutarlas
                local_vars = {"df": df, "px": px, "go": go, "pd": pd}
                exec(st.session_state.generated_code, local_vars)
                
                # Rescatamos la figura creada dentro del exec()
                fig = local_vars.get("fig")
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                    st.divider()
                    st.subheader("Comparación")
                    cc1, cc2 = st.columns(2)
                    cc1.image(img_bytes, caption="Original")
                    cc2.plotly_chart(fig, use_container_width=True, key="comp")
                else:
                    st.error("No se generó la variable `fig`.")
            except Exception as e:
                st.error(f"Error de ejecución: {e}")
                # Mostramos la traza exacta del error usando traceback
                with st.expander("Traceback"): st.code(traceback.format_exc())

else:
    st.info("Sube una imagen para comenzar el análisis.", icon=":material/upload:")