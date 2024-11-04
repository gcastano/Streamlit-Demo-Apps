import streamlit as st  # Importa la biblioteca Streamlit para crear la interfaz de usuario.
import db  # Importa el módulo db (probablemente personalizado) para interactuar con la base de datos.
from datetime import datetime  # Importa la clase datetime para trabajar con fechas y horas.

# Definimos los parámetros de configuración de la aplicación
st.set_page_config(
    page_title="Ejemplo CRUD con Streamlit y SQLModel", #Título de la página
    page_icon="📊", # Ícono
    layout="wide", # Forma de layout ancho o compacto
    initial_sidebar_state="expanded" # Definimos si el sidebar aparece expandido o colapsado
)

st.header("Ejemplo CRUD con :red-background[Streamlit] y :blue[SQLModel]")

# Obtiene la lista de roles desde la base de datos.
listaRoles = db.getRoles()
# Obtiene la lista de países desde la base de datos.
listaPaises = db.getCountries()

# Define una función para eliminar una encuesta por su ID.
def eliminarSurvey(id):    
    db.deleteSurvey(id)  # Elimina la encuesta de la base de datos.
    st.toast(f"Survey {id}:  Eliminado exitosamente")  # Muestra un mensaje de éxito al usuario.

# Define una función para mostrar un formulario de encuesta dentro de un diálogo.
@st.dialog("Administrar encuesta")  # Decora la función para que se muestre en un diálogo de Streamlit.
def verFormulario(id=None):  # Recibe el ID de la encuesta (opcional, para editar una existente).
    # Inicializa variables con valores predeterminados.
    val_role=None
    val_age=0
    val_years_of_experience=0
    val_country=None
    val_salary=0
    val_main_skills=None
    # Crea listas de roles y países para los selectores.
    roles=list(listaRoles["name"].unique())
    countries=list(listaPaises["name"].unique())
    # Si se proporciona un ID, carga los datos de la encuesta existente.
    if id:
        survey = db.getSurvey(id)
        val_role = roles.index(survey["role"].values[0])
        val_age= survey["age"].values[0]
        val_years_of_experience=survey["years_of_experience"].values[0]
        val_country=countries.index(survey["country"].values[0])
        val_salary=survey["salary"].values[0]
        val_main_skills=survey["main_skills"].values[0]
    # Crea un formulario con Streamlit.
    with st.form("frmSurvey"):
        # Divide el formulario en dos columnas.
        c1,c2 = st.columns(2)
        # Agrega campos al formulario.
        par_role = c1.selectbox("Rol",roles,index=val_role)    
        par_age = c2.number_input("Edad",value=val_age)
        par_years_of_experience =c1.number_input("Años de experiencia",value=val_years_of_experience)
        par_country =c2.selectbox("País",listaPaises['name'].unique(),index=val_country)    
        par_salary= c1.number_input("Salario equivalente en USD",value=val_salary)
        par_main_skills= c2.text_input("Habilidades principales, separadas por coma",value=val_main_skills)
        # Agrega un botón de envío al formulario.
        btnEnviar = st.form_submit_button("Enviar",type='primary')
        # Procesa el formulario cuando se envía.
        if btnEnviar:                        
            itemSurvey=db.SurveyResponse() # Crea una nueva instancia del objeto SurveyResponse.                       
            if id: # Si se proporciona un ID, actualiza la encuesta existente.
                itemSurvey.id=id
            # Asigna los valores del formulario al objeto SurveyResponse.
            itemSurvey.age= par_age
            itemSurvey.years_of_experience= par_years_of_experience
            itemSurvey.main_skills= par_main_skills
            itemSurvey.country_id =  int(listaPaises.loc[listaPaises["name"]==par_country,"id"].values[0])    
            itemSurvey.role_id =  int(listaRoles.loc[listaRoles["name"]==par_role,"id"].values[0])
            itemSurvey.salary= par_salary
            itemSurvey.submitted_at=datetime.now()
            db.saveSurvey(itemSurvey) # Guarda la encuesta en la base de datos.
            st.rerun() # Recarga la aplicación para reflejar los cambios.

# Divide la interfaz en dos columnas.
c1,c2 = st.columns([8,2])
with c1:
    # Muestra las encuestas en un DataFrame.
    dfSurveys = db.getSurveys()
    selected = st.dataframe(dfSurveys,on_select="rerun",selection_mode=["single-row"],use_container_width=True)    
with c2:
    # Agrega botones para crear, editar y eliminar encuestas.
    st.button("Nuevo",on_click=verFormulario,type="primary")
    if len(selected.selection.rows)>0:
        st.button("Editar",on_click=verFormulario,args=[dfSurveys.loc[selected.selection.rows[0],"id"]])    
        st.button("Eliminar",on_click=eliminarSurvey,args=[dfSurveys.loc[selected.selection.rows[0],"id"]])    

    
# st.write(st.session_state)
# st.write(selected.selection.rows)
# st.write(len(selected.selection.rows))