# -----------------------------------------------------------------------------
# EXPLICACIÓN DE LIBRERÍAS Y COMPONENTES
# -----------------------------------------------------------------------------

# sqlmodel: Es una librería para interactuar con bases de datos SQL desde Python.
# Combina la validación de datos de Pydantic con el ORM de SQLAlchemy.
# - Session: Gestiona una "sesión" de conversación con la base de datos. Se usa para
#   añadir, modificar y eliminar objetos, y para ejecutar consultas.
# - select: Es una función que se utiliza para construir sentencias SQL SELECT
#   de una manera pythónica y segura, evitando la inyección de SQL.
# Comando de instalación: pip install sqlmodel

# modelos.dbdatos: Este es un módulo local de tu proyecto (un archivo llamado dbdatos.py
# dentro de una carpeta llamada modelos). Contiene la configuración de la base de datos
# (el 'engine') y las definiciones de los modelos (Category, Subcategory, Expense).
# Lo importamos con el alias 'db' para un acceso más corto.

# -----------------------------------------------------------------------------
# IMPORTACIÓN DE MÓDULOS Y COMPONENTES
# -----------------------------------------------------------------------------

# Importamos el módulo 'dbdatos' que contiene el 'engine' y los modelos.
import modelos.dbdatos as db
# Importamos los componentes necesarios de SQLModel para crear sesiones y consultas.
from sqlmodel import Session, select
# Importamos las clases de los modelos para poder trabajar con ellos (crear, leer, etc.).
from modelos.dbdatos import Category, Subcategory, Expense

# -----------------------------------------------------------------------------
# FUNCIONES CRUD PARA EL MODELO 'Category'
# CRUD: Create, Read, Update, Delete (Crear, Leer, Actualizar, Eliminar)
# -----------------------------------------------------------------------------

def create_category(name: str) -> Category:
    """
    Crea una nueva categoría en la base de datos.

    Args:
        name (str): El nombre de la nueva categoría que se va a crear.

    Returns:
        Category: El objeto de la categoría recién creada, incluyendo su ID asignado por la base de datos.
    """
    # El bloque 'with Session(db.engine) as session:' abre una conexión con la base de datos
    # que se cierra automáticamente al finalizar el bloque, incluso si ocurren errores.
    with Session(db.engine) as session:
        # Creamos una instancia del modelo Category con los datos proporcionados.
        category = Category(name=name)
        # Añadimos el nuevo objeto 'category' a la sesión. Esto lo prepara para ser guardado.
        session.add(category)
        # Confirmamos la transacción. En este punto, los cambios se guardan permanentemente en la base de datos.
        session.commit()
        # Refrescamos el objeto 'category' con los datos de la base de datos. Esto es útil
        # para obtener valores generados automáticamente, como el 'id'.
        session.refresh(category)
        return category

def get_categories() -> list[Category]:
    """
    Obtiene una lista de todas las categorías de la base de datos.

    Returns:
        list[Category]: Una lista que contiene todos los objetos de categoría encontrados.
    """
    with Session(db.engine) as session:
        # Creamos una consulta para seleccionar todos los registros de la tabla Category.
        # session.exec() ejecuta la consulta.
        categories = session.exec(select(Category)).all()
        # .all() obtiene todos los resultados de la consulta como una lista.
        return categories

def get_category_by_id(category_id: int) -> Category | None:
    """
    Busca y obtiene una categoría específica por su clave primaria (ID).

    Args:
        category_id (int): El ID de la categoría que se desea obtener.

    Returns:
        Category | None: El objeto de la categoría si se encuentra, o None si no existe una categoría con ese ID.
    """
    with Session(db.engine) as session:
        # session.get() es la forma más eficiente de obtener un objeto por su clave primaria.
        return session.get(Category, category_id)

def update_category(category_id: int, name: str) -> Category | None:
    """
    Actualiza el nombre de una categoría existente.

    Args:
        category_id (int): El ID de la categoría que se va a actualizar.
        name (str): El nuevo nombre para la categoría.

    Returns:
        Category | None: El objeto de la categoría actualizado, o None si no se encontró la categoría.
    """
    with Session(db.engine) as session:
        # Primero, obtenemos la categoría que queremos actualizar.
        category = session.get(Category, category_id)
        # Verificamos si la categoría fue encontrada.
        if category:
            # Modificamos el atributo 'name' del objeto.
            category.name = name
            # Guardamos los cambios en la base de datos.
            session.commit()
            # Refrescamos el objeto para asegurarnos de que contiene los datos actualizados.
            session.refresh(category)
        return category

def delete_category(category_id: int) -> bool:
    """
    Elimina una categoría de la base de datos.

    Args:
        category_id (int): El ID de la categoría que se va a eliminar.

    Returns:
        bool: True si la categoría se eliminó con éxito, False si no se encontró.
    """
    with Session(db.engine) as session:
        # Obtenemos la categoría a eliminar.
        category = session.get(Category, category_id)
        # Si la categoría existe...
        if category:
            # La marcamos para ser eliminada.
            session.delete(category)
            # Confirmamos la eliminación en la base de datos.
            session.commit()
            return True
        # Si la categoría no se encontró, retornamos False.
        return False

# -----------------------------------------------------------------------------
# FUNCIONES CRUD PARA EL MODELO 'Subcategory'
# -----------------------------------------------------------------------------

def create_subcategory(name: str, category_id: int) -> Subcategory:
    """
    Crea una nueva subcategoría y la asocia a una categoría existente.

    Args:
        name (str): El nombre de la nueva subcategoría.
        category_id (int): El ID de la categoría padre a la que pertenecerá.

    Returns:
        Subcategory: El objeto de la subcategoría recién creada.
    """
    with Session(db.engine) as session:
        subcategory = Subcategory(name=name, category_id=category_id)
        session.add(subcategory)
        session.commit()
        session.refresh(subcategory)
        return subcategory

def get_subcategories() -> list[Subcategory]:
    """
    Obtiene una lista de todas las subcategorías de la base de datos.

    Returns:
        list[Subcategory]: Una lista con todos los objetos de subcategoría.
    """
    with Session(db.engine) as session:
        subcategories = session.exec(select(Subcategory)).all()
        return subcategories

def get_subcategory_by_id(subcategory_id: int) -> Subcategory | None:
    """
    Busca y obtiene una subcategoría específica por su ID.

    Args:
        subcategory_id (int): El ID de la subcategoría a buscar.

    Returns:
        Subcategory | None: El objeto de la subcategoría si se encuentra, o None si no existe.
    """
    with Session(db.engine) as session:
        return session.get(Subcategory, subcategory_id)

def get_subcategories_by_category_id(category_id: int) -> list[Subcategory] | None:
    """
    Obtiene todas las subcategorías que pertenecen a una categoría específica.

    Args:
        category_id (int): El ID de la categoría padre.

    Returns:
        list[Subcategory] | None: Una lista de objetos de subcategoría, o None si no se encuentra ninguna.
    """
    with Session(db.engine) as session:
        # Construimos una consulta que selecciona subcategorías
        # y las filtra con una cláusula WHERE para que coincida el category_id.
        statement = select(Subcategory).where(Subcategory.category_id == category_id)
        subcategories = session.exec(statement).all()
        if subcategories:
            return subcategories
        else:
            return None

def update_subcategory(subcategory_id: int, name: str) -> Subcategory | None:
    """
    Actualiza el nombre de una subcategoría existente.

    Args:
        subcategory_id (int): El ID de la subcategoría a actualizar.
        name (str): El nuevo nombre para la subcategoría.

    Returns:
        Subcategory | None: El objeto de la subcategoría actualizado, o None si no se encontró.
    """
    with Session(db.engine) as session:
        subcategory = session.get(Subcategory, subcategory_id)
        if subcategory:
            subcategory.name = name
            session.commit()
            session.refresh(subcategory)
        return subcategory

def delete_subcategory(subcategory_id: int) -> bool:
    """
    Elimina una subcategoría de la base de datos.

    Args:
        subcategory_id (int): El ID de la subcategoría a eliminar.

    Returns:
        bool: True si se eliminó con éxito, False si no se encontró.
    """
    with Session(db.engine) as session:
        subcategory = session.get(Subcategory, subcategory_id)
        if subcategory:
            session.delete(subcategory)
            session.commit()
            return True
        return False

# -----------------------------------------------------------------------------
# FUNCIONES CRUD PARA EL MODELO 'Expense'
# -----------------------------------------------------------------------------

def create_expense(amount: float, date: str, subcategory_id: int, description: str = "") -> Expense:
    """
    Crea un nuevo registro de gasto.

    Args:
        amount (float): El monto del gasto.
        date (str): La fecha del gasto en formato de texto (ej: "AAAA-MM-DD").
        subcategory_id (int): El ID de la subcategoría a la que pertenece el gasto.
        description (str, optional): Una descripción opcional del gasto. Por defecto es "".

    Returns:
        Expense: El objeto del gasto recién creado.
    """
    # NOTA: El modelo original no tenía category_id en Expense, así que se ha eliminado delos parámetros de la función.
    with Session(db.engine) as session:
        expense = Expense(
            amount=amount,
            date=date,
            subcategory_id=subcategory_id,
            description=description
        )
        session.add(expense)
        session.commit()
        session.refresh(expense)
        return expense

def get_expenses() -> list[Expense]:
    """
    Obtiene una lista de todos los gastos registrados en la base de datos.

    Returns:
        list[Expense]: Una lista con todos los objetos de gasto.
    """
    with Session(db.engine) as session:
        expenses = session.exec(select(Expense)).all()
        return expenses

def get_expenses_by_date(date: str) -> list[Expense] | None:
    """
    Obtiene todos los gastos registrados en una fecha específica.

    Args:
        date (str): La fecha a buscar en formato "AAAA-MM-DD".

    Returns:
        list[Expense] | None: Una lista de gastos de esa fecha, o None si no hay ninguno.
    """
    with Session(db.engine) as session:
        # Filtramos los gastos donde el campo 'date' coincida con el valor proporcionado.
        statement = select(Expense).where(Expense.date == date)
        expenses = session.exec(statement).all()
        if expenses:
            return expenses
        else:
            return None

def get_expense_by_id(expense_id: int) -> Expense | None:
    """
    Busca y obtiene un gasto específico por su ID.

    Args:
        expense_id (int): El ID del gasto a buscar.

    Returns:
        Expense | None: El objeto de gasto si se encuentra, o None si no existe.
    """
    with Session(db.engine) as session:
        return session.get(Expense, expense_id)

def update_expense(expense_id: int, amount: float, date: str, subcategory_id: int, description: str = "") -> Expense | None:
    """
    Actualiza los detalles de un registro de gasto existente.

    Args:
        expense_id (int): El ID del gasto a actualizar.
        amount (float): El nuevo monto del gasto.
        date (str): La nueva fecha del gasto.
        subcategory_id (int): El nuevo ID de la subcategoría.
        description (str, optional): La nueva descripción.

    Returns:
        Expense | None: El objeto de gasto actualizado, o None si no se encontró.
    """
    with Session(db.engine) as session:
        expense = session.get(Expense, expense_id)
        if expense:
            # Actualizamos cada uno de los campos del objeto.
            expense.amount = amount
            expense.date = date
            expense.subcategory_id = subcategory_id
            expense.description = description
            session.commit()
            session.refresh(expense)
        return expense

def delete_expense(expense_id: int) -> bool:
    """
    Elimina un registro de gasto de la base de datos.

    Args:
        expense_id (int): El ID del gasto a eliminar.

    Returns:
        bool: True si el gasto se eliminó con éxito, False si no se encontró.
    """
    with Session(db.engine) as session:
        expense = session.get(Expense, expense_id)
        if expense:
            session.delete(expense)
            session.commit()
            return True
        return False