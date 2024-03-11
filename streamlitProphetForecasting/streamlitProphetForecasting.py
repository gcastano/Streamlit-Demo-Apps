import streamlit as st
import pandas as pd
from prophet import Prophet #pip install prophet
import plotly.express as px

# Definimos los parámetros de configuración de la aplicación
st.set_page_config(
    page_title="Predicción de series de tiempo con Prophet", #Título de la página
    page_icon="📊", # Ícono
    layout="wide", # Forma de layout ancho o compacto
    initial_sidebar_state="expanded" # Definimos si el sidebar aparece expandido o colapsado
)

st.header('Predicción de series de tiempo con Prophet')
st.warning('Se debe cargar un archivo csv cuya primera columna sea una fecha y la segunda sea un valor a predecir')
# declaramos el control para cargar archivos
archivo_cargado = st.file_uploader("Elige un archivo",type='csv')
# Si existe un archivo cargado ejecutamos el código
if archivo_cargado is not None:   
    st.toast(archivo_cargado.name,icon='📄')
    # Se puede cargar con pandas si se tiene detectado el tipo de archivo
    df = pd.read_csv(archivo_cargado)
    # Definimos las frecuencias del control
    frequencias=['Día', 'Semana', 'Mes', 'Año']
    # Definimos los códigos de cada frecuencia
    frequenciasCodigo =['D', 'W', 'M', 'Y']
    # Definimos las columnas
    c1,c2= st.columns([30,70])
    with c1:
        # Mostramos el dataframe
        st.dataframe(df,use_container_width=True)
    with c2:
        # Mostramos el control de selección de frecuencias
        parFrecuencia=st.selectbox('Frecuencia de los datos',options=['Día', 'Semana', 'Mes', 'Año'])
        # Mostramos el control para seleccionar el horizonte de predicción
        parPeriodosFuturos = st.slider('Periodos a predecir',5,300,5)
        # Botón para ejecutar la predicción
        btnEjecutarForecast= st.button('Ejecutar predicción',type='primary')
    
    #Cuando se presione el botón ejecutamos el código
    if btnEjecutarForecast:
        # Renombramos las columnas a como lo existe Prophet ds = Fecha, y= Valor
        df.columns=['ds','y']
        # Cargamos el Prophet
        m = Prophet()
        # Ejecutamos el modelo
        m.fit(df)
        # Detectamos la frecuencia entregada
        frequencia=frequenciasCodigo[frequencias.index(parFrecuencia)]
        # Generamos la predicción de acuerdo a la frecuencia y los periodos solicitados
        future = m.make_future_dataframe(periods=parPeriodosFuturos,freq=frequencia)
        # Guardamos la predicción
        forecast = m.predict(future)
        # Sacamos a parte solo los valores de la predicción
        dfPrediccion=forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(parPeriodosFuturos)
        # Generamos la gráfica de modelo Prophet
        fig1 = m.plot(forecast)
        # Generamos tabs o pestañas para mostrar gráficos y datos
        tab1,tab2 =st.tabs(['Resultado','Gráfico Prophet'])
        # Asignamos al dataset df una columna Tipo que indique los datos reales
        df['Tipo']= 'Real' 
        # Asignamos al dataset dfPredicción una columna Tipo que indique los datos de Predicción
        dfPrediccion['Tipo']= 'Predicción' 
        # Renombramos la columna yhat que retorna el modelo como y
        dfPrediccion=dfPrediccion.rename(columns={'yhat':'y'})
        # Concatenamos los datos reales y la predicción
        dfResultado = pd.concat([df.sort_values(by='ds'),dfPrediccion[['ds','y','Tipo']]])
        with tab1:
            # En el primer tab mostramos la predicción completa
            c1,c2 = st.columns([30,70])
            with c1:
                st.dataframe(dfResultado)
                # Convertimos el dataframe a CSV y lo guardamos en una variable
                ArchivoCSV=dfResultado.to_csv(index=False).encode('utf-8')
                # Creamos el nombre del nuevo archivo
                archivoNuevo=archivo_cargado.name
                archivoNuevo = f'prediccion_{archivoNuevo}'
                # Usamos el botón de descarga de Streamlit
                st.download_button(
                    label="Descargar resultado como CSV", #Etiqueta del botón
                    data=ArchivoCSV, #Datos a descargar
                    file_name=archivoNuevo, #Nombre del archivo
                    mime='text/csv', # Formato a descargar
                    type='primary' # Tipo de botón
                )
            with c2:
                # Mostramos el gráfico de los resutados de la predicción
                fig = px.line(dfResultado,x='ds',y='y',color='Tipo')
                st.plotly_chart(fig,use_container_width=True)
        with tab2:
            # En el tab2, mostramos la gráfica que genera Prophet
            st.write(fig1)
