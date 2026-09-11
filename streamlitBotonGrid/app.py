"""
Uso de energía por país y continente
-------------------------------------
Demo de la versatilidad de st.dataframe: LineChartColumn (mini-gráficos por fila),
ImageColumn (banderas) y ButtonColumn (nuevo, abre un popup con el detalle por país).

LIBRERÍAS UTILIZADAS Y COMANDOS DE INSTALACIÓN:
------------------------------------------------
1. pandas: Librería de Python fundamental para la manipulación, limpieza y análisis 
   de datos estructurados (tablas). Permite realizar operaciones complejas de manera vectorizada.
   - Instalación: pip install pandas

2. streamlit: Framework web de código abierto para Python que permite crear aplicaciones
   y dashboards interactivos de datos en minutos sin necesidad de saber HTML, CSS o JavaScript.
   - Instalación: pip install streamlit

Fuentes:
- primary-energy-use.csv: consumo de energía (TWh) por país y año (Our World in Data).
- country-and-continent-codes-list-csv.csv: mapeo país -> continente y código ISO alpha-2
  (usado para armar la URL de bandera en https://flagsapi.com/, sin depender de pycountry).
"""

import pandas as pd
import streamlit as st

# Configuración inicial de la página de Streamlit. Debe ser el primer comando de Streamlit llamado.
st.set_page_config(
    page_title="Uso de energía por continente",
    page_icon=":material/bolt:",
    layout="wide",
)

RUTA_ENERGIA = "primary-energy-use.csv"
RUTA_PAISES = "country-and-continent-codes-list-csv.csv"


@st.cache_data
def cargar_datos() -> pd.DataFrame:
    """
    Carga y limpia los conjuntos de datos de energía y de países, uniéndolos 
    en un solo DataFrame. Emplea la caché de Streamlit (@st.cache_data) para no 
    volver a leer los CSVs en cada recarga de la app.

    Returns:
        pd.DataFrame: DataFrame consolidado con información de energía, continentes y banderas.
    """
    # Se carga el CSV de energía y se renombra la columna para mayor claridad.
    energia = pd.read_csv(RUTA_ENERGIA).rename(columns={"Total energy supply": "Consumo"})

    # keep_default_na=False: el código alpha-2 de Namibia es literalmente "NA" y
    # pandas lo interpretaría como nulo (NaN) si se dejan los NA por defecto.
    paises = pd.read_csv(RUTA_PAISES, keep_default_na=False)
    
    # Transformación pandas: Elimina filas duplicadas basándose en el código de 3 letras.
    # Luego, selecciona únicamente las columnas que nos interesan usando una lista.
    paises = paises.drop_duplicates(subset="Three_Letter_Country_Code", keep="first")[
        ["Three_Letter_Country_Code", "Continent_Name", "Two_Letter_Country_Code"]
    ]

    # Transformación pandas (Merge/Join): 
    # Inner join: descarta automáticamente agregados regionales/income-groups del
    # dataset de energía (World, OWID_*, "... (EI)", etc.) que no son países reales.
    # Después del cruce, eliminamos la columna repetida 'Three_Letter_Country_Code'.
    datos = energia.merge(
        paises, left_on="Code", right_on="Three_Letter_Country_Code", how="inner"
    ).drop(columns="Three_Letter_Country_Code")

    # Creación de una nueva columna calculada: 
    # Se concatena texto con la columna Two_Letter_Country_Code para generar la URL de la bandera.
    datos["Bandera"] = (
        "https://flagsapi.com/" + datos["Two_Letter_Country_Code"] + "/flat/64.png"
    )
    return datos


def construir_resumen(df: pd.DataFrame, grupo_cols: list[str]) -> pd.DataFrame:
    """
    Agrupa los datos según las columnas especificadas y el año, calculando el consumo total.
    Luego extrae la serie histórica (para el mini-gráfico) y los datos del último año.
    
    Construido íntegramente con operaciones vectorizadas de pandas (groupby/idxmax/join),
    sin loops manuales sobre listas, lo que lo hace altamente eficiente.

    Args:
        df (pd.DataFrame): DataFrame original con la información del consumo.
        grupo_cols (list[str]): Columnas por las cuales se desea agrupar (ej. continente o país).

    Returns:
        pd.DataFrame: DataFrame resumen con la serie histórica y el último registro por grupo.
    """
    # 1. Agrupar por las columnas indicadas + Año, sumar el consumo y ordenar.
    agrupado = (
        df.groupby(grupo_cols + ["Year"], as_index=False)["Consumo"]
        .sum()
        .sort_values(grupo_cols + ["Year"])
    )
    
    # 2. Serie anual ascendente por grupo (requerida por LineChartColumn en Streamlit).
    # agg(list) toma todos los valores de consumo de un grupo y los convierte en una lista [10, 20, 30...].
    serie_anual = agrupado.groupby(grupo_cols)["Consumo"].agg(list).rename("Consumo por año")

    # 3. Extraer la fila del último año por cada grupo.
    # idxmax() encuentra el índice donde ocurre el año máximo (último año).
    # loc[] extrae esas filas específicas.
    ultimo_anio = agrupado.loc[agrupado.groupby(grupo_cols)["Year"].idxmax()].set_index(
        grupo_cols
    )[["Year", "Consumo"]].rename(columns={"Year": "Último año", "Consumo": "Total último año"})

    # 4. Unimos (join) la información del último año con la serie histórica creada en el paso 2
    # y reseteamos el índice para volver a tener las columnas agrupadas como columnas normales.
    return ultimo_anio.join(serie_anual).reset_index()


@st.dialog("Países", width="large")
def mostrar_popup_paises(continente: str, df: pd.DataFrame) -> None:
    """
    Crea un diálogo modal (popup) en Streamlit que muestra el detalle de consumo 
    por país para un continente específico.

    Args:
        continente (str): Nombre del continente seleccionado.
        df (pd.DataFrame): DataFrame completo con los datos a filtrar.
    """
    st.subheader(f"Consumo de energía por país — {continente}")

    # Filtrado de Pandas: Se toman únicamente las filas cuyo continente coincida.
    df_continente = df[df["Continent_Name"] == continente]
    
    # Se invoca la función de resumen pero ahora agrupando a nivel de país.
    resumen_paises = construir_resumen(df_continente, ["Code", "Entity", "Bandera"])
    
    # Se ordena el resumen de mayor a menor consumo del último año.
    resumen_paises = resumen_paises.sort_values(
        "Total último año", ascending=False
    ).rename(columns={"Entity": "País"})

    # Se dibuja la tabla en la interfaz de Streamlit, configurando columnas especiales.
    st.dataframe(
        resumen_paises[
            ["Bandera", "País", "Consumo por año", "Último año", "Total último año"]
        ],
        hide_index=True,
        use_container_width=True,
        column_config={
            "Bandera": st.column_config.ImageColumn("Bandera", width="small"), # Muestra la URL como imagen
            "País": st.column_config.TextColumn("País"),
            "Consumo por año": st.column_config.AreaChartColumn( # Genera el mini-gráfico de líneas con la lista
                "Consumo por año", width="medium"
            ),
            "Último año": st.column_config.NumberColumn("Último año", format="%d"),
            "Total último año": st.column_config.NumberColumn(
                "Total último año", format="%,d TWh"
            ),
        },
    )


def manejar_click_continente(resumen_continentes: pd.DataFrame, datos: pd.DataFrame) -> None:
    """
    Función de callback o manejador de eventos. Se ejecuta al presionar un botón de la tabla.
    Extrae el índice de la fila clicada desde st.session_state y abre el popup correspondiente.

    Args:
        resumen_continentes (pd.DataFrame): Datos resumidos por continente.
        datos (pd.DataFrame): Dataset general.
    """
    # st.session_state guarda el estado de interacciones. En este caso el click del botón.
    click = st.session_state.click_continente        
    # Extraemos el nombre del continente usando iloc de pandas sobre la fila (row) afectada.
    continente = resumen_continentes.iloc[click["row"]]["Continente"]
    # Invocamos la función del popup modal
    mostrar_popup_paises(continente, datos)


def main() -> None:
    """
    Función principal que orquesta la aplicación. 
    Carga datos, genera el resumen por continente y dibuja el DataFrame principal.
    """
    st.title(":material/bolt: Uso de energía por continente")
    st.caption(
        "Suma de consumo de energía por año y continente. Clic en **Ver países** "
        "para ver el detalle por país del continente, ordenado de mayor a menor."
    )

    datos = cargar_datos()

    # Generamos el resumen agrupado por Continente
    resumen_continentes = construir_resumen(datos, ["Continent_Name"])
    resumen_continentes = resumen_continentes.rename(
        columns={"Continent_Name": "Continente"}
    )
    
    # Transformación pandas: Utilizamos .apply con una función lambda para agregar
    # un ícono visual al texto de los botones.
    resumen_continentes["Ver países"] = resumen_continentes["Continente"].apply(lambda x: f":material/visibility: Ver países de {x}")
    
    # Ordenamos de mayor a menor y reseteamos el índice de Pandas (útil tras ordenar).
    resumen_continentes = resumen_continentes.sort_values(
        "Total último año", ascending=False
    ).reset_index(drop=True)

    # Dibuja la tabla principal con gráficos, formato de números y botones
    st.dataframe(
        resumen_continentes[
            [
                "Continente",
                "Consumo por año",
                "Último año",
                "Total último año",
                "Ver países",
            ]
        ],
        hide_index=True,
        use_container_width=True,
        column_config={
            "Continente": st.column_config.TextColumn("Continente"),
            "Consumo por año": st.column_config.LineChartColumn( # Genera el gráfico lineal histórico
                "Consumo por año (histórico)", width="large"
            ),
            "Último año": st.column_config.NumberColumn("Último año", format="%d"),
            "Total último año": st.column_config.NumberColumn(
                "Total último año", format="%,d TWh"
            ),
            "Ver países": st.column_config.ButtonColumn( # Columna especial de Streamlit para botones interactivos
                "Detalle",
                type="primary",                
                on_click=manejar_click_continente, # Evento a ejecutar al hacer click
                args=(resumen_continentes, datos), # Parámetros que recibe la función de evento
                key="click_continente",            # Llave en st.session_state que almacenará la interacción
            ),
        },
    )
    with st.expander("Ver detalles técnicos"):
        st.session_state.click_continente    
        resumen_continentes


if __name__ == "__main__":
    main()