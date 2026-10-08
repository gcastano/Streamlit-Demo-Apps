import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import joblib
import io

# =========================================================
# IMPORTACIÓN DE LIBRERÍAS DE SKTIME (Series de Tiempo)
# =========================================================
# sktime ofrece una interfaz estandarizada (similar a scikit-learn) para series de tiempo.
from sktime.forecasting.naive import NaiveForecaster
from sktime.forecasting.exp_smoothing import ExponentialSmoothing
from sktime.forecasting.ets import AutoETS
from sktime.forecasting.arima import AutoARIMA
from sktime.forecasting.theta import ThetaForecaster
from sktime.forecasting.trend import PolynomialTrendForecaster
from sktime.forecasting.compose import make_reduction

# Scikit-learn (Usaremos Random Forest adaptándolo a series temporales a través de sktime)
from sklearn.ensemble import RandomForestRegressor

# Métricas de evaluación para entender qué tan bien predijo nuestro modelo
from sktime.performance_metrics.forecasting import mean_absolute_percentage_error, mean_squared_error, mean_absolute_error

import warnings
warnings.filterwarnings("ignore") # Para evitar que advertencias matemáticas ensucien la terminal

# =========================================================
# CONFIGURACIÓN DE LA PÁGINA (STREAMLIT)
# =========================================================
# st.set_page_config siempre debe ser el primer comando de Streamlit. 
# Permite definir el título de la pestaña, ícono y si el layout ocupará todo el ancho de la pantalla ("wide").
st.set_page_config(page_title="Pronóstico de Series de Tiempo", layout="wide", page_icon=":material/timeline:")

# st.title imprime un título principal (H1) en la aplicación web.
st.title(":material/timeline: Aplicación de Aprendizaje: Pronóstico de Series de Tiempo")

# Diccionario utilizado más adelante para mostrar descripciones en la interfaz de usuario.
MODEL_DESCRIPTIONS = {
    "Ingenuo (Naive)": "Útil como línea base (baseline). Asume que el futuro será igual al último valor observado. Se usa principalmente para comprobar si el esfuerzo de aplicar modelos más complejos realmente aporta valor.",
    "Tendencia Polinómica": "Modela la tendencia general (creciente o decreciente) trazando una línea matemática suave. Excelente para series donde lo más importante es el crecimiento a largo plazo sin importar los picos cortos.",
    "Suavización Exponencial": "Da mayor peso e importancia a los datos más recientes. Excelente para series donde el pasado lejano pierde relevancia y se esperan cambios graduales.",
    "Auto ETS": "Busca automáticamente la mejor combinación de los componentes de Error, Tendencia y Estacionalidad. Es un método muy robusto y estándar en la industria para pronósticos de negocios.",
    "Auto ARIMA": "Clásico modelo estadístico que se basa en la correlación de los datos consigo mismos en el pasado. Ideal para series con patrones estadísticos estables a lo largo del tiempo.",
    "Theta": "Método muy rápido y eficiente que destacó por su excelente desempeño en competencias mundiales de predicción (M3). Funciona de maravilla en series de ventas o finanzas con tendencia y estacionalidad.",
    "Bosques Aleatorios (Machine Learning)": "Utiliza un algoritmo de Machine Learning adaptado a series temporales (Random Forest). Es muy poderoso para encontrar relaciones complejas no lineales, pero requiere más datos históricos para aprender bien sin sobreajustarse."
}

# st.tabs permite organizar el contenido en pestañas horizontales para no saturar la vista.
tab1, tab2 = st.tabs([":material/model_training: Entrenar y Evaluar Modelos", ":material/upload_file: Cargar Modelo Guardado"])

# Trabajaremos dentro de la primera pestaña
with tab1:
    # st.markdown interpreta texto en formato Markdown (negritas, listas, cursivas, etc.)
    st.markdown("""
    **Paso 1:** Carga tus datos históricos, elige los modelos que quieres aprender a usar y encuentra el mejor para tu serie de tiempo.
    **Paso 2:** Descarga el modelo ganador para usarlo más adelante (en la otra pestaña).
    """)

    # st.file_uploader crea un área para que el usuario arrastre archivos (en este caso csv o excel)
    uploaded_file = st.file_uploader("Carga tu archivo Excel o CSV", type=['csv', 'xlsx'], key="train_file")

    if uploaded_file is not None:
        try:
            # LECTURA DEL ARCHIVO SEGÚN SU EXTENSIÓN
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
                
            st.write("### Vista previa de los datos")
            st.dataframe(df.head()) # st.dataframe muestra tablas interactivas con scroll
            
            st.write("### 1. Configuración de la Serie de Tiempo")
            # st.columns divide el espacio horizontalmente para colocar widgets lado a lado
            col1, col2, col3 = st.columns(3)
            with col1:
                # st.selectbox crea un menú desplegable. Aquí el usuario escoge qué columna es la fecha.
                date_col = st.selectbox("Selecciona la columna de Fecha", df.columns, key="train_date")
            with col2:
                # El usuario escoge qué columna numérica es la que desea predecir.
                val_col = st.selectbox("Selecciona la columna de Valor a predecir", df.columns, key="train_val")
            with col3:
                # st.number_input crea una caja numérica. La estacionalidad (sp) indica cada cuántos periodos el ciclo se repite.
                sp = st.number_input(
                    "Estacionalidad (Periodos por ciclo)", 
                    min_value=1, max_value=365, value=1,
                    help="""
**¿Qué número poner aquí?**
Representa cuántas filas de tus datos forman un ciclo completo que se repite.
- **Datos Mensuales (ciclo anual):** Usa `12`.
- **Datos Trimestrales (ciclo anual):** Usa `4`.
- **Datos Diarios:** Se recomienda usar `7` para capturar el fuerte patrón de Lunes a Domingo. 

⚠️ *¡Precaución!* Aunque matemáticamente un año tiene 365 días, **NO se recomienda poner 365**. Modelos clásicos como ARIMA o ETS exigen cálculos inmensos para esa cifra y podrían fallar o congelar la computadora. Para datos diarios, usar 7 es el estándar práctico.
"""
                )
                
            horizon = st.number_input("Horizonte de predicción (¿Cuántos periodos a futuro quieres estimar?)", min_value=1, max_value=365, value=12)
            
            st.write("### 2. Selección de Modelos a Entrenar")
            # st.expander es un panel plegable. Ideal para ocultar texto largo y explicativo.
            with st.expander(":material/menu_book: Leer descripción de los casos de uso de cada modelo", expanded=True):
                for m_name, desc in MODEL_DESCRIPTIONS.items():
                    st.markdown(f"- **{m_name}:** {desc}")
                    
            # st.multiselect permite elegir múltiples opciones. Por defecto las marcamos todas.
            selected_models_names = st.multiselect(
                "Selecciona los modelos que deseas entrenar y comparar:",
                options=list(MODEL_DESCRIPTIONS.keys()),
                default=list(MODEL_DESCRIPTIONS.keys())
            )
            
            # El código dentro del "if st.button" SOLO se ejecuta cuando el usuario hace clic en el botón.
            if st.button(":material/play_arrow: Entrenar y Proyectar", type="primary"):
                if not selected_models_names:
                    # st.error muestra un mensaje rojo de alerta.
                    st.error(":material/error: Por favor, selecciona al menos un modelo de la lista para poder entrenar.")
                else:
                    # st.spinner muestra un "cargando..." giratorio mientras ocurre un proceso pesado.
                    with st.spinner("Procesando datos y entrenando modelos seleccionados..."):
                        
                        # PREPARACIÓN DE LOS DATOS PARA SERIES DE TIEMPO
                        df_ts = df.copy()
                        df_ts[date_col] = pd.to_datetime(df_ts[date_col]) # Aseguramos que sea formato Fecha
                        df_ts = df_ts.sort_values(date_col) # Es CRÍTICO que el historial esté ordenado cronológicamente
                        df_ts.set_index(date_col, inplace=True) # La fecha debe ser el índice del DataFrame
                        
                        # sktime prefiere que el índice tenga una "frecuencia" (ej. diaria, mensual).
                        try:
                            df_ts.index = df_ts.index.to_period(freq=pd.infer_freq(df_ts.index))
                        except:
                            pass # Si pandas no logra detectar la frecuencia automáticamente, lo dejamos así.
                        
                        y = df_ts[val_col] # Esta es nuestra Serie (target variable)
                        
                        # VALIDACIÓN DE DATOS
                        if len(y) <= horizon * 2:
                            st.error(f":material/error: No hay suficientes datos. Tienes {len(y)} registros, y para evaluar un horizonte de {horizon} de forma segura, necesitas al menos el doble de historial.")
                        else:
                            # SPLIT DE DATOS (EVALUACIÓN)
                            # Para saber si un modelo es bueno, no usamos todo el historial para entrenar.
                            # Cortamos el final de la serie (equivalente al horizonte) y fingimos que no lo conocemos (y_test).
                            y_train = y.iloc[:-horizon] # Desde el principio hasta antes de los últimos "horizon" registros
                            y_test = y.iloc[-horizon:]  # Solo los últimos "horizon" registros
                            
                            # DICCIONARIO DE MODELOS A EVALUAR
                            # Cada modelo recibe los parámetros necesarios para adaptarlo a la estacionalidad seleccionada (sp).
                            available_models = {
                                # Usa el último valor observado; sp indica la frecuencia de la estacionalidad.
                                "Ingenuo (Naive)": NaiveForecaster(strategy="last", sp=sp),
                                # Ajusta una recta lineal a los datos y utiliza la tendencia polinómica.
                                "Tendencia Polinómica": PolynomialTrendForecaster(degree=1),
                                # Suaviza los datos con un modelo exponencial; sp se aplica cuando es mayor que 1.
                                "Suavización Exponencial": ExponentialSmoothing(sp=sp) if sp > 1 else ExponentialSmoothing(),
                                # Selecciona automáticamente el modelo ETS y usa sp como frecuencia estacional; n_jobs habilita el procesamiento paralelo.
                                "Auto ETS": AutoETS(auto=True, sp=sp, n_jobs=-1),
                                # Selecciona automáticamente ARIMA y utiliza sp como frecuencia estacional; se ocultan las advertencias de ajuste.
                                # ARIMA combina autorregresión, diferenciación y media móvil.
                                "Auto ARIMA": AutoARIMA(sp=sp, suppress_warnings=True),
                                # Aplica una descomposición Theta con la frecuencia estacional seleccionada; si sp es 1, usa una frecuencia básica.
                                "Theta": ThetaForecaster(sp=sp if sp > 1 else 1),
                                # make_reduction convierte Random Forest en un modelo recursivo; window_length usa sp o 3 como historial mínimo.
                                "Bosques Aleatorios (Machine Learning)": make_reduction(RandomForestRegressor(n_estimators=50, random_state=42), window_length=sp if sp > 1 else 3, strategy="recursive")
                            }
                            
                            # Filtramos el diccionario dejando solo los que eligió el usuario en el multiselect
                            models_to_train = {k: available_models[k] for k in selected_models_names}
                            
                            # Variables para almacenar resultados
                            results = []
                            projections = {}
                            trained_models = {}
                            failed_models = []
                            
                            progress_bar = st.progress(0) # Barra de progreso visual
                            status_text = st.empty() # st.empty reserva un espacio vacío que podemos sobreescribir luego
                            
                            # BUCLE PRINCIPAL DE ENTRENAMIENTO Y EVALUACIÓN
                            for i, (name, model) in enumerate(models_to_train.items()):
                                status_text.info(f":material/sync: Entrenando y evaluando modelo: **{name}**...")
                                try:
                                    # 1. EVALUACIÓN DE EFICACIA
                                    model.fit(y_train) # Entrenamos con la parte "vieja" de los datos
                                    fh = np.arange(1, horizon + 1) # Creamos el Forecasting Horizon (fh), p.ej: [1,2,3...12]
                                    y_pred = model.predict(fh=fh) # Le pedimos al modelo predecir el horizonte de prueba
                                    
                                    # Calculamos qué tan diferente fue lo que predijo (y_pred) vs la realidad (y_test)
                                    mape = mean_absolute_percentage_error(y_test, y_pred)
                                    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                                    mae = mean_absolute_error(y_test, y_pred)
                                    
                                    results.append({
                                        "Modelo": name,
                                        "MAPE (%)": mape * 100,
                                        "RMSE": rmse,
                                        "MAE": mae
                                    })
                                    
                                    # 2. PROYECCIÓN REAL AL FUTURO
                                    # Ya evaluamos qué tan bueno es. Ahora, para que el usuario lo aproveche,
                                    # lo clonamos y lo entrenamos pero esta vez con TODOS LOS DATOS (incluyendo y_test).
                                    model_full = model.clone()
                                    model_full.fit(y)
                                    y_future = model_full.predict(fh=fh) # Esta vez predice hacia el futuro desconocido
                                    
                                    projections[name] = y_future # Guardamos su proyección
                                    trained_models[name] = model_full # Guardamos el modelo entrenado en la memoria
                                    
                                except Exception as e:
                                    failed_models.append((name, str(e))) # Si las matemáticas del modelo explotan (ej. matriz singular), lo atrapamos.
                                    
                                # Actualizar la barra de progreso
                                progress_bar.progress((i + 1) / len(models_to_train))
                                
                            status_text.success(":material/check_circle: ¡Entrenamiento completado!")
                            
                            if failed_models:
                                st.error(":material/warning: **Atención:** Algunos modelos no pudieron ejecutarse con tus datos:")
                                for fm_name, fm_err in failed_models:
                                    st.warning(f"- **{fm_name}**: Falló por problemas matemáticos o falta de datos suficientes para este algoritmo. (Detalle: {fm_err})")
                                
                            if results:
                                # Uso de SESSION STATE de Streamlit
                                # En Streamlit, cuando haces click en un botón (ej. "Descargar"), el código se vuelve a ejecutar entero desde la línea 1.
                                # Todo lo que esté dentro de este "if st.button" se borrará. Para que los resultados sobrevivan, los guardamos en st.session_state
                                st.session_state['trained_models'] = trained_models
                                st.session_state['results_df'] = pd.DataFrame(results)
                                st.session_state['projections'] = projections
                                st.session_state['historical_y'] = y
                                st.session_state['horizon'] = horizon
                                st.session_state['best_model_name'] = pd.DataFrame(results).loc[pd.DataFrame(results)['MAPE (%)'].idxmin(), 'Modelo']

            # Este bloque se ejecuta si tenemos resultados guardados en la memoria, ya sea del botón recién presionado
            # o de una recarga de la página donde session_state los ha preservado.
            if 'results_df' in st.session_state and not st.session_state['results_df'].empty:
                st.write("---")
                st.write("### :material/bar_chart: Métricas de Evaluación")
                
                with st.expander(":material/psychology: ¿Cómo se evalúan y eligen estos modelos?", expanded=True):
                    st.markdown("""
                    Para evaluar los modelos, **ocultamos** el final de tus datos históricos (equivalente al horizonte que elegiste) y le pedimos al modelo que "prediga el pasado reciente". Luego comparamos qué tan cerca estuvo de la realidad.
                    
                    - **MAPE (%) - Error Porcentual Absoluto Medio:** Es la métrica más fácil de entender para negocios. Te dice en promedio qué porcentaje te estás equivocando. (Ej: Un MAPE del 5% significa que las predicciones varían un 5% de la realidad). **¡La aplicación usa esta métrica para recomendar al ganador!**
                    - **MAE - Error Absoluto Medio:** Te dice en tus mismas unidades (ej: dólares, ventas, pasajeros) cuánto se equivocó en promedio.
                    - **RMSE - Raíz del Error Cuadrático Medio:** Es similar al MAE, pero penaliza mucho más fuerte los **errores grandes**. Si prefieres un modelo que nunca se equivoque de forma grave, debes fijarte en que el RMSE sea bajo.
                    """)

                # .style.highlight_min pinta de verde los valores más pequeños (mejores) de esas columnas.
                st.dataframe(st.session_state['results_df'].style.highlight_min(subset=['MAPE (%)', 'RMSE', 'MAE'], color='#c1f0c1'))
                
                best_model_name = st.session_state['best_model_name']
                st.success(f":material/emoji_events: **Modelo Recomendado (entre los evaluados exitosos): {best_model_name}**\n\n*(Tiene el menor margen de error porcentual - MAPE)*")
                
                # ==========================================
                # GRAFICANDO CON PLOTLY
                # ==========================================
                st.write("### :material/show_chart: Gráfico de Comparación de Proyecciones")
                fig_comp = go.Figure() # Creamos un lienzo en blanco
                
                y_hist = st.session_state['historical_y']
                # Convertimos los índices (fechas) para que el gráfico las lea bien
                idx_hist = y_hist.index.to_timestamp() if hasattr(y_hist.index, "to_timestamp") else y_hist.index
                
                # Añadimos la línea de datos históricos (color oscuro)
                fig_comp.add_trace(go.Scatter(x=idx_hist, y=y_hist.values, mode='lines', name='Datos Históricos', line=dict(color='#1E293B')))
                
                # Iteramos sobre las proyecciones y añadimos una línea para cada modelo
                for name, y_fut in st.session_state['projections'].items():
                    idx_fut = y_fut.index.to_timestamp() if hasattr(y_fut.index, "to_timestamp") else y_fut.index
                    fig_comp.add_trace(go.Scatter(x=idx_fut, y=y_fut.values, mode='lines', name=f'{name}'))
                    
                # Aplicamos el diseño general del gráfico
                fig_comp.update_layout(title="Comparación de los Modelos Entrenados", xaxis_title="Fecha", yaxis_title="Valor", hovermode="x unified", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                # st.plotly_chart inyecta el gráfico interactivo de plotly a streamlit
                st.plotly_chart(fig_comp, use_container_width=True)

                # ==========================================
                # DETALLES E INTERVALOS DE CONFIANZA
                # ==========================================
                st.write("---")
                st.write("### :material/manage_search: Detalle del Modelo y Rangos de Confianza")
                st.info(":material/info: Selecciona uno de los modelos entrenados para ver su proyección junto a los rangos de confianza al 95%. (Si el modelo lo soporta)")
                
                selected_detail_model = st.selectbox("Selecciona un modelo para visualizar y/o descargar:", list(st.session_state['trained_models'].keys()), index=list(st.session_state['trained_models'].keys()).index(best_model_name))
                
                # Rescatamos el modelo seleccionado
                model_full = st.session_state['trained_models'][selected_detail_model]
                fh_full = np.arange(1, st.session_state['horizon'] + 1)
                y_future_detail = st.session_state['projections'][selected_detail_model]
                idx_fut_detail = y_future_detail.index.to_timestamp() if hasattr(y_future_detail.index, "to_timestamp") else y_future_detail.index
                
                fig_detail = go.Figure()
                fig_detail.add_trace(go.Scatter(x=idx_hist, y=y_hist.values, mode='lines', name='Datos Históricos', line=dict(color='#1E293B')))
                fig_detail.add_trace(go.Scatter(x=idx_fut_detail, y=y_future_detail.values, mode='lines', name=f'Proyección ({selected_detail_model})', line=dict(color='#2563EB')))
                
                try:
                    # model_full.predict_interval calcula las bandas superior e inferior al 95% de confianza estadística
                    pred_int = model_full.predict_interval(fh=fh_full, coverage=0.95)
                    
                    # Extraemos las columnas inferior y superior
                    lower_col = [c for c in pred_int.columns if 'lower' in str(c).lower()][0]
                    upper_col = [c for c in pred_int.columns if 'upper' in str(c).lower()][0]
                    
                    y_lower = pred_int[lower_col]
                    y_upper = pred_int[upper_col]
                    
                    # Para graficar un área sombreada en Plotly, dibujamos desde la línea superior hacia adelante
                    # y luego desde la línea inferior hacia atrás, y rellenamos ("toself").
                    fig_detail.add_trace(go.Scatter(
                        x=np.concatenate([idx_fut_detail, idx_fut_detail[::-1]]),
                        y=np.concatenate([y_upper.values, y_lower.values[::-1]]),
                        fill='toself',
                        fillcolor='rgba(37,99,235,0.2)', # Azul con transparencia
                        line=dict(color='rgba(255,255,255,0)'),
                        hoverinfo="skip",
                        showlegend=True,
                        name='Intervalo de Confianza (95%)'
                    ))
                except Exception as e:
                    # Modelos como Machine Learning por defecto en sktime no tienen intervalos de confianza probabilísticos.
                    st.warning(f":material/warning: El modelo '{selected_detail_model}' no soporta rangos de confianza o hubo un error matemático al calcularlos.")
                
                fig_detail.update_layout(title=f"Proyección y Rangos de Confianza: {selected_detail_model}", xaxis_title="Fecha", yaxis_title="Valor", hovermode="x unified", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_detail, use_container_width=True)

                # ==========================================
                # DESCARGA DEL MODELO
                # ==========================================
                st.write("### :material/save: Guardar Modelo")
                # io.BytesIO permite guardar el archivo temporalmente en la memoria RAM en lugar de crear un archivo en tu disco duro
                buffer = io.BytesIO()
                joblib.dump(st.session_state['trained_models'][selected_detail_model], buffer) # joblib serializa y guarda el modelo entero
                
                # El botón de descarga envía los bytes desde la memoria hacia el navegador del usuario como un archivo .joblib
                st.download_button(
                    label=f":material/download: Descargar modelo '{selected_detail_model}' (.joblib)",
                    data=buffer.getvalue(),
                    file_name=f"modelo_{selected_detail_model.replace(' ', '_').lower()}.joblib",
                    mime="application/octet-stream"
                )

        except Exception as e:
            st.error(f":material/error: Error al procesar: {e}")

# Trabajaremos dentro de la segunda pestaña
with tab2:
    st.markdown("""
    Si ya entrenaste y descargaste un modelo en la pestaña anterior, puedes cargarlo aquí para realizar nuevas proyecciones rápidamente.
    """)
    # Solicitamos un archivo con terminación joblib
    uploaded_model = st.file_uploader("Sube tu archivo de modelo (.joblib)", type=['joblib'])
    
    if uploaded_model is not None:
        try:
            # joblib.load lee el archivo subido y lo vuelve a convertir en el objeto matemático original (AutoARIMA, Theta, etc)
            loaded_model = joblib.load(uploaded_model)
            st.success(":material/check_circle: Modelo cargado exitosamente.")
            
            st.write("### Configuración de la Proyección")
            colA, colB, colC = st.columns(3)
            with colA:
                new_horizon = st.number_input("¿Cuántos periodos a futuro?", min_value=1, max_value=365, value=12, key="load_horizon")
            with colB:
                start_date = st.date_input("Fecha de inicio de la proyección")
            with colC:
                freq_options = {"Diaria": "D", "Semanal": "W", "Mensual (Fin de mes)": "ME", "Anual": "YS"}
                freq_selection = st.selectbox("Frecuencia", list(freq_options.keys()))
                freq_code = freq_options[freq_selection]
            
            if st.button(":material/play_arrow: Proyectar con Modelo Cargado", type="primary"):
                # No necesitamos entrenar (fit) nuevamente porque ya viene entrenado en el .joblib
                fh = np.arange(1, new_horizon + 1)
                y_pred_new = loaded_model.predict(fh=fh) # Predicción directa!
                
                # Asignamos las fechas exactas basadas en la solicitud del usuario
                # Esto es muy útil porque al exportar/importar, a veces se pierde el contexto del calendario original.
                future_dates = pd.date_range(start=start_date, periods=new_horizon, freq=freq_code)
                y_pred_new.index = future_dates
                
                fig2 = go.Figure()
                idx_new = y_pred_new.index # Ya no necesitamos convertir porque son explícitamente DatetimeIndex
                fig2.add_trace(go.Scatter(x=idx_new, y=y_pred_new.values, mode='lines+markers', name='Proyección', line=dict(color='#2563EB')))
                
                # Intentamos graficar la sombra del intervalo de confianza para este modelo pre-entrenado
                try:
                    pred_int = loaded_model.predict_interval(fh=fh, coverage=0.95)
                    pred_int.index = future_dates # También alineamos las fechas del intervalo
                    lower_col = [c for c in pred_int.columns if 'lower' in str(c).lower()][0]
                    upper_col = [c for c in pred_int.columns if 'upper' in str(c).lower()][0]
                    y_lower = pred_int[lower_col]
                    y_upper = pred_int[upper_col]
                    
                    fig2.add_trace(go.Scatter(
                        x=np.concatenate([idx_new, idx_new[::-1]]),
                        y=np.concatenate([y_upper.values, y_lower.values[::-1]]),
                        fill='toself',
                        fillcolor='rgba(37,99,235,0.2)',
                        line=dict(color='rgba(255,255,255,0)'),
                        name='Intervalo de Confianza (95%)'
                    ))
                except:
                    pass

                fig2.update_layout(title="Proyección del Modelo Cargado", xaxis_title="Fecha de Proyección", yaxis_title="Valor", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig2, use_container_width=True)
                
                # pd.DataFrame formatea los resultados para que se muestren en una tabla limpia.
                df_results = pd.DataFrame({"Fecha/Periodo": idx_new.strftime('%Y-%m-%d'), "Valor Proyectado": y_pred_new.values})
                st.dataframe(df_results, hide_index=True) # hide_index=True oculta el número de fila [0,1,2...]
                
        except Exception as e:
            st.error(f":material/error: Error al cargar o utilizar el archivo: {e}")
