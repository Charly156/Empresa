##Importación de bibliotecas##
import streamlit as st
import folium
from folium.plugins import HeatMap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import calendar
import seaborn as sns
import altair as alt
from datetime import datetime, date, time
import plotly.express as px

st.set_page_config(layout='wide')
st.header('Dashboard de negocio')
st.markdown("***")

df = pd.read_excel('nuevo_archivo.xlsx')
col1, col2 = st.columns(2)

with col1:
    col1_1, col1_2 = st.columns(2)
    with col1_1:
        st.subheader('Personas que se subieron a los juegos en la semana')

    with col1_2:
        st.subheader('Saturación actual por juego')

        # Datos ficticios de saturación: (latitud, longitud, saturacion)
        datos_saturacion = [
            (28.35964, -81.56152, 0.8),
            (28.35665, -81.55838, 0.6),
            (28.35626, -81.56045, 0.9),
            (28.35645, -81.56312, 0.5),
            (28.35523, -81.55871, 0.7)
        ]

        # Crea un objeto de mapa centrado en una ubicación inicial
        mapa = folium.Map(location=[datos_saturacion[0][0], datos_saturacion[0][1]], zoom_start=15)

        # Agrega un mapa de calor con los datos de saturación
        HeatMap(data=datos_saturacion, radius=15).add_to(mapa)

        # Muestra el mapa en Streamlit
        st.markdown(folium.Map()._repr_html_(), unsafe_allow_html=True)

        # Muestra el mapa
        st.markdown(folium.Map()._repr_html_(), unsafe_allow_html=True)

    st.subheader('Visitas por juego')
    # Convierte la columna 'timestamp' a tipo datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Agrega una columna con el nombre del mes
    df['nombre_mes'] = df['timestamp'].dt.strftime('%B')  # %B devuelve el nombre completo del mes

    # Define el orden de los meses
    order_of_months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    df['nombre_mes'] = pd.Categorical(df['nombre_mes'], categories=order_of_months, ordered=True)

    # Agrupa los datos por sensor y mes, calculando el total de visitas por mes
    df_monthly = df.groupby(['sensor_id', 'nombre_mes']).sum().reset_index()

    # Configura el estilo de la gráfica
    sns.set_theme()

    # Crea la gráfica de calor horizontal
    plt.figure(figsize=(14, 8))
    heatmap_data = df_monthly.pivot(index='sensor_id', columns='nombre_mes', values='total_visits')
    sns.heatmap(heatmap_data, cmap='viridis', annot=True, fmt='g', cbar_kws={'label': 'Total de Visitas'})
    plt.title('Total de Visitas Mensuales por Sensor')
    plt.xlabel('Mes')
    plt.ylabel('Sensor')
    plt.show()

with col2:
    st.subheader('Personas que se subieron a cada juego')

    st.subheader('Total de visitas vs basura')


# Generar datos de ejemplo para el mapa de calor
data = np.random.random((10, 10))

# Crear el mapa de calor con plotly express
fig = px.imshow(data, color_continuous_scale='Viridis')

# Mostrar el mapa de calor en Streamlit
st.plotly_chart(fig)