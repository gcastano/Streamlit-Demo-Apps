import streamlit as st
import pandas as pd
import requests

# -----------------------------------------------------------------------------
# SECCIÓN DE INSTALACIÓN Y LIBRERÍAS
# -----------------------------------------------------------------------------
# Para ejecutar este código, necesitas instalar las siguientes librerías:
# pip install streamlit pandas requests

# EXPLICACIÓN DE LIBRERÍAS:
# - streamlit: Framework para crear aplicaciones web de datos en Python rápidamente.
# - pandas: La herramienta principal para manipulación y análisis de datos (DataFrames).
# - requests: Permite hacer peticiones HTTP para traer recursos de internet (en este caso, CSS).

# Configuración básica de la página de Streamlit
st.set_page_config(page_title="Material Table with Buttons", layout="wide")
st.title("Tabla con Botones usando Materialize CSS en Streamlit usando `st.components.v2.component`")

# -----------------------------------------------------------------------------
# CREACIÓN DEL DATAFRAME (PANDAS)
# -----------------------------------------------------------------------------
# Creamos un DataFrame simple para el ejemplo.
# Un DataFrame es una estructura de datos tabular bidimensional (filas y columnas).
df = pd.DataFrame({
    'ID': ['1', '2', '3'],    
    'Item Name': ['Eclair', 'Jellybean', 'Lollipop'],
    'Item Price': [0.87, 3.76, 7.00]
})


@st.dialog("Detalle del Item")
def generarPopup(id, df, titulo):
    """
    Genera una ventana modal (popup) mostrando los detalles de un registro específico.
    
    Args:
        id (str): El ID del registro a mostrar.
        df (pd.DataFrame): El DataFrame completo donde buscar los datos.
        titulo (str): El título de la acción (Editar, Eliminar, etc.).
    """
    st.subheader(f'{titulo}: {id}')
    
    # -------------------------------------------------------------------------
    # TRANSFORMACIÓN PANDAS: FILTRADO
    # -------------------------------------------------------------------------
    # Filtramos el DataFrame original para obtener solo la fila donde la columna 'ID'
    # coincide con el 'id' recibido por la función.
    df_popup = df[df['ID'] == id]
    
    contenido_html = '<div class="card">\n<div class="card-content">\n'
    
    # Iteramos sobre las columnas del DataFrame filtrado
    for col in df_popup.columns:
        # df_popup.iloc[0][col]: 
        # .iloc[0] accede a la primera fila (índice 0) del resultado filtrado.
        # [col] accede al valor de la columna actual.
        contenido_html += f'    <p><strong>{col}:</strong> {df_popup.iloc[0][col]}</p>\n'
        
    contenido_html += '</div>\n</div>\n'
    st.html(contenido_html)

def generar_tabla_con_botones(dataframe, btnselect=None, btnedit=None, btndelete=None):
    """
    Convierte un DataFrame de Pandas en una tabla HTML con estilos de Materialize CSS
    y añade botones de acción configurables.

    Args:
        dataframe (pd.DataFrame): Los datos a visualizar.
        btnselect (bool): Si es True, añade botón de seleccionar.
        btnedit (bool): Si es True, añade botón de editar.
        btndelete (bool): Si es True, añade botón de eliminar.

    Returns:
        str: Cadena de texto con el código HTML de la tabla.
    """
    # Inicio de la tabla HTML con clase 'striped' de Materialize
    tabla_html = '<table class="striped">\n<thead>\n<tr>\n'
    
    # Generamos los encabezados (th) iterando sobre los nombres de las columnas del DataFrame
    for col in dataframe.columns:
        tabla_html += f'    <th>{col}</th>\n'
    tabla_html += '    <th>Action</th>\n</tr>\n</thead>\n<tbody>\n'

    # -------------------------------------------------------------------------
    # TRANSFORMACIÓN PANDAS: ITERACIÓN
    # -------------------------------------------------------------------------
    # iterrows() es un generador que permite recorrer el DataFrame fila por fila.
    # Devuelve el índice y la serie (fila) con los datos.
    for index, row in dataframe.iterrows():
        tabla_html += '<tr>\n'
        for col in dataframe.columns:
            # Accedemos al valor de la celda usando row[col]
            tabla_html += f'    <td>{row[col]}</td>\n'
        
        # Lógica para construir la celda de acciones con botones
        acciones= "<td>"
        # data-link="accion_id" es clave para que JS sepa qué botón se pulsó y sobre qué ID
        if btnselect:
            acciones += f'    <a data-link="select_{row["ID"]}" class="btn-floating waves-effect waves-light btn"><i class="material-icons left">check</i></a>\n'
        if btnedit:
            acciones += f'    <a data-link="edit_{row["ID"]}" class="btn-floating waves-effect waves-light btn"><i class="material-icons left">edit</i></a>\n'
        if btndelete:
            acciones += f'    <a data-link="delete_{row["ID"]}" class="btn-floating waves-effect waves-light btn"><i class="material-icons left">delete</i></a>\n'
        acciones+= "</td>"
        tabla_html += acciones
        tabla_html += '</tr>\n'

    tabla_html += '</tbody>\n</table>'
    return tabla_html

# Obtenemos los estilos CSS externos usando requests para asegurar que la tabla tenga estilo
styles= """
<link href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css" rel="stylesheet">
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
"""
st.write(styles, unsafe_allow_html=True)
# st.html(styles)

resultado = requests.get('https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css', timeout=5)
resultado2 = requests.get('https://fonts.googleapis.com/icon?family=Material+Icons', timeout=5)



# Concatenamos los estilos CSS obtenidos
CSS = resultado.text + "\n" + resultado2.text

# JavaScript para manejar los eventos de clic dentro del componente personalizado
JS = """
export default function(component) {
    const { data, setTriggerValue, parentElement } = component;
    const newElement = document.createElement('div');
    parentElement.appendChild(newElement);
    newElement.innerHTML = data;

    const links = newElement.querySelectorAll('a');

    // Añade un evento onclick a cada botón generado en la tabla
    links.forEach((link) => {
        link.onclick = (e) => {
            // Envía de vuelta a Python la acción y el ID (ej: "edit_2")
            setTriggerValue('clicked', link.getAttribute('data-link'));
        };
    });
}
"""

# Definición del componente personalizado de Streamlit (Custom Component V2)
# https://docs.streamlit.io/develop/api-reference/custom-components/st.components.v2.component
material_table = st.components.v2.component(
    "material_table_with_buttons",
    # css=CSS,
    js=JS,
    isolate_styles = False,
)

# Generamos el HTML de la tabla partiendo del DataFrame
paragraph_html = generar_tabla_con_botones(df, btnselect=True, btnedit=True, btndelete=True)

# Renderizamos el componente y capturamos el resultado (interacciones del usuario)
result = material_table(data=paragraph_html, on_clicked_change=lambda: None, key="table_with_buttons")
st.write(result)

# Lógica para manejar la respuesta del componente
if result and 'clicked' in result:
    clicked_action = result['clicked']
    if clicked_action:
        # Separamos la acción del ID (ej: "edit_2" -> action="edit", id="2")
        action, id = clicked_action.split('_')
        
        # Llamamos al popup correspondiente según la acción
        if action == 'select':
            generarPopup(id, df, "Seleccionar")
        elif action == 'edit':
            generarPopup(id, df, "Editar")
        elif action == 'delete':
            generarPopup(id, df, "Eliminar")