import streamlit as st
import laya
import json
from datetime import datetime

# Configuración de página - sin icono problemático
st.set_page_config(
    page_title="LAYA - Decisiones Tipo Sistema 1",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'About': 'Demo LAYA - Tipos nativos de pregunta (choice, score, noul) https://github.com/'
    }
)

st.title(":blue[LAYA - Decisiones Tipo Sistema 1]")
st.markdown("---")

st.header(":violet[:material_code_blocks: Ejemplo de código del patrón LAYA]")
st.markdown(
    "Este es el patrón exacto para invocar LAYA y recuperar los resultados, "
    "tal como fue proporcionado. Se usa únicamente el modelo LAYA; no hay APIs externas."
)
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
comments_text = st.text_area(
    "Comentarios:",
    height=200,
    placeholder="Ejemplo:\nHi, we were billed twice for March. Please refund the duplicate today or we will cancel our plan.",
    key="comments_input",
)

with st.container(horizontal=True, vertical_alignment="center"):
    # Parámetro de umbral de churn
    churn_threshold = st.slider(
        "Umbral de Churn (%):",
        min_value=1,
        max_value=95,
        value=40,
        help="Porcentaje mínimo de probabilidad para considerar riesgo de churn alto",
        width=300
    )
    churn_threshold = churn_threshold / 100.0  # Convertir a decimal para comparación
    btnEjecutar =st.button(":material_search: Ejecutar Evaluación LAYA",type="primary")

# Inicializar variables al inicio
results = []
n_comments = 0
comment_word = ""

if btnEjecutar:
    if not comments_text.strip():
        st.warning("Por favor, ingresa al menos un comentario.", icon=":material/warning:")
    else:
        # Parse comments - one per line, ignore empty lines
        comments = [c.strip() for c in comments_text.split("\n") if c.strip()]
        n_comments = len(comments)
        comment_word = "coment" + ("o" if n_comments == 1 else "arios")
        
        # Map language selection to LAYA checkpoint
        lang_map = {
            "automático": "multilingual",
            "English": "english",
            "Multilingual": "multilingual",
        }
        selected_lang = lang_map[lang_option]
        
        # Initialize LAYA router with selected checkpoint
        router = laya.Router()
        router.load(selected_lang)
        
        # Display info about the selected configuration
        st.info(":material_info: Checkpoint LAYA: **{selected_lang}**".format(selected_lang=selected_lang))
        st.info(":material_info: Procesando {} {}...".format(n_comments, comment_word))
        
        # Classification keywords for department (matching the new criteria)
        billing_kw = ["factura", "pago", "reembolso", "cobro", "reembolso"]
        tech_kw = ["bug", "caída", "error", "sistema", "fallo", "problema técnico"]
        sales_kw = ["venta", "precio", "promoción", "compra"]
        logistics_kw = ["entrega", "envío", "devolución", "tracking"]
        customer_service_kw = ["atención al cliente", "soporte", "ayuda", "quejas", "reclamos"]
        
        # Process each comment with LAYA using the exact pattern from the example
        results = []
        progress_bar = st.progress(0)
        
        for i, comment in enumerate(comments):
            
            try:
                # Exact pattern from the example:
                # result = router.predict(state, questions)
                result = laya.Router().predict(
                    state=comment,
                    questions={
                        "department": {"type": "choice", "instructions": "Qué departamento debería manejar este?",
                                        "criteria": {"facturacion": "facturas, pagos, reembolsos",
                                                    "tecnologia": "bugs, caídas de sistema, problemas técnicos, página web",
                                                    "logistica": "entregas, envíos, devoluciones, tracking",
                                                    "ventas": "consultas de ventas, precios, promociones",
                                                    "servicio al cliente": "atención al cliente, soporte, ayuda, quejas, reclamos",
                                                    "other": "everything else"}},
                        "sentiment": {"type": "score", "instructions": "Cuál es el sentimiento?",
                                    "criteria": ["negativo", "neutral", "positivo"]},
                        "churn_risk": {"type": "noul", "instructions": "¿El usuario amenaza con cancelar o absorber?"},
                    }
                )
                
                # === Retrieve results exactly as the example shows ===
                # department choice result (the selected category)
                dept_answer = result["answers"]["department"]["choice"]
                
                # churn_risk noul result (probability the answer is yes)
                churn_answer = result["answers"]["churn_risk"]["noul"]
                
                # routing model (english or multilingual)
                routing_model = result["routing"]["model"]
                
                # sentiment answer from the score type question
                # The score type returns: type, score, legend, probabilities, etc.
                # not a "choice" field like department
                sentiment_data = result["answers"].get("sentiment", {})
                sentiment_score = sentiment_data.get("score", 0)
                sentiment_legend = sentiment_data.get("legend", {})
                
                score_key = str(round(sentiment_score))

                # 3. Buscar la etiqueta correspondiente en la leyenda
                sentiment_answer = sentiment_data["legend"][score_key]
                
                
                # Additional: infer department from comment text based on new criteria
                # (fallback if LAYA returns "other" but keywords suggest otherwise)
                comment_lower = comment.lower()
                inferred_dept = dept_answer  # use LAYA's result as primary
                
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
                results.append({
                    "comment": comment,
                    "dept_answer": inferred_dept,  # use inferred if LAYA gave "other"
                    "churn_answer": churn_answer,
                    "routing_model": routing_model,
                    "sentiment_answer": sentiment_answer,
                    "sentiment_score": sentiment_score,
                    "raw_result": result,
                })
                
            except Exception as e:
                results.append({
                    "comment": comment,
                    "error": str(e),
                })
        
            progress_bar.progress((i + 1) / len(comments), text="Procesando comentario {}/{}".format(i + 1, len(comments)))
        
        progress_bar.empty()
        
        # === RESUMEN AL INICIO (dentro de container con borde) ===
        st.markdown("### :material/table_chart: Resumen de Evaluación LAYA")
        
        # Container con borde para el resumen
        with st.container(border=True):
            # Calculate summary statistics
            dept_counts = {}
            sentiment_counts = {"positivo": 0, "negativo": 0, "neutral": 0}
            churn_yes = 0
            churn_no = 0
            
            for r in results:
                if "error" not in r:
                    # Department
                    dept = r["dept_answer"]
                    dept_counts[dept] = dept_counts.get(dept, 0) + 1
                    
                    # Sentiment
                    sent = r["sentiment_answer"].lower()
                    if sent in sentiment_counts:
                        sentiment_counts[sent] += 1
                    
                    # Churn risk
                    if r["churn_answer"] > churn_threshold:
                        churn_yes += 1
                    else:
                        churn_no += 1
            
            # Create dataframes for summary
            import pandas as pd
            
            # Department dataframe
            dept_df = pd.DataFrame([
                {"Departamento": dept.title(), "Cantidad": count}
                for dept, count in dept_counts.items()
            ]) if dept_counts else pd.DataFrame([{"Departamento": "N/A", "Cantidad": 0}])
            
            # Sentiment dataframe
            sent_df = pd.DataFrame([
                {"Sentimiento": sent.title(), "Cantidad": count}
                for sent, count in sentiment_counts.items()
            ]) if any(sentiment_counts.values()) else pd.DataFrame([{"Sentimiento": "N/A", "Cantidad": 0}])
            
            # Churn dataframe
            churn_df = pd.DataFrame([
                {"Riesgo": "SÍ (Alta Probabilidad)", "Cantidad": churn_yes},
                {"Riesgo": "NO (Baja Probabilidad)", "Cantidad": churn_no}
            ]) if churn_yes + churn_no > 0 else pd.DataFrame([{"Riesgo": "N/A", "Cantidad": 0}])
            
            # Mostrar tablas con st.dataframe
            st.markdown("**Distribución por Departamento:**")
            st.dataframe(dept_df, hide_index=True, column_config={"Departamento": st.column_config.TextColumn("Departamento"), "Cantidad": st.column_config.NumberColumn("Cantidad")})
            
            st.markdown("**Distribución por Sentimiento:**")
            st.dataframe(sent_df, hide_index=True, column_config={"Sentimiento": st.column_config.TextColumn("Sentimiento"), "Cantidad": st.column_config.NumberColumn("Cantidad")})
            
            st.markdown("**Riesgo de Churn:**")
            st.dataframe(churn_df, hide_index=True, column_config={"Riesgo": st.column_config.TextColumn("Riesgo"), "Cantidad": st.column_config.NumberColumn("Cantidad")})
            
            # Total comments processed
            st.markdown(f"**Total procesado**: {n_comments} comentarios")
        
        st.markdown("---")
        
        # === Display per-comment results ===
        st.markdown("### :material_comment: Resultados por Comentario")
        
        for i, r in enumerate(results):
            with st.container(border=True):                
                st.write("**Texto original:**", r["comment"])
                
                if "error" in r:
                    st.error(":material_error: Error: {}".format(r['error']))
                else:
                    with st.container(horizontal=True):
                        st.metric(label="Departamento (Elección)", value=r["dept_answer"].upper(), 
                                  delta_description="Modelo: {}".format(r['routing_model']),icon=":material/category:",width=500)
                        sentiment_display = r["sentiment_answer"].capitalize()
                        if sentiment_display == "Negativo":
                            sentiment_display = f":red[{sentiment_display}]"
                        elif sentiment_display == "Positivo":
                            sentiment_display = f":green[{sentiment_display}]"
                        elif sentiment_display == "Neutral":
                            sentiment_display = f":yellow[{sentiment_display}]"
                        st.metric(label="Sentimiento (Puntaje)", value=sentiment_display, 
                                  delta_description="Score: {}".format(r['sentiment_score']),icon=":material/sentiment_satisfied:",width=300)
                        churn_display = ":red[SÍ (probabilidad alta)]" if r["churn_answer"] > churn_threshold else ":green[NO (probabilidad baja)]"
                        st.metric(label="Riesgo de Churn (Noul)", value=churn_display, 
                                  delta_description="Probabilidad: {:.2%}".format(r['churn_answer']),icon=":material/cancel:")
                    
                    with st.expander("Ver resultado LAYA completo"):
                        st.write(":material_json: JSON completo del resultado LAYA:")
                        st.code(json.dumps(r["raw_result"], indent=2, ensure_ascii=False), language="json")
        
        st.markdown("---")
        st.caption(":material_robot: Motor LAYA • Patrón exacto: router.predict(state, questions) • Tipos nativos: choice + score + noul • Sin APIs externas")
else:
    st.markdown(":material_folder: Selecciona un idioma, pega comentarios y haz clic para evaluar con LAYA usando el patrón exacto del ejemplo.")