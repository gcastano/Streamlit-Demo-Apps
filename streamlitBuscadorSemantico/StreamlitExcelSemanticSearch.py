# Importa las librerías necesarias
import streamlit as st  # Para la creación de la aplicación web
import pandas as pd  # Para la manipulación y análisis de datos
import numpy as np  # Para operaciones numéricas eficientes
import spacy  # Para el procesamiento del lenguaje natural (NLP)
from sklearn.feature_extraction.text import TfidfVectorizer  # Para convertir texto a vectores TF-IDF
# Ejemplo de TF-IDF
# https://remykarem.github.io/tfidf-demo/
from sklearn.metrics.pairwise import cosine_similarity  # Para calcular la similitud del coseno entre vectores

# Instala las librerías necesarias (si aún no lo has hecho)
# pip install streamlit pandas numpy spacy scikit-learn

# Configuración de la página de Streamlit
st.set_page_config(
    page_title="Búsqueda de fórmulas de Excel",  # Título de la página
    page_icon="💻",  # Icono de la página
    layout="wide",  # Diseño de página ancho para aprovechar al máximo el espacio
    initial_sidebar_state="expanded"  # Barra lateral expandida por defecto
)

# Lista de componentes de procesamiento de lenguaje natural (NLP) de spaCy que no se utilizarán
# Estos componentes se desactivan para mejorar el rendimiento, ya que no son necesarios para esta tarea.
unwanted_pipes = ["ner", "parser"]

# Carga el modelo de lenguaje español de spaCy
# Este modelo se utiliza para tokenizar el texto y obtener las raíces de las palabras (lemas).
nlp = spacy.load("es_core_news_sm")

# Función para tokenizar el texto utilizando spaCy
def spacy_tokenizer(doc):
    """
    Tokeniza el texto utilizando spaCy y realiza un procesamiento básico:

    1. Deshabilita los componentes de NLP no deseados (NER y análisis sintáctico).
    2. Tokeniza el texto (lo divide en palabras y signos de puntuación).
    3. Obtiene el lema (raíz de la palabra) de cada token.
    4. Filtra los tokens para mantener solo palabras alfabéticas y eliminar signos de puntuación y espacios en blanco.

    Args:
        doc: El texto a tokenizar.

    Returns:
        Una lista de tokens (lemas) del texto.
    """
    with nlp.disable_pipes(*unwanted_pipes):
        return [t.lemma_ for t in nlp(doc) if not t.is_punct and not t.is_space and t.is_alpha]

# Función para generar las características TF-IDF del corpus
@st.cache_resource  # Almacena en caché el resultado de la función para mejorar el rendimiento
def generarFeatures(corpus):
    """
    Genera las características TF-IDF del corpus:

    1. Crea un objeto TfidfVectorizer, que se utiliza para convertir una colección de documentos de texto en una matriz de características TF-IDF.
    2. Ajusta el vectorizador al corpus (aprende el vocabulario y los pesos IDF).
    3. Transforma el corpus en una matriz TF-IDF, donde cada fila representa un documento y cada columna representa una palabra del vocabulario.

    Args:
        corpus: Una lista de documentos de texto.

    Returns:
        Una tupla que contiene:
            - La matriz de características TF-IDF.
            - El objeto vectorizador TF-IDF.
    """
    vectorizer = TfidfVectorizer(tokenizer=spacy_tokenizer)
    features = vectorizer.fit_transform(corpus)
    return features, vectorizer

# Función para obtener los índices de los k elementos principales de una matriz
def top_k(arr, k):
    """
    Devuelve los índices de los k elementos principales de una matriz.

    Args:
        arr: La matriz.
        k: El número de elementos principales a devolver.

    Returns:
        Una matriz NumPy que contiene los índices de los k elementos principales.
    """
    kth_largest = (k + 1) * -1
    return np.argsort(arr)[:kth_largest:-1]

# Carga los archivos CSV que contienen las fórmulas de Excel en español e inglés
# Estos archivos deben estar en la misma carpeta que el script de Python.
dfFormulasES = pd.read_csv('excelformulasES.csv')
dfFormulasEN = pd.read_csv('excelformulasEN.csv')

# Título de la aplicación
st.header('Búsqueda de fórmulas de Excel')

# URLs de las fuentes de las fórmulas
URL_ES = "https://support.microsoft.com/es-es/office/funciones-de-excel-por-orden-alfab%C3%A9tico-b3944572-255d-4efb-bb96-c6d90033e188"
URL_EN = "https://support.microsoft.com/en-us/office/excel-functions-alphabetical-b3944572-255d-4efb-bb96-c6d90033e188"

# Muestra las URLs de las fuentes de las fórmulas
st.info(f"Formula Sources: [SPANISH]({URL_ES}), [ENGLISH]({URL_EN})")

# Selector de idioma
parIdioma = st.radio('Idioma / Language', options=['Español', 'English'], index=0, horizontal=True)

# Inicializa las variables en función del idioma seleccionado
if parIdioma == 'Español':
    dfFormulasES['corpus'] = dfFormulasES['descripcion'] + ' ' + dfFormulasES['formula']
    corpus = dfFormulasES['corpus'].values.astype('U')  # Convierte el texto a Unicode
    etiquetaBusqueda = 'Para qué busca la fórmula'
    etiquetaBoton = 'Buscar'
    etiquetaCantResult = 'Cantidad de resultados'
    etiquetaNoEncontrado = 'No se encontraron fórmulas con las características solicitadas: '
    dfFormulas = dfFormulasES
    tabs=['Búsqueda semántica','Datos']
else:
    dfFormulasEN['corpus'] = dfFormulasEN['descripcion'] + ' ' + dfFormulasEN['formula']
    corpus = dfFormulasEN['corpus'].values.astype('U')
    etiquetaBusqueda = 'What kind of formula are you looking for?'
    etiquetaCantResult = 'Number of results'
    etiquetaBoton = 'Search'
    etiquetaNoEncontrado = 'No formulas were found with the characteristics: '
    dfFormulas = dfFormulasEN
    tabs=['Semantic Search','Data']

# Crea dos pestañas: "Búsqueda semántica" y "Datos"
tabBuscar,tabDatos = st.tabs(tabs)

# Contenido de la pestaña "Búsqueda semántica"
with tabBuscar:
    # Genera las características TF-IDF del corpus
    features, vectorizer = generarFeatures(corpus)
        
    # Cuadro de texto para la búsqueda
    parTexto = st.text_input(etiquetaBusqueda)

    # Control deslizante para seleccionar la cantidad de resultados
    parNumResult = st.number_input(etiquetaCantResult, min_value=5, max_value=20, value=10)

    # Botón de búsqueda
    btnBuscar = st.button(etiquetaBoton)

    # Cuando se presiona el botón de búsqueda
    if btnBuscar:
        # Procesa la consulta
        query = [parTexto]
        query_tfidf = vectorizer.transform(query) # Vectorizamos la consulta

        # Calcula la similitud del coseno entre la consulta y todas las fórmulas
        cosine_similarities = cosine_similarity(features, query_tfidf).flatten()        
        
        # Obtiene los índices de las fórmulas más similares
        top_related_indices = top_k(cosine_similarities, parNumResult)
        similarities = cosine_similarities[top_related_indices]        
        
        # Divide la página en tres columnas
        cols = st.columns(3)
        i = 0
 
        # Muestra las fórmulas más similares        
        if similarities.sum() > 0:
            # Filtramos los items encontrados
            dfFormulasEncontradas =dfFormulas.iloc[top_related_indices]
            # Aplicamos los niveles de similitud
            dfFormulasEncontradas['similitud']=similarities
            
            # Itera sobre las fórmulas encontradas y las muestra en las columnas
            for index, fila in dfFormulasEncontradas.sort_values('similitud', ascending=False).iterrows():
                formula = fila['formula']
                nombreFormula = fila['nombreFormula']
                if formula != nombreFormula:
                    formula = f'{formula} / {nombreFormula}'
                sintaxis = fila['sintaxis'].replace('=', '')
                sintaxis = f'={sintaxis}'
                descripcion = fila['descripcion']
                similarity = fila['similitud']
                url = fila['url']
                categoria = fila['categoria']
                texto = f"""<div style='background-color:#F1FADA;margin:5px;padding:10px;border-radius:10px'>
                <a href='{url}'><h4>{formula}</h4></a><i>{categoria}</i><br />
                <code>{sintaxis}</code><br />
                {descripcion}</div>
                    """
                if similarity > 0:
                    if i == 3:
                        i = 0
                    col = cols[i]
                    col.write(texto, unsafe_allow_html=True)
                    col.progress(similarity, f"Similitud **:blue[{similarity:.2%}]**")
                    i = i + 1
        else:
            st.warning(f'{etiquetaNoEncontrado} **{parTexto}**')

# Contenido de la pestaña "Datos"
with tabDatos:
    # Muestra el DataFrame con las fórmulas en una tabla interactiva
    st.dataframe(dfFormulas[['formula','nombreFormula', 'categoria', 'descripcion', 'sintaxis']],use_container_width=True)