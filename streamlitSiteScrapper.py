import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

st.set_page_config(
    page_title="Website Scraper",
    page_icon="💻",    
    initial_sidebar_state="expanded"
)

# Extrae el texto de una página web
def extraerTextoDeURL(url):
    urlOrigen = requests.get(url)
    soup = BeautifulSoup(urlOrigen.content,"html.parser")
    return soup.get_text()

# Convierte un dataframe a CSV
def convertir_df_to_csv(df):
    return df.to_csv(index=False).encode("utf-8")

# Función que procesa una URL y llena un dataframe
def procesarURLDataFrame(url,nivelMaximo):
    """Procesa una URL y llena un dataframe con los textos
    Args:
        url (_type_): Enlace que se desea analizar
        nivelMaximo (_type_): Nivel máximo del nivel de análisis
    """        
    global df
    baseUrl='/'.join(url.split('/')[0:3])        
    source_url = requests.get(url)
    soup = BeautifulSoup(source_url.content,"html.parser")
    for link in soup.find_all('a',href=True):        
        urlActual=link.get('href')            
        if "?" in urlActual:
            urlActual= urlActual.split("?")[0]
        elif "#" in urlActual:
            urlActual= urlActual.split("#")[0]
        if (baseUrl not in urlActual and "http" in urlActual) or len(urlActual)<=1 or urlActual[-4:] in ['.jpg','.svg','.png']:
            continue
        elif urlActual[0]=='/':
            urlSitio = baseUrl + urlActual
        else:
            urlSitio=urlActual
        try:
            if len(links) >=100:
                return
            if urlSitio not in links:                                                                            
                textoSitio = extraerTextoDeURL(urlSitio).strip()                
                links.append(urlSitio)
                if "404" not in textoSitio:
                    dfNuevo = pd.DataFrame({'link':[urlSitio],'text':[textoSitio]})                        
                    df = pd.concat([df,dfNuevo])
                    nivelActual = len(urlSitio.split('/')) - len(urlSitio.split('/')[0:3])                    
                    if nivelActual <= nivelMaximo:
                        st.info(f'Procesando: {urlSitio} Nivel: {nivelActual}')                            
                        procesarURLDataFrame(urlSitio,nivelMaximo)
                    else:
                        st.warning(f'Omitido: {urlSitio} Nivel: {nivelActual}')
                else:
                    dfNuevo = pd.DataFrame({'link':[urlSitio],'text':['']})
                    df = pd.concat([df,dfNuevo])
                    st.error(f'No encontrado: {urlSitio} en Sitio: {url}')
        except Exception as e:
            st.error(f'Error: {e}')

st.header('Website scraper 💻')
parURL= st.text_input("Sitio web a procesar")
parNivelMaximo= st.number_input("Niveles de análisis",value=2,min_value=1)
btnIniciar=st.button("Iniciar",type="primary")

if len(parURL)>0 and btnIniciar:

    df = pd.DataFrame()
    links = []
    
    with st.status(f"Procesando sitio **{parURL}**") as status:
        with st.container(height=600):
            procesarURLDataFrame(parURL, parNivelMaximo)
        status.update(label="Sitio procesado!", state="complete", expanded=False)

    csv = convertir_df_to_csv(df)

    st.download_button(
        label="Bajar datos como CSV",
        data=csv,
        file_name="site_scrapping.csv",
        mime="text/csv",
    )
    st.dataframe(df)
    