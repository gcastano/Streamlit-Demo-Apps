# ==========================================
# IMPORTACIÓN DE LIBRERÍAS
# ==========================================
# Streamlit: Librería para crear interfaces web interactivas con puro Python de forma rápida.
import streamlit as st
# Laya: Motor/Librería de IA que permite enrutar y clasificar texto basado en reglas (Sistema 1).
import laya
# Json: Librería estándar de Python para manipular datos en formato JSON (JavaScript Object Notation).
import json
# Datetime: Librería estándar para manejar fechas y horas (importada por defecto aunque no se use activamente aquí).
from datetime import datetime

# Configuración inicial de la página web generada por Streamlit.
# layout="wide" hace que la aplicación ocupe todo el ancho de la pantalla.
st.set_page_config(
    page_title="LAYA - Decisiones Tipo Sistema 1",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'About': 'Demo LAYA - Tipos nativos de pregunta (choice, score, noul) https://github.com/'
    }
)

# Títulos e introducción visual en la aplicación
st.title(":blue[LAYA - Decisiones Tipo Sistema 1]")
st.markdown("---")

st.header(":violet[:material_code_blocks: Ejemplo de código del patrón LAYA]")
st.markdown(
    "Este es el patrón exacto para invocar LAYA y recuperar los resultados, "
    "tal como fue proporcionado. Se usa únicamente el modelo LAYA; no hay APIs externas."
)

# st.code muestra fragmentos de código en la UI con formato resaltado
st.code("""
from laya import Router

router = Router()  # downloads a checkpoint on first use; Router(preload=True) loads all three up front

state = "Hi, we were billed twice for March. Please refund the duplicate today or we will cancel our plan."
questions = {
    "department": {"type": "choice", "instructions": "Qué departamento debería manejar este?",
                   "criteria": {"facturacion": "facturas, pagos, reembolsos",
                                "tecnologia": "bugs, caídas de sistema, problemas técnicos",
                                "ventas": "consultas de ventas, precios, promociones",
                                "other": "everything else"}},
    "sentiment": {"type": "score", "instructions": "Cuál es el sentimiento?",
                "criteria": ["negativo", "neutral", "positivo"]},
    "churn_risk": {"type": "noul", "instructions": "¿El usuario amenaza con cancelar o abandonar?"},
}

result = router.predict(state, questions)
print(result["answers"]["department"]["choice"])  # facturacion (or tecnologia/ventas/other)
print(result["answers"]["churn_risk"]["noul"])    # probability the answer is yes
print(result["routing"]["model"])                 # english
"""
)

st.markdown("")

st.header(":violet[:material_globe: Seleccionar Idioma]")
st.markdown(
    "Selecciona el idioma de los comentarios. Esto determina qué checkpoint de LAYA "
    "utilizará para el análisis."
)

# st.radio crea botones de opción para que el usuario seleccione una configuración de idioma.
lang_option = st.radio(
    "Idioma:",
    options=["automático", "English", "Multilingual"],
    index=0,
    help=(
        "• Automático: LAYA detecta el idioma automáticamente (checkpoint multilingual)\n"
        "• English: Motor en inglés (optimizado para texto en inglés)\n"
        "• Multilingual: Motor multi-idioma (100+ idiomas soportados)"
    ),
)

st.markdown("---")

st.header(":violet[:material/comment: Ingresar Comentarios]")
st.markdown(
    "Pega múltiples comentarios (uno por línea). LAYA evaluará cada uno usando el "
    "patrón `router.predict(state, questions)` mostrado arriba. Las líneas vacías son ignoradas."
)

# st.text_area permite al usuario ingresar texto en múltiples líneas.
comments_text = st.text_area(
    "Comentarios:",
    height=200,
    placeholder="Ejemplo:\nHi, we were billed twice for March. Please refund the duplicate today or we will cancel our plan.",
    key="comments_input",
)

# Contenedor para colocar el slider de umbral y el botón en la misma fila
with st.container(horizontal=True, vertical_alignment="center"):
    # Parámetro de umbral de churn (slider para ajustar sensiblidad de abandono)
    churn_threshold = st.slider(
        "Umbral de Churn (%):",
        min_value=1,
        max_value=95,
        value=40,
        help="Porcentaje mínimo de probabilidad para considerar riesgo de churn alto",
        width=300
    )
    # Convertimos de porcentaje (1-100) a decimal (0.01 - 0.95) para facilitar la matemática.
    churn_threshold = churn_threshold / 100.0  
    
    # Botón de ejecución principal de la aplicación
    btnEjecutar = st.button(":material_search: Ejecutar Evaluación LAYA",type="primary")

# Inicializar variables vacías al inicio para evitar errores de referencias nulas
results = []
n_comments = 0
comment_word = ""

# ==========================================
# LÓGICA PRINCIPAL DE PROCESAMIENTO
# ==========================================
if btnEjecutar:
    # Validamos que haya texto ingresado antes de procesar
    if not comments_text.strip():
        st.warning("Por favor, ingresa al menos un comentario.", icon=":material/warning:")
    else:
        # Parse comments - List comprehension para extraer comentarios línea por línea, ignorando los vacíos.
        comments = [c.strip() for c in comments_text.split("\n") if c.strip()]
        n_comments = len(comments)
        comment_word = "coment" + ("o" if n_comments == 1 else "arios")
        
        # Mapeamos la selección de idioma en la interfaz hacia el modelo correspondiente en LAYA
        lang_map = {
            "automático": "multilingual",
            "English": "english",
            "Multilingual": "multilingual",
        }
        selected_lang = lang_map[lang_option]
        
        # Inicializamos el Router de LAYA y cargamos el idioma seleccionado
        router = laya.Router()
        router.load(selected_lang)
        
        # Mostrar información sobre el estado de la configuración seleccionada en la UI
        st.info(":material_info: Checkpoint LAYA: **{selected_lang}**".format(selected_lang=selected_lang))
        st.info(":material_info: Procesando {} {}...".format(n_comments, comment_word))
        
        # Palabras clave de clasificación (fallback) en caso de que LAYA asigne la categoría "other"
        billing_kw = ["factura", "pago", "reembolso", "cobro", "reembolso"]
        tech_kw = ["bug", "caída", "error", "sistema", "fallo", "problema técnico"]
        sales_kw = ["venta", "precio", "promoción", "compra"]
        logistics_kw = ["entrega", "envío", "devolución", "tracking"]
        customer_service_kw = ["atención al cliente", "soporte", "ayuda", "quejas", "reclamos"]
        
        results = []
        progress_bar = st.progress(0) # Barra de progreso visual
        
        # Iteramos sobre cada comentario extraído
        for i, comment in enumerate(comments):
            
            try:
                # Invocamos la API local de LAYA. Pasamos el texto (state) y las preguntas a responder.
                result = laya.Router().predict(
                    state=comment,
                    questions={
                        # Pregunta de tipo 'choice': LAYA debe elegir una opción dentro de los criterios.
                        "department": {"type": "choice", "instructions": "Qué departamento debería manejar este?",
                                        "criteria": {"facturacion": "facturas, pagos, reembolsos",
                                                    "tecnologia": "bugs, caídas de sistema, problemas técnicos, página web",
                                                    "logistica": "entregas, envíos, devoluciones, tracking",
                                                    "ventas": "consultas de ventas, precios, promociones",
                                                    "servicio al cliente": "atención al cliente, soporte, ayuda, quejas, reclamos",
                                                    "other": "everything else"}},
                        # Pregunta de tipo 'score': LAYA devuelve un valor numérico/puntuación asociado a un criterio.
                        "sentiment": {"type": "score", "instructions": "Cuál es el sentimiento?",
                                    "criteria": ["negativo", "neutral", "positivo"]},
                        # Pregunta de tipo 'noul': Evalúa probabilidad o riesgo booleano.
                        "churn_risk": {"type": "noul", "instructions": "¿El usuario amenaza con cancelar o absorber?"},
                    }
                )
                
                # === Extracción de resultados del JSON/Dict devuelto por LAYA ===
                # Respuesta de elección de departamento
                dept_answer = result["answers"]["department"]["choice"]
                
                # Probabilidad de churn (abandono)
                churn_answer = result["answers"]["churn_risk"]["noul"]
                
                # Modelo utilizado en el routing
                routing_model = result["routing"]["model"]
                
                # Extracción de datos del análisis de sentimiento
                sentiment_data = result["answers"].get("sentiment", {})
                sentiment_score = sentiment_data.get("score", 0)
                sentiment_legend = sentiment_data.get("legend", {})
                
                score_key = str(round(sentiment_score))

                # Buscar la etiqueta (texto) correspondiente en la leyenda usando la puntuación redondeada
                sentiment_answer = sentiment_data["legend"][score_key]
                
                # Lógica Adicional (Fallback): 
                # Si LAYA responde "other", usamos palabras clave para inferir el departamento.
                comment_lower = comment.lower()
                inferred_dept = dept_answer 
                
                if any(kw in comment_lower for kw in billing_kw) and dept_answer == "other":
                    inferred_dept = "facturacion"
                elif any(kw in comment_lower for kw in tech_kw) and dept_answer == "other":
                    inferred_dept = "tecnologia"
                elif any(kw in comment_lower for kw in sales_kw) and dept_answer == "other":
                    inferred_dept = "ventas"
                elif any(kw in comment_lower for kw in logistics_kw) and dept_answer == "other":
                    inferred_dept = "logistica"
                elif any(kw in comment_lower for kw in customer_service_kw) and dept_answer == "other":
                    inferred_dept = "servicio al cliente"
                
                # Guardamos los resultados limpios y estructurados en nuestra lista 'results'
                results.append({
                    "comment": comment,
                    "dept_answer": inferred_dept, 
                    "churn_answer": churn_answer,
                    "routing_model": routing_model,
                    "sentiment_answer": sentiment_answer,
                    "sentiment_score": sentiment_score,
                    "raw_result": result,
                })
                
            except Exception as e:
                # En caso de error, lo capturamos para evitar que la aplicación se caiga y lo registramos
                results.append({
                    "comment": comment,
                    "error": str(e),
                })
            
            # Actualizamos la barra de progreso
            progress_bar.progress((i + 1) / len(comments), text="Procesando comentario {}/{}".format(i + 1, len(comments)))
        
        progress_bar.empty() # Limpiamos la barra al terminar
        
        # ==========================================
        # RESUMEN Y ANÁLISIS DE DATOS CON PANDAS
        # ==========================================
        st.markdown("### :material/table_chart: Resumen de Evaluación LAYA")
        
        # Creamos un contenedor con bordes para agrupar visualmente el resumen
        with st.container(border=True):
            # 1. Variables para calcular estadísticas
            dept_counts = {}
            sentiment_counts = {"positivo": 0, "negativo": 0, "neutral": 0}
            churn_yes = 0
            churn_no = 0
            
            # 2. Iteramos sobre los resultados para contar frecuencias
            for r in results:
                if "error" not in r:
                    # Contamos incidencias por departamento
                    dept = r["dept_answer"]
                    dept_counts[dept] = dept_counts.get(dept, 0) + 1
                    
                    # Contamos frecuencias de sentimientos
                    sent = r["sentiment_answer"].lower()
                    if sent in sentiment_counts:
                        sentiment_counts[sent] += 1
                    
                    # Evaluamos el riesgo de churn frente al umbral
                    if r["churn_answer"] > churn_threshold:
                        churn_yes += 1
                    else:
                        churn_no += 1
            
            # Pandas: Librería fundamental en análisis de datos. Aquí convertimos
            # nuestros diccionarios a DataFrames para mostrarlos como tablas limpias en la web.
            import pandas as pd
            
            # Transformación 1: Dataframe de Departamentos
            # Usamos list comprehension para crear una lista de diccionarios, que Pandas convierte fácilmente a una tabla.
            dept_df = pd.DataFrame([
                {"Departamento": dept.title(), "Cantidad": count}
                for dept, count in dept_counts.items()
            ]) if dept_counts else pd.DataFrame([{"Departamento": "N/A", "Cantidad": 0}])
            
            # Transformación 2: Dataframe de Sentimientos
            sent_df = pd.DataFrame([
                {"Sentimiento": sent.title(), "Cantidad": count}
                for sent, count in sentiment_counts.items()
            ]) if any(sentiment_counts.values()) else pd.DataFrame([{"Sentimiento": "N/A", "Cantidad": 0}])
            
            # Transformación 3: Dataframe de Churn
            churn_df = pd.DataFrame([
                {"Riesgo": "SÍ (Alta Probabilidad)", "Cantidad": churn_yes},
                {"Riesgo": "NO (Baja Probabilidad)", "Cantidad": churn_no}
            ]) if churn_yes + churn_no > 0 else pd.DataFrame([{"Riesgo": "N/A", "Cantidad": 0}])
            
            # Mostrar las tablas generadas con st.dataframe de forma atractiva, ocultando el índice por defecto.
            st.markdown("**Distribución por Departamento:**")
            st.dataframe(dept_df, hide_index=True, column_config={"Departamento": st.column_config.TextColumn("Departamento"), "Cantidad": st.column_config.NumberColumn("Cantidad")})
            
            st.markdown("**Distribución por Sentimiento:**")
            st.dataframe(sent_df, hide_index=True, column_config={"Sentimiento": st.column_config.TextColumn("Sentimiento"), "Cantidad": st.column_config.NumberColumn("Cantidad")})
            
            st.markdown("**Riesgo de Churn:**")
            st.dataframe(churn_df, hide_index=True, column_config={"Riesgo": st.column_config.TextColumn("Riesgo"), "Cantidad": st.column_config.NumberColumn("Cantidad")})
            
            st.markdown(f"**Total procesado**: {n_comments} comentarios")
        
        st.markdown("---")
        
        # ==========================================
        # RESULTADOS INDIVIDUALES POR COMENTARIO
        # ==========================================
        st.markdown("### :material_comment: Resultados por Comentario")
        
        # Mostramos una vista detallada de la evaluación de cada texto
        for i, r in enumerate(results):
            with st.container(border=True):                
                st.write("**Texto original:**", r["comment"])
                
                if "error" in r:
                    st.error(":material_error: Error: {}".format(r['error']))
                else:
                    with st.container(horizontal=True):
                        # Mostramos las métricas de clasificación para cada área evaluada
                        st.metric(label="Departamento (Elección)", value=r["dept_answer"].upper(), 
                                  delta_description="Modelo: {}".format(r['routing_model']),icon=":material/category:",width=500)
                        
                        # Colorear texto condicionalmente basado en el sentimiento
                        sentiment_display = r["sentiment_answer"].capitalize()
                        if sentiment_display == "Negativo":
                            sentiment_display = f":red[{sentiment_display}]"
                        elif sentiment_display == "Positivo":
                            sentiment_display = f":green[{sentiment_display}]"
                        elif sentiment_display == "Neutral":
                            sentiment_display = f":yellow[{sentiment_display}]"
                            
                        st.metric(label="Sentimiento (Puntaje)", value=sentiment_display, 
                                  delta_description="Score: {}".format(r['sentiment_score']),icon=":material/sentiment_satisfied:",width=300)
                                  
                        # Lógica visual para la alerta de Churn
                        churn_display = ":red[SÍ (probabilidad alta)]" if r["churn_answer"] > churn_threshold else ":green[NO (probabilidad baja)]"
                        st.metric(label="Riesgo de Churn (Noul)", value=churn_display, 
                                  delta_description="Probabilidad: {:.2%}".format(r['churn_answer']),icon=":material/cancel:")
                    
                    # Acordeón colapsable para ver el archivo JSON completo sin saturar la pantalla
                    with st.expander("Ver resultado LAYA completo"):
                        st.write(":material_json: JSON completo del resultado LAYA:")
                        st.code(json.dumps(r["raw_result"], indent=2, ensure_ascii=False), language="json")
        
        st.markdown("---")
        st.caption(":material_robot: Motor LAYA • Patrón exacto: router.predict(state, questions) • Tipos nativos: choice + score + noul • Sin APIs externas")
else:
    # Mensaje por defecto cuando aún no se ha presionado "Ejecutar"
    st.markdown(":material_folder: Selecciona un idioma, pega comentarios y haz clic para evaluar con LAYA usando el patrón exacto del ejemplo.")