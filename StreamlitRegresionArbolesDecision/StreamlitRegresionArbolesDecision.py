# ==============================================================================
# LIBRERÍAS Y SUS COMANDOS DE INSTALACIÓN
# ==============================================================================

# streamlit: Una librería de Python que permite crear aplicaciones web interactivas 
# para proyectos de ciencia de datos y machine learning con muy poco código.
# Para instalarla, ejecuta en tu terminal: pip install streamlit
import streamlit as st

# pandas: Es una librería fundamental para la manipulación y análisis de datos en Python. 
# Proporciona estructuras de datos como el DataFrame, que es esencial para trabajar
# con datos tabulares (como los de un archivo CSV).
# Para instalarla, ejecuta en tu terminal: pip install pandas
import pandas as pd

# pickle: Este módulo es parte de la librería estándar de Python. Se utiliza para
# serializar y deserializar objetos de Python, lo que significa que puedes guardar
# objetos (como un modelo de machine learning entrenado) en un archivo y cargarlo
# más tarde para usarlo. No requiere instalación adicional.
import pickle

# plotly.express: Es una interfaz de alto nivel para Plotly, que permite crear
# figuras y gráficos interactivos y de alta calidad de manera muy sencilla.
# Para instalarla, ejecuta en tu terminal: pip install plotly
import plotly.express as px

# ==============================================================================
# DESCRIPCIÓN DEL PROYECTO
# Este script de Python utiliza la librería Streamlit para crear una aplicación web interactiva.
# El propósito de la aplicación es estimar el precio de las propiedades (casas o apartamentos)
# en la ciudad de Medellín, Colombia.

# Funcionalidades principales:
# 1.  Carga un modelo de machine learning pre-entrenado (un árbol de decisión) desde un archivo .pkl.
# 2.  Permite al usuario introducir características de una propiedad a través de una interfaz web
#     (tipo de propiedad, barrio, número de habitaciones, baños, área, etc.).
# 3.  Utiliza el modelo para predecir el precio de la propiedad basándose en las características
#     introducidas por el usuario.
# 4.  Muestra la predicción y estadísticas comparativas de propiedades similares existentes en el
#     dataset original.
# 5.  Visualiza distribuciones de precios, áreas y habitaciones para las propiedades similares
#     mediante histogramas interactivos.
# ==============================================================================

# Configuración de la página de Streamlit.
# page_title: Define el título que aparece en la pestaña del navegador.
# layout="wide": Hace que el contenido de la aplicación ocupe todo el ancho de la pantalla.
st.set_page_config(page_title="Estimación precio de propiedades Medellín", layout="wide")

# Muestra un título principal en la aplicación web.
st.title("Estimación precio de propiedades Medellín")

# Carga del modelo de machine learning.
# 'rb' significa 'read binary' (leer en modo binario), que es el modo necesario para
# abrir archivos guardados con pickle.
# La variable 'modelo' ahora contiene el objeto del modelo entrenado, listo para hacer predicciones.
modelo = pickle.load(open("modeloArbolEstimacionBR.pkl", "rb"))

# Carga de los datasets desde archivos CSV usando pandas.
# pd.read_csv() lee un archivo de valores separados por comas y lo convierte en un DataFrame de pandas.
# dfNeighbourhood: Contiene la correspondencia entre los nombres de los barrios y su versión codificada numéricamente.
dfNeighbourhood = pd.read_csv("neighbourhood.csv")
# dfPropertyType: Contiene la correspondencia entre los tipos de propiedad y su versión codificada.
dfPropertyType = pd.read_csv("property_type.csv")
# dfPropiedades: Contiene el dataset principal con todas las propiedades y sus características.
dfPropiedades = pd.read_csv("propiedades.csv")

# Creación de tres columnas para organizar la interfaz de usuario.
# Esto ayuda a distribuir los elementos de entrada y salida de forma ordenada.
c1,c2,c3 = st.columns(3)

# La primera columna (c1) contendrá los inputs principales sobre la propiedad.
with c1:    
    # st.selectbox crea una lista desplegable para que el usuario elija una opción.
    # El primer argumento es la etiqueta que ve el usuario.
    # 'options' se llena con los valores únicos de la columna 'property_type' del DataFrame dfPropertyType.
    property_type = st.selectbox("Tipo de propiedad", options=dfPropertyType['property_type'].unique())
    neighbourhood = st.selectbox("Barrio", options=dfNeighbourhood['neighbourhood'].unique())
    
    # st.number_input crea un campo para que el usuario ingrese un número.
    # min_value y max_value definen el rango permitido.
    # 'value' establece el valor por defecto que se muestra al cargar la página.
    rooms = st.number_input("Habitaciones", min_value=1, max_value=10, value=3)
    baths = st.number_input("Baños", min_value=1.0, max_value=10.0, value=2.0)

# La segunda columna (c2) contendrá el resto de los inputs.
with c2:    
    age = st.number_input("Antigüedad (años)", min_value=0.0, max_value=100.0, value=1.0)
    area = st.number_input("Área (m²)", min_value=10.0, max_value=5000.0, value=83.0)
    garages = st.number_input("Garajes", min_value=0, max_value=5, value=1)
    stratum = st.selectbox("Estrato", options=[1, 2, 3, 4, 5, 6], index=3) # index=3 selecciona el '4' como valor por defecto.

    # ==========================================================================
    # TRANSFORMACIÓN DE DATOS CON PANDAS (Label Encoding)
    # ==========================================================================
    # El modelo de machine learning no entiende texto ("Apartamento", "El Poblado"),
    # solo números. Por lo tanto, debemos convertir las selecciones del usuario
    # a los códigos numéricos con los que fue entrenado el modelo.

    # 1. Búsqueda del código para 'property_type':
    # dfPropertyType['property_type'] == property_type: Crea una serie booleana (True/False) que es True
    # donde el valor de la columna 'property_type' coincide con la selección del usuario.
    # .loc[...]: Usa esta serie booleana para localizar la fila correcta en el DataFrame.
    # , 'property_type_Encoded']: De esa fila, selecciona el valor de la columna 'property_type_Encoded'.
    # .values[0]: Convierte el resultado a un array de NumPy y extrae el primer (y único) elemento.
    property_type_encoded = dfPropertyType.loc[dfPropertyType['property_type'] == property_type, 'property_type_Encoded'].values[0]
    
    # 2. Búsqueda del código para 'neighbourhood' (mismo proceso que el anterior).
    neighbourhood_encoded = dfNeighbourhood.loc[dfNeighbourhood['neighbourhood'] == neighbourhood, 'neighbourhood_Encoded'].values[0]

# La tercera columna (c3) se usará para mostrar el resultado de la predicción y estadísticas.
with c3:
    # Se crea un diccionario para organizar los datos de entrada del usuario.
    # El formato {0: valor} es necesario para que pandas lo interprete como una
    # única fila al crear el DataFrame que se pasará al modelo.
    input_dict = {
        'rooms': {0: rooms},
        'baths': {0: baths},
        'area': {0: area},
        'age': {0: age},
        'garages': {0: garages},
        'stratum': {0: stratum},
        'property_type_Encoded': {0: property_type_encoded},
        'neighbourhood_Encoded': {0: neighbourhood_encoded}
    }
    
    # st.container(border=True) crea un contenedor con un borde visible para agrupar elementos.
    with st.container(border=True):
        # El modelo espera recibir los datos en un DataFrame de pandas.
        # pd.DataFrame.from_dict() convierte el diccionario en un DataFrame.
        # modelo.predict() toma este DataFrame y devuelve un array con la predicción.
        resultado = modelo.predict(pd.DataFrame.from_dict(input_dict))
        
        # st.metric muestra un valor numérico de forma destacada, con una etiqueta.
        # f"${resultado[0]:,.0f}" formatea el número:
        # - resultado[0]: Obtiene el primer valor del array de predicción.
        # - : ,      : Agrega separadores de miles (ej. 1,000,000).
        # -   .0f    : Muestra el número como un flotante sin decimales.
        st.metric(label="Precio estimado (COP)", value=f"${resultado[0]:,.0f}")

        # Contenedor horizontal para mostrar varias métricas una al lado de la otra.
        with st.container(horizontal=True):
            # ==========================================================================
            # FILTRADO DE DATOS CON PANDAS PARA ESTADÍSTICAS COMPARATIVAS
            # ==========================================================================
            # Aquí filtramos el DataFrame original para encontrar propiedades que coincidan
            # con el tipo y barrio seleccionados por el usuario.
            # (dfPropiedades['property_type'] == property_type): Condición 1
            # (dfPropiedades['neighbourhood'] == neighbourhood): Condición 2
            # El operador '&' las combina (ambas deben ser ciertas).
            dfFiltrado = dfPropiedades[(dfPropiedades['property_type'] == property_type) & (dfPropiedades['neighbourhood'] == neighbourhood)]
            
            # Se muestran métricas calculadas a partir del DataFrame filtrado.
            st.metric(label="Propiedades en el dataset", value=len(dfFiltrado)) # len() cuenta el número de filas.
            st.metric(label="Precio promedio (COP)", value=f"${dfFiltrado['price'].mean():,.0f}") # .mean() calcula el promedio.
            st.metric(label="Área promedio (m²)", value=f"{dfFiltrado['area'].mean():,.0f} m²")
            st.metric(label="Habitaciones (Promedio)", value=f"{dfFiltrado['rooms'].mean():,.1f}")
            st.metric(label="Baños (Promedio)", value=f"{dfFiltrado['baths'].mean():,.1f}")
            st.metric(label="Garajes (Promedio)", value=f"{dfFiltrado['garages'].mean():,.1f}")

# Se crea una nueva sección con 3 columnas para los gráficos.
cols =st.columns(3)

# Primer gráfico en la primera columna.
with cols[0]:
    # px.histogram crea un histograma interactivo con Plotly Express.
    # dfFiltrado es el DataFrame con los datos a graficar (ya filtrados).
    # x="price" indica que la variable a analizar en el eje X es el precio.
    # nbins=10 define el número de barras en el histograma.
    fig = px.histogram(dfFiltrado, x="price", nbins=10, title=f"Distribución de precios - {neighbourhood} - {property_type}")    
    fig.update_layout(bargap=0.2)  # Ajusta el espacio entre las barras del histograma.
    with st.container(border=True):
        # st.plotly_chart renderiza el gráfico de Plotly dentro de la app de Streamlit.
        # use_container_width=True hace que el gráfico se ajuste al ancho de la columna.
        st.plotly_chart(fig, use_container_width=True)

# Segundo gráfico en la segunda columna.
with cols[1]:
    fig = px.histogram(dfFiltrado, x="area", nbins=10, title=f"Distribución de área - {neighbourhood} - {property_type}")
    fig.update_layout(bargap=0.2)
    with st.container(border=True):
        st.plotly_chart(fig, use_container_width=True)

# Tercer gráfico en la tercera columna.
with cols[2]:
    fig = px.histogram(dfFiltrado, x="rooms", nbins=10, title=f"Distribución de habitaciones - {neighbourhood} - {property_type}")
    fig.update_layout(bargap=0.2)
    with st.container(border=True):
        st.plotly_chart(fig, use_container_width=True)