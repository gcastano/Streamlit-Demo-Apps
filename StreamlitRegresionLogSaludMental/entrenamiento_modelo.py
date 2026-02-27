# ==========================================
# 📦 INSTALACIÓN DE LIBRERÍAS NECESARIAS
# Ejecuta este comando en tu terminal antes de empezar:
# pip install streamlit pandas scikit-learn joblib
# ==========================================

import streamlit as st  # Librería para crear aplicaciones web de ciencia de datos rápidamente.
import pandas as pd  # La herramienta principal para manipulación y análisis de datos (DataFrames).
from sklearn.model_selection import train_test_split  # Para dividir datos en entrenamiento y prueba.
from sklearn.preprocessing import StandardScaler, OneHotEncoder  # Para escalar números y convertir texto a números.
from sklearn.impute import SimpleImputer  # Para rellenar datos faltantes (nulos).
from sklearn.compose import ColumnTransformer  # Para aplicar diferentes preprocesamientos a diferentes columnas.
from sklearn.linear_model import LogisticRegression  # El algoritmo de Machine Learning que usaremos.
from sklearn.pipeline import Pipeline  # Para encadenar pasos (limpieza -> procesamiento -> modelo) en un solo objeto.
from sklearn.metrics import accuracy_score, classification_report  # Para medir qué tan bueno es el modelo.
import joblib  # Para guardar el modelo entrenado en un archivo y usarlo después.

# Configuración inicial de la página de Streamlit
st.set_page_config(page_title="Entrenamiento Modelo Salud Mental", page_icon="⚙️", layout="wide")

st.title("⚙️ Entrenamiento del Modelo de Salud Mental")
st.write("""
Sube tu dataset (CSV) para entrenar el modelo de Regresión Logística. 
El sistema procesará los datos, entrenará la IA y te dará un reporte sobre su viabilidad.
""")

# 1. Cargar el dataset
# st.file_uploader permite al usuario subir archivos desde su navegador.
archivo_subido = st.file_uploader("Sube el archivo 'Mental_Health_Lifestyle_Dataset.csv'", type=["csv"])

if archivo_subido is not None:
    # ---------------------------------------------------------
    # PANDAS: Lectura de datos
    # `pd.read_csv` convierte el archivo CSV en un DataFrame de Pandas.
    # ---------------------------------------------------------
    df = pd.read_csv(archivo_subido)    
    st.success("¡Archivo cargado correctamente!")
    
    with st.expander("Ver vista previa de los datos"):
        # PANDAS: Visualización preliminar
        # Rellenamos nulos solo para la vista previa visual, no afecta el entrenamiento aún.
        df = df.fillna({'Mental Health Condition': 'Healthy'})        
        st.dataframe(df)
    
    # Botón para iniciar el entrenamiento
    if st.button("🚀 Entrenar Modelo", type="primary"):
        with st.spinner('Procesando datos y entrenando el modelo...'):
            
            # 2. Limpieza básica con Pandas
            # Verificamos si la columna objetivo existe.
            if 'Mental Health Condition' not in df.columns:
                st.error("El archivo no contiene la columna objetivo 'Mental Health Condition'.")
                st.stop()
            
            # PANDAS transformation: dropna
            # Eliminamos las filas donde no sabemos el diagnóstico (target).
            # En aprendizaje supervisado, no podemos entrenar sin la respuesta correcta.
            df = df.dropna(subset=['Mental Health Condition'])

            # 3. Separar características (X) y variable objetivo (y)
            # PANDAS transformation: drop y selección de series
            # X = Todo menos la respuesta. y = Solo la respuesta.
            X = df.drop('Mental Health Condition', axis=1)
            y = df['Mental Health Condition']

            # Definición manual de listas de columnas para procesarlas por separado
            columnas_numericas = ['Age', 'Sleep Hours', 'Work Hours per Week', 
                                  'Screen Time per Day (Hours)', 'Social Interaction Score', 'Happiness Score']
            columnas_categoricas = ['Country', 'Gender', 'Exercise Level', 'Diet Type', 'Stress Level']

            # Validación de columnas
            faltantes = [col for col in columnas_numericas + columnas_categoricas if col not in X.columns]
            if faltantes:
                st.error(f"Faltan las siguientes columnas en el dataset: {faltantes}")
                st.stop()

            # 4. Crear "Mini-Pipelines" para preprocesamiento
            # Un Pipeline asegura que las transformaciones se apliquen en orden exacto.
            
            # Pipeline Numérico:
            # 1. Imputer: Si falta un número (NaN), pon la mediana de esa columna.
            # 2. Scaler: Normaliza los datos para que variables grandes (Salario) no opaquen a pequeñas (Edad).
            #            El Scaler deja los datos con media 0 y desviación estándar 1, lo que ayuda a la Regresión Logística a encontrar patrones más fácilmente.
            # La Regresión Logística funciona mejor cuando las características numéricas están en la misma escala.
            pipeline_numerico = Pipeline(steps=[
                ('imputer', SimpleImputer(strategy='median')),  
                ('scaler', StandardScaler())  
            ])

            # Pipeline Categórico:
            # 1. Imputer: Si falta texto, pon el valor más repetido (moda).
            # 2. Encoder: Convierte texto ("Male", "Female") en números binarios (0, 1) que la IA entienda.
            pipeline_categorico = Pipeline(steps=[
                ('imputer', SimpleImputer(strategy='most_frequent')),
                ('encoder', OneHotEncoder(handle_unknown='ignore'))  
            ])

            # 5. ColumnTransformer
            # Aplica el pipeline numérico a las cols numéricas y el categórico a las categóricas simultáneamente.
            preprocesador = ColumnTransformer(
                transformers=[
                    ('num', pipeline_numerico, columnas_numericas),
                    ('cat', pipeline_categorico, columnas_categoricas)
                ])

            # Creación del Pipeline Maestro
            # Une el preprocesador con el modelo final (Regresión Logística).
            modelo_pipeline = Pipeline(
                steps=[
                    # Paso 1: Aplicar el preprocesador (limpieza, imputación, encoding)
                    ('preprocesador', preprocesador),
                    # Paso 2: Aplicar Regresión Logística con configuración optimizada
                    ('clasificador', LogisticRegression(
                        # Maneja múltiples clases (más de 2 categorías de salud mental)
                        multi_class='multinomial',
                        # Algoritmo de optimización: mejor para problemas multiclase
                        solver='lbfgs',
                        # Número máximo de iteraciones para la convergencia del modelo
                        max_iter=1000
                    ))
                ]
            )

            # 6. Dividir datos y Entrenar
            # train_test_split: Separa el 20% de los datos para examen final (test) y 80% para estudiar (train).
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # .fit(): Aquí ocurre la "magia". El modelo aprende los patrones matemáticos.
            modelo_pipeline.fit(X_train, y_train)

            # 7. Evaluar
            # .predict(): Ponemos a prueba el modelo con datos que nunca ha visto (X_test).
            y_pred = modelo_pipeline.predict(X_test)
            
            # Métricas de éxito
            precision = accuracy_score(y_test, y_pred)
            reporte_dict = classification_report(y_test, y_pred, zero_division=0, output_dict=True)
            
            # Guardar el modelo usando Joblib
            # Esto crea un archivo binario .pkl que contiene toda la lógica aprendida.
            archivo_modelo = 'modelo_salud_mental.pkl'
            joblib.dump(modelo_pipeline, archivo_modelo)

        # ---------------- RESULTADOS EN PANTALLA ----------------
        st.divider()
        st.header("📊 Resultados del Entrenamiento")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Precisión del Modelo (Accuracy)", value=f"{precision * 100:.2f}%")
        
        with col2:
            st.success(f"💾 El modelo se ha guardado exitosamente como `{archivo_modelo}`")

        st.subheader("Reporte de Clasificación Detallado")
        # PANDAS: Transposición
        # Convertimos el diccionario del reporte a DataFrame y usamos .transpose() para rotarlo y leerlo mejor.
        df_reporte = pd.DataFrame(reporte_dict).transpose()
        st.dataframe(df_reporte.style.format("{:.2f}"))
        
        with st.expander("📖 Explicación de Métricas de Evaluación del Modelo"):
            st.write("""
        - **Precisión (Precision)**: Indica la proporción de verdaderos positivos sobre el total de positivos predichos. Es útil cuando el costo de un falso positivo es alto. Un valor alto (cercano a 1) es deseable, mientras que un valor bajo indica que el modelo está haciendo muchas predicciones incorrectas.            
        - **Exhaustividad (Recall)**: También conocido como sensibilidad, mide la proporción de verdaderos positivos sobre el total de positivos reales. Es importante en contextos donde es crítico identificar todos los casos positivos. Un valor alto es bueno, mientras que un valor bajo sugiere que el modelo está perdiendo muchos casos positivos.            
        - **F1-Score**: Es la media armónica entre precisión y exhaustividad. Es útil cuando se necesita un balance entre ambas métricas. Un F1-score alto indica un buen equilibrio entre precisión y recall, mientras que un bajo sugiere que el modelo no está funcionando bien en ninguno de los dos aspectos.            
        - **Support**: Representa el número de ocurrencias de cada clase en el conjunto de datos. Es importante tener en cuenta el soporte al evaluar las métricas, ya que un modelo puede tener un buen rendimiento en clases con alto soporte, pero un rendimiento deficiente en clases con bajo soporte.
        
        **Umbrales a considerar**:
        - Precisión y Recall: Valores por encima de 0.7 son generalmente considerados buenos, pero esto puede variar según el contexto.
        - F1-Score: Un valor por encima de 0.6 es aceptable, mientras que por encima de 0.8 es excelente.
        """)
            
        # ---------------- EXPLICACIÓN Y RECOMENDACIÓN ----------------
        st.divider()
        st.header("📝 Análisis de Viabilidad del Modelo")
        
        # Lógica condicional simple para dar feedback al usuario sobre la calidad del modelo.
        if precision >= 0.85:
            st.success("""
            **VEREDICTO: ✅ Altamente Recomendado para uso preliminar.**
            
            **Explicación:** El modelo ha logrado una precisión excelente (mayor al 85%). Esto significa que ha encontrado patrones matemáticos fuertes y claros entre el estilo de vida del paciente y su diagnóstico de salud mental. Se puede utilizar como herramienta de apoyo (triaje clínico) con un alto grado de confianza, aunque siempre recordando que no reemplaza el criterio de un médico.
            """)
        elif precision >= 0.65:
            st.warning("""
            **VEREDICTO: ⚠️ Utilizar con Precaución.**
            
            **Explicación:** El modelo tiene un rendimiento aceptable/moderado (entre 65% y 85%). Ha encontrado algunos patrones útiles, pero comete errores considerables. 
            
            *¿Se puede usar?* Sí, pero solo con fines experimentales, educativos o como una segunda opinión muy superficial. Se recomienda conseguir más datos (más filas) o probar algoritmos más complejos (como Random Forest o XGBoost) para mejorar esta precisión antes de llevarlo a un entorno clínico.
            """)
        else:
            st.error("""
            **VEREDICTO: ❌ NO recomendado para uso real.**
            
            **Explicación:** La precisión obtenida es baja (menor al 65%). En problemas de salud, un modelo con esta precisión equivale casi a "adivinar" o equivocarse de forma constante. 
            
            *¿Por qué ocurre esto?* 
            1. Es probable que no exista una correlación lineal fuerte entre las variables (ej. comer comida chatarra no siempre equivale directamente a PTSD).
            2. La Regresión Logística es un modelo simple y los datos pueden ser demasiado complejos.
            
            *Conclusión:* **No utilices este modelo para predecir riesgos en pacientes reales.** Se necesita una limpieza profunda de datos, agregar nuevas variables médicas o cambiar el tipo de Inteligencia Artificial.
            """)