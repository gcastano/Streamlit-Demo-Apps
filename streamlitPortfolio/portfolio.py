import streamlit as st
import pandas as pd
from pyairtable import Api # https://pyairtable.readthedocs.io/en/stable/getting-started.html
from datetime import datetime

st.set_page_config(
    page_title="Germán Castaño - Portfolio",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargamos fecha actual
today = datetime.today().strftime("%Y")

# Cargamos librerías de MaterializeCSS, Material Icons y Font Awesome
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css">', unsafe_allow_html=True)
st.markdown('<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">', unsafe_allow_html=True)
st.markdown('<link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css" rel="stylesheet">', unsafe_allow_html=True)

# Adicionamos estilos personalizados para mejorar el diseño
customStyle ="""
            <style type="text/css">
            /*Aumenta el tamaño de las cards*/
            .card.large{
                height:550px!important;
            }
            /*Aumenta el contenido disponible*/
            .card.large .card-content{
                max-height:fit-content!important;
            }
            /* Aumenta la fuente de los tabs de Streamlit*/
            button[data-baseweb="tab"] p{
                font-size:20px!important;
            }
            /* Remueve el espacio en el encabezado por defecto de las apps de Streamlit */
            div[data-testid="stAppViewBlockContainer"]{
                padding-top:0px;
            }
            </style>
            """
# Cargamos los estilos
st.html(customStyle)

# Cargamos la API Keu
AIRTABLE_API_KEY = st.secrets.AIRTABLE_API_KEY
# Seleccionamos el base id de Airtable
AIRTABLE_BASE_ID='appEBN5hR96QYDdrn'

# Creamos el objeto de Airtable
api = Api(AIRTABLE_API_KEY)
# Cargamos las tablas
tblprofile = api.table(AIRTABLE_BASE_ID, 'profile')
tblprojects = api.table(AIRTABLE_BASE_ID, 'projects')
tblskills = api.table(AIRTABLE_BASE_ID, 'skills')
tblContacts = api.table(AIRTABLE_BASE_ID, 'contacts')

# Cargamos los valores recuperados de las tablas

profile = tblprofile.all()[0]['fields']
name=profile['Name']
profileDescription=profile['Description']
profileTagline=profile['tagline']
linkedInLink=profile['linkedin']
xLink=profile['x']
githubLink=profile['github']
picture=profile['picture'][0]['url']

# Creamos la plantilla de perfil con las clases CSS de MaterializeCSS 
# https://materializecss.com/
profileHTML=f"""
<div class="row">
<h1>{name} <span class="blue-text text-darken-3">Portfolio</span> </h1>
<h5>{profileTagline}</h5>
</div>
<div class="row">
    <div class="col s12 m12">
        <div class="card">
            <div class="card-content">
                <div class="row">                    
                    <div class="col s12 m2">
                        <img class="circle responsive-img" src="{picture}">
                        </div>
                        <div class="col s12 m10 ">
                            <span class="card-title">About me</span>
                            <p>{profileDescription}</p>
                            <div class="card-action">
                            <a href="{linkedInLink}" class="blue-text text-darken-3"><i class="fa-brands fa-linkedin fa-2xl"></i></i></a>
                            <a href="{githubLink}" class="blue-text text-darken-3"><i class="fa-brands fa-github fa-2xl"></i></a>
                            <a href="{xLink}" class="blue-text text-darken-3"><i class="fa-brands fa-x-twitter fa-2xl"></i></a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
            """
# Mostramos el HTML generado
st.html(profileHTML)

# Creamos los tabs de Streamlit
tabSkils,tabPortfolio,tabContact =st.tabs(['My skills','My projects','Contact'])

# Mostramos el tab de Skills
with tabSkils:
    skills=""
    # Hacemos el ciclo creando las plantillas de Skills
    for skill in tblskills.all(sort=['-Level']):
        # st.write(skill['fields'])
        skill=skill['fields']
        skillName = skill['Name']
        skillDescription = skill['Notes']    
        skillLevel = skill['Level']
        skillStars=""
        for i in range(1,6):
            if i<=skillLevel:
                skillStars=skillStars+'<i class="material-icons">star</i>'
            else:
                skillStars=skillStars+'<i class="material-icons">star_border</i>'
                
        skillYears = skill['startYear']   
        skillExperience = int(today) -int(skillYears)
        skillHTML = f"""                    
                <div class="col s12 m4">
                    <div class="card small">
                        <div class="card-content">
                            <span class="card-title">{skillName}</span>
                            <p>{skillDescription}</p>
                        </div>
                        <div class="card-action">
                            <div class="col s12 m6">
                                <p>Level:<br/> {skillStars}</p>
                            </div>
                            <div class="col s12 m6">
                                <p fon>Since:<br/> {skillYears} - {skillExperience} years</p>
                            </div>
                        </div>
                    </div>
                </div>
                    """
        skills=skills+skillHTML
    skillsHTML=f"""
            <div class="row">            
                {skills}       
            </div>       
        """     
    # Mostramos los skills
    st.html(skillsHTML) 
with tabPortfolio:       
    projects=""
    skillsHTML=""
    knowledgeHTML=""
    # Hacemos el ciclo creando las plantillas de proyectos
    for project in tblprojects.all():
        # st.write(skill['fields'])
        projectid= project['id']
        project=project["fields"]
        projectName = project['Name']        
        projectDescription = project['Description']    
        # Creamos la lista de Skills y Knowledge
        projectSkils = project['skills']
        skillsHTML=[f'<div class="chip green lighten-4">{p}</div>' for p in projectSkils]
        skillsHTML="".join(skillsHTML)
        projectKnowledge = project['Knowledge']        
        knowledgeHTML=[f'<div class="chip blue lighten-4">{p}</div>' for p in projectKnowledge]
        knowledgeHTML="".join(knowledgeHTML)
        
        projectLink = project['link'] 
        projectImageUrl = project['image'][0]['url']        
        projectHTML = f"""                    
                <div class="col s12 m6">
                    <div class="card large">                    
                        <div class="card-image" style="height:200px">
                            <a href="{projectLink}"><img src="{projectImageUrl}"></a>
                        </div>                        
                        <div class="card-content">
                            <span class="card-title">{projectName}</span>                                                        
                            <p>{projectDescription}</p>
                            <div class="row hide-on-small-only">
                            <div class="col s12 m6">
                            <h6>Knowledge:</h6>
                            {knowledgeHTML}
                            </div>
                            <div class="col s12 m6">
                            <h6>Skills:</h6>
                            {skillsHTML}
                            </div>
                            </div>
                        </div>  
                        <div class="card-action right-align">
                        <a href="{projectLink}" class="waves-effect waves-light btn-large white-text blue darken-3"><i class="material-icons left">open_in_new</i>View</a>                        
                        </div>                                               
                    </div>
                </div>
                    """
        projects=projects+projectHTML
    projectsHTML=f"""
            <div class="row">            
                {projects}       
            </div>       
        """     
    # Mostramos los proyectos
    st.html(projectsHTML)        
with tabContact:
    st.info("If you think I can help you with some of your projects or entrepreneurships, send me a message I'll contact you as soon as I can. I'm always glad to help")
    with st.container(border=True):
        parName = st.text_input("Your name")
        parEmail = st.text_input("Your email")
        parPhoneNumber = st.text_input("WhatsApp phone number, with country code")
        parNotes = st.text_area("What can I do for you")
        btnEnviar = st.button("Send",type="primary")
    if btnEnviar:
        tblContacts.create({"Name":parName,"email":parEmail,"phoneNumber":parPhoneNumber,"Notes":parNotes})
        st.toast("Message sent")
st.markdown('<script src="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js"></script>', unsafe_allow_html=True)
