from typing import List, Optional
# pip install sqlmodel
from sqlmodel import Field, Relationship, SQLModel, create_engine, Session,select
from datetime import datetime
import pandas as pd
# pip install configparser
from configparser import ConfigParser

# Definición de la clase Country que representa la tabla de países
class Country(SQLModel, table=True):
    __table_args__ = {'extend_existing':True}
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, nullable=False)
    
    # Relación con la tabla SurveyResponse, un país puede tener múltiples respuestas de encuesta
    responses: List["SurveyResponse"] = Relationship(back_populates="country")

# Definición de la clase Role que representa la tabla de roles
class Role(SQLModel, table=True):
    __table_args__ = {'extend_existing':True} 
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, nullable=False)
    
    # Relación con la tabla SurveyResponse, un rol puede tener múltiples respuestas de encuesta
    responses: List["SurveyResponse"] = Relationship(back_populates="role")

# Definición de la clase SurveyResponse que representa la tabla de respuestas de la encuesta
class SurveyResponse(SQLModel, table=True):
    __table_args__ = {'extend_existing':True}
    id: Optional[int] = Field(default=None, primary_key=True)
    role_id: int = Field(foreign_key="role.id")
    age: int
    years_of_experience: int
    country_id: int = Field(foreign_key="country.id")
    salary: float
    main_skills: str
    submitted_at: datetime = Field(default=datetime.utcnow)
 

    # Relación con la tabla Role, una respuesta pertenece a un rol
    role: Role = Relationship(back_populates="responses")
    # Relación con la tabla Country, una respuesta pertenece a un país
    country: Country = Relationship(back_populates="responses")

# Función para crear la base de datos y las tablas
def create_db_and_tables():    
    SQLModel.metadata.create_all(engine)


# Credenciales de la base de datos
config = ConfigParser()
config.read("./config.ini")
DB_USERNAME=config["postgres"]["DB_USERNAME"]
DB_PASSWORD=config["postgres"]["DB_PASSWORD"]
DB_URL =config["postgres"]["DB_URL"] 
DB_PORT=config.getint("postgres","DB_PORT")
DB_NAME=config["postgres"]["DB_NAME"]

# Creación del motor de la base de datos
engine = create_engine(f'postgresql+psycopg2://{DB_USERNAME}:{DB_PASSWORD}@{DB_URL}:{DB_PORT}/{DB_NAME}')#, echo=True)
# Creación de la sesión de la base de datos
session = Session(engine)




# Función para convertir una lista de objetos SQLModel a un DataFrame de pandas
def sqmodel_to_df(objs: List[SQLModel]) -> pd.DataFrame:
    """Convert a SQLModel objects into a pandas DataFrame."""
    records = [i.model_dump() for i in objs]
    df = pd.DataFrame.from_records(records)
    return df

# Función para obtener todos los roles
def getRoles():
    with Session(engine) as session:
        statement = select(Role)
        roles = session.exec(statement).all()
        return sqmodel_to_df(roles)

# Función para obtener todas las encuestas
def getSurveys():
    with Session(engine) as session:
        statement = select(SurveyResponse)
        survey = session.exec(statement).all()        
        dfSurveys =sqmodel_to_df(survey)
        dfSurveys['role']=[x.role.name for x in survey]
        dfSurveys['country']=[x.country.name for x in survey]
        return dfSurveys[["id","role_id","role","age","years_of_experience","country_id","country","salary","main_skills","submitted_at"]]

# Función para obtener una encuesta por su ID
def getSurvey(id):
    with Session(engine) as session:        
        survey = session.get(SurveyResponse,int(id))
        dfSurveys =sqmodel_to_df([survey])
        dfSurveys['role']=survey.role.name
        dfSurveys['country']=survey.country.name
        return dfSurveys[["id","role_id","role","age","years_of_experience","country_id","country","salary","main_skills","submitted_at"]]

# Función para obtener todos los países
def getCountries():
    with Session(engine) as session:
        statement = select(Country)
        countries = session.exec(statement).all()
        return sqmodel_to_df(countries)

# Función para guardar un rol
def saveRole(itemRole):
    session.add(itemRole)
    session.commit()

# Función para guardar o actualizar una encuesta
def saveSurvey(itemSurvey):
    if itemSurvey.id==None:
        try:
            session.add(itemSurvey)
            session.commit()
        except:
            session.rollback()
    else:
        with session:
            # survey = SurveyResponse(id=itemSurvey.id)
            statement = select(SurveyResponse).where(SurveyResponse.id == int(itemSurvey.id))
            results = session.exec(statement)
            survey = results.one()
            survey.years_of_experience=itemSurvey.years_of_experience
            survey.age=itemSurvey.age
            survey.main_skills=itemSurvey.main_skills
            survey.country_id=itemSurvey.country_id
            survey.role_id=itemSurvey.role_id
            survey.salary=itemSurvey.salary
            survey.submitted_at=itemSurvey.submitted_at
            try:
                session.add(survey)            
                session.commit()
            except Exception as error:
                # Manejo de excepciones durante la actualización
                print("An exception occurred:", error) # An exception occurred: division by zero
                session.rollback()
            
    

# Función para eliminar una encuesta por su ID
def deleteSurvey(survey_id):
    with Session(engine) as session:
        statement = select(SurveyResponse).where(SurveyResponse.id == int(survey_id))
        results = session.exec(statement)
        survey = results.one()

        session.delete(survey)
        session.commit()
        
# Función para cargar países desde un archivo CSV
def loadCountries():
    dfCountries = pd.read_csv("world_countries_dataset.csv",usecols=['Country'])    
    for index, row in dfCountries.iterrows():
        itemCountry = Country(name=row["Country"])
        session.add(itemCountry)
    session.commit()

# Función para cargar roles predefinidos
def loadRoles():
    roles = ["Analista de datos","Científico de Datos","Ingeniero de Datos"]
    for roleItem in roles:
        newRole = Role(name=roleItem)    
        session.add(newRole)
    session.commit()


    
# itemSurvey=SurveyResponse(id=16)
# itemSurvey.age= 40
# itemSurvey.years_of_experience= 25
# saveSurvey(itemSurvey)
# getSurvey(16)
# getSurveys()
# print(getRoles())
# create_db_and_tables()
# loadCountries()
# loadRoles()