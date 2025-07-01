# =============================================================================
# LIBRERÍAS Y MÓDULOS NECESARIOS
# =============================================================================
#
# Streamlit: Es un framework de código abierto para crear y compartir aplicaciones
# web para ciencia de datos y machine learning de forma rápida y sencilla.
# No necesitas saber HTML, CSS o JavaScript.
# Comando para instalar: pip install streamlit
#
# Requests: Es una librería estándar para hacer peticiones HTTP en Python.
# La usaremos para obtener la imagen de perfil del usuario desde una URL.
# Comando para instalar: pip install requests
#
# =============================================================================

import streamlit as st
import requests

# Este código se basa en la documentación oficial de Streamlit para la autenticación:
# https://docs.streamlit.io/develop/tutorials/authentication/google

# Configura la página para que utilice el diseño "wide" (ancho),
# ocupando todo el ancho disponible del navegador.
st.set_page_config(layout="wide", page_title="Ejemplo Streamlit Google Auth")

# Muestra el título principal de la aplicación web.
st.title("Ejemplo de inicio de sesión con Google en Streamlit")

def login_screen():
    """
    Muestra la pantalla de inicio de sesión cuando un usuario no está autenticado.
    Presenta un encabezado, un subencabezado y un botón que, al ser presionado,
    inicia el flujo de autenticación de Google gestionado por Streamlit.
    """
    st.header("Esta aplicación es privada.")
    st.subheader("Por favor, inicia sesión.")
    # El botón "st.button" inicia el flujo de login gracias al argumento on_click=st.login.
    # st.login() es una función nativa de Streamlit que redirige al usuario a la
    # página de inicio de sesión de Google.
    # El texto ":material/login:" es un atajo para usar los iconos de Material Design.
    st.button(":material/login: Iniciar sesión con Google", on_click=st.login)

# =============================================================================
# LÓGICA PRINCIPAL DE LA APLICACIÓN
# =============================================================================

# st.experimental_user es un objeto que contiene la información del usuario autenticado.
# El atributo .is_logged_in devuelve True si el usuario ha iniciado sesión y False en caso contrario.
# Este condicional es el núcleo de la aplicación: decide si mostrar la pantalla de login o el contenido principal.
if not st.experimental_user.is_logged_in:
    # Si el usuario NO ha iniciado sesión, llamamos a la función que muestra la pantalla de login.
    login_screen()
else:
    # Si el usuario SÍ ha iniciado sesión, se ejecuta este bloque de código.
    # Usamos "with st.sidebar:" para que todo el contenido indentado a continuación
    # aparezca en la barra lateral de la aplicación.
    with st.sidebar:
        # Creamos un contenedor para organizar mejor los elementos de la barra lateral.
        with st.container():
            # Dividimos el contenedor en dos columnas para alinear la imagen y la información del usuario.
            # El ratio [1, 3] significa que la segunda columna será 3 veces más ancha que la primera.
            c1, c2 = st.columns([1, 3])    
            
            with c1:
                # Verificamos si el objeto de usuario contiene una URL de imagen de perfil.
                if st.experimental_user.picture:
                    try:
                        # Usamos la librería 'requests' para hacer una petición GET a la URL de la imagen.
                        response = requests.get(st.experimental_user.picture)
                        # Si el código de estado de la respuesta es 200 (OK), significa que la imagen se obtuvo correctamente.
                        if response.status_code == 200:
                            # Mostramos la imagen en la aplicación. response.content contiene los bytes de la imagen.
                            st.image(response.content, width=100)
                        else:
                            # Si hay un problema al descargar la imagen (ej: error 404), mostramos una advertencia.
                            st.warning("No se pudo cargar la imagen de perfil.")
                    except Exception as e:
                        # Capturamos cualquier otra excepción (ej: problemas de red) y mostramos un mensaje de error.
                        st.warning(f"Error al cargar la imagen: {e}")
                else:
                    # Si el usuario de Google no tiene una imagen de perfil, informamos de ello.
                    st.info("No hay imagen de perfil disponible.")  
            
            with c2:
                st.header("Información del usuario")                
                # Accedemos y mostramos el nombre y el email del usuario.
                # Estos datos son proporcionados por Google después de una autenticación exitosa.
                st.write(f"**Nombre:** \n {st.experimental_user.name}")
                st.write(f"**Correo electrónico:** \n{st.experimental_user.email}")    
        
        # Creamos un botón para cerrar sesión.
        # Al hacer clic, se ejecuta la función nativa st.logout(), que borra la sesión del usuario.
        st.button(":material/logout: Cerrar sesión", on_click=st.logout)

    # st.json() es una forma útil de visualizar datos en formato JSON.
    # .to_dict() convierte el objeto de usuario en un diccionario de Python.
    # Esto es excelente para depuración, ya que nos permite ver toda la información
    # que Google ha devuelto sobre el usuario.
    st.json(st.experimental_user.to_dict())