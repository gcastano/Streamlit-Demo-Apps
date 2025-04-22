import streamlit as st

st.html('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css" integrity="sha512-Evv84Mr4kqVGRNSgIGL/F/aIDqQb7xQ2vcrdIwxfjThSH8CSR7PBEakCr51Ck+w+/U6swU2Im1vVX0SVk9ABhg==" crossorigin="anonymous" referrerpolicy="no-referrer" />')
st.html('<script src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/js/all.min.js" integrity="sha512-b+nQTCdtTBIRIbraqNEwsjB6UvL3UEMkXnhzd8awtCYh0Kcsjl9uEgwVFVbhoj3uu1DO1ZMacNvLoyJJiNfcvg==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>')
def metricaIcono(mensajePrincipal,mensajeSecundario,icono):
    with st.container(border=True):
        col1, col2 = st.columns([2, 8])
        with col1:
            # st.write(f"# :material/{icono}:")
            st.html('<span style="font-size: 3em; color: Tomato;"><i class="fa-solid fa-camera"></i></span>')
        with col2:
            st.markdown(f"<h4 style='text-align: left; color: black;'>{mensajeSecundario}</h4>", unsafe_allow_html=True)
            st.markdown(f"<h5 style='text-align: left; color: black;'>{mensajePrincipal}</h5>", unsafe_allow_html=True)
            # st.html(f"**{mensajePrincipal}**")
            

cols = st.columns(3)
with cols[0]:
    metricaIcono("Total de ventas", "1000", "attach_money")