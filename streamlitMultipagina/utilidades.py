import streamlit as st

def generarMenu():
    with st.sidebar:
        st.page_link('appPrincipal.py',label="Inicio", icon="🏚️")
        st.page_link('pages/1_pagina_A.py',label="Tablero A", icon="📄")
        st.page_link('pages/2_pagina_B.py',label="Tablero B", icon="📄")