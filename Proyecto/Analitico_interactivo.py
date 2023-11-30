##Importación de bibliotecas##
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import calendar
import seaborn as sns
import altair as alt
import folium
from streamlit_folium import folium_static
from datetime import datetime, date, time
import plotly.express as px

st.set_page_config(layout='wide')
def convert_df(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode('utf-8')

##Lectura del archivo##
general = pd.read_excel('tabular_data_general.xlsx', index_col=0)
maternidad = pd.read_excel('tabular_data_maternidad.xlsx', index_col=0)
docentes = pd.read_excel('tabular_data_docentes.xlsx', index_col = 0)

##Título del dashboard##
st.header('Dashboard analítico')
st.markdown("***")

##Nueva columna Day##
general['Day'] = general['timestamp'].dt.day_name()
maternidad['Day'] = maternidad['timestamp'].dt.day_name()
docentes['Day'] = docentes['timestamp'].dt.day_name()

##Nueva columna Date##
general['Date'] = general['timestamp'].dt.date
maternidad['Date'] = maternidad['timestamp'].dt.date
docentes['Date'] = docentes['timestamp'].dt.date

##Nueva columna Outer_count##
general['solo_outer'] = general['incoming_outer_count']-general['incoming_inner_count']
maternidad['solo_outer'] = maternidad['incoming_outer_count']-maternidad['incoming_inner_count']
docentes['solo_outer'] = docentes['incoming_outer_count']-docentes['incoming_inner_count']

##Creación de nuevo data frame para flujo semanal##
general['General'] = general['total_visits']
maternidad['Maternidad'] = maternidad['total_visits']
docentes['Docentes'] = docentes['total_visits']

##Creacion de nuevos valores##
general['id_gen'] = general['sensor_id'] 
maternidad['id_mat'] = maternidad['sensor_id'] 
docentes['id_doc'] = docentes['sensor_id'] 

flujo_general = general[['timestamp', 'General','id_gen']].groupby(['timestamp','id_gen']).sum().reset_index()
flujo_maternidad = maternidad[['timestamp','Maternidad','id_mat']].groupby(['timestamp','id_mat']).sum().reset_index()
flujo_docentes = docentes[['timestamp', 'Docentes','id_doc']].groupby(['timestamp','id_doc']).sum().reset_index()

flujo_gm = flujo_general.merge(flujo_maternidad, left_on = 'timestamp', right_on = 'timestamp')
flujo_sensores = flujo_gm.merge(flujo_docentes, left_on = 'timestamp', right_on = 'timestamp')
flujo_sensores['Day'] = flujo_sensores['timestamp'].dt.day_name()

##Creación del filtro del control de fechas##
#Selección y control de fechas
st.sidebar.header('Control de fechas')
start_date = st.sidebar.date_input('Fecha de inicio', general['timestamp'].min())
end_date = st.sidebar.date_input('Fecha de fin', general['timestamp'].max())

#Convertir objetos a datetime64[ns]
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

#Crear filtros
general_filtrado = general[(general['timestamp'] >= start_date) & (general['timestamp'] <= end_date)]
maternidad_filtrado = maternidad[(maternidad['timestamp'] >= start_date) & (maternidad['timestamp'] <= end_date)]
docentes_filtrado = docentes[(docentes['timestamp'] >= start_date) & (docentes['timestamp'] <= end_date)]
flujo_filtrado = flujo_sensores[(flujo_sensores['timestamp'] >= start_date) & (flujo_sensores['timestamp'] <= end_date)]

##Creación de columnas para el layout##
col1, col2 = st.columns(2)

##Columna 1##
with col1:
    
    ##Creación de subcolumnas##
    col1_1, col1_2 = st.columns(2)

    #Subcolumna 1
    with col1_1:
        #El mapa en la parte superior izquierda
        # Cargar el archivo de Excel en un DataFrame
        df = pd.read_excel("Ubicaciones.xlsx", index_col=0)

        # Crear un mapa con Folium
        st.subheader("Mapa de Sensores")

        # Slider para ajustar el nivel de zoom del mapa
        zoom_level = st.slider("Ajusta el nivel de zoom:", 1, 17, 5)

        # Crear un DataFrame con todas las ubicaciones
        map_data = pd.DataFrame({
            "latitude": df["sensor_latitude"],
            "longitude": df["sensor_longitude"]
        })

        # Mostrar el mapa
        st.map(map_data, zoom=zoom_level)

    #Subcolumna 2
    with col1_2:
        st.subheader('Saturación promedio')
        sensores = flujo_filtrado.groupby(['id_gen', 'id_mat', 'id_doc'])[['General', 'Maternidad', 'Docentes']].mean().reset_index()
        fig = px.scatter(sensores, x='id_gen', y='General', size='General', size_max=max(sensores['General']))
        fig.add_trace(px.scatter(sensores, x='id_mat', y='Maternidad', size='Maternidad', size_max=max(sensores['Maternidad'])).data[0])
        fig.add_trace(px.scatter(sensores, x='id_doc', y='Docentes', size='Docentes', size_max=max(sensores['Docentes'])).data[0])
        st.plotly_chart(fig, use_container_width=True, width=700)
    
    #El gráfico de flujo semanal en la parte superior
    #izquierda

    dias_numeros = {
        'Monday': 1,
        'Tuesday': 2,
        'Wednesday': 3,
        'Thursday': 4,
        'Friday': 5,
        'Saturday': 6,
        'Sunday': 7
    }
    flujo_filtrado['day_number'] = flujo_filtrado['Day'].map(dias_numeros)
    
    st.subheader('Flujo semanal: 3 sensores')
    flujos = flujo_filtrado.groupby('day_number')[['General','Maternidad','Docentes']].sum().reset_index()
    flujos['Day'] = flujos['day_number'].apply(lambda x: calendar.day_name[x-1])

    fig = px.line(flujos, x='Day', y=['General','Maternidad','Docentes'])

    st.plotly_chart(fig, use_container_width=True)

##Columna 2##
with col2:
    ##Creación de pestañas para las bases de datos##
    tab1, tab2, tab3 = st.tabs(['General', 'Maternidad', 'Docentes'])

    ##Pestaña general##
    with tab1:
        Gen1, Gen2 = st.columns(2)

        #Arriba a la izquierda
        with Gen1:
            st.subheader('Total de visitas')
            totalvisits_byday = general_filtrado.groupby('Day')['total_visits'].sum().reset_index()
            fig = px.bar(totalvisits_byday, x='Day', y='total_visits', 
                         category_orders={'Day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                           'Saturday', 'Sunday']}, color = 'Day', color_continuous_scale='Viridis')
            st.plotly_chart(fig, use_container_width=True, width=700)

        #Arriba a la derecha
        with Gen2:
            st.subheader('Inner vs Outer')
            fig = px.pie(general_filtrado, 
                         values=general_filtrado[['incoming_inner_count','solo_outer']].sum(), 
                         names=general_filtrado[['incoming_inner_count','solo_outer']].sum().index, 
                         color = general_filtrado[['incoming_inner_count','solo_outer']].sum().index, 
                         color_discrete_sequence=px.colors.qualitative.Set1)
            st.plotly_chart(fig, use_container_width=True, width=700)
        
        #Abajo en el centro
        st.subheader('Visitas por día')
        fig = px.box(general_filtrado, x='Day', y='total_visits', 
                     category_orders={'Day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                           'Saturday', 'Sunday']}, color='Day', color_discrete_sequence=px.colors.qualitative.Set1)
        st.plotly_chart(fig)

    #Pestaña de maternidad
    with tab2:
        Mat1, Mat2 = st.columns(2)

        #Arriba a la izquierda
        with Mat1:
            st.subheader('Total de visitas')
            totalvisits_byday = maternidad_filtrado.groupby('Day')['total_visits'].sum().reset_index()
            fig = px.bar(totalvisits_byday, x='Day', y='total_visits', category_orders={'Day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                           'Saturday', 'Sunday']}, color = 'Day', color_continuous_scale='Viridis')
            st.plotly_chart(fig, use_container_width=True, width=700)
        
        #Arriba a la derecha
        with Mat2:
            st.subheader('Inner vs Outer')
            fig = px.pie(maternidad_filtrado, 
                         values=maternidad_filtrado[['incoming_inner_count','solo_outer']].sum(), 
                         names=maternidad_filtrado[['incoming_inner_count','solo_outer']].sum().index, 
                         color = maternidad_filtrado[['incoming_inner_count','solo_outer']].sum().index, 
                         color_discrete_sequence=px.colors.qualitative.Set1)
            st.plotly_chart(fig, use_container_width=True, width=700)

        #Abajo en el centro
        st.subheader('Visitas por día')
        fig = px.box(docentes_filtrado, x='Day', y='total_visits',
                      category_orders={'Day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                           'Saturday', 'Sunday']}, color='Day', color_discrete_sequence=px.colors.qualitative.Set1)
        st.plotly_chart(fig)

    #Pestaña de docentes
    with tab3:
        Doc1, Doc2 = st.columns(2)

        #Arriba a la izquierda
        with Doc1:
            st.subheader('Total de visitas')
            fig, ax = plt.subplots()
            totalvisits_byday = docentes_filtrado.groupby('Day')['total_visits'].sum().reset_index()
            fig = px.bar(totalvisits_byday, x='Day', y='total_visits', category_orders={'Day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                           'Saturday', 'Sunday']}, color = 'Day', color_continuous_scale='Viridis')
            st.plotly_chart(fig, use_container_width=True, width=700)
        
        #Arriba a la derecha
        with Doc2:
            st.subheader('Inner vs Outer')
            fig = px.pie(docentes_filtrado, 
                         values=docentes_filtrado[['incoming_inner_count','solo_outer']].sum(), 
                         names=docentes_filtrado[['incoming_inner_count','solo_outer']].sum().index, 
                         color = docentes_filtrado[['incoming_inner_count','solo_outer']].sum().index, 
                         color_discrete_sequence=px.colors.qualitative.Set1)
            st.plotly_chart(fig, use_container_width=True, width=700)

        #Abajo en el centro
        st.subheader('Visitas por día')
        fig = px.box(maternidad_filtrado, x='Day', y='total_visits', 
                     category_orders={'Day': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                           'Saturday', 'Sunday']}, color='Day', color_discrete_sequence=px.colors.qualitative.Set1)
        st.plotly_chart(fig)

#Crear check box
show_dt = st.sidebar.checkbox('Visualizar Tablas de datos', value = False)

if show_dt:
    #Usar st.dataframe para mostrar el DataFrame en Streamlit
    st.title('Datos General')
    st.dataframe(general)

    #st.download_button('Descargar datos', data,'general_data.csv')
    csv = convert_df(general)

    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='general_data.csv',
        mime='text/csv',
    )

    #Usar st.dataframe para mostrar el DataFrame en Streamlit
    st.title('Datos Docentes')
    st.dataframe(docentes)

    #st.download_button('Descargar datos', data,'general_data.csv')
    csv = convert_df(docentes)

    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='docentes_data.csv',
        mime='text/csv',
    )

    #Usar st.dataframe para mostrar el DataFrame en Streamlit
    st.title('Datos Maternidad')
    st.dataframe(maternidad)

    #st.download_button('Descargar datos', data,'general_data.csv')
    csv = convert_df(maternidad)

    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='maternidad_data.csv',
        mime='text/csv',
    )