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

##Lectura del archivo##
general = pd.read_excel('tabular_data_general.xlsx', index_col=0)
maternidad = pd.read_excel('tabular_data_maternidad.xlsx', index_col=0)
docentes = pd.read_excel('tabular_data_docentes.xlsx')

##Nueva columna Hour##
general['Hour'] = general['timestamp'].dt.hour
maternidad['Hour'] = maternidad['timestamp'].dt.hour
docentes['Hour'] = docentes['timestamp'].dt.hour

##Nueva columna Outer_count##
general['solo_outer'] = general['incoming_outer_count']-general['incoming_inner_count']
maternidad['solo_outer'] = maternidad['incoming_outer_count']-maternidad['incoming_inner_count']
docentes['solo_outer'] = docentes['incoming_outer_count']-docentes['incoming_inner_count']

st.header('Dashboard de tiempo real')
st.markdown("***")

##Creación de pestañas para las bases de datos##
tab1, tab2, tab3 = st.tabs(['General', 'Maternidad', 'Docentes'])

with tab1:
    day_data_gen= general[((general['timestamp'].dt.year==2023) & (general['timestamp'].dt.month==8)&(general['timestamp'].dt.day==2))].copy()

    gen1, gen2, gen3 = st.columns(3)

    with gen1:
        st.subheader('Tasa de entradas')
        tasa = int(round((day_data_gen['incoming_inner_count'].sum()/day_data_gen['solo_outer'].sum())*100,))
        gen1.metric('',f'{tasa}%','')

        ##Creación del gráfico de donas##
        st.subheader('Inner vs Outer')
        fig = px.pie(day_data_gen, 
                        values=day_data_gen[['incoming_inner_count','solo_outer']].sum(), 
                        names=day_data_gen[['incoming_inner_count','solo_outer']].sum().index,
                        hole = 0.5, color = day_data_gen[['incoming_inner_count','solo_outer']].sum().index, 
                        color_discrete_sequence=px.colors.qualitative.Set1)
        st.plotly_chart(fig, use_container_width=True)

    with gen2:
        st.subheader('Número de personas')
        #Seleccionar última hora
        last_row=day_data_gen.iloc[-1]

        #Calcular total
        num_personas=int(last_row['total_visits'].sum())

        gen2.metric('',f'{num_personas}','')

        st.subheader('Saturación actual')
        #Crear límites
        lim_s=general['total_visits'].mean() + np.std(general['total_visits'])
        lim_m=general['total_visits'].mean()
        lim_i=general['total_visits'].mean() - np.std(general['total_visits'])

        #-----------------------Visualizar datos--------------------------
        if day_data_gen['total_visits'].sum() > lim_s:
            st.subheader(":blue[Alta]") #Agregar color
            st.subheader(":gray[Media]")
            st.subheader(":gray[Baja]")
        elif day_data_gen['total_visits'].sum() >= lim_i and day_data_gen['total_visits'].sum() <= lim_s:
            st.subheader(":gray[Alta]")
            st.subheader(":blue[Media]") #Agregar color
            st.subheader(":gray[Baja]")
        elif day_data_gen['total_visits'].sum() < lim_i:
            st.subheader(":gray[Alta]")
            st.subheader(":gray[Media]")
            st.subheader(":blue[Baja]") #Agregar color

    with gen3:
        st.subheader('Visitas acumuladas')
        # Calcular el total de visitas sumando la columna 'total_visits'
        total_visitas = int(day_data_gen['total_visits'].sum())
        gen3.metric('',f'{total_visitas}','')

        st.subheader('Flujo por hora')
        horas = day_data_gen.groupby('Hour')['total_visits'].sum().reset_index()
        fig = px.line(horas, x='Hour', y= 'total_visits')
        st.plotly_chart(fig, use_container_width=True)

with tab2:
    day_data_mat= maternidad[((maternidad['timestamp'].dt.year==2023) & (maternidad['timestamp'].dt.month==8)&(maternidad['timestamp'].dt.day==2))].copy()
    mat1, mat2, mat3 = st.columns(3)

    with mat1:
        st.subheader('Tasa de entradas')
        tasa = int(round((day_data_mat['incoming_inner_count'].sum()/day_data_mat['solo_outer'].sum())*100,))
        mat1.metric('',f'{tasa}%','')

        ##Creación del gráfico de donas##
        st.subheader('Inner vs Outer')
        fig = px.pie(day_data_mat, 
                        values=day_data_mat[['incoming_inner_count','solo_outer']].sum(), 
                        names=day_data_mat[['incoming_inner_count','solo_outer']].sum().index,
                        hole = 0.5, color = day_data_mat[['incoming_inner_count','solo_outer']].sum().index, 
                        color_discrete_sequence=px.colors.qualitative.Set1)
        st.plotly_chart(fig, use_container_width=True)

    with mat2:
        st.subheader('Número de personas')
         #Seleccionar última hora
        last_row=day_data_mat.iloc[-1]

        #Calcular total
        num_personas=int(last_row['total_visits'].sum())

        mat2.metric('',f'{num_personas}','')

        st.subheader('Saturación actual')
        #Crear límites
        lim_s=maternidad['total_visits'].mean() + np.std(general['total_visits'])
        lim_m=maternidad['total_visits'].mean()
        lim_i=maternidad['total_visits'].mean() - np.std(general['total_visits'])

        #-----------------------Visualizar datos--------------------------
        if day_data_mat['total_visits'].sum() > lim_s:
            st.subheader(":blue[Alta]") #Agregar color
            st.subheader(":gray[Media]")
            st.subheader(":gray[Baja]")
        elif day_data_mat['total_visits'].sum() >= lim_i and day_data_gen['total_visits'].sum() <= lim_s:
            st.subheader(":gray[Alta]")
            st.subheader(":blue[Media]") #Agregar color
            st.subheader(":gray[Baja]")
        elif day_data_mat['total_visits'].sum() < lim_i:
            st.subheader(":gray[Alta]")
            st.subheader(":gray[Media]")
            st.subheader(":blue[Baja]") #Agregar color

    with mat3:
        st.subheader('Visitas acumuladas')

        # Calcular el total de visitas sumando la columna 'total_visits'
        total_visitas = int(day_data_mat['total_visits'].sum())

        mat3.metric('',f'{total_visitas}','')

        st.subheader('Flujo por hora')
        horas = day_data_mat.groupby('Hour')['total_visits'].sum().reset_index()
        fig = px.line(horas, x='Hour', y= 'total_visits')
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    day_data_doc= docentes[((docentes['timestamp'].dt.year==2023) & (docentes['timestamp'].dt.month==8)&(docentes['timestamp'].dt.day==2))].copy()
    doc1, doc2, doc3 = st.columns(3)

    with doc1:
        st.subheader('Tasa de entradas')
        tasa = int(round((day_data_doc['incoming_inner_count'].sum()/day_data_doc['solo_outer'].sum())*100,))
        doc1.metric('',f'{tasa}%','')

        ##Creación del gráfico de donas##
        st.subheader('Inner vs Outer')
        fig = px.pie(day_data_doc, 
                        values=day_data_doc[['incoming_inner_count','solo_outer']].sum(), 
                        names=day_data_doc[['incoming_inner_count','solo_outer']].sum().index,
                        hole = 0.5, color = day_data_doc[['incoming_inner_count','solo_outer']].sum().index, 
                        color_discrete_sequence=px.colors.qualitative.Set1)
        st.plotly_chart(fig, use_container_width=True)

    with doc2:
        st.subheader('Número de personas')
         #Seleccionar última hora
        last_row=day_data_doc.iloc[-1]

        #Calcular total
        num_personas=int(last_row['total_visits'].sum())

        doc2.metric('',f'{num_personas}','')
        

        st.subheader('Saturación actual')
        #Crear límites
        lim_s=docentes['total_visits'].mean() + np.std(general['total_visits'])
        lim_m=docentes['total_visits'].mean()
        lim_i=docentes['total_visits'].mean() - np.std(general['total_visits'])

        #-----------------------Visualizar datos--------------------------
        if day_data_doc['total_visits'].sum() > lim_s:
            st.subheader(":blue[Alta]") #Agregar color
            st.subheader(":gray[Media]")
            st.subheader(":gray[Baja]")
        elif day_data_doc['total_visits'].sum() >= lim_i and day_data_gen['total_visits'].sum() <= lim_s:
            st.subheader(":gray[Alta]")
            st.subheader(":blue[Media]") #Agregar color
            st.subheader(":gray[Baja]")
        elif day_data_doc['total_visits'].sum() < lim_i:
            st.subheader(":gray[Alta]")
            st.subheader(":gray[Media]")
            st.subheader(":blue[Baja]") #Agregar color

    with doc3:
        st.subheader('Visitas acumuladas')
        # Calcular el total de visitas sumando la columna 'total_visits'
        total_visitas = int(day_data_doc['total_visits'].sum())
        doc3.metric('',f'{total_visitas}','')

        st.subheader('Flujo por hora')
        horas = day_data_doc.groupby('Hour')['total_visits'].sum().reset_index()
        fig = px.line(horas, x='Hour', y= 'total_visits')
        st.plotly_chart(fig, use_container_width=True)