# Importar las librerías necesarias
import streamlit as st  # Para crear la interfaz web. Instalar con: pip install streamlit
import pandas as pd  # Para manipular datos. Instalar con: pip install pandas

# Cargar el archivo CSV con los datos de días festivos
dfHolidays = pd.read_csv("WorldHolidays.csv", sep=";")

# Configurar la página de Streamlit
st.set_page_config(page_title="Calculadora Freelance", layout="wide")

# Añadir CSS personalizado
st.html(
    """
    <style>    
    div[data-testid="stVerticalBlockBorderWrapper"] div div div:has(div.st-key-parametros)
    {
        background-color:white
    }
    div[data-testid="stVerticalBlockBorderWrapper"] div div div:has(div.st-key-ecuacion),
    div[data-testid="stVerticalBlockBorderWrapper"] div div div:has(div.st-key-resultados)
    {
        background-color:white
    }
    label[data-testid="stMetricLabel"] p, /*Para la etiqueta de las métricas*/
    label[data-testid="stWidgetLabel"] p /*Para la etiqueta de los input*/
    {
        font-size: 25px;
    }
    div[data-baseweb="select"], /*Para el selector de países*/
    div[data-testid="stTooltipHoverTarget"], /*Para el selector de países*/
    input /*Para los inputs*/
    {
        font-size: 18px!important;
    }
    div[data-testid="stMetricValue"]{
        font-weight:bold;
        color: #0068c9;
    }
    </style>
    """
)

# Mostrar el encabezado
st.header(":blue[:material/request_quote:] Calculadora Freelance")

# Función para actualizar los festivos en la sesión
def actualizarFestivos(valor):
    if "festivos" not in st.session_state:
        st.session_state.festivos = valor

with st.container(border=True,key="parametros"):
    # Crear columnas para los inputs
    c1, c2, c3, c4 = st.columns(4)  

    # Selector de país
    parpais = c1.selectbox(":blue[:material/public:] Selecciona tu país", dfHolidays["Country"].unique(), key="input-pais", help="Selecciona el país para cargar los festivos estándar")
    st.session_state.festivos = dfHolidays.loc[dfHolidays["Country"] == parpais, "MinHolidays"].values[0]

    # Input para días festivos
    parFestivos = c2.number_input(":blue[:material/event:] Días festivos", min_value=0, max_value=365, value=int(st.session_state.festivos), key="input-festivos")

    # Input para días de la semana trabajados
    pardias_semana = c3.number_input(":blue[:material/work:] Días de la semana a trabajar", min_value=1, max_value=7, value=5, key="input-dias-semana")

    # Input para horas trabajadas por día
    parhoras_dia = c4.number_input(":blue[:material/hourglass_bottom:] Horas a trabajar por día", min_value=1, max_value=24, value=8, key="input-horas-dia")

    # Crear nuevas columnas para más inputs
    c1, c2 = st.columns(2)

    # Input para días de vacaciones
    pardias_vacaciones = c1.number_input(":blue[:material/beach_access:] Días de vacaciones", min_value=1, value=15, key="input-vacaciones")

    # Input para días de incapacidad o permisos
    pardias_incapacidad_permisos = c2.number_input(":blue[:material/medical_information:] Días incapacidad o permisos", min_value=0, max_value=24, value=8, key="input-incapacidad-permisos", help="Son días que estimas no trabajar por enfermedad o actividades personales")

    # Crear nuevas columnas para más inputs
    c1, c2, c3 = st.columns(3)

    # Input para salario deseado
    parSalarioDeseado = c1.number_input(":green[:material/payments:] Salario deseado")

    # Input para gastos mensuales
    parGastosMensuales = c2.number_input(":green[:material/shopping_basket:] Gastos mensuales", value=0, key="input-gastos-mensuales")

    # Input para porcentaje de utilidades
    parPorcentajeUtilidades = c3.number_input(":green[:material/savings:] Porcentaje de utilidades", min_value=0, max_value=100, value=30, key="input-porcentaje-utilidades")

# Cálculo de días y horas laborales
diasLaborales = 365 - parFestivos - pardias_vacaciones - pardias_incapacidad_permisos
# Cálculo de días laborales netos teniendo en cuenta la cantidad de días por semana a trabajar
diasLaborales= diasLaborales *(pardias_semana/7)
# Cálculo de horas laborales
horasLaborales = diasLaborales *parhoras_dia

# Cálculo de ingresos requeridos
parIngresosRequeridos = (parSalarioDeseado + parGastosMensuales) * (1 + parPorcentajeUtilidades / 100)

# Cálculo del costo por hora
costohora = parIngresosRequeridos * 12 / horasLaborales

#Horas laborales al mes
horasLaboralesMes = horasLaborales / 12
# Mostrar los resultados en un contenedor
with st.container(border=True,key="resultados"):
    st.subheader("Resultados")
    columnas = st.columns(5)
    columnas[0].metric("Días laborales al año", f"{diasLaborales:,.0f} días")
    columnas[1].metric("Horas laborales al año", f"{horasLaborales:,.0f} horas")
    columnas[2].metric("Horas laborales al mes", f"{horasLaboralesMes:,.0f} horas")
    columnas[3].metric("Ingresos requeridos mensuales", f"$ {parIngresosRequeridos:,.2f}")
    columnas[4].metric("Precio por hora", f" $ {costohora:,.2f}")

# Mostrar la ecuación utilizada en un contenedor
with st.container(border=True,key="ecuacion"):
    st.subheader("Fórmula utilizada")   
    c1, c2 = st.columns(2)
    with c1:
        # Editor de ecuaciones en formato LaTeX https://editor.codecogs.com/
        # Importante no olvidar que los \ deben ir dobles y que si se ponen espacios en la ecuación, deben ir con \ antes
        parEcuacion = """
        \\left(\\frac{(Salario + Gastos)*12}{Horas\ Laborables Año}\\right)*(1+\%\ utilidad)=Costo\ por\ hora          
        """
        
        st.latex(parEcuacion)  # Mostrar la ecuación en formato LaTeX
    with c2:
        parEcuacion = f"""
        \\left(\\frac{{{parSalarioDeseado:,.0f} + {parGastosMensuales:,.0f}}}{{{horasLaborales:,.0f}}}\\right)*(1+{parPorcentajeUtilidades:,.2f} \%)={costohora:,.2f}  

        """
        st.latex(parEcuacion)  # Mostrar la ecuación en formato LaTeX con los valores ingresados