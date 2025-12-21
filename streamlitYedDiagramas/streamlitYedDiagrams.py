# Librerías principales
# Instalación: pip install streamlit
import streamlit as st
# Librería para manipulación y análisis de datos.
# Instalación: pip install pandas
import pandas as pd
# Librería para creación y análisis de grafos complejos.
# Instalación: pip install networkx
import networkx as nx
# La librería yfiles_graphs_for_streamlit permite renderizar grafos interactivos de alta calidad.
# Instalación: pip install yfiles-graphs-for-streamlit
from yfiles_graphs_for_streamlit import StreamlitGraphWidget, Node, Edge, Layout


# === LIBRERÍAS UTILIZADAS ===
# streamlit: Framework para crear aplicaciones web de datos en Python de forma rápida.
#   -> Instalación: pip install streamlit
# pandas: Librería estándar para manipulación, limpieza y análisis de datos tabulares.
#   -> Instalación: pip install pandas
# networkx: Librería especializada en la creación, manipulación y estudio de la estructura y dinámica de redes complejas (grafos).
#   -> Instalación: pip install networkx

# Configuración inicial de la página de Streamlit
st.set_page_config(
    page_title="yFiles Graphs for Streamlit",
    layout="wide",
)

st.title("Ejemplo Diagrama de Metro de Nueva York con yFiles Graphs for Streamlit")

# === CARGA Y TRANSFORMACIÓN DE DATOS CON PANDAS ===
# Cargamos los archivos CSV. 'dfRutas' contiene las conexiones (aristas) y 'dfEstaciones' los detalles de cada parada (nodos).
dfRutas = pd.read_csv("metro_ny.csv")
dfEstaciones = pd.read_csv("metro_ny_stations.csv") 

# Transformación de datos: Normalización Min-Max con Pandas
# Objetivo: Escalar la columna "avg_daily_passengers" a un rango entre 0 y 1.
# ¿Por qué? Para visualizaciones como mapas de calor (heatmaps), necesitamos valores relativos (intensidad)
# en lugar de valores absolutos (número de personas).
# Fórmula aplicada a toda la columna (vectorización): (Valor - Mínimo) / (Máximo - Mínimo)
dfEstaciones["avg_daily_passengers_normalized"] = (
    dfEstaciones["avg_daily_passengers"] - dfEstaciones["avg_daily_passengers"].min()
) / (dfEstaciones["avg_daily_passengers"].max() - dfEstaciones["avg_daily_passengers"].min())

# === CREACIÓN DEL GRAFO MATEMÁTICO CON NETWORKX ===
# Usamos 'from_pandas_edgelist' para convertir un DataFrame de conexiones en un objeto Grafo.
# Esto permite usar algoritmos de grafos (como ruta más corta) sobre nuestros datos tabulares.
G = nx.from_pandas_edgelist(
    dfRutas,
    source="origin_stop_name",     # Columna que define el nodo de inicio
    target="destination_stop_name", # Columna que define el nodo final
    edge_attr=["distance_meters", "travel_time_est_minutes"], # Atributos que se guardan en cada conexión (pesos)
    create_using=nx.DiGraph()      # Especificamos que es un Grafo Dirigido (la dirección importa)
)

# Visualización básica rápida usando el método from_graph
st.subheader("Visualización Básica Directa desde NetworkX")
tabGrafo, tabRutas = st.tabs(["Grafo de Rutas", "Datos de Rutas"])

with tabGrafo:
    c1,c2 = st.columns([2,8]) # División de columnas: 30% controles, 70% visualización
    ruta_mas_corta = None
    with c1:
        # Selectores para definir origen y destino basados en los nombres de las estaciones
        parOrigen = st.selectbox("Selecciona estación de origen:", dfEstaciones["station_name"].tolist())
        parDestino = st.selectbox("Selecciona estación de destino:", dfEstaciones["station_name"].tolist())
        
        if st.button("Calcular ruta más corta", type="primary"):
            try:
                # Algoritmo de Dijkstra (implementado en NetworkX) para encontrar el camino más corto
                # weight="distance_meters" indica que queremos minimizar la distancia física, no el número de paradas.
                ruta_mas_corta = nx.shortest_path(G, source=parOrigen, target=parDestino, weight="distance_meters")
                
                # Cálculo de la longitud de la ruta en metros
                ruta_mas_corta_mts = nx.shortest_path_length(G, source=parOrigen, target=parDestino, weight="distance_meters")
                # Cálculo del tiempo estimado usando el otro atributo de la arista
                ruta_mas_corta_tiempo = nx.shortest_path_length(G, source=parOrigen, target=parDestino, weight="travel_time_est_minutes")
                
                st.info(f"* Distancia total: **{ruta_mas_corta_mts} metros** \n\n* Tiempo estimado: **{ruta_mas_corta_tiempo} minutos.**")                
            except nx.NetworkXNoPath:
                st.error(f"No existe una ruta entre {parOrigen} y {parDestino}.")
    with c2:
        with st.container(border=True):
            # Lógica de renderizado del grafo
            if ruta_mas_corta:
                # Si hay una ruta calculada, coloreamos el camino de rojo (#ff6347) y el resto gris (#6F8993)
                # Utilizamos funciones lambda para aplicar lógica condicional a cada nodo y arista durante el renderizado.
                st.success(f"La ruta más corta de {parOrigen} a {parDestino} es:\n\n > **{' -> '.join(ruta_mas_corta)}**")
                nodesArray=[x for x in G.nodes]            
                StreamlitGraphWidget.from_graph(G, 
                                                node_color_mapping=lambda node: "#ff6347" if nodesArray[node["id"]] in ruta_mas_corta else "#6F8993",
                                                edge_color_mapping=lambda edge: "#ff6347" if (nodesArray[edge["start"]] in ruta_mas_corta and nodesArray[edge["end"]] in ruta_mas_corta) else "#B0C4DE",                                            
                                                edge_label_mapping=lambda edge: f"{edge['properties']['distance_meters']} m / {edge['properties']['travel_time_est_minutes']} min"
                                                ).show(graph_layout=Layout.ORTHOGONAL)
            else:
                # Visualización por defecto sin ruta seleccionada
                StreamlitGraphWidget.from_graph(G,edge_label_mapping=lambda edge: f"{edge['properties']['distance_meters']} m / {edge['properties']['travel_time_est_minutes']} min").show(graph_layout=Layout.ORTHOGONAL)
with tabRutas:
    # Muestra los datos crudos para inspección
    st.dataframe(dfRutas)


def generarEstructura():
    """
    Transforma los DataFrames de Pandas en objetos Node y Edge de yFiles.
    
    Esta función es necesaria para la visualización avanzada, ya que permite
    inyectar propiedades ricas (como coordenadas geográficas, zonas y datos normalizados)
    que no siempre se transfieren automáticamente desde NetworkX simple.

    Returns:
        tuple: (lista de objetos Node, lista de objetos Edge) listos para el widget.
    """
    # Comprensión de lista para crear nodos:
    # Iteramos sobre cada fila del DataFrame convertido a diccionario.
    # Asignamos atributos visuales y lógicos a cada nodo.
    nodes = [
        Node(station["station_name"], 
             {
                 "label": station["station_name"], 
                 "borough": station["borough"], 
                 "lines": station["lines"], 
                 "is_transfer": station["is_transfer"], 
                 "zone": station["zone"],
                 # 'coordinates' es clave para que el grafo respete la geografía real si se usa layout manual/geográfico
                 "coordinates": [station["latitude"], station["longitude"]], 
                 "avg_daily_passengers": station["avg_daily_passengers"],
                 # Pasamos el valor normalizado calculado previamente para el heatmap
                 "avg_daily_passengers_normalized": station["avg_daily_passengers_normalized"]
             })
        for station in dfEstaciones.to_dict('records')
    ]

    # Comprensión de lista para crear aristas (conexiones):
    edges = [
        Edge(route["origin_stop_name"], 
             route["destination_stop_name"],
             properties={
                 "distance_meters": route["distance_meters"], 
                 "travel_time_est_minutes": route["travel_time_est_minutes"]
             })
        for route in dfRutas.to_dict('records')
    ]
    
    return nodes, edges

# Generamos las estructuras de datos avanzadas
estaciones, rutas = generarEstructura()

st.subheader("Visualización Avanzada con Controles")
tabGrafo,tabDatos,tabRutas = st.tabs(["Grafo Avanzado","Datos de Estaciones","Datos de Rutas"])
with tabGrafo:
    with st.container(border=True,horizontal=True):
        # Controles de interactividad en Streamlit
        parHabilitarGrupo = st.checkbox("Habilitar agrupamiento por zona")
        parHabilitarHeatmap = st.checkbox("Habilitar heatmap por pasajeros diarios promedio")

    # Renderizado del Widget Avanzado
    # Aquí utilizamos la clase StreamlitGraphWidget directamente (no from_graph) para máximo control
    StreamlitGraphWidget(
        nodes=estaciones,
        edges=rutas,
        
        # Agrupamiento dinámico:
        # Si el checkbox está activo, agrupa visualmente los nodos basándose en la columna "zone".
        node_parent_group_mapping="zone" if parHabilitarGrupo else None,
        
        # Color condicional de nodos (Lambda):
        # Verde (#98ddc6) si es estación de transferencia, gris azulado (#6F8993) si no lo es.
        node_color_mapping=lambda node: "#98ddc6" if node["properties"]["is_transfer"]=="Yes" else "#6F8993",        
        
        # Mapeo de coordenadas: Usa la lista [lat, long] que preparamos en generarEstructura()
        node_coordinate_mapping="coordinates",
        
        # Etiquetas de las aristas mostrando distancia y tiempo
        edge_label_mapping=lambda edge: f"{edge['properties']['distance_meters']} m / {edge['properties']['travel_time_est_minutes']} min",
        
        # Heatmap (Mapa de calor):
        # Utiliza la columna normalizada (0 a 1) para pintar "halos" de calor alrededor de los nodos con más tráfico.
        heat_mapping="avg_daily_passengers_normalized" if parHabilitarHeatmap else None,

    ).show(graph_layout=Layout.HIERARCHIC) # Layout jerárquico organiza el grafo por niveles o flujos
with tabDatos:
    # Muestra los datos crudos para inspección
    st.dataframe(dfEstaciones)
with tabRutas:
    # Muestra los datos crudos para inspección
    st.dataframe(dfRutas)