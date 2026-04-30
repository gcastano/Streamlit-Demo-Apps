# 📊 Chart Vision — AI Chart Analyzer

Aplicación Streamlit que analiza imágenes de gráficas usando Google Gemini y genera código Plotly para reproducirlas.

## Características

- 📷 **Carga de imágenes** · PNG, JPG, WEBP
- 🤖 **Análisis con Gemini** · Detecta tipo de gráfica, ejes, datos y colores
- 📋 **Editor de datos interactivo** · `st.data_editor` con tipos de columna automáticos
- 💻 **Editor de código** · Código Plotly editable directamente en la app
- ▶️ **Ejecución en vivo** · Renderiza la gráfica y la compara con el original

## Instalación

```bash
pip install -r requirements.txt
```

## Configuración

Crea el archivo `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "tu-api-key-aqui"
```

Obtén tu API Key en: https://aistudio.google.com/app/apikey

## Ejecución

```bash
streamlit run app.py
```

## Flujo de uso

1. **Sube** una imagen de cualquier tipo de gráfica
2. **Analiza** con Gemini (detecta tipo, extrae datos y esquema de colores)
3. **Edita** los datos en el editor interactivo si es necesario
4. **Genera** el código Plotly con un clic
5. **Edita** el código si deseas ajustes finos
6. **Ejecuta** y compara la gráfica generada con el original
