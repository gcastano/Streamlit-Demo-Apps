import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from PIL import Image

# Configura la página de Streamlit
st.set_page_config(
    page_title="Gráficos tipo publicación",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal de la aplicación
st.header("Gráficos mejorados para publicaciones")

# Carga de datos desde archivos CSV
dfDatos = pd.read_csv("./car-sales.csv")
dfDatosExportadores = pd.read_csv("./Exporters-of-Electric-motor-Vehicles-2018---2022.csv",usecols=['Continent', 'Country', 'Year','Trade Value','Trade Value Growth Value'])
dfDatosImportadores = pd.read_csv("./Importers-of-Electric-motor-Vehicles-2018---2022.csv",usecols=['Continent', 'Country', 'Year','Trade Value','Trade Value Growth Value'])
dfDatosImpoExpo=dfDatosImportadores.merge(dfDatosExportadores,on=['Continent', 'Country', 'Year'],suffixes=["_impo","_expo"])

# Función para aplicar formato a los gráficos
def aplicarFormatoChart(fig,bgcolor='#FFFFFF',verleyenda=False,margin = dict(l=20, r=20,b=100,t=100),colorGridY="silver",verLineaX=False,verLineaY=False,ejeXVisible=True,ejeYVisible=True,verXgrid=False,verYgrid=True,verTituloX=True,verTituloY=True,Xtickmode="auto",Ytickmode="auto",verSpikesX=False,verSpikesY=False):
    """Aplica formato predefinido a los gráficos de Plotly.

    Args:
        fig: Objeto de figura de Plotly.
        bgcolor: Color de fondo.
        verleyenda: Mostrar leyenda (True/False).
        margin: Márgenes del gráfico. dict(l=20, r=20,b=100,t=100)
        colorGridY: Color de la grilla del eje Y.
        verLineaX: Mostrar línea del eje X (True/False).
        verLineaY: Mostrar línea del eje Y (True/False).
        ejeXVisible: Mostrar eje X (True/False).
        ejeYVisible: Mostrar eje Y (True/False).
        verXgrid: Mostrar grilla del eje X (True/False).
        verYgrid: Mostrar grilla del eje Y (True/False).
        verTituloX: Mostrar título del eje X (True/False).
        verTituloY: Mostrar título del eje Y (True/False).
        Xtickmode: Modo de ticks del eje X. (linear,array,auto)
        Ytickmode: Modo de ticks del eje Y. (linear,array,auto)

    Returns:
        fig: Objeto de figura de Plotly con formato aplicado.
    """
    # Actualiza el diseño del gráfico
    fig.update_layout(paper_bgcolor=bgcolor, 
                      plot_bgcolor=bgcolor, 
                      margin=margin,                       
                      xaxis=dict(tickmode=Xtickmode), 
                      yaxis=dict(tickmode=Ytickmode))
    # Configura los ejes X e Y
    fig.update_xaxes(showline=verLineaX,
                    linewidth=2,
                    linecolor=colorGridY,
                    visible=ejeXVisible,
                    showgrid=verXgrid)
    fig.update_yaxes(showline=verLineaY,
                    linewidth=2,
                    linecolor=colorGridY,
                    visible=ejeYVisible,
                    showgrid=verYgrid)
    # Configura la leyenda y la grilla
    fig.update_layout(showlegend=verleyenda)
    fig.update_yaxes(gridcolor=colorGridY)
    fig.update_xaxes(gridcolor=colorGridY)
    # Configura el tamaño de la fuente de los ticks
    fig.update_xaxes(tickfont_size=17)
    fig.update_yaxes(tickfont_size=17)
    # Habilita los marcadores de los ejes (spikes)
    fig.update_xaxes(showspikes=verSpikesX)
    fig.update_yaxes(showspikes=verSpikesY)
    # Configura los ticks del eje X y Y
    fig.update_layout(xaxis=dict(ticks='outside',
                    ticklen=10,
                    tickcolor=colorGridY)
                    )
    fig.update_layout(yaxis=dict(ticks='outside',
                    ticklen=10,
                    tickcolor=colorGridY)
                      )
    # Oculta los títulos de los ejes si es necesario
    if not verTituloX:  fig.update_xaxes(title_text='')
    if not verTituloY:  fig.update_yaxes(title_text='')
    return fig

# Función para añadir la fuente al gráfico
def adicionarFuenteChart(fig,fuente,y=-0.2,x=0):
    """Añade la fuente al gráfico.

    Args:
        fig: Objeto de figura de Plotly.
        fuente: Texto de la fuente.
        y: Posición vertical de la fuente.

    Returns:
        fig: Objeto de figura con la fuente añadida.
    """
    fig.add_annotation(showarrow=False,
                    text=fuente,
                    font=dict(size=12),
                    xref='x domain',
                    x=x,
                    yref='y domain', y=y
                    )
    fig.update_layout(margin = dict(b=100))
    return fig

# Función para añadir texto al último punto del gráfico
def adicionarTextoUltimoPunto(fig,df,campoX,campoY,color):
    """Añade texto al último punto de una serie en el gráfico.

    Args:
        fig: Objeto de figura de Plotly.
        df: DataFrame con los datos.
        campoX: Nombre de la columna del eje X.
        campoY: Nombre de la columna del eje Y.
        color: Color del texto.

    Returns:
        fig: Objeto de figura con el texto añadido.
    """
    df=df.sort_values(campoX)
    valorX=df.iloc[-1][campoX]
    valorY=df.iloc[-1][campoY]
    fig.add_annotation(x=valorX, y=valorY, text=f"<span style='font-size:15px;color:{color};font-weight:bold'>{valorY:,.0f}</span>", showarrow=True, arrowhead=1)
    return fig

# Función para generar el título y subtítulo del gráfico
def generarTitulo(titulo,subtitulo,colorTitulo="black",colorSubtitulo="grey"):
    """Genera el título y subtítulo formateados en HTML.

    Args:
        titulo: Texto del título.
        subtitulo: Texto del subtítulo.
        colorTitulo: Color del título.
        colorSubtitulo: Color del subtítulo.

    Returns:
        str: Título y subtítulo formateados en HTML.
    """
    titulo = f"""<b><span style='font-size:25px;color:{colorTitulo}'>{titulo}</span></b></br></br><span style='color:{colorSubtitulo}'>{subtitulo}</span>"""
    return titulo

# Función para ubicar la leyenda
def ubicarLegenda(fig,yanchor="top",xanchor="left",y=0.99,x=0.01):
    """Ubica la leyenda en el gráfico.

    Args:
        fig: Objeto de figura de Plotly.
        yanchor: Anclaje vertical de la leyenda.
        xanchor: Anclaje horizontal de la leyenda.
        y: Posición vertical de la leyenda.
        x: Posición horizontal de la leyenda.

    Returns:
        fig: Objeto de figura con la leyenda ubicada.
    """
    return fig.update_layout(legend=dict(yanchor=yanchor, y=y, xanchor=xanchor, x=x))


def adicionarImagen(fig,rutaImagen):
    """Añade una imagen al gráfico.

    Args:
        fig: Objeto de figura de Plotly.
        rutaImagen: Ruta de la imagen.

    Returns:
        fig: Objeto de figura con la imagen añadida.
    """
    imagen=Image.open(rutaImagen)
    return fig.add_layout_image(
        dict(
            source=imagen,
            xref="paper", yref="paper",
            x=1, y=1.05,
            sizex=0.2, sizey=0.2,
            xanchor="right", yanchor="bottom"
        )
    )

def adicionarImagenFondo(fig,rutaImagen):
    """Añade una imagen de fondo al gráfico.

    Args:
        fig: Objeto de figura de Plotly.
        rutaImagen: Ruta de la imagen.

    Returns:
        fig: Objeto de figura con la imagen de fondo añadida.
    """
    imagen=Image.open(rutaImagen)
    return fig.add_layout_image(
            dict(
                source=imagen,
                xref="paper",
                yref="paper",
                x=0.25,
                y=1,
                sizex=0.8,
                sizey=0.8,
                # sizing="strcotaetch",
                opacity=0.5,
                layer="below")
        )


# --- Gráfico 1: Ventas de autos eléctricos vs Autos no eléctricos ---

colorVerde="#3FA796"
colorRojo = "#B06161"
dfDatosGrafico=dfDatos[dfDatos["Entity"]=="World"]

titulo=generarTitulo(titulo="Ventas de autos eléctricos vs Autos no eléctricos",subtitulo="Ventas año a año de vehículos eléctricos vs los no eléctricos")
fig = px.line(data_frame= dfDatosGrafico,
              x='Year',
              y=["Electric cars sold","Non-electric car sales"],
              title=titulo,
              height=600, 
              labels={'Year':'Año',
                      'Electric cars sold':'Autos eléctricos',
                      'Non-electric car sales':'Autos no Eléctricos',
                      'value':'Unidades vendidas'}, 
              markers=True, 
              color_discrete_map={'Electric cars sold':colorVerde,'Non-electric car sales':colorRojo})
fig = aplicarFormatoChart(fig,verLineaX=True, verXgrid=True,verYgrid=False, ejeYVisible=False,verTituloX=False, Xtickmode="linear")

# Añade una línea vertical para indicar la pandemia
fig.add_vline(x=2020, line_width=1, line_dash="dash", line_color="red", annotation_text="Pandemia 2020", annotation_position="top left")
# Cambia la posición de los ejes
fig.update_layout(xaxis={'side': 'bottom'}, 
                  yaxis={'side': 'right'})
# Añade anotaciones para las series
fig.add_annotation(x=2012, y=4000000, text=f"<span style='font-size:15px;color:{colorVerde}'>Autos eléctricos</span>", showarrow=False, arrowhead=1)
fig.add_annotation(x=2012, y=63000000, text=f"<span style='font-size:15px;color:{colorRojo}'>Autos no eléctricos</span>", showarrow=False, yshift=10)
# Añade texto al último punto de cada serie
fig = adicionarTextoUltimoPunto(fig,dfDatosGrafico,campoX="Year",campoY="Electric cars sold",color=colorVerde)
fig = adicionarTextoUltimoPunto(fig,dfDatosGrafico,campoX="Year",campoY="Non-electric car sales",color=colorRojo)
# Añade la fuente del gráfico
fig = adicionarFuenteChart(fig,"Data sources: International Energy Agency. Global EV Outlook 2024. – processed by <a href='https://ourworldindata.org/electric-car-sales'> Our World In Data</a>")
# Personaliza la información que se muestra al pasar el mouse sobre los puntos
fig.update_traces(hovertemplate = "<span style='font-size:20px;background-color:ghostwhite'>En el Año <b>%{x}</b> las ventas<br>fueron de <b>%{y:,.0f}</b> autos</span>")
# Muestra el gráfico en dos columnas
c1,c2 = st.columns(2)
with c1:
    st.plotly_chart(fig,use_container_width=True,key="chart1")
with c2:
    fig2 = aplicarFormatoChart(fig,verYgrid=True,verTituloX=False,verLineaX=True,Xtickmode="linear")
    st.plotly_chart(fig2,use_container_width=True,key="chart2")



# --- Gráfico 2: China lidera la venta de autos eléctricos ---

topCountries = ['China','United States','Germany','South Korea','Japan','Belgium']
dfDatos=dfDatos[~dfDatos['Entity'].isin(['Europe','European Union (27)','World'])]
dfDatos['China']=np.where(dfDatos['Entity']=='China',"China","Other Countries")
dfDatos['topCountries']=np.where(dfDatos['Entity'].isin(topCountries),dfDatos['Entity'],"Otros países") 
dfPaises=dfDatos[~dfDatos['Entity'].isin(['Europe','European Union (27)','World'])]
colores=["#C62E2E","#14658B","#187EAD","#1D97CF","#23B6FA","#22B2F5","#88d2f5"]

titulo = generarTitulo(titulo="China lidera la venta de autos eléctricos", subtitulo="A partir del 2020 las ventas de autos eléctricos aumentaron en los principales productores", colorTitulo="#3A98B9")
dfPaisesGrupo=dfPaises.groupby(["Year","topCountries"])["Electric cars sold","Non-electric car sales"].sum().reset_index().sort_values(["Year","Electric cars sold"], ascending=[True,False])
fig = px.line(data_frame=dfPaisesGrupo, 
              x='Year', 
              y="Electric cars sold", 
              color="topCountries", 
              title=titulo, width=1000, height=600, 
              labels={'Year':'Año','Electric cars sold':'Autos eléctricos', 
                      'Non-electric car sales':'Autos no Eléctricos', 
                      'value':'Unidades vendidas','topCountries':"Principales productores"}, 
              color_discrete_sequence=colores, custom_data=["topCountries","Non-electric car sales"])
fig = aplicarFormatoChart(fig,verLineaX=False,verleyenda=True)

# Añade un rectángulo vertical para indicar el periodo post-pandemia
fig.add_vrect(x0='2021', x1='2023',line_width=3, line_dash="solid", line_color="#DDE6ED",fillcolor='#DDDDDD',opacity=0.2,annotation_text="Post Pandemia Covid 19", annotation_position="top left")
# Cambia la posición de los ejes
fig.update_layout(xaxis={'side': 'bottom'}, yaxis={'side': 'right'})
# Ubica la leyenda
fig =ubicarLegenda(fig)
# Añade una imagen de fondo
fig=adicionarImagenFondo(fig,"electric-car-transport-svgrepo-com.png")
# Resalta la línea de China
fig.update_traces(line={'width': 4}, selector = ({'name':'China'}))
# Personaliza la información que se muestra al pasar el mouse sobre los puntos
fig.update_traces(hovertemplate = "<span style='font-size:15px;background-color:ghostwhite'><b>%{customdata[0]}</b> en el año <b>%{x}</b><br>tuvo ventas de <b>%{y:,.0f}</b> autos eléctricos</br> y <b>%{customdata[1]:,.0f}</b> autos no eléctricos</span>")


c1,c2 = st.columns(2)
with c1:
    st.plotly_chart(fig,use_container_width=True)
with c2:
    # --- Gráfico 2 (versión de barras) ---
    fig = px.bar(data_frame= dfPaisesGrupo, x='Year', y="Electric cars sold", color="topCountries", title=titulo, width=1000, height=600, labels={'Year':'Año','Electric cars sold':'Autos eléctricos', 'Non-electric car sales':'Autos no Eléctricos', 'value':'Unidades vendidas','topCountries':"Principales productores"}, color_discrete_sequence=colores, barmode="group", custom_data=["topCountries"])
    fig = aplicarFormatoChart(fig,verLineaX=False,verleyenda=True)
    fig =ubicarLegenda(fig)
    fig=adicionarImagen(fig,"electric-car-svgrepo-com.png")
    fig.update_traces(hovertemplate = "<span style='font-size:15px;background-color:ghostwhite'><b>%{customdata[0]}</b> en el año <b>%{x}</b><br>tuvo ventas de <b>%{y:,.0f}</b> </br>autos eléctricos</span>")
    st.plotly_chart(fig,use_container_width=True)


# --- Gráfico 3: Importaciones vs Exportaciones de autos eléctricos en 2022 ---

titulo = generarTitulo(titulo="Importaciones vs Exportaciones de autos eléctricos en 2022", 
                       subtitulo=f"Cómo se comportaron los <span style='color:{colorRojo};font-weight:bold'>principales productores</span> de autos en 2022 vs el resto del mundo", colorTitulo="#3A98B9", colorSubtitulo="silver")
dfDatosImpoExpo["topCountries"]=np.where(dfDatosImpoExpo['Country'].isin(topCountries),dfDatosImpoExpo['Country'],"") 
dfDatosImpoExpo["topCountriesExpo"]=np.where(dfDatosImpoExpo['Country'].isin(topCountries),dfDatosImpoExpo["Trade Value_expo"],"") 
fig=px.scatter(dfDatosImpoExpo[dfDatosImpoExpo["Year"]==2022],
               x="Trade Value_impo",y="Trade Value Growth Value_expo", 
               custom_data=["Country","topCountriesExpo","Trade Value_expo"], 
               size="Trade Value_expo", 
               color="Country", 
               labels={"Trade Value_impo":"Importaciones en USD",
                       "Trade Value_expo":"Exportaciones en USD",
                       "Trade Value Growth Value_expo":"Aumento de exportaciones en USD"}, 
               color_discrete_sequence=["#187EAD"], 
               color_discrete_map={x:colorRojo for x in dfDatosImpoExpo["Country"].unique() if x in topCountries}, 
               title=titulo, text="topCountries")

fig.update_traces(textposition='top center')
fig.update_traces(hovertemplate = "<span style='font-size:15px;background-color:ghostwhite'><b>%{customdata[0]}</b> en el año <b>2022</b><br>tuvo exportaciones de <b>USD $ %{customdata[2]:,.0f}</b>")
fig.update_traces(texttemplate = "<b>%{text}</b><br>%{customdata[1]:$,.0f}")
fig=aplicarFormatoChart(fig,verSpikesX=True,verSpikesY=True)
fig = adicionarFuenteChart(fig,fuente="Fuente: The Observatory of Economic Complexity (OEC) https://oec.world/en/profile/hs/electric-motor-vehicles",y=-0.3,x=-0.05)
fig.update_layout(yaxis_tickprefix = 'USD $',xaxis_tickprefix = 'USD $')

st.plotly_chart(fig,use_container_width=True)


# --- Gráfico 4: Exportaciones de autos eléctricos por país en 2022 ---

titulo = generarTitulo(titulo="Exportaciones de autos eléctricos por país en 2022", subtitulo=f"Alemania sigue en la cabeza pero China se va acercando", colorTitulo="#3A98B9", colorSubtitulo="silver")

df=dfDatosImpoExpo[dfDatosImpoExpo["Year"]==2022]
fig = px.treemap(df, 
                 path=[px.Constant("Mundo"), 'Continent', 'Country'], 
                 values="Trade Value_expo", color="Trade Value_expo",
                 color_continuous_scale=["#C5EBFC","#4CC0F6",colorRojo], 
                 color_continuous_midpoint=np.average(df["Trade Value_expo"], weights=df["Trade Value_expo"]), title=titulo)
fig.update_traces(textinfo='label+text+value+percent root')
fig.update_traces(texttemplate='<span style="font-size:1.2em;font-weight:bold">%{label}</span> <br> $%{value:,.0f} <br> %{percentRoot}')
fig.update_traces(marker=dict(cornerradius=5))
fig.update_traces(hovertemplate = "<span style='font-size:15px;background-color:ghostwhite'><b>%{label}</b> en el año <b>2022</b><br>tuvo exportaciones por valor de <b>USD $ %{value:,.0f}</b></span>")

st.plotly_chart(fig,use_container_width=True)