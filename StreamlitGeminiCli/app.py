import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(page_title="Dashboard CO2 Global", layout="wide", page_icon=":material/public:")

# --- INYECCIÓN DE CSS PERSONALIZADO ---
st.markdown("""
    <style>
    /* Fondo principal de la app */
    .stApp {
        background-color: #EEEEEE;
    }

    /* Estilo para los contenedores (cards) */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        border: 1px solid #E0E0E0 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
        margin-bottom: 1.5rem !important;
    }

    /* Quitar bordes internos si existen */
    div[data-testid="stVerticalBlock"] > div {
        border: none !important;
    }

    /* Estilo de métricas */
    [data-testid="stMetricValue"] {
        color: #2FA084 !important;
        font-weight: 700;
    }
    
    [data-testid="stMetricLabel"] {
        color: #1F6F5F !important;
    }

    /* Ajuste para que las gráficas sean transparentes */
    .js-plotly-plot .plotly .main-svg {
        background-color: transparent !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ---
st.markdown("""
    <div style='text-align: center; padding: 1.5rem;'>
        <h1 style='color: #1F6F5F; margin-bottom: 0;'>Análisis de Emisiones de CO2 Global</h1>
        <p style='font-size: 1.1em; color: #555;'>Visualización de datos climáticos y eficiencia económica</p>
        <hr style='border-top: 3px solid #2FA084; width: 50%; margin: 10px auto;'>
    </div>
""", unsafe_allow_html=True)

# Carga de datos
@st.cache_data
def load_data():
    df = pd.read_csv('visualizing_global_co2_data.csv')
    return df

df = load_data()

# --- BARRA LATERAL ---
with st.sidebar:
    st.header(":material/tune: Filtros")
    
    min_year, max_year = int(df['year'].min()), int(df['year'].max())
    year_range = st.slider("Periodo de Tiempo", min_year, max_year, (1970, max_year))
    
    all_countries = sorted(df['country'].unique())
    selected_countries = st.multiselect(
        "Países a Comparar", 
        all_countries, 
        default=["World", "China", "United States", "India"]
    )
    
    metrics_map = {
        "co2": "CO2 Total (Mt)",
        "co2_per_capita": "CO2 Per Cápita (t)",
        "co2_per_gdp": "CO2 por PIB (kg/$)"
    }
    selected_metric = st.selectbox("Seleccionar Métrica", list(metrics_map.keys()), format_func=lambda x: metrics_map[x])

# Filtrado Global
df_filtered = df[(df['year'].between(*year_range)) & (df['country'].isin(selected_countries))]

# --- DASHBOARD ---

# KPIs Section
with st.container(border=True):
    st.markdown("### :material/analytics: Resumen del Periodo")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    total_co2 = df_filtered['co2'].sum()
    avg_pc = df_filtered['co2_per_capita'].mean()
    growth = df_filtered['co2_growth_prct'].mean()
    
    kpi1.metric("CO2 Acumulado", f"{total_co2/1000:,.1f} Gt")
    kpi2.metric("Media Per Cápita", f"{avg_pc:.2f} t")
    kpi3.metric("Crecimiento Anual", f"{growth:.1f}%")
    
    # Participación vs Mundo
    world_co2 = df[(df['country'] == 'World') & (df['year'] == year_range[1])]['co2']
    if not world_co2.empty:
        latest_world = world_co2.iloc[0]
        latest_sel = df_filtered[df_filtered['year'] == year_range[1]]['co2'].sum()
        share = (latest_sel / latest_world * 100) if latest_world > 0 else 0
        kpi4.metric("% Global (Último Año)", f"{share:.1f}%")
    else:
        kpi4.metric("% Global", "N/A")

# Main Charts
col_a, col_b = st.columns(2)

with col_a:
    with st.container(border=True):
        st.markdown(f"### :material/show_chart: Tendencia de {metrics_map[selected_metric]}")
        fig_line = px.line(df_filtered, x='year', y=selected_metric, color='country',
                          template="plotly_white", color_discrete_sequence=px.colors.qualitative.Safe)
        fig_line.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=350,
                              paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_line, width='stretch')

with col_b:
    with st.container(border=True):
        st.markdown(f"### :material/public: Mapa ({year_range[1]})")
        df_map = df[df['year'] == year_range[1]]
        fig_map = px.choropleth(df_map, locations="iso_code", color=selected_metric,
                               hover_name="country", color_continuous_scale="GnBu")
        fig_map.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=350,
                             paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_map, width='stretch')

# Breakdown Section
with st.container(border=True):
    st.markdown("### :material/layers: Composición de Emisiones")
    src_list = ['coal_co2', 'oil_co2', 'gas_co2', 'cement_co2', 'flaring_co2']
    df_src = df_filtered.groupby('year')[src_list].sum().reset_index()
    fig_area = px.area(df_src, x='year', y=src_list, template="plotly_white",
                      labels={"value": "Millones de Toneladas", "variable": "Fuente"},
                      color_discrete_sequence=px.colors.qualitative.Prism)
    fig_area.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=300,
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_area, width='stretch')

# Data Table Section
st.divider()
with st.container(border=True):
    st.markdown("### :material/table_view: Explorador de Datos")
    f_col1, f_col2 = st.columns(2)
    f_countries = f_col1.multiselect("Filtrar por País", all_countries, key="table_filter_country")
    f_years = f_col2.multiselect("Filtrar por Año", sorted(df['year'].unique(), reverse=True), key="table_filter_year")
    
    df_final = df.copy()
    if f_countries: df_final = df_final[df_final['country'].isin(f_countries)]
    if f_years: df_final = df_final[df_final['year'].isin(f_years)]
    if not f_countries and not f_years: df_final = df_filtered
    
    st.dataframe(df_final, width='stretch', height=350)
    st.download_button(
        label="Descargar registros filtrados (CSV)",
        data=df_final.to_csv(index=False).encode('utf-8'),
        file_name='co2_filtered_data.csv',
        mime='text/csv'
    )
