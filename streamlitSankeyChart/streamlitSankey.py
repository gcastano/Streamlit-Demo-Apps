# --- Librerías Requeridas ---

# Plotly: Una librería de gráficos interactivos de Python.
# Proporciona una amplia gama de tipos de gráficos, incluyendo diagramas de Sankey.
# Es excelente para crear visualizaciones web dinámicas y estéticamente agradables.
# Instalación: pip install plotly
import plotly.graph_objects as go # Módulo principal para crear figuras complejas y personalizadas.
import plotly.express as px # Plotly Express es una interfaz de alto nivel para Plotly, útil para crear figuras rápida y fácilmente con menos código.
# Instalación: pip install plotly (normalmente se instala junto con plotly)

# Pandas: Librería fundamental para la manipulación y análisis de datos en Python.
# Ofrece estructuras de datos como DataFrames (tablas bidimensionales) y Series (columnas),
# que son esenciales para cargar, limpiar, transformar y analizar datos tabulares.
# Instalación: pip install pandas
import pandas as pd

# Streamlit: Framework de Python para crear aplicaciones web interactivas para ciencia de datos y machine learning.
# Permite convertir scripts de datos en aplicaciones web compartibles de forma rápida, sin necesidad de experiencia en desarrollo web frontend.
# Instalación: pip install streamlit
import streamlit as st

# --- Configuración de la Página de Streamlit ---
# Configura el layout de la página para que sea ancho ('wide'), lo que permite que los elementos ocupen más espacio horizontal.
# Establece el título que aparece en la pestaña del navegador ('page_title').
# Asigna un ícono a la página ('page_icon'), que también aparece en la pestaña del navegador. Se pueden usar emojis o identificadores de Material Icons.
st.set_page_config(layout="wide", page_title="Diagrama de Sankey Interactivo", page_icon=":bar_chart:")

# --- Títulos y Descripción en la App Streamlit ---
# Muestra un encabezado principal (H1) en la aplicación web usando st.header.
# Se pueden usar identificadores de Material Icons como :material/timeline:
st.header(":material/timeline: Diagrama de Sankey para Análisis de Ventas")
# Muestra un texto introductorio utilizando Markdown para formato (st.markdown).
# Explica el propósito de la aplicación y guía al usuario sobre cómo interactuar con ella.
st.markdown("Este diagrama de Sankey permite analizar la distribución de las ventas por país, línea de producto y estado. Puedes filtrar los datos por año, país, línea de producto y estado usando los controles a continuación.")

# --- Carga de Datos ---
# Lee los datos de ventas desde un archivo CSV ('sales_data_sample.csv') utilizando la función read_csv de Pandas.
# El parámetro 'encoding="latin1"' se usa para asegurar la correcta lectura de caracteres especiales que pueden estar presentes
# en archivos CSV que no usan la codificación estándar UTF-8 (común en algunos datasets con textos en lenguas europeas).
# Asegúrate de que el archivo 'sales_data_sample.csv' esté en el mismo directorio que el script de Python,
# o proporciona la ruta completa al archivo.
# Fuente del dataset: https://www.kaggle.com/datasets/kyanyoga/sample-sales-data
dfVentas = pd.read_csv("./sales_data_sample.csv", encoding="latin1")

# --- Controles de Filtrado en Streamlit ---
# Crea 5 columnas en la interfaz de Streamlit para organizar los controles de filtrado de forma horizontal.
# 'st.columns(5)' devuelve una lista de 5 objetos de columna.
cols = st.columns(5)

# Columna 1: Filtro por Año
with cols[0]: # Se utiliza 'with' para asignar los siguientes elementos de Streamlit a esta columna específica.
  # Crea un widget de selección (selectbox) para que el usuario elija un año.
  # El primer argumento es la etiqueta que se muestra sobre el selectbox ("Selecciona el año").
  # El segundo argumento es la lista de opciones. 'dfVentas["YEAR_ID"].unique()' obtiene los valores únicos de la columna 'YEAR_ID'.
  parAno = st.selectbox("Selecciona el año", dfVentas["YEAR_ID"].unique())
  # Filtra el DataFrame principal 'dfVentas' para mantener solo las filas donde la columna 'YEAR_ID'
  # coincide con el año seleccionado por el usuario ('parAno').
  # El resultado se guarda en un nuevo DataFrame 'dfVentasAnual'. Este es el DataFrame base para los siguientes filtros y el gráfico.
  dfVentasAnual = dfVentas[dfVentas["YEAR_ID"] == parAno]

# Columna 2: Selección de Métrica (Valor)
with cols[1]:
  # Crea un selectbox para elegir la métrica a visualizar: 'QUANTITYORDERED' (cantidad) o 'SALES' (ventas).
  parValor = st.selectbox(
      "Selecciona el valor", # Etiqueta del selectbox.
      ["QUANTITYORDERED", "SALES"], # Lista de opciones (nombres de las columnas en el DataFrame).
      # 'format_func' permite mostrar etiquetas más descriptivas al usuario en el selectbox ("Unidades Vendidas", "Ventas Totales")
      # en lugar de los nombres de columna originales ('QUANTITYORDERED', 'SALES').
      # Se usa una función lambda para reemplazar los nombres de columna por las etiquetas deseadas.
      format_func=lambda x: x.replace("QUANTITYORDERED", "Unidades Vendidas").replace("SALES", "Ventas Totales")
  )

# Columna 3: Filtro por País
with cols[2]:
  # Crea un selectbox para filtrar por país.
  # Se añade la opción "Todos" al principio de la lista de países únicos.
  # 'list(dfVentasAnual["COUNTRY"].unique())' obtiene los países únicos del DataFrame *ya filtrado por año*.
  # El operador '+' concatena la lista ["Todos"] con la lista de países.
  parPais = st.selectbox("Selecciona el País", ["Todos"] + list(dfVentasAnual["COUNTRY"].unique()))

# Columna 4: Filtro por Línea de Producto
with cols[3]:
  # Crea un selectbox para filtrar por línea de producto.
  # Similar al filtro de país, se añade "Todos" y se usan las líneas de producto únicas del DataFrame filtrado por año.
  parProducto = st.selectbox("Selecciona la Línea de Producto", ["Todos"] + list(dfVentasAnual["PRODUCTLINE"].unique()))

# Columna 5: Filtro por Estado
with cols[4]:
  # Crea un selectbox para filtrar por estado de la orden (e.g., 'Shipped', 'Cancelled').
  # Se añade "Todos" y se usan los estados únicos del DataFrame filtrado por año.
  parStatus = st.selectbox("Selecciona el Estado", ["Todos"] + list(dfVentasAnual["STATUS"].unique()))

# --- Preparación de Etiquetas y Sufijos para el Gráfico ---
# Define un sufijo y una etiqueta basados en la métrica seleccionada ('parValor').
# Estos se usarán en el gráfico Sankey para formatear los valores y dar nombre al nodo raíz.
if parValor == "QUANTITYORDERED":
    sufijo = " und"  # Sufijo para unidades (e.g., "1,234 und").
    etiqueta = "Unidades Vendidas" # Etiqueta del nodo raíz que representa el total general.
else: # Si parValor es "SALES"
    sufijo = " USD" # Sufijo para moneda (dólares) (e.g., "5,678 USD").
    etiqueta = "Ventas Totales" # Etiqueta del nodo raíz para ventas.

# --- Aplicación de Filtros Adicionales ---
# Aplica los filtros de País, Línea de Producto y Estado al DataFrame 'dfVentasAnual'
# solo si el usuario NO seleccionó la opción "Todos".
# Si el usuario seleccionó "Todos", el DataFrame no se modifica para esa dimensión.

# Filtra por país si se seleccionó un país específico (diferente de "Todos").
if parPais != "Todos":
    # Sobrescribe dfVentasAnual manteniendo solo las filas donde 'COUNTRY' coincide con el país seleccionado.
    dfVentasAnual = dfVentasAnual[dfVentasAnual["COUNTRY"] == parPais]
# Filtra por línea de producto si se seleccionó una específica.
if parProducto != "Todos":
    # Sobrescribe dfVentasAnual manteniendo solo las filas donde 'PRODUCTLINE' coincide con la línea seleccionada.
    dfVentasAnual = dfVentasAnual[dfVentasAnual["PRODUCTLINE"] == parProducto]
# Filtra por estado si se seleccionó uno específico.
if parStatus != "Todos":
    # Sobrescribe dfVentasAnual manteniendo solo las filas donde 'STATUS' coincide con el estado seleccionado.
    dfVentasAnual = dfVentasAnual[dfVentasAnual["STATUS"] == parStatus]

# --- Transformación de Datos para el Diagrama de Sankey ---
# El diagrama de Sankey requiere datos en un formato específico: 'origen' (source), 'destino' (target), 'valor' (value).
# Se crearán tres DataFrames intermedios, cada uno representando un nivel del flujo en el diagrama.
# Estos DataFrames se calcularán a partir del DataFrame 'dfVentasAnual' (ya filtrado).

# 1. Agrupación: Métrica Total -> País (Primer nivel del flujo)
# Agrupa los datos filtrados por la columna 'COUNTRY'.
# Calcula la suma de la métrica seleccionada ('parValor', que es 'SALES' o 'QUANTITYORDERED') para cada país.
# 'reset_index()' convierte el resultado agrupado (que es una Serie de Pandas con índice 'COUNTRY') de nuevo en un DataFrame con columnas 'COUNTRY' y 'parValor'.
# 'rename()' cambia los nombres de las columnas para que se ajusten al formato esperado por Sankey:
#   - 'COUNTRY' se renombra a 'destino' (el país es el destino del flujo desde el total).
#   - La columna de la métrica ('SALES' o 'QUANTITYORDERED') se renombra a 'valor'.
dfVentasAnual1 = dfVentasAnual.groupby(["COUNTRY"])[parValor].sum().reset_index().rename(columns={"COUNTRY": "destino", parValor: "valor"})
# Asigna el nodo raíz ('origen') para este nivel. El origen es la etiqueta general definida antes (ej. "Ventas Totales").
dfVentasAnual1["origen"] = etiqueta
# Calcula el porcentaje que representa el 'valor' de cada país sobre el total general de 'valor' en este nivel.
# Esto es útil para mostrar información adicional en el hover del gráfico.
dfVentasAnual1["porcentaje"] = dfVentasAnual1["valor"] / dfVentasAnual1["valor"].sum()

# 2. Agrupación: País -> Línea de Producto (Segundo nivel del flujo)
# Agrupa los datos por 'COUNTRY' y 'PRODUCTLINE'.
# Calcula la suma de la métrica seleccionada para cada combinación de país y línea de producto.
# 'reset_index()' convierte el resultado agrupado en un DataFrame.
# Renombra las columnas:
#   - 'PRODUCTLINE' se convierte en 'destino' (la línea de producto es el destino del flujo desde el país).
#   - La columna de la métrica ('parValor') se renombra a 'valor'.
#   - 'COUNTRY' se convierte en 'origen' (el país es el origen del flujo hacia la línea de producto).
dfVentasAnual2 = dfVentasAnual.groupby(["COUNTRY", "PRODUCTLINE"])[parValor].sum().reset_index().rename(columns={"PRODUCTLINE": "destino", parValor: "valor", "COUNTRY": "origen"})
# Calcula el porcentaje que representa cada línea de producto DENTRO de su respectivo país ('origen').
# Se usa 'groupby("origen")["valor"]' para agrupar por país.
# '.transform(lambda x: x / x.sum())' aplica una función a cada grupo: divide el valor de cada fila por la suma total del valor de su grupo (país).
# Esto da la proporción de cada línea de producto dentro de las ventas/unidades totales de ese país específico.
dfVentasAnual2["porcentaje"] = dfVentasAnual2.groupby("origen")["valor"].transform(lambda x: x / x.sum())

# 3. Agrupación: Línea de Producto -> Estado (Tercer nivel del flujo)
# Agrupa los datos por 'STATUS' y 'PRODUCTLINE'.
# Calcula la suma de la métrica seleccionada para cada combinación de estado y línea de producto.
# 'reset_index()' convierte a DataFrame.
# Renombra las columnas:
#   - 'PRODUCTLINE' se convierte en 'origen' (la línea de producto es el origen del flujo hacia el estado).
#   - La columna de la métrica ('parValor') se renombra a 'valor'.
#   - 'STATUS' se convierte en 'destino' (el estado es el destino del flujo desde la línea de producto).
dfVentasAnual3 = dfVentasAnual.groupby(["STATUS", "PRODUCTLINE"])[parValor].sum().reset_index().rename(columns={"PRODUCTLINE": "origen", parValor: "valor", "STATUS": "destino"})
# Calcula el porcentaje que representa cada estado DENTRO de su respectiva línea de producto ('origen').
# Similar al paso anterior, se agrupa por 'origen' (línea de producto) y se calcula la proporción de cada estado dentro de esa línea.
dfVentasAnual3["porcentaje"] = dfVentasAnual3.groupby("origen")["valor"].transform(lambda x: x / x.sum())

# --- Combinación de los Flujos ---
# Concatena verticalmente los tres DataFrames ('dfVentasAnual1', 'dfVentasAnual2', 'dfVentasAnual3')
# en un único DataFrame 'dfDatos'. Este DataFrame contiene ahora todas las relaciones ('origen', 'destino', 'valor')
# necesarias para construir el diagrama de Sankey completo.
dfDatos = pd.concat([dfVentasAnual1, dfVentasAnual2, dfVentasAnual3])

# Ordena los datos combinados por 'origen' y luego por 'destino' en orden ascendente (False significa descendente).
# Esto es opcional, pero puede ayudar a que la disposición inicial del gráfico sea un poco más consistente o predecible.
# 'reset_index(drop=True)' reestablece el índice del DataFrame combinado (después de concatenar y ordenar)
# para que sea una secuencia numérica simple (0, 1, 2, ...), descartando el índice anterior.
dfDatos = dfDatos.sort_values(["origen", "destino"], ascending=False).reset_index(drop=True)

# --- Preparación de Nodos y Colores para Plotly ---

# Obtiene una lista única de todos los nombres de nodos que aparecen tanto en la columna 'origen' como en 'destino'.
# Primero, se convierten ambas columnas a listas con '.to_list()'.
# Luego, se suman las listas para combinarlas.
# Finalmente, se convierte la lista combinada a un 'set()' para eliminar automáticamente los nombres duplicados.
# El resultado 'nodos' es un conjunto con todas las etiquetas únicas (Total, Países, Líneas de Producto, Estados).
nodos = set(dfDatos["origen"].to_list() + dfDatos["destino"].to_list())
# Crea un diccionario llamado 'nodos_indices'. Este diccionario mapea cada nombre de nodo (string) a un índice numérico único (entero).
# Se utiliza una comprensión de diccionario: para cada 'indice' y 'nodo' obtenidos al enumerar el conjunto 'nodos',
# se crea un par clave-valor donde la clave es el 'nodo' y el valor es el 'indice'.
# Plotly Sankey requiere que los nodos de origen (source) y destino (target) se especifiquen mediante estos índices numéricos, no por sus nombres.
nodos_indices = {nodo: indice for indice, nodo in enumerate(nodos)}

# Define paletas de colores usando Plotly Express para diferenciar visualmente los nodos o flujos.
# Se crea un diccionario 'paletaPaises' que asigna un color a cada país único encontrado en el origen del segundo nivel ('dfVentasAnual2["origen"].unique()').
# Se usan las paletas cualitativas 'Pastel' y 'Pastel1' de Plotly Express. 'zip' empareja cada país con un color.
paletaPaises = {pais: color for pais, color in zip(dfVentasAnual2["origen"].unique(), px.colors.qualitative.Pastel + px.colors.qualitative.Pastel1)}
# Se crea un diccionario 'paletaProductos' que asigna un color a cada línea de producto única (destino del segundo nivel).
# Se usan las paletas cualitativas 'Safe' y 'Bold' de Plotly Express.
paletaProductos = {producto: color for producto, color in zip(dfVentasAnual2["destino"].unique(), px.colors.qualitative.Safe + px.colors.qualitative.Bold)}

# --- Mapeo de Índices y Colores al DataFrame de Flujos ---

# Añade una nueva columna 'origen_indice' al DataFrame 'dfDatos'.
# '.map(nodos_indices)' busca cada valor de la columna 'origen' en el diccionario 'nodos_indices'
# y asigna el índice numérico correspondiente a la nueva columna.
dfDatos["origen_indice"] = dfDatos["origen"].map(nodos_indices)
# Añade una nueva columna 'destino_indice' de la misma manera, mapeando los nombres de la columna 'destino'.
dfDatos["destino_indice"] = dfDatos["destino"].map(nodos_indices)

# Asigna un color a cada flujo (link) en el DataFrame 'dfDatos' basado en su origen o destino.
# La lógica intenta asignar color basado en si el 'origen' es un país (usando 'paletaPaises').
# Si no se encuentra en 'paletaPaises' (e.g., es la etiqueta total o una línea de producto),
# '.fillna()' intenta llenar los valores faltantes (NaN) mapeando el 'origen' con 'paletaProductos'.
# Si aún falta (e.g., el origen es la etiqueta total), un segundo '.fillna()' intenta mapear el 'destino' con 'paletaPaises'.
# Esta lógica prioriza colorear por país de origen, luego por línea de producto de origen, y como último recurso por país de destino.
# (La efectividad del último fillna puede depender de la estructura exacta y los filtros).
dfDatos["color"] = dfDatos["origen"].map(paletaPaises).fillna(dfDatos["origen"].map(paletaProductos)).fillna(dfDatos["destino"].map(paletaPaises))
# Convierte los colores obtenidos (que están en formato 'rgb(r,g,b)') a formato 'rgba(r,g,b,a)' añadiendo un valor alfa (transparencia).
# '.str.replace("rgb", "rgba")' reemplaza "rgb" por "rgba".
# '.str.replace(")", ",0.4)")' reemplaza el paréntesis de cierre ")" por ",0.4)", añadiendo una transparencia del 40%.
# Esto hace que los links (flujos) sean semitransparentes, mejorando la legibilidad cuando se superponen.
dfDatos["color"] = dfDatos["color"].str.replace("rgb", "rgba").str.replace(")", ",0.4)")

# --- Creación del Gráfico Sankey con Plotly ---

# Crea una figura de Plotly utilizando `graph_objects` (go).
# La figura contiene un único objeto `go.Sankey`.
fig = go.Figure(data=[go.Sankey(
    # 'valueformat': Especifica el formato de los números que se muestran en los nodos y tooltips (hover).
    # ",.0f" significa usar coma como separador de miles y mostrar 0 decimales.
    valueformat=",.0f",
    # 'valuesuffix': Añade un sufijo al final de los valores mostrados. Usa el 'sufijo' definido antes (" und" o " USD").
    valuesuffix=sufijo,

    # --- Definición de los Nodos ---
    # 'node': Es un diccionario que configura la apariencia y comportamiento de los nodos (rectángulos).
    node=dict(
      pad=15,             # Espaciado vertical (padding) entre los nodos dentro de la misma columna.
      thickness=15,       # Grosor (ancho) de las barras de los nodos.
      label=list(nodos),  # Lista de etiquetas (strings) para cada nodo. Se obtiene convirtiendo el set 'nodos' a lista.
      # 'hovertemplate': Define el texto que aparece cuando el cursor pasa sobre un nodo.
      # '%{label}' muestra la etiqueta del nodo.
      # '%{value:,.0f}' muestra el valor total que pasa por el nodo, formateado.
      # '<extra></extra>' (implícito) oculta información adicional que Plotly podría añadir por defecto.
      hovertemplate="%{label}<br>Valor: %{value:,.0f}",
      # color = dfDatos["color"], # Se podría asignar color a los nodos aquí si se deseara, pero está comentado.
                                 # Actualmente, los nodos toman un color gris por defecto.
    ),

    # --- Definición de los Links (Flujos) ---
    # 'link': Es un diccionario que configura la apariencia y comportamiento de los links (las bandas de flujo entre nodos).
    link=dict(
      # 'source': Lista de índices numéricos de los nodos de origen para cada link. Se toma de la columna 'origen_indice' del DataFrame.
      source=dfDatos["origen_indice"],
      # 'target': Lista de índices numéricos de los nodos de destino para cada link. Se toma de la columna 'destino_indice'.
      target=dfDatos["destino_indice"],
      # 'value': Lista de los valores (magnitud) de cada link. Determina el grosor del link. Se toma de la columna 'valor'.
      value=dfDatos["valor"],
      # 'hovercolor': Color que adopta el link cuando el cursor pasa sobre él.
      hovercolor="grey",
      # 'customdata': Permite asociar datos adicionales a cada link, que pueden ser usados en el hovertemplate.
      # Aquí se asocia la columna 'porcentaje' calculada previamente.
      customdata=dfDatos["porcentaje"],
      # 'hovertemplate': Define el texto que aparece al pasar el cursor sobre un link.
      # '%{source.label}' y '%{target.label}' muestran las etiquetas de los nodos de origen y destino.
      # '%{value:,.0f}' muestra el valor del link.
      # '%{customdata:.2%}' muestra el valor de 'customdata' (el porcentaje) formateado como porcentaje con 2 decimales.
      hovertemplate="%{source.label} -> %{target.label}<br>Valor: %{value:,.0f}<br>Porcentaje: %{customdata:.2%}",
      # 'color': Lista de colores para cada link. Se toma de la columna 'color' del DataFrame (con transparencia ya aplicada).
      color=dfDatos["color"],
      # Ejemplo alternativo (comentado) de asignación de color basado en el valor/porcentaje:
      # Se podría colorear los links según su magnitud o porcentaje relativo.
      # color = dfDatos["porcentaje"].apply(lambda x: "rgba(0, 0, 255, "+str(x)+")" if x > 0.05 else "rgba(0, 0, 255, 0.1" + str(x) + ")"),
))])

# --- Personalización del Layout del Gráfico ---
# 'update_layout' modifica la configuración general de la figura.
fig.update_layout(
    # 'margin': Ajusta los márgenes alrededor del área del gráfico (izquierda, derecha, arriba, abajo).
    # Se reducen los márgenes izquierdo y derecho (l=0, r=0) y el inferior (b=0) para maximizar el espacio para el gráfico.
    # Se deja un margen superior (t=50) para el título.
    margin=dict(l=0, r=0, t=50, b=0),
    # 'height': Establece la altura de la figura en píxeles.
    height=600,
)
# Añade un título al gráfico. Se usa formato HTML básico dentro del string:
# <b>...</b> para poner el texto en negrita.
# <br> para un salto de línea.
# f"..." permite incluir variables como el año seleccionado ('parAno').
# <a>...</a> crea un hipervínculo a la fuente de datos en Kaggle.
fig.update_layout(title_text=f"<b>Distribución ventas año {parAno}</b><br>Origen: <a href='https://www.kaggle.com/datasets/kyanyoga/sample-sales-data'>Kaggle</a>")
# 'update_traces' modifica propiedades específicas de las trazas (en este caso, la traza Sankey).
# Ajusta el color y tamaño de la fuente del texto que aparece *dentro* de los nodos/links (si Plotly los muestra).
fig.update_traces(textfont_color="black", textfont_size=15) #, selector=dict(type='sankey')) # El selector es opcional si solo hay una traza Sankey.

# --- Visualización en Streamlit ---
# Muestra la figura Plotly 'fig' en la aplicación Streamlit.
# 'st.plotly_chart' es la función de Streamlit para renderizar gráficos de Plotly.
# 'use_container_width=True' hace que el gráfico se ajuste automáticamente al ancho del contenedor de Streamlit (en este caso, la página completa debido al layout="wide").
# 'theme=None' indica que se use el tema por defecto de Plotly, en lugar de intentar adaptar el tema de Streamlit (que a veces puede causar conflictos visuales).
st.plotly_chart(fig, use_container_width=True, theme=None)

# Añade una línea divisoria horizontal en la app Streamlit
st.divider()

# --- SEGUNDO EJEMPLO: SANKEY ALPHABET INCOME ---
# Este bloque de código crea un segundo diagrama de Sankey independiente,
# utilizando un conjunto de datos diferente sobre los ingresos de Alphabet (Google).

# Carga los datos desde otro archivo CSV.
dfAlphabet=pd.read_csv("./AlphabetIncomeQ4_2024.csv", encoding="latin1")
# Ordena los datos por 'origen' y 'destino' en orden descendente.
dfAlphabet=dfAlphabet.sort_values(["origen","destino"],ascending=[False,False]).reset_index(drop=True)

# Prepara los nodos y sus índices numéricos, igual que en el primer ejemplo.
nodos = set(dfAlphabet["origen"].to_list() + dfAlphabet["destino"].to_list())
nodos_indices = {nodo: indice for indice, nodo in enumerate(nodos)}
dfAlphabet["origen_indice"] = dfAlphabet["origen"].map(nodos_indices)
dfAlphabet["destino_indice"] = dfAlphabet["destino"].map(nodos_indices)

# Define listas de nombres de nodos para asignar colores específicos manualmente.
# Esto permite agrupar visualmente diferentes tipos de ingresos y beneficios.
revenueAzul = [ # Nodos relacionados con ingresos publicitarios y otros.
  "Search advertising",
  "YouTube",
  "Google AdMob",
  "Ad Revenue",
  "Other (Revenue Source)",
  "Revenue"
]
revenueAmarillo=["Google Play","Google Cloud"] # Nodos de ingresos de Play y Cloud.
profitVerde = [ # Nodos relacionados con beneficios y otros ingresos/costos.
  "Gross profit",
  "Operating profit",
  "Net profit",
  "Pre-Tax Profit",
  "Other Income"
]

# Crea una lista de colores para los nodos.
coloresNodos =[]
# Itera sobre la lista única de nodos.
for nodo in nodos:
  colorNodo="#cc0001" # Color por defecto (rojo - probablemente para costos o elementos no categorizados).
  if nodo in revenueAzul:
    colorNodo="#4286f1" # Asigna azul si el nodo está en la lista revenueAzul.
  elif nodo in revenueAmarillo:
    colorNodo="#f9be06" # Asigna amarillo si el nodo está en la lista revenueAmarillo.
  elif nodo in profitVerde:
    colorNodo="#2ba02d" # Asigna verde si el nodo está en la lista profitVerde.
  coloresNodos.append(colorNodo) # Añade el color determinado a la lista.

# Crea la figura Plotly para el segundo Sankey.
fig = go.Figure(data=[go.Sankey(
    valueformat=",.0f", # Formato de valor (miles con coma, 0 decimales).
    valuesuffix=" B", # Sufijo para miles de millones (Billions).

    # Configuración de Nodos
    node=dict(
      pad=15,
      thickness=30,       # Nodos más gruesos que en el primer ejemplo.
      label=list(nodos),
      hovertemplate="%{label}<br>Valor: $ %{value:,.1f} B", # Hovertemplate específico con $ y 1 decimal.
      color = coloresNodos, # Asigna la lista de colores creada manualmente a los nodos.
      align="right",      # Alinea las etiquetas de los nodos a la derecha (puede ayudar si los nodos están a la izquierda).
    ),

    # Configuración de Links
    link=dict(
      source=dfAlphabet["origen_indice"],
      target=dfAlphabet["destino_indice"],
      value=dfAlphabet["valor"],
      hovercolor="grey",
      # No se usa customdata aquí.
      hovertemplate="%{source.label} -> %{target.label}<br>Valor: $ %{value:,.1f} B", # Hovertemplate específico para links.
      # Asume que el CSV ya tiene una columna 'color' predefinida para los links.
      # Si no la tiene, esto dará un error o los links no tendrán color.
      # Se debería verificar si 'AlphabetIncomeQ4_2024.csv' contiene una columna 'color'.
      # Si no, habría que definir una lógica similar a la del primer ejemplo o asignar un color fijo.
      color=dfAlphabet["color"],
))])

# Personalización del Layout del segundo gráfico.
fig.update_layout(
    margin=dict(l=0, r=0, t=50, b=0),
    height=600,
)
# Título específico para este gráfico, con fuente más grande y en negrita.
fig.update_layout(title_text="Resultados de Alphabet para el Q4 2024",titlefont_size=30,titlefont_weight="bold")
fig.update_traces(textfont_color="black", textfont_size=15)

# Muestra el segundo gráfico Sankey en la aplicación Streamlit.
st.plotly_chart(fig, use_container_width=True, theme=None)