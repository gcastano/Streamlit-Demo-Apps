import streamlit as st
import humanize # https://python-humanize.readthedocs.io/en/latest/
from millify import millify # https://github.com/azaitsev/millify
from datetime import date, datetime
from streamlit_date_picker import date_picker, PickerType
import locale



hoy = date.today()

# Definimos los parámetros de configuración de la aplicación
st.set_page_config(
    page_title="Ejemplos Humanizando valores",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.header('Ejemplo de humanización de valores y fechas')
parIdioma = st.radio('Idioma',options=['Inglés','Español'],index=0,horizontal=True)
idiomaValor = 'en'
if parIdioma == 'Español':    
    _t = humanize.i18n.activate("es_ES") # Cambiamos a español para Humanize
    locale.setlocale(locale.LC_ALL,'es_ES.UTF-8') # Cambiamos a español para Python
    idiomaValor = 'es'

def human_format(num,lang='en'):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    if lang == 'es':        
        if magnitude  in [3,5,7]:
           num=num*1000 
        valueScale =['', 'K', 'M', 'M', 'B','B','T','T']
    else:        
        valueScale = ['', 'K', 'M', 'B', 'T']
    return '{} {}'.format('{:,.1f}'.format(num).rstrip('0').rstrip('.'),valueScale[magnitude])
st.divider()
st.subheader('Humanizando :blue[valores numéricos]')
parValor = st.number_input('Número')

c1,c2,c3,c4=st.columns(4)
with c1:
    st.subheader('Formatos nativos')
    st.metric('Valor Original',parValor)
    st.metric('Valor Formato',f'{parValor:,.0f}')
with c2:
    st.subheader('Formatos Humanize')
    st.metric('Valor intcomma',humanize.intcomma(parValor))
    st.metric('Valor intcomma decimales',humanize.intcomma(parValor,2))
    st.metric('Valor intword',humanize.intword(parValor))
with c3:
    st.subheader('Formatos Milify')
    st.metric('Valor millify simple',millify(parValor))
    st.metric('Valor millify con decimales',millify(parValor,2))
with c4:
    st.subheader('Formatos función Python')
    st.metric('Valor',human_format(parValor,idiomaValor))
st.divider()
st.subheader('Humanizando :green[Fechas]')
parFecha = st.date_input('Fecha hora')

if parFecha >= hoy:
    c1,c2=st.columns(2)    
    duracionFecha=None
else:
    duracionFecha = hoy-parFecha
    c1,c2,c3=st.columns(3)
with c1:
    st.subheader('Formatos nativos de fecha con strftime')
    st.metric('Valor formato base',parFecha.strftime("%d/%m/%Y"))
    st.metric('Valor con nombre mes resumido',parFecha.strftime("%b %d, %Y"))
    st.metric('Valor con mes completo',parFecha.strftime("%B %d, %Y"))
    st.metric('Valor con día y mes resumido',parFecha.strftime("%a %b %d, %Y"))
    st.metric('Valor con día y mes completo',parFecha.strftime("%A %B %d, %Y"))
with c2:
    st.subheader('Formatos Humanize')
    st.metric('Valor naturaldate',humanize.naturaldate(parFecha))
    st.metric('Valor naturalday',humanize.naturalday(parFecha,'%b %d %Y'))
if duracionFecha:
    with c3:
        st.subheader('Formatos Humanize duración')
        st.metric('Valor naturaldelta',humanize.naturaldelta(duracionFecha))
        st.metric('Valor precisedelta',humanize.precisedelta(duracionFecha,format='%0.2f'))
st.divider()
st.subheader('Humanizando :orange[Horas]')
parFechaHora = date_picker(picker_type=PickerType.time, value=datetime.now(), key='date_picker')
parFechaHora=datetime.strptime(parFechaHora, '%Y-%m-%d %H:%M:%S')
c1,c2=st.columns(2)
with c1:
    st.subheader('Formatos nativos de fecha')
    st.metric('Valor Horas 24H',parFechaHora.strftime("%d/%m/%Y %H:%M:%S"))
    st.metric('Valor Horas am/pm',parFechaHora.strftime("%b %d, %Y %I:%M %p"))
with c2:
    st.subheader('Formatos Humanize')
    st.metric('Valor naturaltime',humanize.naturaltime(parFechaHora))
    st.metric('Valor precisedelta simple',humanize.precisedelta(parFechaHora,format='%0.2f'))
    st.metric('Valor precisedelta sin segundos',humanize.precisedelta(parFechaHora,format='%0.2f',minimum_unit='minutes'))
    
