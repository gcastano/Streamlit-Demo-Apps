"""
Librerías utilizadas en este script:
- streamlit: Framework de Python ideal para crear aplicaciones web interactivas para ciencia de datos de forma rápida.
- chromadb: Para consultar nuestra base de datos vectorial local.
    https://github.com/chroma-core/chroma
Comando de instalación:
pip install streamlit chromadb sentence-transformers
"""

import streamlit as st
import chromadb
from chromadb.utils import embedding_functions

# --- Configuración de la página ---
# Definimos el título, icono y hacemos que el diseño ocupe todo el ancho de la pantalla (layout="wide")
st.set_page_config(page_title="Sistema de recomendaciones de series de televisión", page_icon="⚡", layout="wide")

# --- Conexión a la Base de Datos Vectorial ---
@st.cache_resource
def init_db():
    """
    Inicializa la conexión con ChromaDB.
    El decorador @st.cache_resource asegura que la base de datos se conecte solo una vez,
    guardando el recurso en caché para que la aplicación no se vuelva lenta al recargar.
    
    Returns:
        collection: La colección de ChromaDB lista para hacer consultas.
    """
    client = chromadb.PersistentClient(path="./chroma_db")
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    collection = client.get_collection(name="tv_shows_collection", embedding_function=emb_fn)
    return collection

try:
    collection = init_db()
except Exception as e:
    # Mostramos un error amigable si el usuario olvidó correr el primer script
    st.error("No se encontró la base de datos. Ejecuta 'build_vectordb.py' primero.")
    st.stop() # Detiene la ejecución de la app web

@st.cache_data
def get_show_list():
    """
    Obtiene la lista completa de shows desde ChromaDB para llenar nuestro menú desplegable (Selectbox).
    Usa @st.cache_data porque estamos guardando datos simples (un diccionario) que no cambian seguido.
    
    Returns:
        dict: Diccionario en formato { "Nombre del show": "ID del show" }.
    """
    # Solo traemos los metadatos y los ids, no necesitamos los vectores pesados aquí
    all_data = collection.get(include=["metadatas"])
    show_dict = {meta['name']: id_ for id_, meta in zip(all_data['ids'], all_data['metadatas'])}
    return show_dict

@st.dialog("Información del Show", width="medium")
def display_show_info(meta):
    """
    Crea una ventana modal emergente (Dialog) en Streamlit para mostrar detalles
    extendidos de una serie como el resumen y su reparto principal.
    
    Args:
        meta (dict): Los metadatos de la serie obtenidos desde ChromaDB.
    """
    st.subheader(f"{meta['name']}", divider=True)
    st.write(meta['summary'])
    st.subheader("Cast Principal", divider=True)   
    
    # Creamos 2 columnas para organizar la lista de actores
    cols = st.columns(2)
    for i, actor in enumerate(meta['cast'].split(",")):
        with cols[i % 2]: # Alternamos los actores entre la columna 0 y la columna 1
            st.write(f":blue[:material/person:] {actor.strip()}")

def get_genres_str(genres_list):
    """
    Toma un string de géneros separados por comas y los convierte en etiquetas visuales
    (badges azules) usando la sintaxis Markdown nativa de Streamlit.
    
    Args:
        genres_list (str): Cadena de texto con géneros (ej: "Drama,Comedy").
        
    Returns:
        str: Cadena formateada para Streamlit (ej: ":blue-badge[Drama] :blue-badge[Comedy]").
    """
    genres = genres_list.split(",")
    genres = [f":blue-badge[{genre.strip()}]" for genre in genres]
    genres_str = " ".join(genres)
    return genres_str

# Estilos CSS personalizados inyectados para darle un aspecto moderno oscuro a las tarjetas de series
estilo ="""
<style>
    div[class*="st-key-tv_card"] {
        background-color: #101526;
    }
    
    div[data-testid="stImageContainer"] {
        position: relative; 
        display: inline-block; 
    }

    div[data-testid="stImageContainer"] img {
        display: block;
        width: 100%;
        height: auto;
    }

    div[data-testid="stImageContainer"]::before {
        content: "";
        position: absolute; 
        top: 0; left: 0; right: 0; bottom: 0;
        background: linear-gradient(to bottom, transparent, rgba(16, 21, 38, 1));
        z-index: 1; 
    }
</style>
"""
# unsafe_allow_html permite inyectar HTML/CSS directamente a la app
st.markdown(estilo, unsafe_allow_html=True)

# Cargamos el diccionario de series para la interfaz
show_dict = get_show_list()

# Control de estado de la sesión: Permite saber si el usuario ya hizo una búsqueda
if "consultado" not in st.session_state:
    st.session_state.consultado = False

# --- Interfaz de Usuario ---
st.title(":material/tv_gen: Recomendador de series de TV con :blue[Vector DB]")
st.markdown("Impulsado por **ChromaDB** y **BERT**. Consultas en milisegundos sobre bases de datos vectoriales.")

st.header(":material/search: Búsqueda")
# st.selectbox crea un menú desplegable con todas las series ordenadas alfabéticamente
selected_name = st.selectbox("Selecciona una serie base:", sorted(list(show_dict.keys())))

with st.expander("Filtros extra (opcional)"):
    st.caption("La Vector DB permite filtrar metadatos ANTES de buscar similitudes.")
    # Permite al usuario seleccionar un rating mínimo para los resultados recomendados
    min_rating = st.slider("Rating Mínimo", 0.0, 10.0, 0.0, 0.5)

if selected_name:    
    # Obtenemos el ID de la serie que el usuario seleccionó
    selected_id = show_dict[selected_name]
    st.session_state.consultado = True
    
    # 1. Obtener el vector del show seleccionado desde la DB
    show_data = collection.get(ids=[selected_id], include=["embeddings", "metadatas"])
    target_embedding = show_data['embeddings'][0]
    base_meta = show_data['metadatas'][0]
    
    # Mostramos información de la serie sobre la cual vamos a basar la búsqueda
    st.subheader(f"Basado en:")
    with st.container(border=True,horizontal=True,key="tv_card_base"):
        st.image(base_meta['image'], width=150)
        with st.container():
            st.write(f"##### {base_meta['name']} (:yellow[:material/star:] {round(base_meta['rating'],1)})")
            st.write(f"_{base_meta['summary']}_")
            genres_str = get_genres_str(base_meta['genres'])
            st.write(f":material/theater_comedy: {genres_str}")
            c1, c2,c3,c4 = st.columns(4)
            with c1:
                st.caption("Estreno")
                st.write(f":blue[:material/calendar_month:] {base_meta['premiered']}")
            with c2:
                st.caption("Duración prom. episodio")
                st.write(f":blue[:material/schedule:] {base_meta['avg_runtime_minutes']} min")
            with c3:
                st.caption("Estado")
                st.write(f":blue[:material/android_cell_4_bar:] {base_meta['status']}")
            with c4:
                st.caption("Contenido")
                st.write(f":blue[:material/stacks:] {base_meta['seasons_count']} temporadas ({base_meta['episodes_count']} eps)")
    st.divider()

    # 2. Consultar la Vector DB por los vecinos más cercanos (ANN - Approximate Nearest Neighbors)
    # Pedimos n_results=11 porque muy probablemente el primer resultado sea la misma serie buscada.
    results = collection.query(
        query_embeddings=[target_embedding],
        n_results=16,
        where={"rating": {"$gte": min_rating}}, # BÚSQUEDA HÍBRIDA: Filtro estilo SQL ($gte = mayor o igual) + Similitud Vectorial
        include=["metadatas", "distances"]
    )
    
    # Extraemos las listas de resultados que nos devolvió ChromaDB.
    # 'distances' indica qué tan lejos matemáticamente está un vector de otro. Menor distancia = Mayor similitud.
    ids_found = results['ids'][0]
    metadatas_found = results['metadatas'][0]
    
    # Filtramos por comprensión para omitir la serie original si es que aparece en los resultados
    recs =[(m, d) for i, m, d in zip(ids_found, metadatas_found, results['distances'][0]) if i != selected_id]

    # Mostrar resultados en forma de tarjetas utilizando 5 columnas
    cols = st.columns(5)
    for i, (meta, distance) in enumerate(recs):
        # i % 5 hace que el ciclo asigne secuencialmente las tarjetas a las columnas 0, 1, 2, 3 y 4
        with cols[i % 5]:
            with st.container(border=True, key=f"tv_card_{i}"):                                
                st.badge(f"**Distancia:** {distance:.4f}",color="green")
                st.image(meta['image'], width="stretch")
                
                with st.container(key=f"info_tv_{i}"):
                    st.markdown(f"#### {meta['name']}")
                    
                    genres_str = get_genres_str(meta['genres'])
                    st.write(f":blue[:material/theater_comedy:] {genres_str}")
                    
                    # Columnas internas para la data estructurada
                    c1, c2 = st.columns(2)
                    with c1:
                        st.caption("Estreno")
                        st.write(f":blue[:material/calendar_month:] {meta['premiered']}")
                        st.caption("Duración prom. episodio")
                        st.write(f":blue[:material/schedule:] {meta['avg_runtime_minutes']} min")
                    with c2:
                        st.caption("Estado")
                        st.write(f":blue[:material/android_cell_4_bar:] {meta['status']}")
                        st.caption("Contenido")
                        st.write(f":blue[:material/stacks:] {meta['seasons_count']} temporadas ({meta['episodes_count']} eps)")
                    st.divider()
                                    
                    c1, c2 = st.columns(2, vertical_alignment="center")
                    with c1:
                        st.write(f"##### :yellow[:material/star:]: **{round(meta['rating'], 1)}**")
                    with c2:
                        # Botón para abrir el modal (ventana emergente) usando on_click
                        with st.container(horizontal_alignment="right"):
                            btn = st.button("Más info", key=f"info_{i}", on_click=display_show_info, args=(meta,), type="primary")