# Streamlit: Librería para crear aplicaciones web interactivas en Python.
# Instalación: pip install streamlit
import streamlit as st

# Diccionario que define la estructura de navegación de la aplicación.
# Cada clave representa una sección principal del menú de navegación,
# y su valor es una lista de páginas asociadas a esa sección.
pages = {
    # Sección "Control Gastos" con sus respectivas páginas.
    "Control Gastos": [
        # Página para gestionar gastos.
        st.Page(
            "gastos.py",  # Archivo Python que contiene el código de la página.
            title="Gastos",  # Título que se mostrará en la pestaña del navegador y en el menú.
            icon=":material/shopping_cart:"  # Ícono que se mostrará junto al título en el menú.
        ),
        # Página para analizar gastos.
        st.Page(
            "analisis.py",  # Archivo Python que contiene el código de la página.
            title="Análisis de Gastos",  # Título que se mostrará en la pestaña del navegador y en el menú.
            icon=":material/bar_chart:"  # Ícono que se mostrará junto al título en el menú.
        ),
    ],
    # Sección "Configuración" con sus respectivas páginas.
    "Configuración": [
        # Página para gestionar categorías y subcategorías.
        st.Page(
            "categorias.py",  # Archivo Python que contiene el código de la página.
            title="Categorías y Subcategorías",  # Título que se mostrará en la pestaña del navegador y en el menú.
            icon=":material/network_node:"  # Ícono que se mostrará junto al título en el menú.
        ),
    ],
}

# Crea un objeto de navegación con la estructura definida en el diccionario `pages`.
# Esto genera un menú lateral con las secciones y páginas especificadas.
pg = st.navigation(pages)

# Ejecuta la aplicación de Streamlit con la navegación configurada.
# Esto mostrará la interfaz de usuario según la página seleccionada en el menú.
pg.run()
