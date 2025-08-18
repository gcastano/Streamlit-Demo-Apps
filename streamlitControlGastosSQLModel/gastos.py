# Streamlit: Librería para crear aplicaciones web interactivas en Python.
# Instalación: pip install streamlit
import streamlit as st

# Importación de módulos locales para manejar la base de datos y operaciones CRUD.
import modelos.dbdatos as db
import crud

# Configuración de la página de Streamlit.
st.set_page_config(page_title="Registro de Gastos", layout="wide")

@st.dialog("Eliminar Gasto")
def delete_expense(expense_id: int, expense_description: str):
    """
    Diálogo para confirmar la eliminación de un gasto.

    Args:
        expense_id (int): ID del gasto a eliminar.
        expense_description (str): Descripción del gasto a eliminar.
    """
    st.write(f"¿Estás seguro de que quieres eliminar el gasto **'{expense_description}'**?")
    st.write("Esta acción no se puede deshacer.")
    st.write("Por favor, confirma que deseas proceder con la eliminación.")

    with st.container(horizontal=True, border=True, vertical_alignment="center", horizontal_alignment="center"):
        if st.button(":material/check:", key=f"confirm_delete_{expense_id}", type="primary"):
            # Llama a la función para eliminar el gasto de la base de datos.
            success = crud.delete_expense(expense_id)
            if success:
                st.toast("Gasto eliminado correctamente.")
                st.rerun()  # Reinicia la aplicación para reflejar los cambios.
            else:
                st.error("Error al eliminar el gasto.")
        if st.button("Cancelar"):
            st.rerun()  # Reinicia la aplicación para cerrar el diálogo.

@st.dialog("Editar Gasto")
def edit_expense(expense_id: int, expense_description: str, amount: float, date: str, category_id: int, subcategory_id: int):
    """
    Diálogo para editar los detalles de un gasto existente.

    Args:
        expense_id (int): ID del gasto a editar.
        expense_description (str): Descripción actual del gasto.
        amount (float): Monto actual del gasto.
        date (str): Fecha actual del gasto.
        category_id (int): ID de la categoría actual del gasto.
        subcategory_id (int): ID de la subcategoría actual del gasto.
    """
    parfecha = st.date_input("Fecha del gasto", value=date)

    # Obtiene las categorías disponibles.
    categorias = crud.get_categories()
    if categorias:
        categorias_nombres = [cat.name for cat in categorias]
        categorias_ids = [cat.id for cat in categorias]
        # Selector para elegir la categoría.
        parcategoria = st.selectbox(
            "Categoría",
            categorias_ids,
            format_func=lambda x: categorias_nombres[categorias_ids.index(x)],
            index=categorias_ids.index(category_id)
        )

        # Obtiene las subcategorías de la categoría seleccionada.
        subcategorias = crud.get_subcategories_by_category_id(parcategoria)
        if subcategorias:
            subcategorias_nombres = [sub.name for sub in subcategorias]
            subcategorias_ids = [sub.id for sub in subcategorias]
            # Selector para elegir la subcategoría.
            parsubcategoria = st.selectbox(
                "Subcategoría",
                subcategorias_ids,
                format_func=lambda x: subcategorias_nombres[subcategorias_ids.index(x)],
                index=subcategorias_ids.index(subcategory_id)
            )
        else:
            st.warning("No hay subcategorías disponibles para la categoría seleccionada.")
    else:
        st.warning("No hay categorías disponibles.")

    # Campos para editar la descripción y el monto del gasto.
    pardescripcion = st.text_input("Descripción", value=expense_description)
    parmonto = st.number_input("Monto", min_value=0.0, value=amount, step=0.01)

    if st.button("Guardar cambios"):
        # Llama a la función para actualizar el gasto en la base de datos.
        updated_expense = crud.update_expense(
            expense_id=expense_id,
            amount=parmonto,
            date=parfecha,
            subcategory_id=parsubcategoria,
            description=pardescripcion
        )
        if updated_expense:
            st.toast(f"Gasto '{updated_expense.description}' actualizado correctamente.")
            st.rerun()  # Reinicia la aplicación para reflejar los cambios.
        else:
            st.error("Error al actualizar el gasto.")

# Título de la página.
st.title(":material/shopping_cart: Registro de Gastos por Fecha")
st.header("Registrar Gasto")

# Creación de dos columnas para organizar el contenido.
c1, c2 = st.columns(2)

with c1:
    # Selector de fecha y categoría para registrar un nuevo gasto.
    parfecha = st.date_input("Fecha del gasto")
    categorias = crud.get_categories()
    if categorias:
        categorias_nombres = [cat.name for cat in categorias]
        categorias_ids = [cat.id for cat in categorias]
        parcategoria = st.selectbox(
            "Categoría",
            categorias_ids,
            format_func=lambda x: categorias_nombres[categorias_ids.index(x)]
        )

        # Obtiene las subcategorías de la categoría seleccionada.
        subcategorias = crud.get_subcategories_by_category_id(parcategoria)
        if subcategorias:
            subcategorias_nombres = [sub.name for sub in subcategorias]
            subcategorias_ids = [sub.id for sub in subcategorias]
            parsubcategoria = st.selectbox(
                "Subcategoría",
                subcategorias_ids,
                format_func=lambda x: subcategorias_nombres[subcategorias_ids.index(x)]
            )
        else:
            st.warning("No hay subcategorías disponibles para la categoría seleccionada.")

with c2:
    # Campos para ingresar la descripción y el monto del nuevo gasto.
    pardescripcion = st.text_input("Descripción")
    parmonto = st.number_input("Monto", min_value=0.0)
    st.caption(f"$ {parmonto:,.0f}")

# Botón para registrar un nuevo gasto.
if st.button("Registrar gasto"):
    if pardescripcion and parmonto > 0:
        # Llama a la función para crear un nuevo gasto en la base de datos.
        crud.create_expense(
            amount=parmonto,
            date=parfecha,
            description=pardescripcion,
            subcategory_id=parsubcategoria
        )
        st.success("Gasto registrado correctamente.")
    else:
        st.warning("Por favor, ingrese una descripción y un monto válido.")

# Lista de gastos registrados para la fecha seleccionada.
gastos = crud.get_expenses_by_date(parfecha)
if gastos:
    st.header(f"Gastos registrados para {parfecha}")
    for gasto in gastos:
        with st.container(horizontal=True, border=True, vertical_alignment="center"):
            st.write(f"{gasto.id}")
            st.write(f"{gasto.subcategory.category.name}")
            st.write(f"{gasto.subcategory.name}")
            st.write(f"{gasto.description}")
            st.write(f"${gasto.amount:,.2f}")
            st.button(
                ":material/edit:",
                key=f"edit_{gasto.id}",
                on_click=edit_expense,
                args=(gasto.id, gasto.description, gasto.amount, gasto.date, gasto.subcategory.category_id, gasto.subcategory_id),
                type="primary"
            )
            st.button(
                ":material/delete:",
                key=f"delete_{gasto.id}",
                on_click=delete_expense,
                args=(gasto.id, gasto.description),
                type="tertiary"
            )
else:
    st.info(f"No hay gastos registrados para {parfecha}.")
