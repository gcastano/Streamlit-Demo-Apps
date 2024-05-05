import streamlit as st
import pandas as pd
import numpy as np
import sqlalchemy as sa
import psycopg2
from sqlalchemy.engine import URL
import plotly.express as px

st.set_page_config(
    page_title="Demo Conexión Streamlit - Postgres Database",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data(ttl=600)
def cargarDatos(queryDatos):
    conString=st.secrets["conString"]    
    engine = sa.create_engine(conString)
        
    dfDatos = pd.read_sql_query(queryDatos, engine)    
    return dfDatos

def ejecutarComandos(query):
    conString=st.secrets["conString"]    
    engine = sa.create_engine(conString)
    engine.execute(query)    
        
    


dfDatos = cargarDatos('select * from tabla')
st.dataframe(dfDatos)

# fig= px.bar(dfDatos.sort_values(by='EPI Score',ascending=False).head(10),x='EPI Score',y='Country', color='Country')

# st.plotly_chart(fig,use_container_width=True)

