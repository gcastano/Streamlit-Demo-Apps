import streamlit as st
from jinja2 import Environment, FileSystemLoader
from pyhtml2pdf import converter
from datetime import date
import io
import glob

# ==========================================
# EXPLICACIÓN DE LIBRERÍAS E INSTALACIÓN
# ==========================================
# 1. streamlit: Framework para crear aplicaciones web de datos rápidamente.
#    Comando: pip install streamlit
# 2. jinja2: Motor de plantillas para Python. Nos permite inyectar variables en código HTML.
#    Comando: pip install Jinja2
# 3. pyhtml2pdf: Herramienta para convertir código HTML renderizado a un archivo PDF.
#    Comando: pip install pyhtml2pdf
# 4. datetime: Librería estándar de Python para manejar fechas.
# 5. io: Librería estándar para manejar flujos de datos (streams), útil para manejar el PDF en memoria.
# 6. glob: Librería estándar para buscar archivos que coincidan con un patrón (ej. *.html).

# Configuración inicial de la página de la aplicación
st.set_page_config(page_title="Generador de Facturas", layout="wide")
st.title(":material/receipt_long: Generador de Facturas PDF")

# Configuración del entorno de Jinja2 para cargar plantillas desde el directorio actual
env = Environment(loader=FileSystemLoader("."))

@st.dialog(title="Vista Previa de la Plantilla", width="large")
def previewPlantilla(rutaPlantilla):
    """
    Muestra una vista previa del código HTML crudo de la plantilla seleccionada.
    
    Args:
        rutaPlantilla (str): La ruta del archivo .html a visualizar.
    """
    # Se abre el archivo en modo lectura con codificación utf-8 para soportar tildes/ñ
    with open(rutaPlantilla, "r", encoding="utf-8") as f:
        template_content = f.read()
    # st.html renderiza el HTML directamente en la interfaz
    st.html(template_content)

@st.cache_data
def generarPDF(html_content):
    """
    Convierte el contenido HTML (string) a un objeto de bytes PDF.
    Utiliza un decorador de caché para evitar regenerar el mismo PDF si el HTML no cambia.

    Args:
        html_content (str): El código HTML ya renderizado con los datos.

    Returns:
        io.BytesIO: El archivo PDF en memoria listo para descarga o visualización.
    """
    pdf_bytes = io.BytesIO()
    # La función converter toma el string HTML y lo guarda en el buffer de bytes
    converter.convert(html_content, pdf_bytes)    
    return pdf_bytes

@st.dialog(title="Factura Generada", width="large")
def abrirPreview(html_content):
    """
    Abre una ventana modal (diálogo) para mostrar el PDF generado y ofrecer la descarga.

    Args:
        html_content (str): El código HTML final con los datos insertados.
    """
    # Llamada a la función de conversión
    pdf_bytes = generarPDF(html_content)
    
    # Botón de descarga para el usuario
    st.download_button(
        label="⬇️ Descargar PDF",
        data=pdf_bytes,
        file_name=f"{invoice_number}.pdf",
        mime="application/pdf"
    )
    st.success("✅ Factura generada exitosamente")
    
    # Visualizador de PDF nativo de Streamlit
    st.pdf(pdf_bytes)


# ==========================================
# SECCIÓN: CONFIGURACIÓN Y SELECCIÓN DE PLANTILLA
# ==========================================
st.header("Configuración")

# Búsqueda de archivos HTML en la carpeta 'plantillas' usando glob
archivo = st.selectbox("Selecciona una plantilla de factura", 
                        options=glob.glob("plantillas/*.html"))

# Normalización de rutas para evitar errores en sistemas Windows (cambia backslash por slash)
archivo = archivo.replace('\\','//')

# Carga de la plantilla seleccionada en Jinja2
template_content = env.get_template(f"./{archivo}")

# Botón para activar el modal de vista previa
st.button("👁️ Vista Previa de la Plantilla", on_click=previewPlantilla, args=(archivo,))


# ==========================================
# SECCIÓN: FORMULARIO DE DATOS
# ==========================================
# Uso de columnas para organizar el layout visualmente
col1, col2 = st.columns(2)

with col1:
    st.subheader("Datos de la Empresa")
    company_name = st.text_input("Nombre Empresa", "Mi empresa de consultoría")
    company_address = st.text_input("Dirección", "Medellín, Colombia")
    company_email = st.text_input("Email", "facturacion@miempresa-consultora.com")
    currency = st.selectbox("Moneda", ["USD", "COP", "EUR"])

with col2:
    st.subheader("Datos de la Factura")
    invoice_number = st.text_input("Número Factura", "INV-0001")
    invoice_date = st.date_input("Fecha Emisión", date.today())
    
    # Lógica condicional para mostrar u ocultar la fecha de vencimiento
    if st.checkbox("Agregar Fecha de Vencimiento"):
        due_date = st.date_input("Fecha Vencimiento")
    else:
        due_date = None
    
st.subheader("Datos del Cliente")
col1, col2 = st.columns(2)
with col1:
    client_name = st.text_input("Nombre Cliente", "Cliente Ejemplo S.A.S")
    taxes = st.number_input("Monto Impuestos", min_value=0.0)
with col2:
    client_email = st.text_input("Email Cliente", "cliente@empresa.com")
    client_price = st.number_input("Precio por Hora", min_value=0.0, value=30.0)

# ==========================================
# SECCIÓN: ITEMS DE LA FACTURA (Lógica de Lista)
# ==========================================
st.subheader("Items de la Factura")
items = [] # Lista para almacenar diccionarios con la info de cada item
num_items = st.number_input("Cantidad de items", min_value=1, max_value=10, value=1)

# Bucle para generar campos dinámicos según el número de items
for i in range(int(num_items)):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        # Se usa key único para evitar conflictos en Streamlit
        item_date = st.date_input(f"Fecha {i+1}", value=date.today(), key=f"date_{i}")
    with col2:
        hours = st.number_input(f"Horas {i+1}", min_value=0.5, step=0.5, key=f"hours_{i}")
    with col3:
        rate = st.number_input(f"Tarifa {i+1}", min_value=0.0, step=1.0, key=f"rate_{i}", value=client_price)
    with col4:
        task = st.text_input(f"Tarea {i+1}", "Descripción", key=f"task_{i}")
    
    # Agregamos los datos transformados a la lista 'items'
    # Nota: Transformamos la fecha a string isoformat para que Jinja2 la pueda leer fácilmente
    items.append({
        "date": item_date.isoformat(),
        "hours": hours,
        "rate": rate,
        "task_executed": task
    })
st.subheader("Totales")
with st.container(border=True,horizontal=True):
    subtotal = sum(item["hours"] * item["rate"] for item in items)
    st.metric("Subtotal", f"{subtotal:.2f} {currency}")
    if taxes:
        st.metric("Impuestos", f"{taxes:.2f} {currency}")
    # Cálculo del total final
    total = subtotal + taxes
    st.metric("Total", f"{total:.2f} {currency}")

st.subheader("Notas")
notes = st.text_area("Notas de la factura", "Pago dentro de los 15 días posteriores a la emisión.")

# ==========================================
# SECCIÓN: CÁLCULOS Y GENERACIÓN
# ==========================================
if st.button("📥 Generar PDF", type="primary"):    
    # Transformación de datos: Cálculo del subtotal usando una expresión generadora
    # Suma (horas * tarifa) de cada item en la lista
    subtotal = sum(item["hours"] * item["rate"] for item in items)
    
    # Cálculo del total final
    total = subtotal + taxes
    
    # Renderizar HTML con Jinja2
    # Aquí pasamos todas las variables de Python a la plantilla HTML
    html_content = template_content.render(
        company_name=company_name,
        company_address=company_address,
        company_email=company_email,
        invoice_number=invoice_number,
        invoice_date=invoice_date.isoformat(),
        due_date=due_date.isoformat() if due_date else None,
        client_name=client_name,
        client_email=client_email,
        currency=currency,
        items=items,
        subtotal=f"{subtotal:.2f}", # Formato string con 2 decimales
        taxes=f"{taxes:.2f}" if taxes else None,
        total=f"{total:.2f}",
        invoice_notes=notes
    )
    
    # Llamamos a la función que abre el modal y genera el PDF
    abrirPreview(html_content)