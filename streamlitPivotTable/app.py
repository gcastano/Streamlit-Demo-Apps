# ==========================================
# INSTALACIÓN DE LIBRERÍAS (Ejecutar en la terminal):
# pip install streamlit pandas streamlit-pivot openpyxl
# Nota: 'openpyxl' es necesario para que pandas pueda leer archivos Excel (.xlsx).
# ==========================================

import streamlit as st
# Pandas: Librería fundamental en Python para la manipulación, limpieza y análisis de datos.
import pandas as pd

# Importar el componente personalizado para renderizar la tabla dinámica en Streamlit.
from streamlit_pivot import st_pivot_table
# https://github.com/streamlit/streamlit-pivot-table
# https://custom-component-pivot-table.streamlit.app/

# Configuración inicial de la página web de Streamlit
# Define el título de la pestaña del navegador y usa todo el ancho de la pantalla (layout="wide")
st.set_page_config(page_title="Análisis con Pivot Table", layout="wide")

# --- FUNCIÓN DE RESET ---
def reset_parametros():
    """
    Limpia el estado de la aplicación.
    
    Itera sobre todas las variables almacenadas en la sesión de Streamlit (st.session_state)
    y elimina aquellas que comiencen con el prefijo "pt_" (parámetros del pivot table).
    Esto devuelve la barra lateral y la tabla a sus valores por defecto.
    """
    for key in list(st.session_state.keys()):
        if key.startswith("pt_"):
            del st.session_state[key]

st.title(":blue[:material/pivot_table_chart:] Análisis de datos con :blue-background[Pivot Table]")
st.markdown("""
1. **Controlado por Sidebar**: Modifica el estado del componente forzando parámetros desde Streamlit.
2. **Pivot Libre**: Muestra el componente en su estado natural (Auto-Detect), permitiéndote arrastrar, soltar, filtrar y usar los menús internos de la tabla directamente en la interfaz.
""")

# ----------------- BARRA LATERAL (SIDEBAR) -----------------
st.sidebar.header("1. Cargar Datos")
# Widget para subir archivos. Acepta formatos de texto (CSV) y hojas de cálculo (Excel).
uploaded_file = st.sidebar.file_uploader("Sube un archivo CSV o Excel", type=["csv", "xlsx", "xls"])

if uploaded_file:
    try:
        # --- TRANSFORMACIONES Y LECTURA DE DATOS CON PANDAS ---
        
        # 1. Lectura del archivo: Dependiendo de la extensión, usamos una función distinta de pandas.
        if uploaded_file.name.endswith('.csv'):
            # pd.read_csv convierte un archivo de texto separado por comas en un DataFrame (tabla bidimensional).
            df = pd.read_csv(uploaded_file)
        else:
            # pd.read_excel convierte un archivo de Excel en un DataFrame.
            df = pd.read_excel(uploaded_file)
            
        # 2. Extracción de nombres de columnas
        # df.columns devuelve los nombres de las columnas. .tolist() los convierte en una lista estándar de Python.
        columnas = df.columns.tolist()
        
        # 3. Filtrado por tipo de dato (Transformación clave)
        # select_dtypes(include=['number']) filtra el DataFrame dejando solo las columnas numéricas (int, float).
        # Esto es vital porque operaciones como promedios o escalas de color solo tienen sentido con números.
        num_cols = df.select_dtypes(include=['number']).columns.tolist()

        # Botón para ejecutar la función de reseteo definida arriba
        st.sidebar.button("🔄 Resetear Sidebar", on_click=reset_parametros, type="primary", use_container_width=True)
        st.sidebar.divider()

        # ----------------- OPCIONES DEL PIVOT TABLE -----------------
        st.sidebar.header("2. Dimensiones y Métricas (Solo para Tab 1)")
        
        # Selectores múltiples para decidir qué datos van en filas, columnas y qué se va a calcular.
        rows = st.sidebar.multiselect("Filas (rows)", options=columnas, key="pt_rows")
        columns = st.sidebar.multiselect("Columnas (columns)", options=columnas, key="pt_columns")
        values = st.sidebar.multiselect("Valores (values)", options=columnas, key="pt_values")
        
        # ----------------- PARÁMETROS DE COMPORTAMIENTO -----------------
        st.sidebar.header("3. Parámetros Avanzados")
        
        # Selector de la función de agregación matemática (suma, promedio, conteo, etc.)
        aggregation = st.sidebar.selectbox("Agregación (aggregation)", 
            options=["sum", "avg", "count", "min", "max", "median", "first", "last"], key="pt_agg")
        
        # Opciones booleanas (True/False) representadas con casillas de verificación (checkboxes)
        show_totals = st.sidebar.checkbox("Mostrar Totales Generales (show_totals)", value=True, key="pt_totals")
        show_subtotals = st.sidebar.checkbox("Habilitar Subtotales (Requerido para agrupar/colapsar)", value=True, key="pt_subtotals")
        sticky_headers = st.sidebar.checkbox("Fijar encabezados (sticky_headers)", value=True, key="pt_sticky")
        
        # ----------------- FORMATO CONDICIONAL -----------------
        st.sidebar.header("4. 🎨 Formato Condicional")
        st.sidebar.caption("Selecciona qué columnas numéricas aplicarán para cada formato.")
        
        # -- A. DATA BARS (Barras horizontales dentro de la celda según su valor) --
        st.sidebar.subheader("A. Data Bars (Barras de relleno)")
        # Nota: Aquí usamos la lista 'num_cols' que filtramos previamente con pandas
        db_cols = st.sidebar.multiselect("Columnas para Data Bars", options=num_cols, key="pt_db_cols")
        if db_cols:
            db_color = st.sidebar.color_picker("Color de barra", value="#1976d2", key="pt_db_color")

        # -- B. COLOR SCALE (Mapa de calor) --
        st.sidebar.subheader("B. Color Scale (Escala de color)")
        cs_cols = st.sidebar.multiselect("Columnas para Color Scale", options=num_cols, key="pt_cs_cols")
        if cs_cols:
            col1, col2 = st.sidebar.columns(2)
            cs_min = col1.color_picker("Color Min", value="#1b2e1b", key="pt_cs_min")
            cs_max = col2.color_picker("Color Max", value="#4caf50", key="pt_cs_max")

        # -- C. THRESHOLD (Cambio de color si supera o es menor a un valor umbral) --
        st.sidebar.subheader("C. Threshold (Umbral)")
        th_cols = st.sidebar.multiselect("Columnas para Threshold", options=num_cols, key="pt_th_cols")
        if th_cols:
            # Diccionario para mapear símbolos matemáticos con los operadores que entiende la librería
            op_map = {
                "> (Mayor que)": "gt",
                "< (Menor que)": "lt",
                "= (Igual a)": "eq",
                ">= (Mayor o igual)": "gte",
                "<= (Menor o igual)": "lte"
            }
            th_op_label = st.sidebar.selectbox("Condición", options=list(op_map.keys()), index=0, key="pt_th_op")
            th_val = st.sidebar.number_input("Valor límite", value=1000.0, key="pt_th_val")
            th_bg = st.sidebar.color_picker("Color de fondo de celda", value="#1565c0", key="pt_th_bg")
            th_bold = st.sidebar.checkbox("Texto en Negrita", value=True, key="pt_th_bold")

        # ----------------- INTERACCIÓN Y TAMAÑO -----------------
        st.sidebar.header("5. Interacción")
        interactive = st.sidebar.checkbox("Modo interactivo (interactive)", value=True, key="pt_interactive")
        locked = st.sidebar.checkbox("Bloquear configuración (locked)", value=False, key="pt_locked")
        enable_drilldown = st.sidebar.checkbox("Habilitar detalle al clic (drilldown)", value=True, key="pt_drill")
        
        max_height = st.sidebar.number_input("Altura máxima (max_height)", min_value=200, max_value=1500, value=500, step=50, key="pt_height")

        # ----------------- RENDERIZAR VISTAS EN PESTAÑAS -----------------
        st.divider()
        
        # Crear los dos Tabs (pestañas) para organizar la vista principal
        tab_controlado, tab_libre = st.tabs(["🎛️ Pivot Controlado por Sidebar", "✨ Pivot Libre (Interacción Natural)"])

        # ==========================================
        # TAB 1: PIVOT CONTROLADO POR SIDEBAR
        # ==========================================
        with tab_controlado:
            st.subheader("Modo Parametrizado")
            st.info("La vista de este pivot se sobreescribe cada vez que cambias algo en la barra lateral.")
            
            # Construir un diccionario con los argumentos base configurados en la barra lateral
            pivot_kwargs = {
                "key": "pivot_dinamico",
                "aggregation": aggregation,
                "show_totals": show_totals,
                "show_subtotals": show_subtotals,
                "interactive": interactive,
                "locked": locked,
                "sticky_headers": sticky_headers,
                "enable_drilldown": enable_drilldown,
                "max_height": int(max_height)
            }
            
            # Agregar dinámicamente las dimensiones solo si el usuario seleccionó alguna
            if rows: pivot_kwargs["rows"] = rows
            if columns: pivot_kwargs["columns"] = columns
            if values: pivot_kwargs["values"] = values

            # Compilar lista de Formato Condicional basada en las selecciones
            cf_list =[]
            if db_cols: cf_list.append({"type": "data_bars", "apply_to": db_cols, "color": db_color, "fill": "gradient"})
            if cs_cols: cf_list.append({"type": "color_scale", "apply_to": cs_cols, "min_color": cs_min, "max_color": cs_max})
            if th_cols: cf_list.append({"type": "threshold", "apply_to": th_cols, "conditions":[{"operator": op_map[th_op_label], "value": th_val, "background": th_bg, "bold": th_bold}]})

            # Si hay formatos condicionales, los añadimos a los argumentos
            if cf_list:
                pivot_kwargs["conditional_formatting"] = cf_list

            # Llamada al componente final pasando el DataFrame (procesado por pandas) y desempaquetando los argumentos (**)
            st_pivot_table(df, **pivot_kwargs)

        # ==========================================
        # TAB 2: PIVOT LIBRE (AUTO-DETECT)
        # ==========================================
        with tab_libre:
            st.subheader("Modo Interacción Natural (UI)")
            st.info("""
            Este componente se carga "limpio". **Usa la propia interfaz de la tabla**:
            * Haz clic en **'Rows / Columns / Values'** dentro del componente para arrastrar las columnas.
            * Usa la **tuerca (⚙)** arriba a la derecha para exportar o cambiar densidades.
            * Haz clic en los **embudos** para filtrar datos.
            * Esta pestaña ignora los parámetros del menú izquierdo.
            """)
            
            # Llamada al componente SIN parámetros adicionales (solo el Dataframe y una key única).
            # Importante: Streamlit requiere un 'key' distinto para evitar conflictos cuando se usa el mismo componente varias veces.
            st_pivot_table(df, key="pivot_libre")

    except Exception as e:
        # Manejo de errores: Si el archivo está corrupto o hay un error, se muestra en pantalla amigablemente.
        st.error(f"Error al procesar el archivo o mostrar el Pivot Table: {e}")
else:
    # Mensaje por defecto cuando no se ha subido ningún archivo aún.
    st.info("👈 Por favor, carga un archivo CSV o Excel en la barra lateral izquierda para comenzar.")