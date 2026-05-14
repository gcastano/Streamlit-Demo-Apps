# 🌍 Dashboard de Emisiones de CO2 Global

Este es un dashboard interactivo desarrollado con **Streamlit** para analizar datos históricos de emisiones de CO2 a nivel mundial. Permite explorar la evolución de las emisiones, comparativas entre países y la relación con el crecimiento económico (PIB).

## 🚀 Características

- **Visualizaciones Interactivas:**
  - Gráficos de líneas para tendencias históricas.
  - Mapas coropléticos (Choropleth) para distribución global.
  - Gráficos de área para el desglose de emisiones por fuente (Carbón, Petróleo, Gas, Cemento, etc.).
- **Indicadores Clave (KPIs):** Resumen dinámico de emisiones totales, promedios per cápita y tasas de crecimiento.
- **Explorador de Datos:** Tabla detallada con filtros específicos por país y año, con opción de descarga en CSV.
- **Diseño Moderno:** Interfaz estilizada con Material Icons y contenedores de bordes redondeados.

## 🛠️ Tecnologías Utilizadas

- **Streamlit:** Framework para la creación de aplicaciones web de datos.
- **Pandas:** Procesamiento y limpieza de datos.
- **Plotly:** Visualizaciones gráficas interactivas.
- **CSS Personalizado:** Estilización avanzada de componentes.

## 📋 Requisitos Previos

Asegúrate de tener Python instalado en tu sistema. Se recomienda el uso de un entorno virtual.

## ⚙️ Instalación

1. Clona este repositorio o descarga los archivos.
2. Instala las dependencias necesarias:
   ```bash
   pip install -r requirements.txt
   ```

## 🏃 Ejecución

Para iniciar la aplicación, ejecuta el siguiente comando en tu terminal:
```bash
streamlit run app.py
```

## 📊 Datos

El dashboard utiliza el archivo `visualizing_global_co2_data.csv` el cual contiene información detallada desde 1750 hasta 2021. Los metadatos y descripciones de las columnas se encuentran en `visualizing_global_CO2_emissions_data_dictionary.xlsx`.
Fuente: https://mavenanalytics.io/data-playground
