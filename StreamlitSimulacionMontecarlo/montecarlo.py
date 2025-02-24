import re
import streamlit as st
def generarVariables(formula):    
    listaVariables = re.findall(r"({{[A-Za-z0-9]+}})", formula)
    formulaSimulacion = formula
    listaNombreVariables = []
    for var in listaVariables:
        nombrevar=var.replace("{{","").replace("}}","")
        if nombrevar not in listaNombreVariables:
            listaNombreVariables.append(nombrevar)
        formulaSimulacion = formulaSimulacion.replace(var,f"variables['{nombrevar}']")
    return formulaSimulacion, listaNombreVariables