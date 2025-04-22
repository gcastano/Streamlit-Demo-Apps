import streamlit as st  # Importa la librería Streamlit para crear la aplicación web. Para instalarla: pip install streamlit
# https://github.com/NathanChen198/streamlit-cookies-controller
from streamlit_cookies_controller import CookieController # Importa la librería para manejar cookies en Streamlit. Para instalarla: pip install streamlit-cookies-controller

# Configura el título de la página, el ícono y el diseño.
st.set_page_config('Cookies con Streamlit', '🍪', layout='wide')

# Crea una instancia del controlador de cookies.
controller = CookieController()

# Obtiene la cookie de nombre de usuario.
usernameCookie = controller.get('username')

# Verifica si la cookie de nombre de usuario existe.
if usernameCookie is None:
    # Si no existe, muestra un formulario de inicio de sesión.
    with st.form("login_form"):
        username = st.text_input("Username") # Campo para ingresar el nombre de usuario.
        password = st.text_input("Password", type="password") # Campo para ingresar la contraseña.
        submit = st.form_submit_button("Login") # Botón para enviar el formulario.
    if submit:
        if username and password:
            # Si se ingresaron nombre de usuario y contraseña, se guarda el nombre de usuario en una cookie.
            controller.set('username', username)
            st.success(f"Welcome, {username}!") # Muestra un mensaje de bienvenida.
            st.rerun() # Recarga la página para reflejar los cambios.
        else:
            st.error("Por favor ingrese un nombre de usuario y una contraseña.") # Muestra un mensaje de error si no se ingresaron las credenciales.
else:
    # Si la cookie de nombre de usuario existe, se configura la barra lateral.
    controller.set('username', usernameCookie) # Setea la cookie nuevamente para mantener la sesión activa
    with st.sidebar:
        st.success(f"Bienvenido, {usernameCookie}!") # Muestra un mensaje de bienvenida.
        btnLogout = st.button("Cerrar sesión") # Botón para cerrar sesión.
        
        if btnLogout:
            controller.remove('username') # Elimina la cookie de nombre de usuario.           
            st.rerun() # Recarga la página para reflejar los cambios.
    # Recupera el estilo de la cookie si existe, sino lo inicializa
    estiloCookie = controller.get('estilo')
    if estiloCookie:
        color = estiloCookie['color']
        tamanoLetra = estiloCookie['tamanoLetra']
    else:
        color = "#00f900"
        tamanoLetra = 20
    # Permite al usuario elegir un color y tamaño de letra, y lo guarda en las cookies
    color = st.color_picker("Elige un color", color) # Selector de color.
    tamanoLetra = st.slider("Tamaño de letra", 10, 100, tamanoLetra) # Control deslizante para el tamaño de letra.
    controller.set('estilo', {"color": color, "tamanoLetra": tamanoLetra}) # Guarda el estilo en una cookie.
    
    # Muestra un saludo personalizado con el color y tamaño de letra elegidos.
    st.markdown(f"<h1 style='color:{color}; font-size:{tamanoLetra}px;'>Hola {usernameCookie}!</h1>", unsafe_allow_html=True)
    

# Obtiene todas las cookies.
cookies = controller.getAll() # Obtiene todas las cookies
st.write(cookies) # Muestra todas las cookies.