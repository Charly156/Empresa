##Importación de bibliotecas##
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import calendar
import seaborn as sns
import altair as alt
from datetime import datetime, date, time
import plotly.express as px

st.set_page_config(layout='wide')
def convert_df(df):
        # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode('utf-8')

##Lectura del archivo##
general = pd.read_excel('tabular_data_general.xlsx', index_col=0)
maternidad = pd.read_excel('tabular_data_maternidad.xlsx', index_col=0)
docentes = pd.read_excel('tabular_data_docentes.xlsx')

##Título del dashboard##
st.header('Dashboard analítico')

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

flujo_general = general[['timestamp', 'General']].groupby('timestamp').sum().reset_index()
flujo_maternidad = maternidad[['timestamp','Maternidad']].groupby('timestamp').sum().reset_index()
flujo_docentes = docentes[['timestamp', 'Docentes']].groupby('timestamp').sum().reset_index()

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
        df = pd.read_excel("sensor_data_general.xlsx", index_col=0)

        st.subheader("Mapa de Sensores")

        # Inicializar el DataFrame para el mapa
        map_data = pd.DataFrame(columns=["latitude", "longitude"])

        # Obtener las ubicaciones y agregarlas al DataFrame
        for index, row in df.iterrows():
            map_data = map_data.append({"latitude": row["sensor_latitude"], "longitude": row["sensor_longitude"]}, ignore_index=True)

        # Calcular el centro del mapa usando la media de todas las coordenadas
        center_lat = map_data["latitude"].mean()
        center_lon = map_data["longitude"].mean()

        # Slider para ajustar el nivel de zoom del mapa
        zoom_level = st.slider("Ajusta el nivel de zoom:", 1, 17, 5)

        # Mostrar el mapa
        st.map(map_data, zoom=zoom_level, center=(center_lat, center_lon), use_container_width=True)
    
    #Subcolumna 2
    with col1_2:
        st.subheader('Saturación promedio')
    
    #El gráfico de flujo semanal en la perte superior
    #izquierda
    # Definir el orden deseado de los días de la semana
    orden_semanal = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # Convertir la columna 'Day' a tipo categórico con el orden especificado
    flujo_filtrado['Day'] = pd.Categorical(flujo_filtrado['Day'], categories=orden_semanal, ordered=True)

    st.subheader('Gráfico de línea')
    fig, ax = plt.subplots()
    flujo_filtrado[['Day','General']].groupby('Day').sum().plot(ax = ax, alpha = 0.7)
    flujo_filtrado[['Day','Maternidad']].groupby('Day').sum().plot(ax = ax, alpha = 0.7)
    flujo_filtrado[['Day','Docentes']].groupby('Day').sum().plot(ax = ax, alpha = 0.7)
    ax.patch.set_alpha(0)
    st.pyplot(fig)

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
            fig, ax = plt.subplots()
            totalvisits_byday = general_filtrado.groupby('Day')['total_visits'].sum().reset_index()
            sns.barplot(data=totalvisits_byday, x='Day', y='total_visits', ax=ax, 
                        palette='viridis', order=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 
                                                  'Friday', 'Saturday', 'Sunday'])
            plt.xticks(rotation=90)
            ax.set_title("visits promedio por día")
            st.pyplot(fig)

        #Arriba a la derecha
        with Gen2:
            st.subheader('Inner vs Outer')
            fig, ax = plt.subplots()
            general_filtrado[['incoming_inner_count','solo_outer']].sum().plot.pie()
            st.pyplot(fig)
        
        #Abajo en el centro
        st.subheader('Visitas por día')
        fig, ax = plt.subplots()
        sns.boxplot(data = general_filtrado.head(7*86), x = 'Day', y = 'total_visits', 
                    palette = 'viridis', ax = ax, 
                    order=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                           'Saturday', 'Sunday'])
        st.pyplot(fig)

    #Pestaña de maternidad
    with tab2:
        Mat1, Mat2 = st.columns(2)

        #Arriba a la izquierda
        with Mat1:
            st.subheader('Total de visitas')
            fig, ax = plt.subplots()
            totalvisits_byday = maternidad_filtrado.groupby('Day')['total_visits'].sum().reset_index()
            sns.barplot(data=totalvisits_byday, x='Day', y='total_visits', ax=ax, 
                        palette='viridis', order=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 
                                                  'Friday', 'Saturday', 'Sunday'])
            plt.xticks(rotation=90)
            ax.set_title("visits promedio por día")
            st.pyplot(fig)
        
        #Arriba a la derecha
        with Mat2:
            st.subheader('Inner vs Outer')
            fig, ax = plt.subplots()
            maternidad_filtrado[['incoming_inner_count','solo_outer']].sum().plot.pie()
            st.pyplot(fig)

        #Abajo en el centro
        st.subheader('Visitas por día')
        fig, ax = plt.subplots()
        sns.boxplot(data = maternidad_filtrado.head(7*86), x = 'Day', y = 'total_visits', 
                    palette = 'viridis', ax = ax, 
                    order=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                           'Saturday', 'Sunday'])
        st.pyplot(fig)

    #Pestaña de docentes
    with tab3:
        Doc1, Doc2 = st.columns(2)

        #Arriba a la izquierda
        with Doc1:
            st.subheader('Total de visitas')
            fig, ax = plt.subplots()
            totalvisits_byday = docentes_filtrado.groupby('Day')['total_visits'].sum().reset_index()
            sns.barplot(data=totalvisits_byday, x='Day', y='total_visits', ax=ax, 
                        palette='viridis', order=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 
                                                  'Friday', 'Saturday', 'Sunday'])
            plt.xticks(rotation=90)
            ax.set_title("visits promedio por día")
            st.pyplot(fig)
        
        #Arriba a la derecha
        with Doc2:
            st.subheader('Inner vs Outer')
            fig, ax = plt.subplots()
            docentes_filtrado[['incoming_inner_count','solo_outer']].sum().plot.pie()
            st.pyplot(fig)

        #Abajo en el centro
        st.subheader('Visitas por día')
        fig, ax = plt.subplots()
        sns.boxplot(data = docentes_filtrado.head(7*86), x = 'Day', y = 'total_visits', 
                    palette = 'viridis', ax = ax, 
                    order=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                           'Saturday', 'Sunday'])
        st.pyplot(fig)

        fig = px.bar(totalvisits_byday, x='Day', y='total_visits')
        st.plotly_chart(fig)

        fig = px.box(docentes_filtrado.head(7*86), x='Day', y='total_visits', category_orders={'Dia': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                           'Saturday', 'Sunday']}, title='Boxplot por Día')
        st.plotly_chart(fig)

#Crear check box
show_dt = st.sidebar.checkbox('Visualizar DataFrame', value = False)

if show_dt:
    #Usar st.dataframe para mostrar el DataFrame en Streamlit
    st.title('Datos General')
    st.dataframe(flujo_sensores)

    #st.download_button('Descargar datos', data,'general_data.csv')
    csv = convert_df(flujo_sensores)

    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='general_data.csv',
        mime='text/csv',
    )