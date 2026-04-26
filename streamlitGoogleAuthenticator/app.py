# =============================================================================
# COMANDOS DE INSTALACIÓN Y EXPLICACIÓN DE LIBRERÍAS
# =============================================================================
# Para ejecutar este código, necesitas instalar las siguientes librerías. 
# Ejecuta este comando en tu terminal:
# ---> pip install streamlit pyotp qrcode[pil] bcrypt pandas
#
# EXPLICACIÓN DE LIBRERÍAS:
# 1. streamlit: Framework de Python para crear aplicaciones web interactivas 
#    de forma rápida y orientada a datos.
# 2. sqlite3: Viene por defecto en Python. Permite interactuar con bases de 
#    datos relacionales ligeras sin necesidad de servidores extra.
# 3. pyotp: Librería fundamental para generar y verificar contraseñas de un 
#    solo uso (TOTP/HOTP). Es el motor de nuestro sistema 2FA.
# 4. qrcode: Sirve para generar imágenes de códigos QR que el usuario escaneará 
#    con apps como Google Authenticator o Authy.
# 5. bcrypt: Estándar de la industria para el hasheo (encriptación) seguro de 
#    contraseñas, protegiéndolas contra ataques de fuerza bruta.
# 6. io (BytesIO): Viene por defecto. Permite manejar datos binarios en memoria 
#    (como la imagen de nuestro QR) sin tener que guardarla en el disco duro.
# 7. pandas (Mencionada): La librería líder en Python para limpieza, 
#    transformación y análisis de datos. (Ver sección de "Datos Sensibles").
# =============================================================================

import streamlit as st
import sqlite3
import pyotp
import qrcode
import bcrypt
from io import BytesIO

# --- CONFIGURACIÓN DE LA PÁGINA ---
# Configuramos el título de la pestaña en el navegador, el ícono y el diseño de la app.
st.set_page_config(
    page_title="Acceso Seguro 2FA",
    page_icon=":material/shield_lock:",
    layout="centered"
)

# --- FUNCIONES DE BASE DE DATOS Y SEGURIDAD ---

def init_db():
    """
    Inicializa la base de datos SQLite y crea la tabla de usuarios si no existe.
    
    Proceso:
    1. Abre (o crea) un archivo llamado 'users.db'.
    2. Crea un cursor para ejecutar comandos SQL.
    3. Ejecuta la sentencia CREATE TABLE para estructurar los datos del usuario:
       - username: Nombre de usuario (Clave primaria, no se puede repetir).
       - password_hash: Contraseña encriptada (nunca en texto plano).
       - totp_secret: La semilla secreta única para generar los códigos 2FA.
    """
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            totp_secret TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    """
    Encripta la contraseña ingresada por el usuario utilizando el algoritmo bcrypt.
    
    Parámetros:
    - password (str): La contraseña en texto plano ingresada en el registro.
    
    Retorna:
    - str: La contraseña hasheada y con 'sal' (salt) agregada para máxima seguridad.
    """
    # bcrypt requiere que la contraseña esté en formato de bytes, por eso usamos .encode()
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    """
    Verifica si una contraseña en texto plano coincide con un hash almacenado.
    
    Parámetros:
    - password (str): Contraseña que el usuario intenta usar para iniciar sesión.
    - hashed (str): El hash de la contraseña guardada en la base de datos.
    
    Retorna:
    - bool: True si coinciden, False si la contraseña es incorrecta.
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_user(username, password, secret):
    """
    Registra un nuevo usuario de forma segura en la base de datos.
    
    Parámetros:
    - username (str): Nombre de usuario elegido.
    - password (str): Contraseña en texto plano (se hasheará antes de guardarse).
    - secret (str): Código secreto generado por pyotp para el 2FA.
    
    Retorna:
    - bool: True si el usuario se creó correctamente, False si el usuario ya existe.
    """
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password_hash, totp_secret) VALUES (?, ?, ?)",
                  (username, hash_password(password), secret))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Si el usuario ya existe, SQLite lanzará un IntegrityError por la Primary Key
        return False
    finally:
        conn.close()

def get_user_data(username):
    """
    Busca y recupera los datos sensibles de un usuario (hash y secreto 2FA).
    
    Parámetros:
    - username (str): El nombre de usuario que está intentando iniciar sesión.
    
    Retorna:
    - tuple o None: Una tupla con (password_hash, totp_secret) si el usuario existe,
      o None si no se encuentra en la base de datos.
    """
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT password_hash, totp_secret FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    return result

# Ejecutamos la inicialización de la BD al arrancar la app.
init_db()

# --- MANEJO DEL ESTADO DE LA SESIÓN ---
# Streamlit se recarga de arriba a abajo en cada interacción. 
# Usamos session_state para "recordar" si el usuario ya hizo login correctamente.
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.title(":material/security: Mi App Segura")
    st.caption("v1.0.0 | Autenticación Segura")
    st.divider()
    
    # Si el usuario tiene sesión activa, le damos la opción de salir (Log out)
    if st.session_state.logged_in:
        st.success(f"Sesión activa: **{st.session_state.current_user}**")
        if st.button("Cerrar Sesión", type="secondary", icon=":material/logout:", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.rerun() # Reinicia la app para aplicar los cambios de estado
    else:
        st.info("Por favor, inicia sesión para acceder al contenido protegido.")
    
    st.write("")
    with st.expander("Información de Seguridad", icon=":material/info:"):
        st.write("Esta aplicación utiliza hash de contraseñas con **bcrypt** y autenticación de dos factores (TOTP).")

# --- INTERFAZ DE USUARIO PRINCIPAL ---

if st.session_state.logged_in:
    # ---------------------------------------------------------
    # VISTA: ÁREA PROTEGIDA (Solo accesible tras el 2FA)
    # ---------------------------------------------------------
    st.title(f"Bienvenido, {st.session_state.current_user} :material/celebration:")
    st.success("Autenticación de dos factores completada con éxito.", icon=":material/check_circle:")
    
    st.divider()
    
    # KPIs y Métricas en un contenedor moderno
    with st.container(border=True):
        st.subheader(":material/dashboard: Panel de Control")
        st.write("Visualización de estado y seguridad de la cuenta.")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Seguridad", "Activa", delta="2FA", delta_color="normal")
        with col2:
            st.metric("Sesión", "Estable")
        with col3:
            st.metric("Estado", "Protegido")
    
    st.write("")
    
    # Simulación de contenido protegido usando pestañas
    tab_data, tab_settings = st.tabs([":material/database: Datos Sensibles", ":material/settings: Configuración"])
    
    with tab_data:
        st.info("Aquí se mostrarían tus datos cifrados.")
        
        # =====================================================================
        # CLASE EDUCATIVA: TRANSFORMACIONES DE DATOS CON PANDAS
        # =====================================================================
        # En una aplicación real orientada a datos, este es el punto exacto 
        # donde integraríamos la librería 'pandas' para transformar información.
        # 
        # EJEMPLO DE FLUJO DE TRANSFORMACIÓN CON PANDAS:
        # 
        # import pandas as pd
        # 
        # 1. Carga de datos (Extracción):
        #    df = pd.read_json('datos_empresa.json') o pd.read_sql(query, conn)
        # 
        # 2. Limpieza de datos (Transformación):
        #    df.dropna(inplace=True)  # Elimina filas con valores vacíos (nulos).
        #    df['last_login'] = pd.to_datetime(df['last_login']) # Convierte texto a fecha.
        # 
        # 3. Filtrado y Agrupación:
        #    # Filtramos usuarios que son Administradores
        #    df_admin = df[df['access_level'] == 'Admin']
        #    # Agrupamos por mes para ver conexiones
        #    df_grouped = df.groupby(df['last_login'].dt.month).size()
        # 
        # 4. Visualización en Streamlit (Carga):
        #    st.dataframe(df_admin) # Muestra la tabla transformada de pandas en pantalla.
        # =====================================================================

        st.code("""
        {
            "id": "USR-9982",
            "last_login": "2024-04-19",
            "access_level": "Admin"
        }
        """, language="json")

    with tab_settings:
        st.write("Gestiona las preferencias de tu cuenta.")
        st.checkbox("Recibir notificaciones por correo")
        st.checkbox("Habilitar registros de auditoría")

else:
    # ---------------------------------------------------------
    # VISTA: LOGIN Y REGISTRO
    # ---------------------------------------------------------
    st.title("Acceso Protegido")
    st.caption("Inicia sesión para continuar")
    
    tab_login, tab_registro = st.tabs([
        ":material/login: Iniciar Sesión", 
        ":material/person_add: Crear Cuenta"
    ])
    
    with tab_login:
        with st.form("login_form", border=True, clear_on_submit=False):
            st.subheader("Credenciales de Acceso")
            
            log_username = st.text_input("Usuario", key="log_user", placeholder="Nombre de usuario")
            log_password = st.text_input("Contraseña", type="password", key="log_pass", placeholder="••••••••")
            
            st.divider()
            st.markdown("**Segundo factor (2FA)**")
            # Este campo recibe los 6 dígitos generados por la app del móvil
            log_code = st.text_input("Código de Authenticator", max_chars=6, key="log_code", help="Código de 6 dígitos de tu app móvil.")
            
            if st.form_submit_button("Acceder", type="primary", icon=":material/login:", use_container_width=True):
                if log_username and log_password and log_code:
                    user_data = get_user_data(log_username)
                    if user_data:
                        stored_hash, stored_secret = user_data
                        
                        # 1er factor: Verificar la contraseña hasheada
                        if check_password(log_password, stored_hash):
                            
                            # 2do factor: Verificar el código TOTP dinámico
                            totp = pyotp.TOTP(stored_secret)
                            if totp.verify(log_code):
                                st.session_state.logged_in = True
                                st.session_state.current_user = log_username
                                st.toast("¡Acceso concedido!", icon="✅")
                                st.rerun()
                            else:
                                st.error("Código 2FA incorrecto o expirado.", icon=":material/error:")
                        else:
                            st.error("Credenciales inválidas.", icon=":material/no_accounts:")
                    else:
                        st.error("Credenciales inválidas.", icon=":material/no_accounts:")
                else:
                    st.warning("Completa todos los campos.")

    with tab_registro:
        with st.container(border=True):
            st.subheader("Nuevo Usuario")
            reg_username = st.text_input("Nombre de usuario deseado", key="reg_user")
            reg_password = st.text_input("Contraseña segura", type="password", key="reg_pass")
            
            if st.button("Registrar y configurar 2FA", type="primary", use_container_width=True, icon=":material/how_to_reg:"):
                if reg_username and reg_password:
                    # Generamos una semilla secreta (Base32) exclusiva para este usuario
                    new_secret = pyotp.random_base32()
                    
                    if create_user(reg_username, reg_password, new_secret):
                        st.success("¡Cuenta creada!", icon=":material/check_circle:")
                        st.info("Escanea el código QR con tu app de autenticación.")
                        
                        # Generamos la URL de aprovisionamiento que las apps de Authenticator entienden
                        totp = pyotp.TOTP(new_secret)
                        uri = totp.provisioning_uri(name=reg_username, issuer_name="Mi App Segura")
                        st.code(uri, language=None)  # Mostramos la URL para referencia (opcional)
                        # Generamos el código QR a partir de la URL y lo almacenamos en memoria (Buffer)
                        qr = qrcode.make(uri)
                        buf = BytesIO()
                        qr.save(buf, format="PNG")
                        
                        col_qr, col_txt = st.columns([1, 1.2])
                        with col_qr:
                            # Mostramos el QR desde la memoria
                            st.image(buf.getvalue(), caption="Código QR", use_container_width=True)
                        with col_txt:
                            st.markdown("**Configuración Manual**")
                            st.caption("Usa este secreto si no puedes escanear:")
                            st.code(new_secret, language=None)
                            st.warning("Guarda el secreto en un lugar seguro.")
                    else:
                        st.error("El nombre de usuario ya existe.")
                else:
                    st.warning("Completa los datos de registro.")