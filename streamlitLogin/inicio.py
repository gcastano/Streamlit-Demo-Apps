import streamlit as st
import login as login

st.header('Página :orange[principal]')
login.generarLogin()
if 'usuario' in st.session_state:
    st.subheader('Información página principal')