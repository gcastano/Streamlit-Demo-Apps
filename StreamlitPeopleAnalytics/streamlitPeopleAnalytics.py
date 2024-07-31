import streamlit as st
import plotly.express as px
import pandas as pd
import datetime
import utils

# Definimos los parámetros de configuración de la aplicación
st.set_page_config(
    page_title="People Analytics Dashboard", #Título de la página
    page_icon="😊", # Ícono
    layout="wide", # Forma de layout ancho o compacto
    initial_sidebar_state="expanded" # Definimos si el sidebar aparece expandido o colapsado
)

utils.local_css('estilo.css')

# paletaColores = color_discrete_sequence=px.colors.colorbrewer.Set2
paletaColores = ['#4c84ff','#fec400','#219C90','#9B86BD','#3AA6B9','#050C9C','#E76F51']

# Carga de datos
archivo = './HR_DATA.csv'
dfDatosHR = pd.read_csv(archivo,parse_dates=['DOB','DateofHire','DateofTermination'])

# Preparación de datos
fechaHoy= datetime.datetime.today()
rangoTrimestre=datetime.timedelta(days=90)
fechaTrimestre=fechaHoy-rangoTrimestre

# Calculamos antigüedad en Años
dfDatosHR['Tenure']=(fechaHoy-dfDatosHR['DateofHire'])/ datetime.timedelta(days=365)
# Calculamos edad en Años
dfDatosHR['Age']=(fechaHoy-dfDatosHR['DOB'])/ datetime.timedelta(days=365)
# Renombramos Sex
dfDatosHR['Sex']=dfDatosHR['Sex'].apply(lambda x:'Women' if x=='F' else 'Men')

# Calculamos rangos de antigüedad
dfDatosHR['TenureRange']=pd.cut(dfDatosHR['Tenure'], bins=[0, 1 ,3, 5, 10, 15, 20,100],
        labels=["<1 y", "1-3 y", "3-5 y","5-10 y","10-15 y","15-20 y","> 20 y"], ordered=False)
# Calculamos rangos de edad
dfDatosHR['AgeRange']=pd.cut(dfDatosHR['Age'], bins=[17, 20 ,30, 40, 50, 60, 70,100],
        labels=["<20 y", "20-30 y", "30-40 y","40-50 y","50-60 y","60-70 y","> 70 y"], ordered=False)

# Convertimos la columna de performance a categórica ordenada
dfDatosHR['PerformanceScore'] = pd.Categorical(dfDatosHR['PerformanceScore'], 
                      categories=['Needs Improvement', 'PIP','Fully Meets','Exceeds'],
                      ordered=True)
# Filtramos empleados Activos
dfEmpleadosActivos =dfDatosHR[dfDatosHR['EmploymentStatus']=='Active']

# Cantidad de empleados
empActivos=len(dfDatosHR[dfDatosHR['EmploymentStatus']=='Active'])
empHombres=len(dfEmpleadosActivos[dfEmpleadosActivos['Sex']=='Men'])
empMujeres=len(dfEmpleadosActivos[dfEmpleadosActivos['Sex']=='Women'])

# Empleados Trimestre
empNuevosTrimestre = len(dfDatosHR[dfDatosHR['DateofHire']>=fechaTrimestre])
empTerminadosTrimestre = len(dfDatosHR[dfDatosHR['DateofTermination']>=fechaTrimestre])

# Cálculo de Antigüedad
empAntiguedad=dfEmpleadosActivos['Tenure'].mean()
empAntiguedadHombres=dfEmpleadosActivos[dfEmpleadosActivos['Sex']=='Men']['Tenure'].mean()
empAntiguedadMujeres=dfEmpleadosActivos[dfEmpleadosActivos['Sex']=='Women']['Tenure'].mean()

# Empleados por departamento y sexo
empActivosDept = dfEmpleadosActivos.groupby(['Department','Sex']).agg(Employees=('EmpID','count')).reset_index()

# Empleados por departamento totales
empActivosDeptTotal = dfEmpleadosActivos.groupby(['Department']).agg(Employees=('EmpID','count')).reset_index()

# Generamos el orden de mayor a menor que usaremos en las gráficas
ordenDeptTotal = empActivosDeptTotal.sort_values('Employees')['Department'].unique()

empActivosDeptTenure = dfEmpleadosActivos.groupby(['Department','TenureRange']).agg(Employees=('EmpID','count')).reset_index()

empActivoAge = dfEmpleadosActivos.groupby(['AgeRange','Sex']).agg(Employees=('EmpID','count')).reset_index()
dfSpanofControl = dfEmpleadosActivos.groupby(['ManagerName']).agg(Employees=('EmpID','count')).reset_index()
empSpanofControl=dfSpanofControl['Employees'].mean()

empHires=dfDatosHR.groupby(pd.Grouper(key="DateofHire",freq='M')).agg(Employees=('EmpID','count')).reset_index()
empHires.columns=['Period','Employees']
empHires['action']='Hire'

empTerminations=dfDatosHR.groupby(pd.Grouper(key="DateofTermination",freq='M')).agg(Employees=('EmpID','count')).reset_index()
empTerminations.columns=['Period','Employees']
empTerminations['Employees']=empTerminations['Employees']*-1
empTerminations['action']='Termination'

empHiresTerminations = pd.concat([empHires,empTerminations])
empHiresTerminations=empHiresTerminations[empHiresTerminations['Period']>=fechaHoy-datetime.timedelta(days=730)]

empTerminations =dfDatosHR[dfDatosHR['EmploymentStatus'].isin(['Voluntarily Terminated','Terminated for Cause'])].groupby('EmploymentStatus').agg(Employees=('EmpID','count')).reset_index()

empTerminationReason =dfDatosHR[dfDatosHR['EmploymentStatus'].isin(['Voluntarily Terminated','Terminated for Cause'])].groupby(['EmploymentStatus','TermReason']).agg(Employees=('EmpID','count')).reset_index()

empTerminationReasonTotal =dfDatosHR[dfDatosHR['EmploymentStatus'].isin(['Voluntarily Terminated','Terminated for Cause'])].groupby(['TermReason']).agg(Employees=('EmpID','count')).reset_index()
ordenTerminationReason = empTerminationReasonTotal.sort_values('Employees')['TermReason'].unique()


empActivoTenure = dfEmpleadosActivos.groupby(['TenureRange','Sex']).agg(Employees=('EmpID','count')).reset_index()
empActivoDeptTenure = dfEmpleadosActivos.groupby(['TenureRange','Department']).agg(Employees=('EmpID','count')).reset_index()
empActivoPerformance = dfEmpleadosActivos.groupby(['PerformanceScore']).agg(Employees=('EmpID','count')).reset_index()

dfEmpSalarios = dfEmpleadosActivos.groupby(['Position','Sex']).agg(PayRate=('PayRate','mean'),Employees=('EmpID','count')).reset_index()

# Gráficos

figPerformance = px.pie(empActivoPerformance.sort_values('Employees'),names='PerformanceScore',values='Employees', color_discrete_sequence=paletaColores)
figPerformance.update_traces(textposition='outside', textinfo='percent+label')
figPerformance =utils.aplicarFormatoChart(figPerformance,titulo="Performance",subtitulo="")



figTerminations = px.pie(empTerminations,names='EmploymentStatus',values='Employees', color_discrete_sequence=paletaColores)
figTerminations.update_traces(textposition='outside', textinfo='percent+label')
figTerminations =utils.aplicarFormatoChart(figTerminations,titulo="Terminations by type",subtitulo="Last 2 years")


figTerminationsReason = px.bar(empTerminationReason,y='TermReason',x='Employees',color='EmploymentStatus', color_discrete_sequence=paletaColores)
figTerminationsReason.update_yaxes(categoryorder='array', categoryarray= ordenTerminationReason)
figTerminationsReason =utils.aplicarFormatoChart(figTerminationsReason,legend=True,titulo="Reason for Terminations",subtitulo="Last 2 years")


figDeptTenure = px.bar(empActivosDeptTenure.sort_values('Employees',ascending=False),y='Department',x='Employees',color='TenureRange', color_discrete_sequence=paletaColores)
figDeptTenure.update_yaxes(categoryorder='array', categoryarray= ordenDeptTotal)
figDeptTenure.update_layout(legend_traceorder="grouped")
figDeptTenure =utils.aplicarFormatoChart(figDeptTenure,legend=True,titulo="Tenure by Department",subtitulo="")


figHireTerminations = px.bar(empHiresTerminations,x='Period',y='Employees',color='action', color_discrete_sequence=paletaColores)
figHireTerminations =utils.aplicarFormatoChart(figHireTerminations,legend=True,titulo="Hires vs Terminations",subtitulo="Last 2 years")


figEmpXDept=px.bar(empActivosDept.sort_values(['Sex','Employees']),x='Employees',y='Department',color='Sex',
           barmode='group',text='Employees',
           color_discrete_map={'Men':paletaColores[0],'Women':paletaColores[1]})
figEmpXDept =utils.aplicarFormatoChart(figEmpXDept,legend=True,titulo="Employees by Department",subtitulo="Grouped by sex")

figEmpAge=px.bar(empActivoAge.sort_values(['Sex']),y='Employees',x='AgeRange',color='Sex',
           barmode='group',text='Employees', color_discrete_map={'Men':paletaColores[0],'Women':paletaColores[1]})
figEmpAge =utils.aplicarFormatoChart(figEmpAge,legend=True,titulo="Employees by Age",subtitulo="Grouped by sex")

figEmpTenure=px.bar(empActivoTenure.sort_values(['Sex']),y='Employees',x='TenureRange',color='Sex',
           barmode='group',text='Employees', color_discrete_map={'Men':paletaColores[0],'Women':paletaColores[1]})
figEmpTenure =utils.aplicarFormatoChart(figEmpTenure,legend=True,titulo="Employees by Tenure",subtitulo="Grouped by sex")

figPerfvsSat = px.scatter(dfEmpleadosActivos.sort_values('PerformanceScore'),x='EngagementSurvey',y='PerformanceScore', color='EngagementSurvey',
                          color_continuous_scale=px.colors.colorbrewer.RdYlGn)
figPerfvsSat =utils.aplicarFormatoChart(figPerfvsSat,legend=False,titulo="Engagement vs Performance",subtitulo="Turn over risk")

figSalarioSexo = px.bar(dfEmpSalarios.sort_values('PayRate'),x='Position',y='PayRate', color='Sex', color_discrete_map={'Men':paletaColores[0],'Women':paletaColores[1]},
                        barmode='group',text='PayRate')
figSalarioSexo.update_traces(textangle=-90, texttemplate = "%{y:,.1f}")
figSalarioSexo =utils.aplicarFormatoChart(figSalarioSexo,legend=True,titulo="Salary Distribution",subtitulo="Turn over risk")

# Tablero

st.header('People Analytics Dashboard - :blue[Company Inc.]')

with st.expander('Data'):    
    st.dataframe(dfDatosHR)
    st.write('**Source:** https://www.kaggle.com/datasets/davidepolizzi/hr-data-set-based-on-human-resources-data-set?')
st.divider()
columnas=st.columns([2,2,2,5,5])
with columnas[0]:
    st.metric('Active Employees',f'{empActivos:,.0f}','employees',delta_color='off')
    porcHombres=empHombres/ empActivos
    st.metric('Men',f'{porcHombres:,.2%}',f'{empHombres:,.0f} emp.',delta_color='off')    
    porcMujeres=empMujeres/ empActivos
    st.metric('Women',f'{porcMujeres:,.2%}',f'{empMujeres:,.0f} emp.', delta_color='off')    
    
with columnas[1]:
    st.metric('Tenure',f'{empAntiguedad:,.2f} years')    
    st.metric('Tenure Women',f'{empAntiguedadMujeres:,.2f} years')        
    st.metric('Tenure Men',f'{empAntiguedadHombres:,.2f} years')        
with columnas[2]:
    st.metric('Hires',f'{empNuevosTrimestre:,.0f}','Last 3 months',delta_color='off')
    st.metric('Terminations',f'{empTerminadosTrimestre:,.2f}','Last 3 months',delta_color='off')
    st.metric('Span of Control',f'{empSpanofControl:,.1f}')
with columnas[3]:
    st.plotly_chart(utils.aplicarFormatoChart(figEmpXDept,legend=True),use_container_width=True)
with columnas[4]:
    st.plotly_chart(utils.aplicarFormatoChart(figEmpAge,legend=True),use_container_width=True)
st.divider()
st.subheader(':blue[Hires and terminations]')
c1,c2,c3= st.columns([4,3,4])
with c1:
    st.plotly_chart(utils.aplicarFormatoChart(figHireTerminations,legend=True),use_container_width=True)
with c2:
    st.plotly_chart(figTerminations,use_container_width=True)
with c3:
    st.plotly_chart(figTerminationsReason,use_container_width=True)

st.divider()
st.subheader(':blue[Tenure and organization]')

c1,c2,c3,c4= st.columns(4)
with c1:    
    st.plotly_chart(figPerformance,use_container_width=True)    
with c2:
    st.plotly_chart(figPerfvsSat,use_container_width=True)
with c3:
    st.plotly_chart(figDeptTenure,use_container_width=True)        
with c4:
    st.plotly_chart(figEmpTenure,use_container_width=True)

st.divider()
st.subheader(':blue[Salary]')
with st.container():
    st.plotly_chart(figSalarioSexo,use_container_width=True)
