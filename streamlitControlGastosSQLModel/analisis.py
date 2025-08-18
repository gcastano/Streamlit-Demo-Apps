import streamlit as st
import modelos.dbdatos as db
import crud
import pandas as pd

expenses = crud.get_expenses()

dfDatos=pd.DataFrame()
for expense in expenses:
    dfDatos = pd.concat([dfDatos, pd.DataFrame([{
        'id': expense.id,
        'date': expense.date,
        'category': expense.subcategory.category.name if expense.subcategory and expense.subcategory.category else 'Sin categoría',
        'subcategory': expense.subcategory.name if expense.subcategory else 'Sin subcategoría',
        'description': expense.description,
        'amount': expense.amount,
    }])], ignore_index=True)

st.set_page_config(page_title="Análisis de Gastos", layout="wide")
st.title(":material/bar_chart: Análisis de Gastos")

with st.container(horizontal=True, vertical_alignment="center", horizontal_alignment="center",):
    st.metric("Total Gastos", f"${dfDatos['amount'].sum():,.2f}", delta=None, delta_color="normal")
    st.metric("Número de Gastos", len(dfDatos), delta=None, delta_color="normal")
if dfDatos.empty:
    st.warning("No hay gastos registrados para mostrar.")

st.header("Gastos Registrados")

if not dfDatos.empty:
    dfDatos['date'] = pd.to_datetime(dfDatos['date'])
    dfDatos['amount'] = dfDatos['amount'].astype(float)
    dfDatos.sort_values(by='date', ascending=False, inplace=True)

    st.dataframe(dfDatos, use_container_width=True)

    st.subheader("Gastos por Categoría")
    gastos_por_categoria = dfDatos.groupby('category').agg({'amount': 'sum'}).reset_index()
    st.bar_chart(gastos_por_categoria.set_index('category'))

    st.subheader("Gastos por Subcategoría")
    gastos_por_subcategoria = dfDatos.groupby('subcategory').agg({'amount': 'sum'}).reset_index()
    st.bar_chart(gastos_por_subcategoria.set_index('subcategory'))
