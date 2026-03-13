"""
Librerías utilizadas en este script:
- pandas: Ideal para manipulación y análisis de datos en tablas (DataFrames).
- chromadb: Base de datos vectorial de código abierto, perfecta para almacenar y consultar "embeddings" de IA.
- sentence-transformers (bajo el capó): Utilizada por ChromaDB para convertir texto en vectores (embeddings).

Comando de instalación:
pip install pandas chromadb sentence-transformers
"""

import pandas as pd
import chromadb
from chromadb.utils import embedding_functions

def create_bert_context(row):
    """
    Toma una fila de nuestro DataFrame y construye un párrafo descriptivo (contexto narrativo).
    Este texto será el que la Inteligencia Artificial convierta a vectores para entender 
    de qué trata cada serie.
    
    Args:
        row (pd.Series): Una fila del DataFrame de pandas.
        
    Returns:
        str: Texto estructurado que describe la serie de TV.
    """
    # Verificamos si los datos no son nulos usando pd.notna(). Si son nulos, asignamos "Unknown" o un texto por defecto.
    genres = row['genres'] if pd.notna(row['genres']) else "Unknown"
    cast = row['cast'] if pd.notna(row['cast']) else "Unknown"
    summary = row['summary'] if pd.notna(row['summary']) else "No summary available."
    language = row['language'] if pd.notna(row['language']) else "Unknown"
    
    # Construimos una oración coherente que agrupe toda la información importante
    return f"This is a {language} TV show. Genres include {genres}. " \
           f"The main cast features {cast}. Plot summary: {summary}"

def build_vector_database():
    """
    Función principal que lee los datos desde un CSV, realiza una limpieza básica con pandas,
    genera los textos de contexto, y finalmente vectoriza y guarda la información en una 
    base de datos vectorial local usando ChromaDB.
    """
    csv_path = "tv_shows_2000.csv"
    print("1. Cargando datos...")
    # Leemos el archivo CSV y lo convertimos en un DataFrame de pandas
    df = pd.read_csv(csv_path)
    
    # --- TRANSFORMACIONES DE DATOS CON PANDAS ---
    
    # Elimina filas que tengan el mismo 'show_id' para evitar duplicados y resetea el índice.
    df = df.drop_duplicates(subset='show_id').reset_index(drop=True)
    
    # Rellena los valores nulos (NaN) de la columna 'rating' calculando el promedio (mean) de todos los ratings.
    df['rating'] = df['rating'].fillna(df['rating'].mean())
    
    # Rellena los valores nulos de 'avg_runtime_minutes' con la mediana (median) para no afectar por valores atípicos.
    df['avg_runtime_minutes'] = df['avg_runtime_minutes'].fillna(df['avg_runtime_minutes'].median())
    
    # Para cualquier otro valor nulo restante en el DataFrame, lo rellenamos con un texto vacío (string vacío).
    df = df.fillna("") 

    print("2. Construyendo el contexto narrativo...")
    # apply(..., axis=1) ejecuta la función 'create_bert_context' fila por fila
    df['bert_text'] = df.apply(create_bert_context, axis=1)

    print("3. Inicializando ChromaDB...")
    # Creamos un cliente persistente. Esto generará una carpeta llamada 'chroma_db' 
    # en tu computadora para guardar los datos y que no se borren al cerrar el script.
    client = chromadb.PersistentClient(path="./chroma_db")
    
    # Configuramos la función de embedding. Le indicamos a Chroma qué modelo de IA usar.
    # "all-MiniLM-L6-v2" es un modelo rápido y eficiente para convertir oraciones a vectores.
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    
    # Creamos o cargamos una colección (equivalente a una "tabla" en bases de datos tradicionales).
    collection = client.get_or_create_collection(
        name="tv_shows_collection", 
        embedding_function=emb_fn
    )

    print("4. Vectorizando e insertando en la Base de Datos (Esto puede tardar unos minutos)...")
    
    # Preparamos las listas que requiere ChromaDB:
    # 1. IDs únicos (como strings)
    ids = df['show_id'].astype(str).tolist()
    # 2. Los documentos o textos que queremos convertir a vectores
    documents = df['bert_text'].tolist()
    
    # 3. Metadatos: Información extra (columnas del CSV) que guardamos junto al vector.
    # Nos permite filtrar búsquedas después o mostrar datos en la interfaz sin tener que volver a leer el CSV.
    # to_dict(orient='records') convierte las columnas seleccionadas en una lista de diccionarios.
    metadatas = df[['name','image','genres','status','premiered','seasons_count', 'episodes_count', 'rating', 'avg_runtime_minutes', 'summary', 'cast']].to_dict(orient='records')

    # Insertamos todo en lotes en la Vector DB. 
    # upsert() es inteligente: si el ID no existe, lo inserta. Si ya existe, actualiza sus datos.
    # ¡Nota!: Aquí ChromaDB toma los 'documents' y calcula los embeddings matemáticos automáticamente.
    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )

    print(f"\n¡Éxito! {len(ids)} shows han sido indexados en la base de datos vectorial local (carpeta './chroma_db').")

# Punto de entrada estándar en Python
if __name__ == "__main__":
    build_vector_database()