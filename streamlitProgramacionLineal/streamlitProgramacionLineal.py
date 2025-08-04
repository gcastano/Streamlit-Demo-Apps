# ==============================================================================
# LIBRERÍAS NECESARIAS
# ==============================================================================
# Para ejecutar este código, necesitas instalar las siguientes librerías:

# 1. Streamlit: Una librería de Python que permite crear y compartir aplicaciones
#    web para ciencia de datos y machine learning de forma rápida y sencilla.
#    Se usa para construir la interfaz de usuario de esta calculadora.
#    Instalación: pip install streamlit
import streamlit as st

# 2. PuLP: Una librería de modelado de optimización lineal en Python.
#    Permite describir problemas de programación lineal de forma muy legible
#    y luego resolverlos utilizando diferentes solvers (CBC, GLPK, etc.).
#    Instalación: pip install pulp
# Ejemplo base https://www.geeksforgeeks.org/python/python-linear-programming-in-pulp/
import pulp as p

# 3. re (Regular Expressions): Un módulo estándar de Python (no necesita instalación).
#    Se utiliza para trabajar con expresiones regulares, que son patrones para
#    encontrar o reemplazar texto. Aquí, lo usamos para identificar los nombres
#    de las variables en las fórmulas que introduce el usuario.
import re

# Ejercicio de optimización lineal con PuLP
# https://www.superprof.es/apuntes/escolar/matematicas/algebralineal/pl/ejercicios-y-problemas-resueltos-de-programacion-lineal.html

# ==============================================================================
# CONFIGURACIÓN DE LA PÁGINA DE STREAMLIT
# ==============================================================================
# st.set_page_config() configura los metadatos y el layout de la página.
# page_title: El título que aparece en la pestaña del navegador.
# layout="wide": Hace que el contenido de la app ocupe todo el ancho de la pantalla.
st.set_page_config(page_title="Programación Lineal con PuLP", layout="wide")

# Título principal de la aplicación que se mostrará en la página.
st.title("Programación Lineal con PuLP")

# ==============================================================================
# DEFINICIÓN DE LA INTERFAZ DE USUARIO (UI)
# ==============================================================================
# Dividimos la pantalla en dos columnas principales para organizar la interfaz.
# La primera columna (cConf) será para la configuración del problema (3/8 del ancho).
# La segunda columna (cResult) será para mostrar los resultados (5/8 del ancho).
# gap="large" aumenta el espacio entre las columnas.
# border=True dibuja un borde alrededor de las columnas para una mejor separación visual.
cConf, cResult = st.columns([3, 5], gap="large", border=True)

# --- COLUMNA DE CONFIGURACIÓN ---
# El bloque 'with cConf:' asegura que todos los comandos de streamlit
# dentro de este bloque se dibujen en la primera columna.
with cConf:
    st.write("#### Definición del problema de programación lineal")
    
    # Campo de texto para que el usuario asigne un nombre al problema de optimización.
    parNombreProblema = st.text_input("Nombre del problema", "Problema_de_Optimizacion")

    # Creamos dos sub-columnas para la función objetivo y el tipo de objetivo.
    c1, c2 = st.columns(2)
    with c1:
        # Campo de texto para que el usuario ingrese la función objetivo.
        # Ejemplo: "3*x + 5*y"
        parProblema = st.text_input("Función Problema (ej: 3*x + 5*y)")
        
        # INSTRUCCIÓN CLAVE: EXTRACCIÓN DE VARIABLES CON EXPRESIONES REGULARES
        # re.findall(r'\w+', parProblema) busca en la cadena 'parProblema'
        # todos los patrones que coincidan con '\w+', que significa "uno o más
        # caracteres de palabra (letras, números o guion bajo)".
        # Si parProblema es "3*x1 + 5*y", esto devolverá ['3', 'x1', '5', 'y'].
        valores_alfanumericos = re.findall(r'\w+', parProblema)        
        # INSTRUCCIÓN CLAVE: FILTRADO DE VARIABLES
        # Usamos una "list comprehension" para quedarnos solo con aquellos elementos
        # que NO son dígitos. Esto filtra los números y nos deja únicamente
        # con los nombres de las variables.
        # Para ['3', 'x1', '5', 'y'], el resultado será ['x1', 'y'].
        valores_alfanumericos = [v for v in valores_alfanumericos if not v.isdigit()]    
    
    with c2:
        # Menú desplegable para seleccionar si el objetivo es minimizar o maximizar.
        parTipoObjetivo = st.selectbox("Tipo de objetivo", ["Minimizar", "Maximizar"])
        
        # Asignamos la constante de PuLP correcta (p.LpMinimize o p.LpMaximize)
        # basándonos en la selección del usuario.
        tipoObjetivo = p.LpMinimize if parTipoObjetivo == "Minimizar" else p.LpMaximize

    # Creamos un diccionario para almacenar los objetos de las variables de PuLP.
    # dict.fromkeys() crea un diccionario donde las claves son los nombres de las
    # variables extraídas y sus valores iniciales son 'None'.
    # Ejemplo: {'x1': None, 'y': None}
    variables = dict.fromkeys(valores_alfanumericos, None)

    st.write("#### Definición de las variables")
    # Creamos una lista de diccionarios para guardar la configuración de cada variable
    # (límites y categoría). Esto facilita la creación dinámica de la UI.
    confVariables= [{"name": var, "lowbound": 0,"upBound":None,"cat":"Continua"} for var in variables.keys()]
    
    # Iteramos sobre la configuración de cada variable para crear sus campos en la UI.
    for var in confVariables:
        # Creamos 4 columnas para cada variable: Nombre, Límite Inferior, Límite Superior, Categoría.
        cols = st.columns(4, vertical_alignment='center')
        nombreVariable = var["name"]
        
        # Mostramos el nombre de la variable de forma destacada usando HTML.
        cols[0].html(f'<div style="text-align:center;background-color:#E7D3D3"><span style="font-size:20px;font-weight:bold;line-height:30px"> {nombreVariable}</span> </div>')
        
        # Campos numéricos para definir los límites inferior y superior de la variable.
        var["lowbound"] = cols[1].number_input(f"Valor mínimo de {var['name']}", min_value=0, value=None, step=1, key=f"low_{var['name']}")
        var["upBound"] = cols[2].number_input(f"Valor máximo de {var['name']}", min_value=0, value=None, step=1, key=f"up_{var['name']}")
        
        # Menú desplegable para definir la categoría de la variable (Continua, Entera o Binaria).
        var["cat"] = cols[3].selectbox(f"Categoría de {var['name']}", ["Continua", "Entera", "Binaria"], key=f"cat_{var['name']}")
        
    # INSTRUCCIÓN CLAVE: PREPARACIÓN DE LA FUNCIÓN OBJETIVO PARA 'EVAL'
    # Esta sección transforma la cadena de texto de la función objetivo en una
    # expresión que Python puede ejecutar con 'eval()'.
    problema = parProblema
    for var in variables:        
        # Reemplazamos cada nombre de variable (ej: "x") por el código que accede
        # al objeto correspondiente en el diccionario (ej: 'variables["x"]').
        # Ejemplo: "3*x + 5*y" se convierte en '3*variables["x"] + 5*variables["y"]'.
        problema = problema.replace(var, f'variables["{var}"]')    
        
    # Área de texto para que el usuario ingrese las restricciones, una por línea.
    restricciones = st.text_area("Restricciones del problema (separadas por saltos de línea)")
    
    # Botón principal que, al ser presionado, iniciará el proceso de solución.
    procesado = st.button("Procesar", type="primary")

# --- COLUMNA DE RESULTADOS ---
# El bloque 'with cResult:' asegura que todos los comandos de streamlit
# dentro de este bloque se dibujen en la segunda columna.
with cResult:
    # Este bloque de código solo se ejecuta si el botón "Procesar" ha sido presionado.
    if procesado:
        # INSTRUCCIÓN CLAVE: VALIDACIÓN DE ENTRADAS
        # Verificamos que el usuario haya ingresado un nombre para el problema.
        if not parNombreProblema:
            st.error("Por favor, ingresa un nombre para el problema.")
            st.stop()  # Detenemos la ejecución si no hay nombre.
        # Verificamos que se haya ingresado una función objetivo válida.
        if not parProblema:
            st.error("Por favor, ingresa una función objetivo válida.")
            st.stop()
        # Verificamos que se hayan definido al menos una variable.
        if len(variables)==0:
            st.error("Por favor, define al menos una variable.")
            st.stop()
        # Verificamos que se hayan ingresado restricciones.
        if not restricciones.strip():
            st.error("Por favor, ingresa al menos una restricción.")
            st.stop()
        # Verificamos que se hayan definido correctamente los límites de las variables.
        for var in confVariables:
            if var["lowbound"] is None:
                st.error(f"Por favor, define un límite inferior para la variable {var['name']}.")
                st.stop()            
        
        
        with st.spinner("Resolviendo el problema..."):
            # INSTRUCCIÓN CLAVE: CREACIÓN DE LAS VARIABLES PuLP
            # Iteramos sobre el diccionario de variables que definimos antes.
            for var in variables:
                # Buscamos la configuración específica (límites, categoría) para esta variable.
                configuracionVariable = [v for v in confVariables if v["name"] == var][0]
                lowBound = configuracionVariable["lowbound"]
                upBound = configuracionVariable["upBound"] if configuracionVariable["upBound"] is not None else None
                cat = configuracionVariable["cat"]
                
                # Creamos el objeto p.LpVariable con la configuración correspondiente.
                # p.LpVariable es el objeto de PuLP que representa una variable de decisión.
                if cat == "Continua":
                    variables[var] = p.LpVariable(var, lowBound=lowBound, upBound=upBound, cat='Continuous')
                elif cat == "Entera":
                    variables[var] = p.LpVariable(var, lowBound=lowBound, upBound=upBound, cat='Integer')
                elif cat == "Binaria":
                    # Para variables binarias, los límites son automáticamente 0 y 1.
                    variables[var] = p.LpVariable(var, cat='Binary')

            # INSTRUCCIÓN CLAVE: CREACIÓN Y DEFINICIÓN DEL PROBLEMA EN PuLP
            # 1. Creamos el objeto del problema con su nombre y el tipo de objetivo.
            Lp_prob = p.LpProblem(parNombreProblema, tipoObjetivo)
            
            # 2. Añadimos la función objetivo al problema.
            # eval() ejecuta la cadena 'problema' como si fuera código Python.
            # Gracias a la preparación anterior, esto se traduce en la suma/resta
            # de los objetos LpVariable, que PuLP entiende como la función objetivo.
            Lp_prob += eval(problema)

            # 3. Añadimos las restricciones al problema.
            # Iteramos sobre cada línea del cuadro de texto de restricciones.
            for restriccion in restricciones.split('\n'):
                restriccion = restriccion.strip() # Limpiamos espacios en blanco.
                if restriccion: # Nos aseguramos de no procesar líneas vacías.
                    # Al igual que con la función objetivo, reemplazamos los nombres
                    # de las variables por el acceso al diccionario.
                    for var in variables:
                        restriccion = restriccion.replace(var, f'variables["{var}"]')
                    # Usamos 'eval()' para añadir la restricción procesada al problema.
                    Lp_prob += eval(restriccion)

            # Mostramos la formulación matemática del problema. PuLP formatea esto
            # automáticamente de una manera muy legible.
            st.write("#### Problema de Programación Lineal")
            st.write(Lp_prob)

            # INSTRUCCIÓN CLAVE: RESOLUCIÓN DEL PROBLEMA
            # Lp_prob.solve() llama al solver por defecto (CBC) para encontrar la solución.
            # Devuelve un estado que indica si se encontró una solución óptima.
            status = Lp_prob.solve()   
            
            st.write("#### Solución del problema")
            # Mostramos el estado de la solución en formato de texto (ej: "Optimal").
            st.write("Estado de la solución:", p.LpStatus[status])

            # INSTRUCCIÓN CLAVE: VISUALIZACIÓN DE RESULTADOS
            # Creamos columnas para mostrar los valores de las variables de forma ordenada.
            colsResult = st.columns(4)
            poscol = 0
            for var in variables:
                # Reiniciamos el contador de columnas para crear una nueva fila.
                if poscol == 4:
                    poscol = 0
                
                # Usamos un bloque 'with' para dibujar en la columna actual.
                with colsResult[poscol]:
                    # p.value(variables[var]) extrae el valor numérico de la variable
                    # una vez que el problema ha sido resuelto.
                    resultado = p.value(variables[var])
                    
                    # st.metric es un widget ideal para mostrar indicadores clave (KPIs).
                    st.metric(label=f":blue[Variable **{var}**]", value=f"{resultado:,.2f}")
                poscol += 1
            
            # Finalmente, mostramos el valor óptimo de la función objetivo.
            # p.value(Lp_prob.objective) extrae el resultado final.
            st.metric(label=f":green[**Resultado Óptimo**]", value=f"{p.value(Lp_prob.objective):,.2f}")