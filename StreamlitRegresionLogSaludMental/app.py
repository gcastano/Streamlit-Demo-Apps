import streamlit as st

pages = [    
        st.Page("uso_modelo.py", title="Evaluar Salud Mental", icon="🧠"),
        st.Page("entrenamiento_modelo.py", title="Entrenar Modelo", icon="⚙️"),    
]

pg = st.navigation(pages,position="top")
pg.run()