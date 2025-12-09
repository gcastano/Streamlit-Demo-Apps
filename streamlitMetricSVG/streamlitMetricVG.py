import streamlit as st
from pathlib import Path

# ==============================================================================
# LIBRERÍAS UTILIZADAS
# ==============================================================================
# 1. streamlit: Framework para crear aplicaciones web de ciencia de datos rápidamente.
#    Comando de instalación: pip install streamlit
#
# 2. pathlib: Librería estándar de Python para manejar rutas de archivos de sistema
#    de forma robusta y agnóstica al sistema operativo (Windows/Mac/Linux).
#    No requiere instalación adicional.
# ==============================================================================

# Configuración inicial de la página: Título en la pestaña del navegador y diseño ancho.
st.set_page_config(page_title="Metric SVG", layout="wide")

# Título principal de la aplicación visible para el usuario.
st.title("Creando Métricas con SVG")

def modificar_svg(archivo, titulo, valor, comparativo, signo="+", descripcion="", width='stretch'):
    """
    Lee una plantilla SVG, realiza transformaciones de texto para inyectar datos
    dinámicos y renderiza la imagen resultante en la interfaz de Streamlit.

    Esta función actúa como un motor de plantillas simple, reemplazando marcadores
    de posición (placeholders) en el código XML del SVG con valores reales.

    Args:
        archivo (str): Nombre del archivo SVG que sirve como plantilla (debe estar en la misma carpeta).
        titulo (str): El texto que reemplazará al marcador [Titulo].
        valor (str): El dato numérico o texto principal que reemplazará a [Valor].
        comparativo (str): Texto secundario (ej. porcentaje de cambio) para [Comparativo].
        signo (str, optional): Indica si la métrica es positiva ("+") o negativa ("-").
                               Si es "-", cambia los colores a rojo. Por defecto es "+".
        descripcion (str, optional): Texto adicional para el marcador [Descripcion]. Por defecto "".
        width (str/int, optional): Ancho de la imagen en Streamlit. Por defecto 'stretch'.

    Returns:
        None: La función renderiza directamente el componente visual en la app.
    """
    
    # Ruta del archivo SVG: Path(__file__).parent asegura que busquemos el archivo
    # en el mismo directorio donde está guardado este script de Python.
    svg_path = Path(__file__).parent / archivo

    # Verificar que el archivo existe antes de intentar abrirlo para evitar errores.
    if svg_path.exists():
        # Lectura del archivo: Abrimos el SVG en modo lectura de texto con encoding utf-8.
        with open(svg_path, "r", encoding="utf-8") as f:
            svg_content = f.read()
        
        # --------------------------------------------------------------------------
        # TRANSFORMACIÓN DE DATOS (Manipulación de Strings)
        # --------------------------------------------------------------------------
        # Aquí simulamos una transformación de datos reemplazando los placeholders
        # definidos en el archivo SVG original con las variables de Python.
        svg_content = svg_content.replace("[Titulo]", titulo)
        svg_content = svg_content.replace("[Valor]", valor)
        
        # Lógica condicional para formato visual:
        # Si la métrica es negativa, cambiamos los colores hexadecimales del SVG.
        # Esto transforma un diseño "verde/positivo" a "rojo/negativo" dinámicamente.
        if signo == "-":
            svg_content = svg_content.replace("#008000", "#FF0000") # Cambia verde oscuro a rojo
            svg_content = svg_content.replace("#dde9af", "#ffd5d5") # Cambia fondo verde claro a rojo claro
            
        svg_content = svg_content.replace("[Comparativo]", comparativo)        
        svg_content = svg_content.replace("[Descripcion]", descripcion)
        
        # Para depuración: st.code(svg_content, language="xml") permitiría ver el código generado.
        
        # Renderizado: Mostramos el contenido SVG modificado como una imagen.
        with st.container():
            st.image(svg_content, width=width)
        
    else:
        # Manejo de errores: Informar al usuario si falta el archivo plantilla.
        st.error(f"Archivo no encontrado: {svg_path}")

# ==============================================================================
# SECCIÓN 1: Métricas Nativas
# ==============================================================================
st.subheader("Métricas con componente nativo de Streamlit:")

# st.container permite agrupar elementos. horizontal=True los pone uno al lado del otro.
with st.container(horizontal=True):
    # st.metric es el componente estándar. Es fácil de usar pero limitado en diseño.
    st.metric(":material/chart_data: Ventas Mensuales", "$ 50,000,000", "+15% vs Mes Anterior")
    st.metric(":blue[Ingresos]", "$ 20,000,000", "-10% vs Mes Anterior")
    # Uso de colores de fondo nativos de Streamlit (novedad en versiones recientes).
    st.metric(":green-background[Unidades]", "5,730 und", "+17% vs Mes Anterior")
    st.metric("Usuarios Activos", "1,200", "+8%")

# ==============================================================================
# SECCIÓN 2: Métricas Personalizadas con SVG
# ==============================================================================
# Selector para permitir al usuario controlar dinámicamente el tamaño de los SVG.
parAncho = st.selectbox(
    "Selecciona el ancho de las métricas:", 
    options=["stretch", "content", 200, 300, 500], 
    index=0
)

st.subheader("Métricas en contenedor horizontal:")

# Renderizamos los SVG personalizados en una fila centrada.
# Llamamos a nuestra función 'modificar_svg' pasando los datos específicos para cada KPI.
with st.container(horizontal=True, horizontal_alignment="center"):     
    modificar_svg("metricaVentas.svg", "Ventas Mensuales", "$ 50,000,000", "+15% vs Mes Anterior", "+", "", parAncho)  
    # Nota: Aquí pasamos "-" como signo, lo que activará el cambio de color a rojo en la función.
    modificar_svg("metricaIngresos.svg", "Ingresos", "$ 20,000,000", "-10% vs Semana Anterior", "-", "", parAncho)
    modificar_svg("metricaColor.svg", "Unidades", "5,730 und", "+17% vs Mes Anterior", "", "", parAncho)
    modificar_svg("metricaHorizontal.svg", "Usuarios Activos", "1,200", "+8%", "+", "Crecimiento Sostenido de Usuarios", parAncho)
    modificar_svg("metricaVentas2.svg", "Ventas Mensuales 2", "$ 40,000,000", "+10%", "+", "Ventas comparativas", parAncho)
st.subheader("Métricas en columnas:")

# st.columns divide el ancho de la página en 4 columnas iguales para un control más preciso del layout.
cols = st.columns(5)

# Asignamos cada métrica a una columna específica.
with cols[0]:
    modificar_svg("metricaVentas.svg", "Ventas Mensuales", "$ 50,000,000", "+15% vs Mes Anterior", "", "", parAncho)
with cols[1]:
    modificar_svg("metricaIngresos.svg", "Ingresos", "$ 20,000,000", "-10% vs Semana Anterior", "-", "", parAncho)
with cols[2]:
    modificar_svg("metricaColor.svg", "Unidades", "5,730 und", "+17% vs Mes Anterior", "", "", parAncho)
with cols[3]:
    modificar_svg("metricaHorizontal.svg", "Usuarios Activos", "1,200", "+8%", "+", "Crecimiento Sostenido de Usuarios", parAncho)
with cols[4]:
    modificar_svg("metricaVentas2.svg", "Ventas Mensuales 2", "$ 40,000,000", "+10%", "+", "Ventas comparativas", parAncho)