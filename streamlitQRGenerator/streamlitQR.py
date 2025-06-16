# Importa la librería Streamlit, que permite crear aplicaciones web interactivas con Python.
# Comando para instalar: pip install streamlit
import streamlit as st

# Importa la librería qrcode, utilizada para generar códigos QR.
# Comando para instalar: pip install qrcode[pil] (el [pil] asegura que se instale con Pillow, necesario para imágenes)
import qrcode

# Importa BytesIO del módulo io, que permite manejar datos binarios en memoria (como si fueran archivos).
# Es parte de la librería estándar de Python, no requiere instalación adicional.
from io import BytesIO

# Importa diferentes estilos de módulos (los "píxeles" del QR) desde qrcode.
# Estos permiten cambiar la forma de los puntos del QR.
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer, SquareModuleDrawer, CircleModuleDrawer, VerticalBarsDrawer, HorizontalBarsDrawer, GappedSquareModuleDrawer

# Importa máscaras de color, específicamente SolidFillColorMask para definir colores sólidos para el frente y fondo del QR.
from qrcode.image.styles.colormasks import SolidFillColorMask

# Importa funcionalidades para generar QR en formato SVG.
import qrcode.image.svg

# Importa StyledPilImage para aplicar estilos avanzados (como colores y formas de módulos) a imágenes QR generadas con Pillow.
from qrcode.image.styledpil import StyledPilImage

# Configura la página de Streamlit: título de la pestaña del navegador y layout ancho.
st.set_page_config(page_title="Generador de QR", layout="wide")
# Establece el título principal visible en la aplicación web.
st.title("Generador de Códigos QR")

# Inicializa una variable en el estado de la sesión de Streamlit.
# 'procesado' se usará para recordar si un VCard QR ya fue generado,
# y así mantenerlo visible incluso si se cambian otros campos antes de volver a generar.
if "procesado" not in st.session_state:
    st.session_state.procesado = False

def hex_to_rgb(hex_color):
    """
    Convierte un código de color hexadecimal a una tupla RGB.

    Args:
        hex_color (str): Una cadena representando el código de color hexadecimal (ej., "#FF0000").

    Returns:
        tuple: Una tupla conteniendo los valores RGB (rojo, verde, azul) como enteros.
    """
    # Elimina el carácter '#' del inicio si está presente.
    hex_color = hex_color.lstrip("#")
    # Convierte los pares de caracteres hexadecimales a enteros (base 16) para R, G y B.
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def generate_qr_img(data, fmt="PNG", fill_color="#000000", back_color="#FFFFFF",drawer=CircleModuleDrawer()):
    """
    Genera una imagen de código QR con los datos y estilos especificados.

    Args:
        data (str): Los datos a codificar en el QR (texto, URL, VCard, etc.).
        fmt (str, optional): El formato de la imagen ("PNG" o "SVG"). Por defecto es "PNG".
        fill_color (str, optional): Color hexadecimal para los módulos (píxeles) del QR. Por defecto es "#000000" (negro).
        back_color (str, optional): Color hexadecimal para el fondo del QR. Por defecto es "#FFFFFF" (blanco).
        drawer (qrcode.image.styles.moduledrawers.pil.PilModuleDrawer, optional):
            El objeto que define el estilo de los módulos del QR.
            Por defecto es CircleModuleDrawer().

    Returns:
        BytesIO: Un buffer en memoria conteniendo los datos de la imagen del QR.
                 Retorna None si el formato no es soportado.
    """
    if fmt == "PNG":
        # Crea una instancia de QRCode con tamaño de caja y borde.
        qr = qrcode.QRCode(box_size=10, border=4)
        # Añade los datos al objeto QR.
        qr.add_data(data)
        # Compila los datos en una matriz QR. 'fit=True' asegura que se use el tamaño óptimo.
        qr.make(fit=True)
        # Crea una máscara de color usando los colores de frente y fondo convertidos a RGB.
        colorMask= SolidFillColorMask(front_color=hex_to_rgb(fill_color), back_color=hex_to_rgb(back_color))
        # Genera la imagen del QR usando StyledPilImage para aplicar el estilo de módulo y la máscara de color.
        img = qr.make_image(image_factory=StyledPilImage, module_drawer=drawer, color_mask=colorMask)
        # Crea un buffer en memoria para guardar la imagen.
        buf = BytesIO()
        # Guarda la imagen en el buffer en formato PNG.
        img.save(buf, format="PNG")
        # Regresa el cursor del buffer al inicio para que pueda ser leído.
        buf.seek(0)
        return buf
    elif fmt == "SVG":
        # Define la fábrica de imágenes para SVG con relleno sólido.
        # Nota: La librería qrcode para SVG no soporta directamente los module_drawers ni color_masks de la misma forma que para PNG con StyledPilImage.
        # Por ello, el SVG generado aquí será con los colores y formas por defecto, ignorando fill_color, back_color y drawer.
        factory=qrcode.image.svg.SvgFillImage
        # Genera la imagen SVG usando la fábrica especificada.
        img = qrcode.make(
            data,
            image_factory=factory
        )
        # Crea un buffer en memoria para guardar la imagen SVG.
        buf = BytesIO()
        # Guarda la imagen SVG en el buffer.
        img.save(buf)
        # Regresa el cursor del buffer al inicio.
        buf.seek(0)
        return buf
    return None # Si el formato no es ni PNG ni SVG


# Define dos columnas en la interfaz de Streamlit, c1 para configuración y c2 para el contenido principal.
# El ratio [1,9] significa que c1 ocupará 1/10 del ancho y c2 ocupará 9/10.
c1,c2 = st.columns([1,9 ])

# Contenido de la primera columna (configuración).
with c1:
    st.subheader("Configuración del QR")
    # Selector de color para los píxeles del QR.
    fill_color = st.color_picker("Color principal (píxeles QR)", "#000000", key="fill_v")
    # Selector de color para el fondo del QR.
    back_color = st.color_picker("Color de fondo", "#FFFFFF", key="back_v")
    # Menú desplegable para seleccionar el estilo de los píxeles del QR.
    modelDrawer = st.selectbox("Estilo de píxeles QR",
        ["Cuadrado", "Redondeado", "Círculo", "Barras Verticales", "Barras Horizontales", "Cuadrado con huecos"],
        index=0, key="model_v" # 'index=0' selecciona "Cuadrado" por defecto.
    )
    # Asigna el objeto drawer correspondiente según la selección del usuario.
    if modelDrawer == "Cuadrado":
        drawer = SquareModuleDrawer()
    elif modelDrawer == "Redondeado":
        drawer = RoundedModuleDrawer()
    elif modelDrawer == "Círculo":
        drawer = CircleModuleDrawer()
    elif modelDrawer == "Barras Verticales":
        drawer = VerticalBarsDrawer()
    elif modelDrawer == "Barras Horizontales":
        drawer = HorizontalBarsDrawer()
    else: # "Cuadrado con huecos"
        drawer = GappedSquareModuleDrawer()

# Contenido de la segunda columna (generación de QR).
with c2:
    # Control segmentado para elegir entre QR simple (texto/URL) o VCard.
    tabSegmento = st.segmented_control(label="", options=["QR Simple", "VCard"],default ="QR Simple", key="tab_v")

    if tabSegmento == "QR Simple":
        st.header("Generar QR desde texto o enlace")
        # Divide la columna c2 en dos subcolumnas para el área de texto y la vista previa del QR.
        c2_main, c2_preview = st.columns([8,2]) # c2_main es más ancha que c2_preview.
        with c2_main:
            # Área de texto para que el usuario ingrese los datos para el QR.
            qr_data = st.text_area("Introduce el texto o enlace para el QR", "")
        with c2_preview:
            # Si hay datos ingresados, se muestra la previsualización del QR.
            if qr_data:
                # Usa un contenedor con borde para agrupar la visualización del QR y los botones de descarga.
                with st.container(border=True):
                    st.subheader("QR")
                    # Genera la imagen PNG del QR.
                    png_buf = generate_qr_img(qr_data, "PNG", fill_color, back_color,drawer)
                    # Muestra la imagen PNG en la app.
                    st.image(png_buf)
                    # Botón para descargar la imagen PNG.
                    st.download_button("Descargar PNG", png_buf, file_name="qr.png", mime="image/png")
                    # Genera la imagen SVG del QR.
                    svg_buf = generate_qr_img(qr_data, "SVG", fill_color, back_color,drawer) # Los estilos no se aplican al SVG con el método actual.
                    # Obtiene los datos del buffer SVG.
                    svg_data = svg_buf.getvalue()
                    # Botón para descargar la imagen SVG.
                    st.download_button("Descargar SVG (Sin estilos)", svg_data, file_name="qr.svg", mime="image/svg+xml")

    else: # tabSegmento == "VCard"
        # Divide la columna c2 en dos subcolumnas para los campos de VCard y la vista previa del QR.
        c2_form, c2_preview_vcard = st.columns([8,2])
        with c2_form:
            st.header("Generar QR para VCard")
            # Campos de texto para los datos de la VCard.
            nombre = st.text_input("Nombre completo")
            telefono = st.text_input("Teléfono")
            email = st.text_input("Email")
            empresa = st.text_input("Empresa")
            cargo = st.text_input("Cargo")
            direccion = st.text_input("Dirección")
            sitio_web = st.text_input("Sitio web")
            # Botón para generar el QR de la VCard.
            btnGenerar = st.button("Generar VCard QR",type="primary")
        with c2_preview_vcard:
            # Si se presiona el botón de generar o si ya se había procesado antes.
            if btnGenerar or st.session_state.procesado:
                # Marca que se ha procesado para mantener visible el QR.
                st.session_state.procesado = True
                # Formatea los datos ingresados en el estándar VCard.
                vcard = f"""BEGIN:VCARD
VERSION:3.0
FN:{nombre}
ORG:{empresa}
TITLE:{cargo}
TEL;TYPE=WORK,VOICE:{telefono}
EMAIL;TYPE=PREF,INTERNET:{email}
ADR;TYPE=WORK:;;{direccion}
URL:{sitio_web}
END:VCARD
"""
                # Usa un contenedor con borde para la previsualización y descarga.
                with st.container(border=True):
                    st.subheader("QR VCard")
                    # Genera la imagen PNG del QR VCard.
                    png_buf = generate_qr_img(vcard, "PNG", fill_color, back_color,drawer)
                    # Muestra la imagen PNG.
                    st.image(png_buf)
                    # Botón para descargar el PNG.
                    st.download_button("Descargar PNG", png_buf, file_name="vcard_qr.png", mime="image/png")

                    # Genera la imagen SVG del QR VCard.
                    svg_buf = generate_qr_img(vcard, "SVG", fill_color, back_color,drawer) # Estilos no aplicados al SVG.
                    # Obtiene los datos del buffer SVG.
                    svg_data = svg_buf.getvalue()
                    # Botón para descargar el SVG.
                    st.download_button("Descargar SVG (Sin estilos)", svg_data, file_name="vcard_qr.svg", mime="image/svg+xml")