# -*- coding: utf-8 -*-
"""
Streamlit Dashboard: Call Center Ecommerce KPIs
===============================================

Dashboard analítico para el líder de un call center de ecommerce.
Solo componentes nativos de Streamlit, tema config.toml e íconos Material.
"""

# ****************************************
# IMPORTACION DE LIBRERÍAS
# ****************************************

# from __future__ import annotations
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# ****************************************
# CONFIGURACIÓN INICIAL
# ****************************************
st.set_page_config(
    page_title="Call Center Ecommerce | Dashboard",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------
# UNICO BLOQUE CSS PERMITIDO
# ----------------------------------------
st.markdown("""
<style>
div[class*='st-key-kpi'] {
    background-color: #FFFFFF;
    border-radius: 10px;
    padding: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}
</style>
""", unsafe_allow_html=True)

# Colores corporativos (usados en gráficos)
AZUL = "#0F4C81"
ROJO = "#D64550"
VERDE = "#2CA02C"
AMBAR = "#F5A623"
GRIS = "#6B7280"
GRIS_CLARO = "#E5E7EB"
TEXTO = "#1F2937"
FONDO = "#FFFFFF"


# ****************************************
# DATASETS: RUTAS Y COLUMNAS
# ****************************************
BASE_DIR = Path(__file__).resolve().parent
RUTA_LLAMADAS = BASE_DIR / "llamadas_cdr.csv"
RUTA_CASOS = BASE_DIR / "casos_tickets.csv"

COLUMNAS_LLAMADAS = [
    "id_llamada", "fecha", "hora", "fecha_hora_entrada",
    "id_cliente", "id_agente", "cola", "tipo_llamada",
    "motivo", "resultado_llamada", "espera_seg", "duracion_seg", "acw_seg",
    "escalado_a", "dia_semana",
]
COLUMNAS_CASOS = [
    "id_caso", "id_llamada", "fecha_apertura", "id_cliente", "id_agente",
    "categoria", "estado_caso", "fcr", "reincidencia",
    "horas_resolucion", "csat", "valor_orden",
]

# ****************************************
# FUNCIONES UTILITARIAS
# ****************************************

def formatear_valor(valor: float | None, formato: str) -> str:
    """Convierte un número a string con el formato deseado."""
    if valor is None or (isinstance(valor, float) and __import__("numpy").isnan(valor)):
        return "--"
    if formato == "pct":
        return f"{valor:.1f}%"
    if formato == "seg":
        return f"{valor:.0f} s"
    if formato == "num":
        return f"{valor:,.0f}"
    if formato == "csat":
        return f"{valor:.2f} / 5"
    if formato == "money":
        return f"${valor:,.0f}"
    if formato == "horas":
        return f"{valor:.1f} h"
    return str(valor)


def aplicar_estilo_grafico(fig, altura: int = 400):
    """Aplica estilo común a los gráficos Plotly."""
    fig.update_layout(
        height=altura,
        template="plotly_white",
        paper_bgcolor=FONDO,
        plot_bgcolor=FONDO,
        font=dict(color=TEXTO),
        margin=dict(l=10, r=10, t=50, b=10),
        legend_title_text="",
        title_font_size=20,
    )
    return fig


# ****************************************
# FUNCIONES DE CARGA Y LIMPIEZA DE DATOS
# ****************************************

def validar_columnas(df: pd.DataFrame, columnas: Any, nombre_archivo: str) -> None:
    """Verifica que el DataFrame tenga todas las columnas esperadas."""
    faltantes = [col for col in columnas if col not in df.columns]
    if faltantes:
        raise ValueError(
            f"El archivo `{nombre_archivo}` no tiene estas columnas: "
            f"{', '.join(faltantes)}"
        )

@st.cache_data(show_spinner=False)
def cargar_llamadas(ruta: str) -> pd.DataFrame:
    """Carga y normaliza el archivo de llamadas CDR."""
    df = pd.read_csv(ruta, encoding="utf-8")
    validar_columnas(df, COLUMNAS_LLAMADAS, Path(ruta).name)

    # Convertir tipos de datos
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df["fecha_hora_entrada"] = pd.to_datetime(
        df["fecha_hora_entrada"], errors="coerce"
    )
    df["hora"] = pd.to_numeric(df["hora"], errors="coerce")
    df = df.dropna(subset=["fecha", "hora"]).copy()
    df["hora"] = df["hora"].astype(int)

    # Llenar valores nulos en columnas de texto
    for col in ["id_llamada", "id_cliente", "cola", "tipo_llamada", "motivo",
                "resultado_llamada", "dia_semana"]:
        df[col] = df[col].fillna("").astype(str).str.strip()

    df["id_agente"] = df["id_agente"].fillna("").astype(str).str.strip()
    df["escalado_a"] = df["escalado_a"].fillna("").astype(str).str.strip()
    df["resultado_llamada"] = df["resultado_llamada"].str.lower()

    # Columnas derivadas para los cálculos
    df["atendida"] = df["resultado_llamada"].eq("atendida")
    df["abandonada"] = df["resultado_llamada"].eq("abandonada")
    df["aht_seg"] = (df["duracion_seg"] + df["acw_seg"]).where(df["atendida"])
    df["cola_etiqueta"] = df["cola"].map(
        {"Soporte_Pedidos": "Soporte pedidos",
         "Soporte_Envios": "Soporte envíos",
         "Retenciones": "Retenciones",
         "Ventas": "Ventas"}
    ).fillna(df["cola"])
    df["motivo_etiqueta"] = df["motivo"].map(
        {"estado_envio": "Estado de envío", "devolucion": "Devolución",
         "problema_pago": "Problema de pago", "cambio_producto": "Cambio de producto",
         "facturacion": "Facturación", "cuenta_claves": "Cuenta / claves",
         "reclamo_calidad": "Reclamo de calidad", "informacion_preventa": "Información preventa"}
    ).fillna(df["motivo"])

    if df.empty:
        raise ValueError("El archivo `llamadas_cdr.csv` no tiene filas válidas.")
    return df

@st.cache_data(show_spinner=False)
def cargar_casos(ruta: str) -> pd.DataFrame:
    """Carga y normaliza el archivo de casos/tickets."""
    df = pd.read_csv(ruta, encoding="utf-8")
    validar_columnas(df, COLUMNAS_CASOS, Path(ruta).name)

    df["fecha_apertura"] = pd.to_datetime(df["fecha_apertura"], errors="coerce")
    df = df.dropna(subset=["fecha_apertura"]).copy()

    for col in ["fcr", "reincidencia"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    for col in ["horas_resolucion", "valor_orden"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["csat"] = pd.to_numeric(df["csat"], errors="coerce").clip(lower=1, upper=5)

    for col in ["id_caso", "id_llamada", "id_cliente", "categoria", "estado_caso"]:
        df[col] = df[col].fillna("").astype(str).str.strip()

    df["id_agente"] = df["id_agente"].fillna("").astype(str).str.strip()
    df["categoria_etiqueta"] = df["categoria"].map(
        {"estado_envio": "Estado de envío", "devolucion": "Devolución",
         "problema_pago": "Problema de pago", "cambio_producto": "Cambio de producto",
         "facturacion": "Facturación", "cuenta_claves": "Cuenta / claves",
         "reclamo_calidad": "Reclamo de calidad", "informacion_preventa": "Información preventa"}
    ).fillna(df["categoria"])

    if df.empty:
        raise ValueError("El archivo `casos_tickets.csv` no tiene filas válidas.")
    return df

# ****************************************
# FUNCIONES DE CÁLCULO DE KPIs
# ****************************************

def calcular_nivel_servicio(df: pd.DataFrame, umbral_seg: int) -> float | None:
    """% de llamadas con espera <= umbral sobre el total ofrecido."""
    if df.empty:
        return None        
    return float(df["espera_seg"].le(umbral_seg).mean() * 100)

def calcular_tasa_abandono(df: pd.DataFrame) -> float | None:
    """% de llamadas abandonadas sobre el total ofrecido."""
    if df.empty:
        return None
    return float(df["abandonada"].mean() * 100)

def calcular_asa(df: pd.DataFrame) -> float | None:
    """Segundos promedio de espera de las llamadas atendidas."""
    atendidas = df.loc[df["atendida"], "espera_seg"]
    if atendidas.empty:
        return None
    return float(atendidas.mean())

def calcular_aht(df: pd.DataFrame) -> float | None:
    """Segundos promedio de (duración + ACW) de llamadas atendidas."""
    atendidas = df.loc[df["atendida"], "aht_seg"].dropna()
    if atendidas.empty:
        return None
    return float(atendidas.mean())

def calcular_tasa_escalamiento(df: pd.DataFrame) -> float | None:
    """Tasa de escalamiento de llamadas."""
    if df.empty:
        return None
    atendidas = df.loc[df["atendida"], "escalado_a"]
    if atendidas.empty:
        return None
    return float(atendidas.ne("").mean() * 100)

def calcular_fcr(casos: pd.DataFrame) -> float | None:
    """% de casos resueltos en el primer contacto."""
    if casos.empty:
        return None
    return float(casos["fcr"].mean() * 100)

def calcular_reincidencia(casos: pd.DataFrame) -> float | None:
    """% de casos con reincidencia (reapertura o nueva llamada)."""
    if casos.empty:
        return None
    return float(casos["reincidencia"].mean() * 100)

def calcular_csat_promedio(casos: pd.DataFrame) -> float | None:
    """Promedio de CSAT en escala 1-5."""
    if casos.empty:
        return None
    notas = casos["csat"].dropna()
    if notas.empty:
        return None
    return float(notas.mean())


def calcular_csat_positivo(casos: pd.DataFrame, umbral: float = 4.0) -> float | None:
    """% de casos con CSAT >= umbral (positivo)."""
    if casos.empty:
        return None
    notas = casos["csat"].dropna()
    if notas.empty:
        return None
    return float(notas.ge(umbral).mean() * 100)

def calcular_horas_resolucion(casos: pd.DataFrame) -> float | None:
    """Horas promedio hasta la resolución de los casos."""
    if casos.empty:
        return None
    horas = casos["horas_resolucion"].dropna()
    if horas.empty:
        return None
    return float(horas.mean())

# ****************************************
# FILTROS LATERAL (máximo 4 selectores)
# ****************************************

def filtrar_llamadas(
    df: pd.DataFrame,
    inicio: date,
    fin: date,
    agentes=None,
    colas=None,
   hora_min=0,
    hora_max=23,
) -> pd.DataFrame:
    """Filtra llamadas por fecha, agentes, colas y franja horaria."""
    if df.empty:
        return df.copy()

    inicio_ts = pd.Timestamp(inicio).normalize()
    fin_ts = pd.Timestamp(fin).normalize() + pd.Timedelta(days=1)

    mascara = df["fecha"].ge(inicio_ts) & df["fecha"].lt(fin_ts)
    mascara &= df["hora"].between(hora_min, hora_max, inclusive="both")

    if agentes:
        mascara &= df["id_agente"].isin(list(agentes))
    if colas:
        mascara &= df["cola"].isin(list(colas))

    return df.loc[mascara].copy()

def filtrar_casos_por_llamadas(casos: pd.DataFrame, llamadas: pd.DataFrame) -> pd.DataFrame:
    """Filtra casos usando las llamadas ya filtradas (mismo id_llamada)."""
    if casos.empty or llamadas.empty:
        return casos.iloc[0:0].copy()
    return casos.loc[casos["id_llamada"].isin(llamadas["id_llamada"].unique())].copy()

def normalizar_seleccion(seleccion) -> list | None:
    """Convierte la selección del multiselect: retorna None si no hay selección específica."""
    if not seleccion:
        return None
    valores = [v for v in seleccion if v != "Todos"]
    return valores or None

# ****************************************
# POPUP: Umbrales editables (@st.dialog)
# ****************************************

@st.dialog("Umbrales de evaluación")
def popup_umbrales(umbrales_actuales: dict) -> dict | None:
    """Popup para modificar los umbrales de las métricas."""
    st.subheader("⚙️ Umbrales de evaluación")

    col1, col2 = st.columns(2)

    with col1:
        nuevo_tiempo_espera = st.number_input(
            "Tiempo mínimo espera (seg)",
            min_value=0, max_value=600, value=int(umbrales_actuales["tiempo_min_espera"]),
            step=5, help="Segundos mínimo de espera para considerar SL (mayor es peor)"
        )
        nuevo_sl = st.number_input(
            "Nivel de Servicio (%)",
            min_value=0, max_value=100, value=int(umbrales_actuales["nivel_servicio"]),
            step=1, help="% llamadas con espera ≤ umbral (mayor es mejor)"
        )
        nuevo_abandono = st.number_input(
            "Tasa de Abandono (%)",
            min_value=0, max_value=100, value=int(umbrales_actuales["abandono"]),
            step=1, help="% llamadas abandonadas (menor es mejor)"
        )
        nuevo_asa = st.number_input(
            "ASA (segundos)",
            min_value=0, max_value=3600, value=int(umbrales_actuales["asa"]),
            step=5, help="Segundos promedio de espera (menor es mejor)"
        )
        nuevo_aht = st.number_input(
            "AHT (segundos)",
            min_value=0, max_value=3600, value=int(umbrales_actuales["aht"]),
            step=5, help="(Conversación + ACW) promedio (menor es mejor)"
        )

    with col2:
        nuevo_escalamiento = st.number_input(
            "Escalamiento (%)",
            min_value=0, max_value=100, value=int(umbrales_actuales["escalamiento"]),
            step=1, help="% llamadas escaladas (menor es mejor)"
        )
        nuevo_fcr = st.number_input(
            "FCR (%)",
            min_value=0, max_value=100, value=int(umbrales_actuales["fcr"]),
            step=1, help="% casos resueltos en primer contacto (mayor es mejor)"
        )
        nueva_reincidencia = st.number_input(
            "Reincidencia (%)",
            min_value=0, max_value=100, value=int(umbrales_actuales["reincidencia"]),
            step=1, help="% casos con reincidencia (menor es mejor)"
        )
        nuevo_csat = st.number_input(
            "CSAT",
            min_value=1, max_value=5, value=int(umbrales_actuales["csat"]),
            step=1, help="Promedio escala 1-5 (mayor es mejor)"
        )
        horas_resolucion = st.number_input(
            "Horas de resolución",
            min_value=0, max_value=168, value=int(umbrales_actuales["horas_resolucion"]),
            step=1, help="Horas promedio hasta resolución (menor es mejor)"
        )

    if st.button("Guardar umbrales", type="primary"):
        actualizados = {
            "nivel_servicio": float(nuevo_sl),
            "tiempo_min_espera": float(nuevo_tiempo_espera),
            "abandono": float(nuevo_abandono),
            "asa": float(nuevo_asa),
            "aht": float(nuevo_aht),
            "escalamiento": float(nuevo_escalamiento),
            "fcr": float(nuevo_fcr),
            "reincidencia": float(nueva_reincidencia),
            "csat": float(nuevo_csat),
            "horas_resolucion": float(horas_resolucion),
        }
        st.session_state["umbrales"] = actualizados
        st.rerun()

    return None


# ****************************************
# POPUP: Definiciones y fórmulas (@st.dialog)
# ****************************************

@st.dialog("Definiciones y fórmulas", width="large")
def popup_definiciones() -> None:
    """Popup con la lista completa de métricas, definiciones y fórmulas."""
    st.subheader("📚 Definiciones y fórmulas de métricas")

    definiciones = [
        ("Nivel de Servicio (SL)", "Llamadas atendidas dentro del tiempo objetivo",
         "Fórmula: (llamadas con espera ≤ umbral) / total × 100",
         "Meta por defecto: 80% — Cuanto mayor, mejor"),
        ("Tasa de Abandono", "Llamadas que se cortan antes de hablar con un agente",
         "Fórmula: llamadas abandonadas / total × 100",
         "Meta por defecto: <8% — Cuanto menor, mejor"),
        ("ASA (Average Speed of Answer)", "Tiempo promedio de espera de las llamadas atendidas",
         "Fórmula: suma de esperas / llamadas atendidas (segundos)",
         "Meta por defecto: ≤30 s — Cuanto menor, mejor"),
        ("AHT (Average Handling Time)", "Tiempo medio de atención por llamada (duración + ACW)",
         "Fórmula: (duración + ACW) promedio / llamadas atendidas (segundos)",
         "Meta por defecto: ≤350 s — Cuanto menor, mejor"),
        ("Escalamiento", "Llamadas que requieren intervención de supervisor o área especializada",
         "Fórmula: llamadas con escalado_a no vacío / atendidas × 100",
         "Meta por defecto: ≤20% — Cuanto menor, mejor"),
        ("FCR (First Contact Resolution)", "Casos resueltos en el primer contacto",
         "Fórmula: casos con fcr = 1 / total × 100",
         "Meta por defecto: ≥70% — Cuanto mayor, mejor"),
        ("Reincidencia", "Casos que requirieron nueva llamada o reapertura después de resolverse",
         "Fórmula: casos con reincidencia = 1 / total × 100",
         "Meta por defecto: ≤30% — Cuanto menor, mejor"),
        ("CSAT (Customer Satisfaction)", "Satisfacción del cliente en escala 1-5",
         "Fórmula: promedio de las notas CSAT (1-5)",
         "Meta por defecto: ≥3.5 — Cuanto mayor, mejor"),
        ("Horas de resolución", "Tiempo promedio hasta la resolución de casos/tickets",
         "Fórmula: promedio de horas_resolucion sobre todos los casos (horas)",
         "Meta por defecto: ≤24 h — Cuanto menor, mejor"),
    ]

    # Tabla con íconos Material
    filas = []
    for nombre, definicion, formula, interpretacion in definiciones:
        filas.append({
            "Métrica": f"**{nombre}**",
            "Definición": definicion,
            "Fórmula": formula,
            "Interpretación": interpretacion,
        })

    st.table(filas)


# ****************************************
# INICIALIZACIÓN DE SESSION_STATE
# ****************************************

# Fechas por defecto: últimos 30 días
if "fecha_min" not in st.session_state:
    try:
        llamadas_raw = cargar_llamadas(str(RUTA_LLAMADAS))
        fecha_min = llamadas_raw["fecha"].min().date()
        fecha_max = llamadas_raw["fecha"].max().date()
    except Exception:
        fecha_min = date(2026, 1, 1)
        fecha_max = date(2026, 12, 31)
    st.session_state.fecha_min = fecha_min
    st.session_state.fecha_max = fecha_max

if "umbrales" not in st.session_state:
    st.session_state["umbrales"] = {
        "nivel_servicio": 80.0,
        "tiempo_min_espera": 20,
        "abandono": 8.0,
        "asa": 30.0,
        "aht": 350.0,
        "escalamiento": 20.0,
        "fcr": 70.0,
        "reincidencia": 30.0,
        "csat": 3.5,
        "horas_resolucion": 24.0,
    }

# ****************************************
# CARGAR DATOS
# ****************************************

try:
    with st.spinner("Cargando datos..."):
        llamadas = cargar_llamadas(str(RUTA_LLAMADAS))
        casos = cargar_casos(str(RUTA_CASOS))
except FileNotFoundError:
    st.error("No se encontraron los archivos CSV. "
             "Verifica que `llamadas_cdr.csv` y `casos_tickets.csv` "
             "estén en la misma carpeta que `app.py`.")
    st.stop()
except ValueError as e:
    st.error(f"Error en los datos: {e}")
    st.stop()
except Exception as e:
    st.error(f"Error inesperado: {e}")
    st.stop()


# Fechas por defecto: últimos 30 días sobre los datos cargados
fecha_min = max(llamadas["fecha"].min().date(), st.session_state.fecha_min)
fecha_max = llamadas["fecha"].max().date()
fecha_inicio_default = max(fecha_min, fecha_max - timedelta(days=29))
fecha_fin_default = fecha_max

# Inicializar filtros en session_state si no existen
filtros_params = {
    "f_fechas": (fecha_inicio_default, fecha_fin_default),
    "f_agentes": ["Todos"],
    "f_colas": ["Todos"],
    "f_horas": (0, 23),
}
for clave, valor in filtros_params.items():
    st.session_state.setdefault(clave, valor)

# Inicializar umbrales editables si no existen (ya se hizo arriba)


# ****************************************
# SIDEBAR: FILTROS (máximo 4)
# ****************************************

st.sidebar.header(":material/filter_alt: Filtros")
st.sidebar.caption("Ajusta el período y los segmentos a analizar.")

# Selector de fechas
fechas = st.sidebar.date_input(
    ":material/calendar_month: Rango de fechas",
    min_value=fecha_min,
    max_value=fecha_max,
    format="DD/MM/YYYY",
    key="f_fechas",
    help="Por defecto muestra los últimos 30 días con datos.",
)

# Normalizar selección de fechas
if isinstance(fechas, (list, tuple)):
    if len(fechas) == 2:
        inicio, fin = fechas
    elif len(fechas) == 1:
        inicio = fin = fechas[0]
    else:
        inicio, fin = fecha_inicio_default, fecha_fin_default
else:
    inicio = fin = fechas
inicio = pd.Timestamp(inicio).date()
fin = pd.Timestamp(fin).date()
if inicio > fin:
    inicio, fin = fin, inicio

# Agentes disponibles
agentes_disponibles = sorted(
    a for a in llamadas["id_agente"].dropna().unique() if a
)
colas_disponibles = sorted(llamadas["cola"].unique())

# Multiselect de agentes (incluye "Todos")
agentes_elegidos = st.sidebar.multiselect(
    ":material/support_agent: Agente(s)",
    options=["Todos", *agentes_disponibles],
    key="f_agentes",
    help="Al seleccionar un agente, se excluyen las llamadas abandonadas "
         "porque no tienen agente asignado.",
)

# Multiselect de colas
colas_elegidas = st.sidebar.multiselect(
    ":material/headset_mic: Cola(s)",
    options=["Todos", *colas_disponibles],
    format_func=lambda v: {"Soporte_Pedidos": "Soporte pedidos",
                         "Soporte_Envios": "Soporte envíos",
                         "Retenciones": "Retenciones",
                         "Ventas": "Ventas"}.get(v, v),
    key="f_colas",
)

# Normalizar selecciones
agentes_filtro = normalizar_seleccion(agentes_elegidos)
colas_filtro = normalizar_seleccion(colas_elegidas)

# Slider de franja horaria
horas_elegidas = st.sidebar.slider(
    ":material/schedule: Franja horaria",
    min_value=0, max_value=23, step=1,
    key="f_horas",
    help="Rango de horas de entrada de llamada (0-23).",
)
hora_min, hora_max = horas_elegidas

# Botón para restablecer filtros
def restablecer_filtros() -> None:
    for clave, valor in filtros_params.items():
        st.session_state[clave] = valor

st.sidebar.button(
    "Restablecer filtros", icon=":material/restart_alt:", on_click=restablecer_filtros
)

# ****************************************
# APLICAR FILTROS Y CALCULAR KPIs
# ****************************************

llamadas_f = filtrar_llamadas(
    llamadas, inicio=inicio, fin=fin,
    agentes=agentes_filtro, colas=colas_filtro,
    hora_min=hora_min, hora_max=hora_max,
)
casos_f = filtrar_casos_por_llamadas(casos, llamadas_f)

# Obtener umbrales activos
umbrales = st.session_state["umbrales"]

# Calcular todos los KPIs con umbrales activos
kpis = {
    "n_llamadas": int(len(llamadas_f)),
    "n_atendidas": int(llamadas_f["atendida"].sum()) if not llamadas_f.empty else 0,
    "n_casos": int(len(casos_f)),
    "sl_pct": calcular_nivel_servicio(llamadas_f, umbrales["tiempo_min_espera"]),
    "abandono_pct": calcular_tasa_abandono(llamadas_f),
    "asa_seg": calcular_asa(llamadas_f),
    "aht_seg": calcular_aht(llamadas_f),
    "escalamiento_pct": calcular_tasa_escalamiento(llamadas_f),
    "fcr_pct": calcular_fcr(casos_f),
    "reincidencia_pct": calcular_reincidencia(casos_f),
    "csat_prom": calcular_csat_promedio(casos_f),
    "csat_positivo_pct": calcular_csat_positivo(casos_f, umbrales["csat"]),
    "horas_resolucion_prom": calcular_horas_resolucion(casos_f),
    "n_agentes": int(llamadas_f.loc[llamadas_f["id_agente"] != "", "id_agente"].nunique()),
}

# Resumen del filtro activo en sidebar
with st.sidebar.expander("Ver filtros activos"):
    st.caption(f"Período: {inicio:%d/%m/%Y} → {fin:%d/%m/%Y}")
    st.caption(f"Llamadas: {kpis['n_llamadas']:,} de {len(llamadas):,}")
    st.caption(f"Casos: {kpis['n_casos']:,} de {len(casos):,}")
    st.caption(f"Horas: {hora_min:02d}:00–{hora_max:02d}:59")


# ****************************************
# BOTONES POPUP EN SIDEBAR
# ****************************************

st.sidebar.divider()
st.sidebar.subheader(":material/tune: Parámetros de evaluación")

# Botón umbrales
if st.sidebar.button("⚙️ Umbrales", width="stretch"):
    popup_umbrales(umbrales)

# Botón definiciones
if st.sidebar.button("📚 Definiciones y fórmulas", width="stretch"):
    popup_definiciones()


if kpis["n_llamadas"] == 0:
    st.info("Sin datos para los filtros seleccionados")
    st.stop()


tab_tablero, tab_datos = st.tabs(
    [":material/dashboard: Tablero", ":material/table: Datos"]
)

with tab_tablero:
    # ****************************************
    # SECCIÓN 1: CABECERA Y KPIs PRINCIPALES
    # ****************************************

    st.header(":material/support_agent: Dashboard Call Center Ecommerce")
    st.caption("Estado de la operación — indicadores principales")

    # Fila de 4 KPIs principales
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        with st.container(key="kpi-sl"):
            sl_valor = kpis["sl_pct"]
            sl_meta = umbrales["nivel_servicio"]
            sl_texto = f"{sl_valor:.1f} %" if sl_valor is not None else "—"
            sl_color = ":green[:material/check_circle:]" if sl_valor is not None and sl_valor >= sl_meta else ":red[:material/error:]"        
            st.metric(
                label="SL · Nivel de servicio",
                value=f"{sl_color} {sl_texto}",
                help=f"Meta activa: ≤ {sl_meta:.0f} % de llamadas con espera ≤ {umbrales['tiempo_min_espera']} s",
                icon=":material/speed:"
            )
            st.caption(f"Meta SL: {sl_meta:.0f} % (umbral: {umbrales['tiempo_min_espera']} s)")

    with c2:
        with st.container(key="kpi-abandono"):
            abandono_valor = kpis["abandono_pct"]
            abandono_meta = umbrales["abandono"]
            abandono_texto = f"{abandono_valor:.1f} %" if abandono_valor is not None else "—"
            abandono_color = ":green[:material/check_circle:]" if abandono_valor is not None and abandono_valor <= abandono_meta else ":red[:material/error:]"
            st.metric(
                label="Tasa de Abandono",
                icon=":material/phone_missed:",
                value=f"{abandono_color} {abandono_texto}",
                help=f"Meta activa: < {abandono_meta:.0f} % de llamadas abandonadas",
            )
            st.caption(f"Meta Abandono: < {abandono_meta:.0f} %")

    with c3:
        with st.container(key="kpi-asa"):
            asa_valor = kpis["asa_seg"]
            asa_meta = umbrales["asa"]
            asa_texto = f"{asa_valor:.0f} s" if asa_valor is not None else "—"
            asa_color = ":green[:material/check_circle:]" if asa_valor is not None and asa_valor <= asa_meta else ":red[:material/error:]"
            st.metric(
                label="ASA · Tiempo medio de respuesta",
                icon=":material/hourglass_top:",
                value=f"{asa_color} {asa_texto}",
                help=f"Meta activa: ≤ {asa_meta:.0f} s",
            )
            st.caption(f"Meta ASA: ≤ {asa_meta:.0f} s")

    with c4:
        with st.container(key="kpi-aht"):
            aht_valor = kpis["aht_seg"]
            aht_meta = umbrales["aht"]
            aht_texto = f"{aht_valor:.0f} s" if aht_valor is not None else "—"
            aht_color = ":green[:material/check_circle:]" if aht_valor is not None and aht_valor <= aht_meta else ":red[:material/error:]"
            st.metric(
                label="AHT · Tiempo medio de atención",
                icon=":material/timer:",
                value=f"{aht_color} {aht_texto}",
                help=f"Meta activa: ≤ {aht_meta:.0f} s (conversación + ACW)",
            )
            st.caption(f"Meta AHT: ≤ {aht_meta:.0f} s")

    # Otras 2 métricas: Volumen, Casos, Agentes y Llamadas/día
    c5, c6, c6b, c6c = st.columns(4)

    with c5:
        with st.container(key="kpi-volumen"):
            st.metric(
                label="Volumen total",
                icon=":material/call:",
                value=f"{kpis['n_llamadas']:,.0f}",
                help="Total llamadas ofrecidas en el período filtrado.",
            )
            st.caption("Número total de llamadas recibidas")

    with c6:
        with st.container(key="kpi-casos"):
            st.metric(
                label="Casos totales",
                icon=":material/rule:",
                value=f"{kpis['n_casos']:,.0f}",
                help="Total casos/tickets en el período filtrado.",
            )
            st.caption("Número total de casos abiertos")

    with c6b:
        with st.container(key="kpi-agentes"):
            st.metric(
                label="Agentes",
                icon=":material/groups:",
                value=f"{kpis['n_agentes']:,.0f}",
                help="Agentes que atendieron llamadas en el período filtrado.",
            )
            st.caption("Agentes con llamadas atendidas")

    with c6c:
        with st.container(key="kpi-llamadas-dia"):
            n_dias = max((fin - inicio).days, 1)
            llamadas_dia = int(llamadas_f["id_llamada"].count() / n_dias) if not llamadas_f.empty else 0
            st.metric(
                label="Llamadas / día",
                icon=":material/calendar_today:",
                value=f"{llamadas_dia:,.0f}",
                help="Promedio de llamadas recibidas por día (entero).",
            )
            st.caption("Promedio diario de volumen")


    # ****************************************
    # SECCIÓN 2: CALIDAD Y FCR
    # ****************************************

    st.header(":material/rule: Calidad y resolución")

    col_izq, col_der = st.columns(2, gap="large")

    with col_izq:
        with st.container(key="kpi-fcr"):
            fcr_valor = kpis["fcr_pct"]
            fcr_meta = umbrales["fcr"]
            fcr_texto = f"{fcr_valor:.1f} %" if fcr_valor is not None else "—"
            fcr_color = ":green[:material/check_circle:]" if fcr_valor is not None and fcr_valor >= fcr_meta else ":red[:material/error:]"
            st.metric(
                label="FCR · Primer contacto",
                icon=":material/check_circle:",
                value=f"{fcr_color} {fcr_texto}",
                help=f"Meta activa: ≥ {fcr_meta:.0f} % de casos resueltos en primer contacto",
            )
            st.caption(f"Meta FCR: ≥ {fcr_meta:.0f} %")

        with st.container(key="kpi-reincidencia"):
            reinc_valor = kpis["reincidencia_pct"]
            reinc_meta = umbrales["reincidencia"]
            reinc_texto = f"{reinc_valor:.1f} %" if reinc_valor is not None else "—"
            reinc_color = ":green[:material/check_circle:]" if reinc_valor is not None and reinc_valor <= reinc_meta else ":red[:material/error:]"
            st.metric(
                label="Reincidencia",
                icon=":material/repeat:",
                value=f"{reinc_color} {reinc_texto}",
                help=f"Meta activa: ≤ {reinc_meta:.0f} % de casos con reincidencia",
            )
            st.caption(f"Meta Reincidencia: ≤ {reinc_meta:.0f} %")

    with col_der:
        with st.container(key="kpi-csat-prom"):
            csat_valor = kpis["csat_prom"]
            csat_meta = umbrales["csat"]
            csat_texto = f"{csat_valor:.2f} / 5" if csat_valor is not None else "—"
            st.metric(
                label="CSAT · Satisfacción promedio",
                icon=":material/star:",
                value=csat_texto,
                help=f"Meta activa: ≥ {csat_meta:.1f} (promedio escala 1-5)",
            )
            st.caption(f"Meta CSAT: ≥ {csat_meta:.1f}")

        with st.container(key="kpi-csat-positivo"):
            csat_pos_valor = kpis["csat_positivo_pct"]
            csat_pos_meta = umbrales["csat"]
            csat_pos_texto = f"{csat_pos_valor:.1f} %" if csat_pos_valor is not None else "—"
            st.metric(
                label="CSAT positivo (≥ 4.0)",
                icon=":material/star:",
                value=f"{csat_pos_texto}",
                help=f"Mínima requerida: {csat_pos_meta:.1f}. % casos con CSAT ≥ 4.0",
            )
            st.caption(f"CSAT mínimo: {csat_pos_meta:.1f}")


    # ****************************************
    # SECCIÓN 3: ANÁLISIS POR HORA Y COLA
    # ****************************************

    st.header(":material/timeline: ¿Qué está pasando?")
    st.caption("Análisis temporal y por canal de atención")

    # Fila 1: Volumen por día y Espera/Abandono por hora
    c7, c8 = st.columns(2)

    with c7:
        with st.container(key="kpi-vol-dia"):
            vol_dia = llamadas_f.groupby(["fecha", "resultado_llamada"], as_index=False).agg(
                llamadas=("id_llamada", "size")
            )
            fig_dia = px.area(
                vol_dia, x="fecha", y="llamadas", color="resultado_llamada",
                color_discrete_map={"atendida": AZUL, "abandonada": ROJO},
                labels={"fecha": "Fecha", "llamadas": "Número de llamadas",
                        "resultado_llamada": "Resultado"},
                title="Llamadas por día",
                category_orders={"resultado_llamada": ["atendida", "abandonada"]},
            )
            st.plotly_chart(aplicar_estilo_grafico(fig_dia, 400), width="stretch")
            st.caption("Evolución diaria distinguiendo llamadas atendidas (azul) y abandonadas (rojo)")

    with c8:
        with st.container(key="kpi-hora"):
            umbral_sl = int(umbrales["tiempo_min_espera"])
            et_ok = f"Atendidas ≤ {umbral_sl} s"
            et_tarde = f"Atendidas > {umbral_sl} s"
            et_aban = "Abandonadas"

            # Categorías excluyentes: suman 100 % por franja
            llamadas_hora = llamadas_f.assign(
                estado=np.select(
                    [llamadas_f["abandonada"],
                     llamadas_f["espera_seg"].le(umbral_sl)],
                    [et_aban, et_ok],
                    default=et_tarde,
                )
            )
            stats_hora = (
                llamadas_hora.groupby(["hora", "estado"]).size().unstack(fill_value=0)
                .reindex(columns=[et_ok, et_tarde, et_aban], fill_value=0)
            )
            stats_hora["franja"] = stats_hora.index.map(lambda h: f"{h:02d}:00")

            # Selector: porcentaje (100 % apilado) o cantidad ( absoluta apilada)
            vista_hora = st.segmented_control(
                "Vista del gráfico", options=["Porcentaje", "<Cantidad"],
                default="Porcentaje", key="vista_hora",
            )

            if vista_hora == "Porcentaje":
                num_hora = stats_hora[[et_ok, et_tarde, et_aban]]
                datos_hora = (
                    num_hora.div(num_hora.sum(axis=1), axis=0)
                    .mul(100).reset_index()
                )
                datos_hora["franja"] = stats_hora["franja"].values
                eje_y = "Porcentaje"
                formato_texto = ".0f"
            else:
                datos_hora = stats_hora.reset_index()
                eje_y = "Llamadas"
                formato_texto = True

            fig_hora = px.bar(
                datos_hora, x="franja", y=[et_ok, et_tarde, et_aban],
                color_discrete_map={et_ok: VERDE, et_tarde: AMBAR, et_aban: ROJO},
                labels={"value": eje_y, "franja": "Franja horaria", "variable": "Estado"},
                title=f"Llamadas por franja horaria ({eje_y.lower()})",
                text_auto=formato_texto,
                category_orders={"variable": [et_ok, et_tarde, et_aban]},
            )
            fig_hora.update_layout(barmode="stack")
            st.plotly_chart(aplicar_estilo_grafico(fig_hora, 420), width="stretch")
            st.caption("Barras apiladas: atendidas dentro del umbral, atendidas después del umbral y abandonadas por cada hora del día")


    # Fila 2: AHT por motivo y Composición por cola
    c9, c10 = st.columns(2)

    with c9:
        with st.container(key="kpi-aht-motivo"):
            atendidas_f = llamadas_f.loc[
                llamadas_f["atendida"] & llamadas_f["aht_seg"].notna()
            ].copy()
            if not atendidas_f.empty:
                orden_motivos = (
                    atendidas_f.groupby("motivo_etiqueta")["aht_seg"]
                    .median().sort_values().index.tolist()
                )
                fig_aht = px.box(
                    atendidas_f, x="aht_seg", y="motivo_etiqueta",
                    color="motivo_etiqueta", points="outliers",
                    category_orders={"motivo_etiqueta": orden_motivos},
                    labels={"aht_seg": "AHT (s) - Tiempo medio atención"},
                    title="AHT (segundos) por motivo atendido",
                )
                fig_aht.add_vline(
                    x=atendidas_f["aht_seg"].mean(), line_dash="dash", line_color=GRIS,
                    annotation_text=f"Promedio general: {atendidas_f['aht_seg'].mean():.0f} s",
                    annotation_position="top",
                )
                fig_aht.update_layout(showlegend=False)
                st.plotly_chart(aplicar_estilo_grafico(fig_aht, 500), width="stretch")
            else:
                st.info("No hay llamadas atendidas con datos de AHT para el filtro actual.")
            st.caption("Distribución de AHT por motivo de llamada; outliers incluidos")


    with c10:
        with st.container(key="kpi-cola"):
            if not llamadas_f.empty:
                cola_data = llamadas_f.groupby("cola", as_index=False).agg(
                    total=("id_llamada", "size"),
                    atendidas=("atendida", "sum"),
                    abandonadas=("abandonada", "sum"),
                )
                cola_data["sl_pct"] = cola_data["atendidas"] / cola_data["total"] * 100
                cola_data["abandono_pct"] = cola_data["abandonadas"] / cola_data["total"] * 100

                fig_cola = px.pie(
                    cola_data, values="total", names="cola",
                    title="Composición por cola",
                    color="cola",
                    color_discrete_map={
                        "Soporte_Pedidos": AZUL,
                        "Soporte_Envios": VERDE,
                        "Retenciones": AMBAR,
                        "Ventas": ROJO,
                    },
                )
                st.plotly_chart(aplicar_estilo_grafico(fig_cola, 400), width="stretch")
            else:
                st.info("No hay datos de colas para el período y filtros seleccionados.")
            st.caption("Porcentaje de llamadas totales distribuidas por cada cola de atención")


    # Fila 3: Indicadores por día de la semana
    DIAS_ES = {
        "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
        "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo",
    }
    ORDEN_DIAS = list(DIAS_ES.values())

    with st.container(key="kpi-dia-semana"):
        if llamadas_f.empty:
            st.info("No hay datos para el período y filtros seleccionados.")
        else:
            por_dia = llamadas_f.assign(
                dia=llamadas_f["dia_semana"].map(DIAS_ES),
                espera_atendida=llamadas_f["espera_seg"].where(llamadas_f["atendida"]),
            ).groupby(
                "dia", as_index=False
            ).agg(
                llamadas=("id_llamada", "size"),
                en_meta=("espera_seg", lambda x: (x <= umbrales["tiempo_min_espera"]).sum()),
                abandonadas=("abandonada", "sum"),
                asa=("espera_atendida", "mean"),
                aht=("aht_seg", "mean"),
            )
            por_dia["sl_pct"] = por_dia["en_meta"] / por_dia["llamadas"] * 100
            por_dia["abandono_pct"] = por_dia["abandonadas"] / por_dia["llamadas"] * 100
            por_dia["dia"] = pd.Categorical(por_dia["dia"], categories=ORDEN_DIAS, ordered=True)
            por_dia = por_dia.sort_values("dia")

            indicadores = {
                "Volumen": ("llamadas", "Llamadas", None, AZUL),
                "Nivel de servicio": ("sl_pct", "Nivel de servicio (%)", umbrales["nivel_servicio"], VERDE),
                "Abandono": ("abandono_pct", "Abandono (%)", umbrales["abandono"], ROJO),
                "ASA": ("asa", "ASA (s)", umbrales["asa"], AMBAR),
                "AHT": ("aht", "AHT (s)", umbrales["aht"], AZUL),
            }
            elegido = st.segmented_control(
                "Indicador", options=list(indicadores), default="Volumen",
                key="ind_dia_semana",
            ) or "Volumen"
            col, etiqueta, meta, color = indicadores[elegido]

            fig_semana = px.bar(
                por_dia, x="dia", y=col, text_auto=".1f" if col != "llamadas" else True,
                labels={"dia": "Día de la semana", col: etiqueta},
                title=f"{etiqueta} por día de la semana",
            )
            fig_semana.update_traces(marker_color=color)
            if meta is not None:
                fig_semana.add_hline(
                    y=meta, line_dash="dash", line_color=ROJO, annotation_text="Meta"
                )
            st.plotly_chart(aplicar_estilo_grafico(fig_semana, 400), width="stretch")

            st.dataframe(
                por_dia[["dia", "llamadas", "sl_pct", "abandono_pct", "asa", "aht"]],
                column_config={
                    "dia": st.column_config.TextColumn("Día"),
                    "llamadas": st.column_config.NumberColumn("Llamadas", format="%d"),
                    "sl_pct": st.column_config.NumberColumn("SL %", format="%.1f%%"),
                    "abandono_pct": st.column_config.NumberColumn("Abandono %", format="%.1f%%"),
                    "asa": st.column_config.NumberColumn("ASA (s)", format="%.1f"),
                    "aht": st.column_config.NumberColumn("AHT (s)", format="%.1f"),
                },
                hide_index=True, width="stretch",
            )
            st.caption("Indicadores operativos agregados por día de la semana según los filtros activos")


    # Fila 4: SL por hora con línea de meta (expander detallado)
    with st.expander("Ver SL y abandono por hora con línea de meta detallada"):
        with st.container(key="kpi-sl-hora-detalle"):
            stats_hora2 = llamadas_f.groupby("hora", as_index=False).agg(
                total=("id_llamada", "size"),
                en_meta=("espera_seg", lambda x: (x <= umbrales["tiempo_min_espera"]).sum()),
                abandonadas=("abandonada", "sum"),
            )
            stats_hora2["sl_pct"] = stats_hora2["en_meta"] / stats_hora2["total"] * 100
            stats_hora2["abandono_pct"] = stats_hora2["abandonadas"] / stats_hora2["total"] * 100
            stats_hora2["franja"] = stats_hora2["hora"].apply(lambda h: f"{h:02d}:00")

            fig_sl2 = px.line(
                stats_hora2, x="hora", y="sl_pct",
                markers=True,
                labels={"hora": "Hora del día", "sl_pct": "Nivel de servicio (%)"},
                title=f"Nivel de servicio por hora (meta: {umbrales['nivel_servicio']:.0f} %)",
            )
            # Agregar línea de meta horizontal
            fig_sl2.add_hline(
                y=umbrales["nivel_servicio"], line_dash="dash",
                line_color=ROJO, annotation_text="Meta SL"
            )
            # También el abandono
            fig_sl2a = px.line(
                stats_hora2, x="hora", y="abandono_pct",
                markers=True,
                labels={"hora": "Hora del día", "abandono_pct": "Abandono (%)"},
                title="Abandono por hora",
            )
            fig_sl2a.add_hline(
                y=umbrales["abandono"], line_dash="dot",
                line_color=ROJO, annotation_text="Meta Abandono"
            )
            st.plotly_chart(aplicar_estilo_grafico(fig_sl2, 420), width="stretch")
            st.plotly_chart(aplicar_estilo_grafico(fig_sl2a, 420), width="stretch")
            st.caption("Líneas punteadas/continuas rojas indican umbrales activos desde session_state")


    # ****************************************
    # SECCIÓN 4: DESEMPEÑO POR AGENTE
    # ****************************************

    st.header(":material/groups: Desempeño del equipo")

    with st.container(key="kpi-ranking-agentes"):
        # Calcular métricas por agente (llamadas atendidas)
        agentes_atendidas = llamadas_f.loc[
            llamadas_f["atendida"] & (llamadas_f["id_agente"] != "")
        ]
        agentes_atendidas = agentes_atendidas.assign(
            en_meta_sl=agentes_atendidas["espera_seg"].le(umbrales["tiempo_min_espera"])
        )

        if not agentes_atendidas.empty:
            # Métricas operativas por agente
            metricas = (
                agentes_atendidas.groupby("id_agente", as_index=False)
                .agg(
                    volumen=("id_llamada", "size"),
                    sl_pct=("en_meta_sl", lambda x: x.mean() * 100),
                    aht_seg=("aht_seg", "mean"),
                    escalamiento_pct=("escalado_a", lambda s: s.ne("").mean() * 100),
                )
                .sort_values("volumen", ascending=False)
            )

            # Métricas de calidad desde casos (si están disponibles)
            if not casos_f.empty:
                calidad = (
                    casos_f.loc[casos_f["id_agente"] != ""]
                    .groupby("id_agente", as_index=False)
                    .agg(
                        casos_total=("id_caso", "size"),
                        fcr_pct=("fcr", lambda s: s.mean() * 100),
                        csat_prom=("csat", "mean"),
                        reincidencia_pct=("reincidencia", lambda s: s.mean() * 100),
                    )
                )
                metricas = metricas.merge(calidad, on="id_agente", how="left")
                metricas["casos_total"] = metricas["casos_total"].fillna(0).astype(int)
            else:
                metricas["casos_total"] = 0
                metricas["fcr_pct"] = None
                metricas["csat_prom"] = None
                metricas["reincidencia_pct"] = None

            # Top 10 agentes por volumen (ordenado para horizontal bar)
            top_10 = metricas.head(10).sort_values("volumen")

            fig_ranking = px.bar(
                top_10, x="volumen", y="id_agente", orientation="h",
                text_auto=True,
                labels={"volumen": "Llamadas atendidas", "id_agente": "Agente"},
                title="Top 10 agentes por volumen de llamadas atendidas",
            )
            st.plotly_chart(aplicar_estilo_grafico(fig_ranking, 500), width="stretch")
            st.caption("Top 10 agentes ordenadas por número de llamadas atendidas")

            # Tabla completa de agentes con formato column_config
            st.subheader("Tabla completa de agentes")

            metricas_decimal = metricas.copy()

            column_config = {
                "id_agente": st.column_config.TextColumn("Agente"),
                "volumen": st.column_config.NumberColumn("Llamadas at.", format="%d"),
                "sl_pct": st.column_config.NumberColumn("SL %", format="%.1f%%"),
                "aht_seg": st.column_config.NumberColumn("AHT (s)", format="%.1f s"),
                "escalamiento_pct": st.column_config.NumberColumn("Esc %", format="%.1f%%"),
                "casos_total": st.column_config.NumberColumn("Casos", format="%d"),
                "fcr_pct": st.column_config.NumberColumn("FCR %", format="%.1f%%"),
                "csat_prom": st.column_config.NumberColumn("CSAT", format="%.2f / 5"),
                "reincidencia_pct": st.column_config.NumberColumn("Reinc %", format="%.1f%%"),
            }

            # Para el semáforo: añadir umbral de SL a la visualización
            metricas_display = metricas_decimal.copy()
            metricas_display["sl_meta"] = umbrales["nivel_servicio"]

            # Renombrar columnas para la display (PercentageColumn ya formateará a %)
            rename_map = {
                "id_agente": "Agente",
                "volumen": "Llamadas at.",
                "sl_pct": "SL %",       # PercentageColumn lo formatea a % desde decimal
                "aht_seg": "AHT (s)",
                "escalamiento_pct": "Esc %",  # PercentageColumn lo formatea a % desde decimal
                "casos_total": "Casos",
                "fcr_pct": "FCR %",     # PercentageColumn lo formatea a % desde decimal
                "csat_prom": "CSAT",
                "reincidencia_pct": "Reinc %",  # PercentageColumn lo formatea a % desde decimal
            }

            st.dataframe(
                metricas_display.rename(columns=rename_map),
                column_config=column_config,
                hide_index=True,
                width="stretch",
            )
            st.caption("SL y porcentajes: verde ≥ meta, rojo < meta (refleja umbral activo desde session_state)")


# ****************************************
# TAB DATOS: DATAFRAMES BASE DE LOS CÁLCULOS
# ****************************************

with tab_datos:
    st.header(":material/table: Datos base de los cálculos")
    st.caption("Registros resultantes de aplicar los filtros del sidebar; "
               "son los DataFrames con los que se calculan los indicadores del tablero.")

    with st.container(key="datos-llamadas"):
        st.subheader("Llamadas (CDR)")
        st.caption(f"{len(llamadas_f):,} de {len(llamadas):,} registros")
        st.dataframe(llamadas_f, hide_index=True, width="stretch")

    with st.container(key="datos-casos"):
        st.subheader("Casos / tickets")
        st.caption(f"{len(casos_f):,} de {len(casos):,} registros")
        st.dataframe(casos_f, hide_index=True, width="stretch")
