# --------------------------------------------------------------------------
# EXPLICACIÓN DE LIBRERÍAS E INSTALACIÓN
# --------------------------------------------------------------------------
# streamlit: Framework para crear aplicaciones web interactivas con Python.
#            Ideal para visualizar datos y crear dashboards rápidamente.
#            Comando de instalación: pip install streamlit
#
# pandas: Librería fundamental para la manipulación y análisis de datos.
#         Proporciona estructuras de datos como DataFrames para trabajar
#         eficientemente con datos tabulares.
#         Comando de instalación: pip install pandas
#
# matplotlib: Librería estándar para crear visualizaciones estáticas,
#             animadas e interactivas en Python. Usada aquí como base
#             para PyWaffle.
#             Comando de instalación: pip install matplotlib
#
# pywaffle: Librería construida sobre Matplotlib para crear gráficos de
#           tipo 'waffle' (gofre o pictograma), útiles para mostrar
#           proporciones o partes de un todo de forma visualmente atractiva.
#           Comando de instalación: pip install pywaffle
#           https://pywaffle.readthedocs.io/en/latest/index.html
# --------------------------------------------------------------------------

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pywaffle import Waffle # Importa específicamente la clase Waffle desde pywaffle

# --------------------------------------------------------------------------
# CONFIGURACIÓN INICIAL DE LA PÁGINA DE STREAMLIT
# --------------------------------------------------------------------------
# Establece la configuración de la página de la aplicación Streamlit.
# Esto debe ser el primer comando de Streamlit que se ejecute.
st.set_page_config(
    page_title="Pictogramas con Streamlit", # Título que aparece en la pestaña del navegador
    layout="wide" # Utiliza el ancho completo de la página para el contenido
)

# Agrega un enlace a la hoja de estilos de Font Awesome para usar iconos personalizados en la aplicación.
st.write('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.0/css/all.min.css"/>', unsafe_allow_html=True)
# --------------------------------------------------------------------------
# TÍTULO DE LA APLICACIÓN
# --------------------------------------------------------------------------
# Muestra el título principal en la aplicación web.
st.header("Adultos con educación terciaria en el mundo")
st.subheader("Pictogramas con Streamlit")

# --------------------------------------------------------------------------
# CARGA Y PREPROCESAMIENTO DE DATOS CON PANDAS
# --------------------------------------------------------------------------
# URL del archivo CSV con los datos de 'Our World In Data'.
# Los datos corresponden al porcentaje de la población con educación terciaria completa.
# storage_options: Se usa para pasar parámetros adicionales al backend de almacenamiento.
#                  En este caso, se establece un 'User-Agent' que algunos servidores
#                  requieren para permitir la descarga programática de datos.
DATA_URL = "https://ourworldindata.org/grapher/share-of-the-population-with-completed-tertiary-education.csv?v=1&csvType=full&useColumnShortNames=true"
df = pd.read_csv(DATA_URL, storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})

# Renombra una columna para que sea más corta y fácil de usar.
# Se cambia el nombre largo 'mf_adults__25_64_years__percentage_of_tertiary_education'
# por 'adults_25_64_tertiary'.
df = df.rename(columns={"mf_adults__25_64_years__percentage_of_tertiary_education": "adults_25_64_tertiary"})

# Filtra el DataFrame para mantener solo las filas donde el año es 1950 o posterior.
# Esto se hace mediante indexación booleana: df["Year"]>=1950 crea una Serie de
# booleanos (True/False) y df[...] selecciona solo las filas donde la condición es True.
df = df[df["Year"]>=1950]

# Crea una copia del DataFrame filtrado por año.
# Esta copia se usará más adelante para la sección de comparación entre países en un año específico,
# sin que se vea afectada por el filtrado por país que se hace a continuación.
dfPaises = df.copy()

# --------------------------------------------------------------------------
# SECCIÓN 1: VISUALIZACIÓN POR PAÍS A TRAVÉS DE LOS AÑOS
# --------------------------------------------------------------------------
# Crea un widget de selección (selectbox) en Streamlit.
# Permite al usuario elegir un país de la lista de países únicos presentes en la columna 'Entity'.
# El país seleccionado se guarda en la variable 'parPais'.
parPais = st.selectbox("Selecciona un país", df["Entity"].unique())

# Filtra el DataFrame principal 'df' para mantener solo las filas correspondientes al país seleccionado.
# Nuevamente, se utiliza indexación booleana.
df = df[df["Entity"]==parPais]

# Filtra el DataFrame 'df' (ya filtrado por país) para incluir solo los años específicos
# en un rango (1950, 1960, 1970,... hasta 2030).
# Se usa range(1950, 2031, 10) para generar la secuencia de años.
# .isin() verifica si los valores de la columna 'Year' están presentes en la secuencia generada.
# .reset_index() reinicia el índice del DataFrame resultante para que sea secuencial (0, 1, 2...).
# Esto es útil después de filtrar, ya que los índices originales pueden quedar discontinuos.
df = df[df["Year"].isin(range(1950, 2031, 10))].reset_index()

# Crea 4 columnas en la interfaz de Streamlit para organizar los gráficos.
cols = st.columns(4)

# Itera sobre cada fila del DataFrame filtrado por país y años específicos.
# .iterrows() devuelve el índice y la fila (como una Serie de Pandas) en cada iteración.
for index, fila in df.iterrows():

    # Obtiene el valor del porcentaje de educación terciaria para la fila actual.
    valor = fila["adults_25_64_tertiary"]
    # Calcula el valor complementario (100 - porcentaje) para el gráfico waffle.
    valor2 = 100 - valor

    # Crea una figura de Matplotlib utilizando la clase Waffle.
    fig = plt.figure(
        FigureClass=Waffle,
        rows=5,                      # Número de filas de iconos en el waffle. 5x10 = 50 iconos total.
        columns=20,                  # Número de columnas de iconos en el waffle.
        values=[valor, valor2],      # Los valores que determinarán las proporciones. Se escalarán a 100.
        font_size=20,
        title={                      # Configuración del título del gráfico.
            'label': f'Adultos de {fila["Entity"]} con educación terciaria \n en el año {fila["Year"]}',
            'loc': 'center',         # Ubicación del título.
            'fontdict': {            # Diccionario para personalizar la fuente del título.
                'fontsize': 20
            }
        },
        labels=["Con educación terciaria", "Sin educación terciaria"], # Etiquetas para la leyenda.
        colors=["#A1C398", "#FFAAAA"], # Colores para cada categoría en 'values'.
        legend={                     # Configuración de la leyenda.
            'loc': 'lower left',     # Posición de la leyenda.
            'bbox_to_anchor': (0, -0.4), # Ajuste fino de la posición de la leyenda (fuera del gráfico).
            'ncol': 2,               # Número de columnas en la leyenda.
            'framealpha': 0,         # Transparencia del marco de la leyenda (0 = invisible).
            'fontsize': 12           # Tamaño de la fuente de la leyenda.
        }
    )
    # Añade el texto del porcentaje exacto en el centro del gráfico waffle.
    fig.text(0.5, 0.5, f'{valor:.2f}%', fontsize=30, color='black', ha='center', va='center')

    # Determina en qué columna (de las 4 creadas) se debe mostrar el gráfico actual.
    # El operador módulo (%) asegura que los gráficos se distribuyan secuencialmente (0, 1, 2, 3, 0, 1...).
    col = index % 4
    # Usa un bloque 'with' para colocar el gráfico dentro de la columna calculada.
    with cols[col]:
        # Muestra la figura de Matplotlib en la aplicación Streamlit.
        # use_container_width=True hace que el gráfico se ajuste al ancho de la columna.
        st.pyplot(fig, use_container_width=True)

# --------------------------------------------------------------------------
# SECCIÓN 2: COMPARACIÓN ENTRE PAÍSES EN UN AÑO ESPECÍFICO
# --------------------------------------------------------------------------
# Crea un widget de selección (selectbox) para elegir un año.
# Utiliza los años únicos presentes en la copia del DataFrame 'dfPaises'.
parAnio = st.selectbox("Selecciona un año", dfPaises["Year"].unique())

# Crea un widget multiselect para que el usuario pueda elegir uno o más países.
# Utiliza los países únicos presentes en la copia del DataFrame 'dfPaises'.
parPais = st.multiselect("Selecciona un país", dfPaises["Entity"].unique())

# Filtra el DataFrame 'dfPaises' para mantener solo las filas del año seleccionado.
dfPaises = dfPaises[dfPaises["Year"]==parAnio]

# Filtra el DataFrame 'dfPaises' (ya filtrado por año) para incluir solo los países seleccionados.
# Se usa .isin() porque 'parPais' es una lista (resultado del multiselect).
# .reset_index() se usa de nuevo para limpiar el índice.
dfPaises = dfPaises[dfPaises["Entity"].isin(parPais)].reset_index()

# Crea un widget checkbox para permitir al usuario elegir el tipo de gráfico waffle.
# value=True: El checkbox está marcado por defecto.
# help="...": Texto de ayuda que aparece al pasar el cursor sobre el checkbox.
parPorPorcentaje = st.checkbox("Por porcentaje", value=True, help="Si está marcado, se mostrará la proporción (hasta 100) sino el valor como puntos.")

# Crea 4 columnas nuevamente para esta sección.
cols = st.columns(4)

# Itera sobre cada fila del DataFrame 'dfPaises' (filtrado por año y países seleccionados).
for index, fila in dfPaises.iterrows():

    # Obtiene el valor del porcentaje de educación terciaria.
    valor = fila["adults_25_64_tertiary"]
    # Calcula el valor complementario (solo necesario si se muestra la proporción).
    valor2 = 100 - valor

    # Crea la figura de Matplotlib/Waffle con lógica condicional basada en el checkbox.
    fig = plt.figure(
        FigureClass=Waffle,
        # Condicional: 5 filas si es proporción (hasta 100), None si es por valor (pywaffle decide).
        rows=5 if parPorPorcentaje else None,
        # Condicional: 10 columnas si es proporción (5x10=50, escalado a 100), None si es por valor.
        columns=20 if parPorPorcentaje else None,
        # Condicional: Usa [valor, valor2] si es proporción, [valor] si es por valor.
        values=[valor, valor2] if parPorPorcentaje else [valor],
        # Usa un carácter específico (círculo) para los iconos del waffle.
        # characters='⬤',        
        characters='✔',
        # characters='☻',
        # characters='♥',
        # characters='☎',
        # Tamaño de la fuente de los caracteres/iconos.
        font_size=20,
        # Configuración del título (igual que antes).
        title={
            'label': f'Adultos de {fila["Entity"]} con educación terciaria \n en el año {fila["Year"]}',
            'loc': 'center',
            'fontdict': {
                'fontsize': 20
            }
        },
        # Condicional: Usa dos colores si es proporción, uno si es por valor.
        colors=["#A1C398", "#FFAAAA"] if parPorPorcentaje else ["#A1C398"],
        # Condicional: Usa dos etiquetas si es proporción, una si es por valor.
        labels=["Con educación terciaria", "Sin educación terciaria"] if parPorPorcentaje else ["Con educación terciaria"],
        # Configuración de la leyenda (igual que antes).
        legend={
            'loc': 'lower left',
            'bbox_to_anchor': (0, -0.4),
            'ncol': 2,
            'framealpha': 0,
            'fontsize': 12
        }
    )
    # Añade el texto del porcentaje en el centro del gráfico (funciona bien en ambos modos).
    fig.text(0.5, 0.5, f'{valor:.2f}%', fontsize=30, color='black', ha='center', va='center')

    # Determina la columna para mostrar el gráfico (igual que antes).
    col = index % 4
    # Muestra el gráfico en la columna correspondiente (igual que antes).
    with cols[col]:
        st.pyplot(fig, use_container_width=True)

# Nota: No hay funciones definidas en este script, por lo que no se añaden docstrings de función.
# Si hubiera funciones, seguirían el formato estándar de docstrings de Python.

def generarPictogramaMultiple(iconos,valores,etiquetas, titulo,colores,tamano=5):        
    with st.container(border=True):
        st.subheader(f"{titulo}")
        colsEtiqueta =st.columns(len(valores))        
        tamanoFuente = int(tamano/2)
        for i in range(len(valores)):
            with colsEtiqueta[i]:
                if len(iconos)>1:
                    icono=iconos[i]
                else:
                    icono=iconos[0]
                st.html(f'<i class="fa-solid {icono} fa-{tamanoFuente}x fa-fw" style="color: {colores[i]}"></i><span style="color: {colores[i]};font-size:{tamanoFuente+0.5}em"> {etiquetas[i]} - {valores[i]}%</span>')
                
        cols =st.columns(20)        
        contador=1
        limite=valores[0]
        color=colores[0]
        valActual=0
        contador=1
        for i in range(20):                                    
            with cols[i]:
                for j in range(5):                
                    if contador>limite:
                        valActual+=1
                        limite=contador+valores[valActual]                        
                    color=colores[valActual]
                    if len(iconos)>1:
                        icono=iconos[valActual]
                    else:
                        icono=iconos[0]                    
                    st.html(f'<i class="fa-solid {icono} fa-{tamano}x fa-fw" style="color: {color};height:50px"></i>')
                    contador+=1
c1,c2=st.columns(2)
with c1:
    generarPictogramaMultiple(["fa-user-graduate","fa-person","fa-cloud"], [37, 60,3],["Graduados","Sin estudio","Otros"], "Graduados", ["#A1C398","#FFAAAA","#90D1CA"],2)