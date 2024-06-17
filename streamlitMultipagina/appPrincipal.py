import streamlit as st
import utilidades as util
st.header('Página principal')

util.generarMenu()
btnPaginaA = st.button('Ir a Página A')
btnPaginaB = st.button('Ir a Página B')

if btnPaginaA:
    st.switch_page('pages/1_pagina_A.py')

if btnPaginaB:
    st.switch_page('pages/2_pagina_B.py')
