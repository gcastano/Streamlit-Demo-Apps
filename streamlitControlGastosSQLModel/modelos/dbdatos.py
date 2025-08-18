# -----------------------------------------------------------------------------
# EXPLICACIÓN DE LIBRERÍAS
# -----------------------------------------------------------------------------

# SQLModel: Es una librería para interactuar con bases de datos SQL desde Python.
# Combina las características de Pydantic (para validación de datos) y SQLAlchemy (un ORM para SQL).
# Facilita la creación de modelos de datos que son al mismo tiempo tablas en la base de datos y
# objetos de Python con tipos definidos.
# Comando de instalación: pip install sqlmodel

# typing: Este módulo proporciona soporte para "type hints" (indicaciones de tipo).
# Ayuda a que el código sea más legible y a detectar errores antes de la ejecución.
# Ya viene incluido en la instalación estándar de Python.
# Comando de instalación: (No se necesita, es parte de Python)

# datetime: Módulo de Python para trabajar con fechas y horas.
# Permite crear, manipular y formatear fechas.
# Ya viene incluido en la instalación estándar de Python.
# Comando de instalación: (No se necesita, es parte de Python)

# pandas: Es una librería fundamental para la manipulación y análisis de datos en Python.
# Proporciona estructuras de datos como el DataFrame, que es una tabla bidimensional
# muy potente y flexible.
# Comando de instalación: pip install pandas

# psycopg2-binary: Es un adaptador de base de datos PostgreSQL para Python. Permite que
# SQLAlchemy (y por lo tanto SQLModel) se comunique con una base de datos PostgreSQL.
# Se necesita al usar la URL de conexión "postgresql+psycopg2://...".
# Comando de instalación: pip install psycopg2-binary

# -----------------------------------------------------------------------------
# IMPORTACIÓN DE MÓDULOS Y COMPONENTES
# -----------------------------------------------------------------------------

from sqlmodel import SQLModel, MetaData, Field, Relationship, create_engine, Session
from typing import Optional, List
import datetime
import pandas as pd
import streamlit as st
# -----------------------------------------------------------------------------
# DEFINICIÓN DE MODELOS DE DATOS (TABLAS DE LA BASE DE DATOS)
# -----------------------------------------------------------------------------

class Category(SQLModel, table=True):
    """
    Representa una categoría principal de gastos.

    Attributes:
        id (Optional[int]): La clave primaria única para la categoría.
        name (str): El nombre de la categoría (ej: "Hogar", "Transporte").
        subcategories (List["Subcategory"]): Una lista de las subcategorías que pertenecen a esta categoría.
    """
    # __table_args__ permite configurar opciones adicionales para la tabla en la base de datos.
    # 'extend_existing': True evita errores si la tabla ya está definida en la metadata.
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    # Define la relación "uno a muchos" con la tabla Subcategory.
    # 'back_populates' conecta esta relación con el atributo 'category' en el modelo Subcategory.
    # 'cascade_delete=True' asegura que si se borra una categoría, todas sus subcategorías también se borren.
    subcategories: List["Subcategory"] = Relationship(back_populates="category", cascade_delete=True)


class Subcategory(SQLModel, table=True):
    """
    Representa una subcategoría de gastos, que pertenece a una categoría principal.

    Attributes:
        id (Optional[int]): La clave primaria única para la subcategoría.
        name (str): El nombre de la subcategoría (ej: "Supermercado", "Gasolina").
        category_id (int): La clave foránea que la vincula con la tabla Category.
        category (Optional[Category]): El objeto Category al que pertenece esta subcategoría.
        expenses (List["Expense"]): Una lista de los gastos asociados a esta subcategoría.
    """
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    # Define la clave foránea que apunta al 'id' de la tabla 'category'.
    category_id: int = Field(foreign_key="category.id")

    # Define la relación inversa con la tabla Category.
    # 'sa_relationship_kwargs={"lazy": "selectin"}' optimiza la carga de datos, cargando
    # la categoría relacionada al mismo tiempo que se carga la subcategoría, evitando consultas adicionales.
    category: Optional[Category] = Relationship(back_populates="subcategories", sa_relationship_kwargs={"lazy": "selectin"})
    # Define la relación "uno a muchos" con la tabla Expense.
    expenses: List["Expense"] = Relationship(back_populates="subcategory")

class Expense(SQLModel, table=True):
    """
    Representa un gasto individual registrado.

    Attributes:
        id (Optional[int]): La clave primaria única para el gasto.
        amount (float): La cantidad monetaria del gasto.
        date (datetime.date): La fecha en que se realizó el gasto.
        description (Optional[str]): Una descripción opcional del gasto.
        subcategory_id (int): La clave foránea que vincula el gasto con una Subcategory.
        subcategory (Optional[Subcategory]): El objeto Subcategory al que pertenece este gasto.
    """
    __table_args__ = {'extend_existing': True}
    id: Optional[int] = Field(default=None, primary_key=True)
    amount: float
    date: datetime.date
    description: Optional[str] = None
    # Define la clave foránea que apunta al 'id' de la tabla 'subcategory'.
    subcategory_id: int = Field(foreign_key="subcategory.id")

    # Define la relación inversa con la tabla Subcategory.
    # 'sa_relationship_kwargs={"lazy": "selectin"}' optimiza la carga de datos relacionados.
    subcategory: Optional[Subcategory] = Relationship(back_populates="expenses", sa_relationship_kwargs={"lazy": "selectin"})

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE LA CONEXIÓN A LA BASE DE DATOS
# -----------------------------------------------------------------------------

# URL de conexión a la base de datos PostgreSQL en Aiven.
# Formato: "dialecto+driver://usuario:contraseña@host:puerto/nombre_db?opciones"
# - postgresql+psycopg2: Indica que usaremos PostgreSQL con el driver psycopg2.
# - sslmode=require: Es una medida de seguridad que fuerza el uso de una conexión encriptada (SSL).
DATABASE_URL =st.secrets["URL_POSTGRES"]

# El "engine" es el punto central de comunicación con la base de datos.
# Gestiona las conexiones y la ejecución de comandos SQL.
engine = create_engine(DATABASE_URL)

# -----------------------------------------------------------------------------
# FUNCIONES AUXILIARES
# -----------------------------------------------------------------------------

def create_db_and_tables():
    """
    Crea todas las tablas definidas como modelos de SQLModel en la base de datos.

    Esta función utiliza la metadata de SQLModel, que ha recopilado la información
    de todas las clases que heredan de `SQLModel` y tienen `table=True`.
    Luego, se conecta a la base de datos a través del `engine` y ejecuta los
    comandos SQL necesarios (`CREATE TABLE ...`) para crear las tablas si no existen.
    """
    SQLModel.metadata.create_all(engine)

def sqlmodel_a_df(objects: List[SQLModel], set_index: bool = True) -> pd.DataFrame:
    """
    Convierte una lista de objetos SQLModel en un DataFrame de Pandas.

    Esta función es útil para pasar datos extraídos de la base de datos a un formato
    tabular que facilita el análisis y la manipulación con la librería pandas.

    Parameters:
    ----------
    objects (List[SQLModel]): Una lista de objetos de cualquier clase que herede de SQLModel.
                              Por ejemplo, una lista de objetos `Expense`.
    set_index (bool, optional): Si es `True`, establece la primera columna del DataFrame
                                (generalmente la clave primaria 'id') como el índice.
                                Por defecto es `True`.

    Returns:
    -------
    pd.DataFrame: Un DataFrame de pandas con los datos de los objetos.
    """

    # 1. Convertir cada objeto SQLModel a un diccionario de Python.
    # El método .dict() es heredado de Pydantic y serializa el objeto.
    # Ejemplo: Expense(id=1, amount=10.5) se convierte en {'id': 1, 'amount': 10.5}.
    records = [obj.dict() for obj in objects]

    # 2. Obtener los nombres de las columnas del primer objeto.
    # El método .schema()["properties"].keys() inspecciona el modelo y extrae
    # los nombres de todos sus campos (ej: 'id', 'amount', 'date', etc.).
    columns = list(objects[0].schema()["properties"].keys())

    # 3. Crear el DataFrame de pandas a partir de los diccionarios.
    # pd.DataFrame.from_records() es un método eficiente para crear un DataFrame
    # desde una lista de diccionarios. Se especifican las columnas para asegurar el orden.
    df = pd.DataFrame.from_records(records, columns=columns)

    # 4. Opcionalmente, establecer la primera columna como el índice del DataFrame.
    # df.set_index() transforma una columna en el índice, lo que puede facilitar
    # la búsqueda y alineación de datos. Si set_index es True, se usa la primera
    # columna de la lista 'columns' (que suele ser el 'id').
    return df.set_index(columns[0]) if set_index else df

# -----------------------------------------------------------------------------
# EJECUCIÓN
# -----------------------------------------------------------------------------

# Para crear las tablas en la base de datos por primera vez, se debe descomentar
# y ejecutar la siguiente línea de código.
# create_db_and_tables()