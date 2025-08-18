# Streamlit: Librería para crear aplicaciones web interactivas en Python.
# Instalación: pip install streamlit
import streamlit as st

# Importación de módulos locales para manejar la base de datos y operaciones CRUD.
import modelos.dbdatos as db
import crud

# Configuración de la página de Streamlit.
st.set_page_config(page_title="Gestión de Categorías", layout="wide")
st.title(":material/network_node: Gestión de Categorías")

# Inicialización de la sesión de la base de datos.
session = db.Session(db.engine)

@st.dialog("Editar Categoría")
def edit_category(category_id: int, new_name: str):
    """
    Diálogo para editar el nombre de una categoría existente.

    Args:
        category_id (int): ID de la categoría a editar.
        new_name (str): Nombre actual de la categoría.
    """
    parCategoria = st.text_input("Nombre categoría", value=new_name)

    if st.button("Guardar cambios"):
        # Llama a la función para actualizar la categoría en la base de datos.
        updated_category = crud.update_category(category_id, parCategoria)
        if updated_category:
            st.toast(f"Categoría {updated_category.name} actualizada correctamente.")
            st.rerun()  # Reinicia la aplicación para reflejar los cambios.
        else:
            st.error("Error al actualizar la categoría.")

@st.dialog("Eliminar Categoría")
def delete_category(category_id: int, category_name: str):
    """
    Diálogo para confirmar la eliminación de una categoría.

    Args:
        category_id (int): ID de la categoría a eliminar.
        category_name (str): Nombre de la categoría a eliminar.
    """
    st.write(f"¿Estás seguro de que quieres eliminar la categoría **'{category_name}'**?")
    st.write("Esta acción no se puede deshacer.")
    st.write("Si eliminas esta categoría, todas las subcategorías y gastos asociados también serán eliminados.")
    st.write("Por favor, confirma que deseas proceder con la eliminación.")

    with st.container(horizontal=True, border=True, vertical_alignment="center", horizontal_alignment="center"):
        if st.button(":material/check:", key=f"confirm_delete_{category_id}", type="primary"):
            # Llama a la función para eliminar la categoría de la base de datos.
            success = crud.delete_category(category_id)
            if success:
                st.toast("Categoría eliminada correctamente.")
                st.rerun()  # Reinicia la aplicación para reflejar los cambios.
            else:
                st.error("Error al eliminar la categoría.")
        if st.button("Cancelar"):
            st.rerun()  # Reinicia la aplicación para cerrar el diálogo.

@st.dialog("Editar Subcategoría")
def edit_subcategory(subcategory_id: int, new_name: str):
    """
    Diálogo para editar el nombre de una subcategoría existente.

    Args:
        subcategory_id (int): ID de la subcategoría a editar.
        new_name (str): Nombre actual de la subcategoría.
    """
    pasubCategoria = st.text_input("Nombre subcategoría", value=new_name)

    if st.button("Guardar cambios"):
        # Llama a la función para actualizar la subcategoría en la base de datos.
        updated_category = crud.update_subcategory(subcategory_id, pasubCategoria)
        if updated_category:
            st.toast(f"Subcategoría {updated_category.name} actualizada correctamente.")
            st.rerun()  # Reinicia la aplicación para reflejar los cambios.
        else:
            st.error("Error al actualizar la subcategoría.")

@st.dialog("Eliminar Subcategoría")
def delete_subcategory(subcategory_id: int, subcategory_name: str):
    """
    Diálogo para confirmar la eliminación de una subcategoría.

    Args:
        subcategory_id (int): ID de la subcategoría a eliminar.
        subcategory_name (str): Nombre de la subcategoría a eliminar.
    """
    st.write(f"¿Estás seguro de que quieres eliminar la subcategoría **'{subcategory_name}'**?")
    st.write("Esta acción no se puede deshacer.")
    st.write("Por favor, confirma que deseas proceder con la eliminación.")

    with st.container(horizontal=True, border=True, vertical_alignment="center", horizontal_alignment="center"):
        if st.button(":material/check:", key=f"confirm_delete_{subcategory_id}", type="primary"):
            # Llama a la función para eliminar la subcategoría de la base de datos.
            success = crud.delete_subcategory(subcategory_id)
            if success:
                st.toast("Subcategoría eliminada correctamente.")
                st.rerun()  # Reinicia la aplicación para reflejar los cambios.
            else:
                st.error("Error al eliminar la subcategoría.")
        if st.button("Cancelar"):
            st.rerun()  # Reinicia la aplicación para cerrar el diálogo.

def verSubcategoria(category_id: int, new_name: str):
    """
    Función para establecer el estado de la sesión y mostrar las subcategorías de una categoría seleccionada.

    Args:
        category_id (int): ID de la categoría seleccionada.
        new_name (str): Nombre de la categoría seleccionada.
    """
    st.session_state['category_id'] = category_id
    st.session_state['category_name'] = new_name

# Creación de dos columnas para organizar el contenido.
c1, c2 = st.columns(2)

with c1:
    st.header("Categorías")

    # Sección para agregar una nueva categoría.
    with st.container(horizontal=True, border=True, vertical_alignment="bottom"):
        nombre_nueva = st.text_input("Nombre de la nueva categoría", key="new_category")
        if st.button(":material/add:", key="add_category"):
            if nombre_nueva:
                # Llama a la función para crear una nueva categoría en la base de datos.
                crud.create_category(nombre_nueva)
                st.success("Categoría agregada correctamente.")
                st.rerun()  # Reinicia la aplicación para reflejar los cambios.
            else:
                st.error("El nombre no puede estar vacío.")

    # Lista de categorías existentes.
    categorias = crud.get_categories()
    for categoria in categorias:
        with st.container(horizontal=True, border=True, vertical_alignment="center"):
            st.write(f"{categoria.id}")
            st.write(f"{categoria.name}")
            st.button(":material/edit:", key=f"edit_{categoria.id}", on_click=edit_category, args=(categoria.id, categoria.name), type="primary")
            if st.button(":material/account_tree:", key=f"view_{categoria.id}", on_click=verSubcategoria, args=(categoria.id, categoria.name), type="secondary"):
                st.rerun()  # Reinicia la aplicación para mostrar las subcategorías.
            st.button(":material/delete:", key=f"delete_{categoria.id}", on_click=delete_category, args=(categoria.id, categoria.name), type="tertiary")

with c2:
    if 'category_id' in st.session_state:
        st.header(f"Subcategorías de {st.session_state['category_name']}")

        # Sección para agregar una nueva subcategoría.
        with st.container(horizontal=True, border=True, vertical_alignment="bottom"):
            nombre_nueva = st.text_input("Nombre de la nueva subcategoría", key="new_subcategory")
            if st.button(":material/add:", key="add_subcategory"):
                if nombre_nueva:
                    # Llama a la función para crear una nueva subcategoría en la base de datos.
                    crud.create_subcategory(nombre_nueva, st.session_state['category_id'])
                    st.success("Subcategoría agregada correctamente.")
                    st.rerun()  # Reinicia la aplicación para reflejar los cambios.
                else:
                    st.error("El nombre no puede estar vacío.")

        # Lista de subcategorías de la categoría seleccionada.
        subcategorias = crud.get_subcategories_by_category_id(st.session_state['category_id'])
        if subcategorias:
            for subcategoria in subcategorias:
                if subcategoria.category_id == st.session_state['category_id']:
                    with st.container(horizontal=True, border=True, vertical_alignment="center"):
                        st.write(f"{subcategoria.id}")
                        st.write(f"{subcategoria.name}")
                        st.button(":material/edit:", key=f"edit_sub_{subcategoria.id}", on_click=edit_subcategory, args=(subcategoria.id, subcategoria.name), type="primary")
                        st.button(":material/delete:", key=f"delete_sub_{subcategoria.id}", on_click=delete_subcategory, args=(subcategoria.id, subcategoria.name), type="tertiary")
    else:
        st.header("Subcategorías")
        st.info("Selecciona una categoría para ver sus subcategorías.")
