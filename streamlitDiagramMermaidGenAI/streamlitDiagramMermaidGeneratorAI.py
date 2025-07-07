# -*- coding: utf-8 -*-

# ------------------- LIBRERÍAS -------------------
# A continuación, se importan todas las librerías necesarias para el funcionamiento de la aplicación.

# --- Streamlit: Framework principal para crear la aplicación web ---
# Streamlit permite construir y compartir aplicaciones web interactivas para ciencia de datos y machine learning
# de forma rápida y sencilla, escribiendo únicamente scripts en Python.
# Comando para instalar: pip install streamlit
import streamlit as st

# --- Google Generative AI (Gemini): Para la generación de contenido con IA ---
# Es el SDK oficial de Google para interactuar con sus modelos de lenguaje generativos, como Gemini.
# Lo usaremos para que la IA entienda la petición del usuario y genere el código del diagrama.
# Comando para instalar: pip install google-generativeai
from google import genai
from google.genai import types

# --- Módulos personalizados ---
# Estos son archivos .py locales que contienen lógica específica para esta aplicación.
# GoogleMermaidAI: Contiene la función para interactuar con la API de Gemini y generar el diagrama.
# MermaidLib: Contiene la función para convertir el código Mermaid en una imagen (PNG, SVG, PDF).
import GoogleMermaidAI as genai_client
import MermaidLib as mermaid

# --- streamlit-mermaid: Componente para renderizar diagramas Mermaid en Streamlit ---
# Facilita la visualización de diagramas creados con la sintaxis de MermaidJS directamente en la app.
# Comando para instalar: pip install streamlit-mermaid
import streamlit_mermaid as stmd


# --- streamlit-pdf-viewer: Componente para mostrar archivos PDF ---
# Permite visualizar el diagrama generado en formato PDF directamente en la interfaz de Streamlit.
# Comando para instalar: pip install streamlit-pdf-viewer
from streamlit_pdf_viewer import pdf_viewer

# --- base64: Librería estándar de Python ---
# Se utiliza para codificar y decodificar datos en Base64. En este caso, para mostrar
# imágenes SVG de forma segura en el HTML de la aplicación.
# No requiere instalación (es parte de la librería estándar de Python).
import base64

# --- Enlaces útiles a la documentación de MermaidJS ---
# MermaidJS cheatsheet: https://jojozhuang.github.io/tutorial/mermaid-cheat-sheet/
# MermaidJS documentation: https://mermaid.js.org/

# --- Configuración de la página de Streamlit ---
# st.set_page_config se usa para establecer metadatos de la página como el título,
# el ícono que aparece en la pestaña del navegador y el layout (ancho).
st.set_page_config(page_title="Generador de diagramas IA", page_icon="💬", layout="wide")

def motrar_svg(svg: str):
    """
    Renderiza una cadena de texto SVG como una imagen en la aplicación Streamlit.

    Esta función toma una cadena que contiene código SVG, la codifica en Base64 y
    luego la incrusta en una etiqueta HTML <img> para que el navegador la pueda mostrar.
    Esto es necesario para visualizar correctamente los SVG generados.

    Args:
        svg (str): Una cadena de texto que contiene el código SVG del diagrama.
    """
    # Codifica la cadena SVG a bytes en formato UTF-8 y luego a Base64.
    b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
    # Crea una cadena HTML con una etiqueta <img> que utiliza un Data URI para mostrar la imagen codificada.
    html = r'<img src="data:image/svg+xml;base64,%s"/>' % b64
    # Escribe el HTML en la aplicación. `unsafe_allow_html=True` es necesario para renderizar HTML personalizado.
    st.html(html)

# Título principal de la aplicación.
st.title(":blue[:material/network_intel_node:] Generador de Diagramas Mermaid con IA")

# Inicializamos la variable `respuesta` a None. Contendrá el código Mermaid generado por la IA.
respuesta = None

# --- Creación de la interfaz con columnas ---
# st.columns crea un layout de columnas. El ratio [2, 3, 4] define el ancho relativo de cada columna.
# c1: Chat y entrada de usuario.
# c2: Editor de código.
# c3: Visualización y descarga del diagrama.
c1, c2, c3 = st.columns([2, 3, 4])

# --- Columna 1: Interfaz de Chat ---
with c1:
    with st.container(border=True, height=800):
        st.subheader(":blue[:material/account_tree: ¿Qué diagrama quieres generar?]",divider ="blue")
        
        # --- Gestión del historial de chat con `st.session_state` ---
        # `st.session_state` es un objeto tipo diccionario que persiste entre re-ejecuciones del script.
        # Es fundamental para mantener el estado de la aplicación, como el historial de chat.
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # --- Mostrar el historial de chat ---
        # Itera sobre el historial guardado y muestra cada mensaje usando el rol correspondiente ("user" o "AI").
        for user, msg in st.session_state.chat_history:
            with st.chat_message(user):
                if user == "AI":
                    # Guardamos la última respuesta de la IA para usarla más adelante.
                    respuesta = msg.strip()  
                    st.markdown("Código Mermaid generado...")
                else:
                    st.markdown(msg)

        # --- Entrada de usuario ---
        # `st.chat_input` muestra un campo de texto fijo en la parte inferior para que el usuario escriba.
        user_input = st.chat_input("Escribe tu mensaje:")

        if user_input:
            # Cuando el usuario envía un mensaje, se reinicia el historial para una nueva conversación.
            st.session_state.chat_history = []
            # Se añade el mensaje del usuario al historial.
            st.session_state.chat_history.append(("user", user_input.strip()))
            
            # --- Llamada a la IA para generar el diagrama ---
            # Se llama a la función del módulo `GoogleMermaidAI` para obtener el código Mermaid.
            respuesta = genai_client.generarDiagrama(user_input)
            
            # Se añade la respuesta de la IA al historial.
            st.session_state.chat_history.append(("AI", respuesta.strip()))
            
            # --- Limpieza y almacenamiento del código del diagrama ---
            # El modelo de IA a menudo devuelve el código dentro de un bloque de código (```mermaid ... ```).
            # Estas líneas limpian esas etiquetas para obtener solo el código puro de Mermaid.
            st.session_state.diagrama = respuesta.replace("```mermaid", "").replace("```", "").strip()
            
            # `st.rerun()` fuerza a la aplicación a ejecutarse de nuevo desde el principio.
            # Esto es útil para actualizar inmediatamente la interfaz con el nuevo estado (el diagrama generado).
            st.rerun()

# --- Columna 2: Editor de Código ---
with c2:
    with st.container(border=True, height=800):
        st.subheader(":grey[:material/code_blocks: Editor de Código Mermaid]",divider ="grey")
        # Solo muestra el editor si ya se ha generado una respuesta de la IA.
        if respuesta:
            # Limpia de nuevo el código por si acaso y lo guarda en el `session_state`.
            st.session_state.diagrama = respuesta.replace("```mermaid", "").replace("```", "").strip()
            # `st.text_area` crea un campo de texto de múltiples líneas. Se usa como un editor simple.
            # El usuario puede modificar el código Mermaid aquí y los cambios se reflejarán en el diagrama.
            st.session_state.diagrama = st.text_area(
                "Diagrama Mermaid",
                value=st.session_state.diagrama.replace("```mermaid", "").replace("```", "").strip(),
                height=600
            )

# --- Columna 3: Visualización del Diagrama y Opciones de Exportación ---
with c3:
    with st.container(border=True, height=800):
        st.subheader(":green[:material/graph_3: Diagrama Mermaid Generado]",divider ="green")
        
        # Se crea una sub-columna para alinear los controles horizontalmente.
        cols = st.columns([4, 4, 2], vertical_alignment="center")
        with cols[0]:
            # `st.segmented_control` crea un botón de selección de opciones.
            parFormato = st.segmented_control("Formato:", options=["PDF", "PNG", "SVG"], default="PNG")
        with cols[1]:
            # Enlace útil para que el usuario pueda editar el código en un editor más avanzado.
            st.markdown(f"Editar en [Mermaid Live Editor](https://mermaid.live/edit)")

        # Verifica si ya existe un diagrama en el estado de la sesión para mostrarlo.
        if "diagrama" in st.session_state:
            # Llama a la función del módulo `MermaidLib` para convertir el código a una imagen.
            imgMermaid, error = mermaid.generarGraficoMermaid(st.session_state.diagrama, parFormato)
            
            # Manejo de errores: si la generación falla, muestra un mensaje de error.
            if error:
                st.error(error)
            else:
                # --- Lógica de visualización y descarga según el formato seleccionado ---
                if parFormato == "PDF":
                    # Botón para descargar el archivo PDF.
                    st.download_button("Descargar PDF", data=imgMermaid, file_name="diagrama.pdf", mime="application/pdf")
                    # Muestra el PDF directamente en la app usando el componente `pdf_viewer`.
                    pdf_viewer(imgMermaid, key="pdf_viewer", width=700, height=1000)
                elif parFormato == "SVG":
                    # Botón para descargar el archivo SVG.
                    st.download_button("Descargar SVG", data=imgMermaid, file_name="diagrama.svg", mime="image/svg+xml")
                    # Llama a la función personalizada para renderizar el SVG.
                    motrar_svg(imgMermaid.decode('utf-8'))
                else:  # Por defecto, se asume PNG
                    # Botón para descargar el archivo PNG (actualmente comentado en el código original).
                    # st.download_button("Descargar PNG", data=imgMermaid, file_name="diagrama.png", mime="image/png")
                    # Muestra la imagen PNG. `use_container_width=True` hace que la imagen se ajuste al ancho de la columna.
                    st.image(imgMermaid, caption="Diagrama Mermaid generado", use_container_width=True)