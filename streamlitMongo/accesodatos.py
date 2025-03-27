import pandas as pd  # Para la manipulación y análisis de datos. Instalación: pip install pandas
from pymongo.mongo_client import MongoClient # Para interactuar con MongoDB. Instalación: pip install pymongo
from pymongo.server_api import ServerApi # Para especificar la versión del API de MongoDB.
import pymongo # Librería principal de MongoDB.
import streamlit as st  # Para crear la aplicación web. Instalación: pip install streamlit

# URI de conexión a MongoDB, almacenada en los secretos de Streamlit
uri = st.secrets["mongoURI"]
# Crea un nuevo cliente y se conecta al servidor MongoDB
client = MongoClient(uri, server_api=ServerApi('1'))

@st.cache_data 
def obtenerPaises():
    """
    Obtiene la lista de países distintos presentes en la colección 'crops'.

    Returns:
        list: Lista de nombres de países.
    """
    db = client["datasetCrops"]
    collection = db["crops"]
    return collection.distinct("Area")

@st.cache_data 
def obtenertipoDatos():
    """
    Obtiene los tipos de datos distintos presentes en la colección 'crops'.

    Returns:
        list: Lista de tipos de datos.
    """
    db = client["datasetCrops"]
    collection = db["crops"]
    return collection.distinct("Element")

@st.cache_data 
def obtenerPaises(parCultivos):
    """
    Obtiene la lista de países que cultivan un cultivo específico.

    Args:
        parCultivos (str): Nombre del cultivo.

    Returns:
        list: Lista de nombres de países.
    """
    db = client["datasetCrops"]
    collection = db["crops"]
    arrayPaises= collection.distinct("Area",{"Item":parCultivos})
    return arrayPaises

@st.cache_data 
def obtenerCultivos():
    """
    Obtiene la lista de cultivos distintos presentes en la colección 'crops'.

    Returns:
        list: Lista de nombres de cultivos.
    """
    db = client["datasetCrops"]
    collection = db["crops"]    
    arrayCultivos= collection.distinct("Item")
    return arrayCultivos

@st.cache_data
def obtenerDatos(parPais,parTipoDatos,parCultivos):
    """
    Obtiene los datos de la colección 'crops' según los filtros especificados.

    Args:
        parPais (list): Lista de nombres de países.
        parTipoDatos (str): Tipo de dato.
        parCultivos (list): Lista de nombres de cultivos.

    Returns:
        pandas.DataFrame: DataFrame con los datos obtenidos.
    """
    db = client["datasetCrops"]    
    collection = db["crops"]
    
    cursor = collection.find({
        "Area": {"$in": parPais},
        "Element": parTipoDatos,
        "Item": {"$in": parCultivos}
    }, {"_id": 0})
    list_cur = list(cursor.sort("Year", pymongo.ASCENDING))
    df = pd.DataFrame(list_cur)
    return df

@st.cache_data
def obtenerDatosCultivo(parCultivo):
    """
    Obtiene los datos de un cultivo específico, pivotando los datos por 'Element'.

    Args:
        parCultivo (str): Nombre del cultivo.

    Returns:
        pandas.DataFrame: DataFrame con los datos obtenidos y pivotados.
    """
    db = client["datasetCrops"]    
    collection = db["crops"]
    
    cursor = collection.find({
        "Item": parCultivo
    }, {"_id": 0})
    list_cur = list(cursor.sort("Year", pymongo.ASCENDING))
    
    df = pd.DataFrame(list_cur)[["Area","Item","Year","Element","Value"]]    
    df= df.pivot_table(index=["Area","Item","Year"], columns="Element", values="Value").reset_index()
    return df
    
@st.cache_data
def obtenerEstadisticasCultivo(parCultivo):
    """
    Obtiene estadísticas de un cultivo específico para el último año disponible.

    Args:
        parCultivo (str): Nombre del cultivo.

    Returns:
        tuple: Un tuple que contiene un DataFrame con las estadísticas y el último año disponible.
    """
    db = client["datasetCrops"]    
    collection = db["crops"]    
    
    cursor = collection.aggregate([{
        "$match":{"Item": parCultivo} # Item = Cultivo
    }, 
    {"$group":{"_id":"$Element", 
               "anio": { "$max": "$Year" }}}])
    list_cur = list(cursor)
    dfAnio = pd.DataFrame(list_cur)
    
    ultimoAnio = dfAnio[dfAnio["_id"]=="Yield"]["anio"].values[0]
    ultimoAnio=int(ultimoAnio)
    
    cursor = collection.aggregate([{
        "$match":{"Item": parCultivo,
                  "Year": ultimoAnio,
                  "Element": {"$in":["Area harvested","Production"]}, # Element in ["Area harvested","Production"]
                  "Value":{'$ne': float('NaN')}} # Value != NaN
    }, 
    {"$group":{"_id":"$Element", 
               "totales": { "$sum": "$Value" }}}])
    list_cur = list(cursor)
    df1 = pd.DataFrame(list_cur)
    
    cursor = collection.aggregate([{
        "$match":{"Item": parCultivo,
                  "Year": ultimoAnio,
                  "Element": "Yield", # Element = Yield
                  "Value":{'$ne': float('NaN')}}
    }, 
    {"$group":{"_id":"$Element", 
               "totales": { "$avg": "$Value" }}}])
    list_cur = list(cursor)
    df = pd.DataFrame(list_cur)
    df = pd.concat([df1,df])    
    return df,ultimoAnio

@st.cache_data
def obtenerEstadisticasCultivoAnio(parCultivo):
    """
    Obtiene estadísticas de un cultivo específico para cada año disponible.

    Args:
        parCultivo (str): Nombre del cultivo.

    Returns:
        pandas.DataFrame: DataFrame con las estadísticas por año.
    """
    db = client["datasetCrops"]    
    collection = db["crops"]    
    
    
    
    cursor = collection.aggregate([{
        "$match":{"Item": parCultivo,
                  "Element": {"$in":["Area harvested","Production"]},
                  "Value":{'$ne': float('NaN')}}
    }, 
    {"$group":{"_id":["$Element","$Year"], 
               "totales": { "$sum": "$Value" }}}])
    list_cur = list(cursor)
    df1 = pd.DataFrame(list_cur)
    
    cursor = collection.aggregate([{
        "$match":{"Item": parCultivo,
                  "Element": "Yield",
                  "Value":{'$ne': float('NaN')}}
    }, 
    {"$group":{"_id":["$Element","$Year"],  # ["Area Harvested","1950"]
               "totales": { "$avg": "$Value" }}}])
    list_cur = list(cursor)
    df = pd.DataFrame(list_cur)
    df = pd.concat([df1,df])   
    df["Element"] = df["_id"].apply(lambda x:x[0]) 
    df["Year"] = df["_id"].apply(lambda x:x[1]) 
    df.drop(columns=["_id"],inplace=True)
    return df