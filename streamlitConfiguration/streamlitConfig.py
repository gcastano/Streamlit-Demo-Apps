import streamlit as st
from configparser import ConfigParser #https://docs.python.org/3/library/configparser.html

# Título de la sección
st.header("Leyendo archivos de configuración")

# --- Usando secrets.toml ---

# Subtítulo de la sección
st.subheader("Usando :red[.streamlit/secrets.toml]",divider="red")

# Accediendo a las variables en secrets.toml
API = st.secrets["API"]
servidor = st.secrets["baseDedatos"]["servidor"]
puerto = st.secrets["baseDedatos"]["puerto"]
pruebas= st.secrets.Pruebas #No permite datos booleanos en las variables
# Mostrando las variables y sus tipos
st.write(f"**API**: {API} - {type(API)}")
st.write(f"**Servidor**: {servidor} - {type(servidor)}")
st.write(f"**Puerto**: {puerto} - {type(puerto)}")
st.write(f"**Pruebas**: {pruebas} - {type(pruebas)}")

# --- Usando ConfigParser ---

st.subheader("Usando :blue[ConfigParser]",divider="blue")

# Creando un objeto ConfigParser
config = ConfigParser()

# Selector de archivos de configuración
parArchivo = st.selectbox("Archivo de configuración", options=["sampleconfig1.ini", "sampleconfig2.ini"])

# Leyendo el archivo de configuración seleccionado
config.read(parArchivo)

# Accediendo a las variables en el archivo .ini
API = config["APIAccess"]["API"]
servidor = config["baseDedatos"]["servidor"]
puerto = config["baseDedatos"]["puerto"]
servidorPruebas = config["baseDedatos"]["servidorPruebas"]

# Mostrando las variables y sus tipos
st.write(f"**API**: {API} - {type(API)}")
st.write(f"**Servidor**: {servidor} - {type(servidor)}")
st.write(f"**Puerto**: {puerto} - {type(puerto)}")

# Cargando un parámetro con tipo de datos específico
st.write("#### Cargando un parámetro con tipo de datos")
# ConfigParser permite obtener valores como enteros, flotantes o booleanos
puerto = config.getint("baseDedatos", "puerto")
st.write(f"**Puerto**: {puerto} - {type(puerto)}")

servidorPruebas = config.getboolean("baseDedatos", "servidorPruebas")
st.write(f"**Servidor Pruebas**: {servidorPruebas} - {type(servidorPruebas)}")

# --- Modificando archivos de configuración ---

st.subheader(f"Modificando archivos de configuración :red-background[*{parArchivo}*]",divider=True)

# Obteniendo valores del archivo de configuración para mostrarlos en los inputs
usuario = config["baseDedatos"]["usuario"]
password = config["baseDedatos"]["password"]

# Inputs para modificar las variables
parServidor = st.text_input("Servidor", value=servidor)
parUsuario = st.text_input("Usuario", value=usuario)
parPassword = st.text_input("Password", value=password)

# Actualizando las variables en el objeto config
config["baseDedatos"]["usuario"] = parUsuario
config["baseDedatos"]["password"] = parPassword
config["baseDedatos"]["servidor"] = parServidor

# Botón para guardar los cambios
btnGuardar = st.button("Guardar configuración")

# Guardando la configuración si se presiona el botón
if btnGuardar:
    with open(parArchivo, 'w') as configfile:
        config.write(configfile)
    st.toast("Configuración guardada", icon=":material/check:")