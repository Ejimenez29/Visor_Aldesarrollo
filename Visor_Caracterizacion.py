import folium.plugins
import streamlit as st
import pandas as pd
import plotly.express as px
import folium #Librería de mapas en Python
from streamlit_folium import st_folium #Widget de Streamlit para mostrar los mapas
from folium.plugins import Search
from folium.plugins import TagFilterButton
from folium.plugins import MarkerCluster #Plugin para agrupar marcadores
from folium.plugins import FastMarkerCluster
from folium.plugins import Fullscreen
from streamlit_folium import folium_static
import webbrowser
import plotly.graph_objs as go

st.set_page_config(
    page_title="VISOR DE DATOS - CARACTERIZACION DE POBLACION VULNERABLE 2024 MUNICIPIO EL PASO - CESAR",
    page_icon="🌐",  
    layout='wide',
    initial_sidebar_state="expanded"
)

st.header('VISOR DE DATOS - CARACTERIZACION DE POBLACION VULNERABLE 2024 MUNICIPIO EL PASO - CESAR')

Fichas = pd.read_excel('Hogares.xlsx',sheet_name='Fichas')
columnas = ['Ficha No.', 'Dirección', 'Nombres Completos', 'Apellidos Completos','Identificacion','Gps latitud', 'Gps longitud', 'Color_Externo', 'Grupo_Vulnerable', 'Limitante', 'Clase_Encuestado','Total de personas del hogar']
Fichas_P= Fichas[[*columnas]]
Fichas_P = Fichas_P.loc[(Fichas_P['Clase_Encuestado']) == ('A')]

tab1,tab2,tab3=st.tabs(['Mapa General','Mapa Detallado' ,'Graficas'])

with tab1:
    parMapa = st.selectbox('Tipo Mapa',options=["open-street-map", "carto-positron","carto-darkmatter"])        
    parTamano = st.checkbox('Tamaño por cantidad de miembros en el hogar')
    if parTamano:
        fig = px.scatter_mapbox(Fichas_P,lat='Gps latitud',lon='Gps longitud', 
                                color='Grupo_Vulnerable', hover_name='Ficha No.',hover_data=['Identificacion','Nombres Completos', 'Apellidos Completos','Grupo_Vulnerable', 'Dirección'],
                                zoom=10, size='Total de personas del hogar',height=600)
    else:
        fig = px.scatter_mapbox(Fichas_P,lat='Gps latitud',lon='Gps longitud', 
                                color='Grupo_Vulnerable', hover_name='Ficha No.',hover_data=['Identificacion','Nombres Completos', 'Apellidos Completos','Grupo_Vulnerable', 'Dirección'],
                                zoom=10,height=600)
        
    fig.update_layout(mapbox_style=parMapa)
    st.plotly_chart(fig,use_container_width=True)
with tab2:
    st.dataframe(Fichas,use_container_width=True)
    m = folium.Map(location=[9.661436,-73.746817], zoom_start=15)
    Marker_Cluster_Fichas = MarkerCluster()
    id= list(Fichas['Identificacion'])
    latitud = list(Fichas['Gps latitud'])
    longitud = list(Fichas['Gps longitud'])
    FastMarkerCluster(data=zip(latitud, longitud,id),name='Poblacion Total').add_to(m)
    columnas = ['Ficha No.','Identificacion','Gps latitud', 'Gps longitud', 'Color_Externo', 'Grupo_Vulnerable', 'Limitante', 'Clase_Encuestado']
    Fichas_P= Fichas[[*columnas]]
    Fichas_P = Fichas_P.loc[(Fichas_P['Clase_Encuestado']) == ('A')]
    i=0
    for index, row in Fichas_P.iterrows():
        Identificacion= id[i]
        Gps_Lat=latitud[i]
        Gps_Lon=longitud[i]
        vector=[]
        vector=row['Limitante'].split(" - ")
        Len_Vector = len(vector)
        columnas = ['Ficha No.', 'Dirección','Tipo_ID','Identificacion','Nombres Completos', 'Apellidos Completos', 'Edad_C', 'Sexos_C', 'Grupo_Vulnerable', 'Limitante']
        html = Fichas[[*columnas]]
        html = html.loc[(html['Ficha No.']) == row['Ficha No.']]
        html = html.to_html(classes="table") #table-striped table-hover table-condensed table-responsive
        popup = folium.Popup(html)
        match (Len_Vector):
            case 1:
                marker=folium.CircleMarker(location=[row['Gps latitud'],row['Gps longitud']], name=row['Identificacion'],tags = [row['Grupo_Vulnerable'], row['Limitante']],
                    popup=popup,
                    radius=3,
                    fill=True,
                    color=row['Color_Externo'],
                    fill_color=row['Color_Externo'], 
                    fill_opacity=1)
            case 2:
                v0=vector[0]
                v1=vector[1]
                marker=folium.CircleMarker(location=[row['Gps latitud'],row['Gps longitud']],name=row['Identificacion'],tags = [row['Grupo_Vulnerable'], v0, v1],
                    popup=popup,
                    radius=3,
                    fill=True,
                    color=row['Color_Externo'],
                    fill_color=row['Color_Externo'], 
                    fill_opacity=1)
        Marker_Cluster_Fichas.add_child(folium.Marker(location=[row['Gps latitud'],row['Gps longitud']], name=row['Identificacion']))
        marker.add_to(m)
        i=i+1
    Grupo_Poblacional = ['Afrocolombiano','Adulto Mayor','Madre cabeza de familia','Desplazado por la Violencia','Indígenas','Rrom y Población LGTBI','Desplazado por desastres naturales', 'Expresidiario', 'Reinsertado']
    TagFilterButton(Grupo_Poblacional).add_to(m)
    Limitante = ['Discapacidad Orgánica','Discapacidad Mental','Discapacidad Motora','Discapacidad Sensorial','Discapacidad Nula','Pluridiscapacidad']
    TagFilterButton(Limitante).add_to(m)
    folium.plugins.Fullscreen(
        position="topright",
        title="Pantalla completa",
        title_cancel="Cancelar",
        force_separate_button=True,
    ).add_to(m)
    Capa_Todos = folium.FeatureGroup(name='Total Fichas',show=False)
    Capa_Todos.add_child(Marker_Cluster_Fichas)
    m.add_child(Capa_Todos)
    folium.TileLayer('CartoDB Positron').add_to(m)
    folium.LayerControl().add_to(m)
    BuscaCodigo_Miembro = Search(
        layer=Capa_Todos,
        geom_type='Point',
        placeholder="Buscar Por ID",
        search_zoom=60,
        collapsed = True,
        search_label = "name",
    ).add_to(m)
    
    Salida=st_folium(m, height=600,use_container_width=True, returned_objects=[])
    m.save('Mimapa.html')
    webbrowser.open('Mimapa.html')
with tab3:
    # Definición de paletas de colores
    paleta_discreta= px.colors.carto.Safe
    paleta_continua = px.colors.sequential.Jet
    paleta_personalizada = ['#AF47D2','#FFBF00','#F9E897','#FFC374','#EE99C2','#387ADF']

    #Grafica Piramidal
    Fig1 = pd.read_excel('Hogares.xlsx',sheet_name='Fig1')
    y = Fig1['Población por Edad']
    x1 = Fig1['Hombres'] * -1
    x2 = Fig1['Mujeres']
    # Create instance of the figure
    fig_1 = go.Figure()
    # Add Trace to Figure
    fig_1.add_trace(go.Bar(
            y=y,
            x=x1,
            name='Hombres',
            orientation='h'
    ))
    # Add Trace to figure
    fig_1.add_trace(go.Bar(
            y=y,
            x=x2,
            name='Mujeres',
            orientation='h'
    ))
    # Update Figure Layout
    fig_1.update_layout(
        template = 'plotly_white',
        title= 'Estructura de Población - Caracterización de Población Vulnerable 2024',
        title_font_size = 24,
        barmode='relative',
        bargap=0.0,
        bargroupgap=0,
        xaxis=dict(
            tickvals=[-2000, -1500, -1000, -500, 0, 500, 100, 1500, 2000],
            ticktext=['2K','1.5K','1K','0.5K','0', '0.5K', '1K', '1.5K', '2K'],
            title='POBLACION EN MILES',
            title_font_size=14
        )
    )
    # Plot figure
    st.plotly_chart(fig_1,use_container_width=True)

    #Grafica Barras Ubicacion
    Fig2 = pd.read_excel('Hogares.xlsx',sheet_name='Fig2')
    fig_2 = px.bar(Fig2, x='Centro Poblado', y =['Poblacion Estimada', 'Población Ajustada por Omisión', 'Caracterización de Población Vulnerable'], barmode = 'overlay', labels={'pop': 'Numero de Habitantes'}, color_discrete_sequence=paleta_personalizada,)
    fig_2.update_layout(
        template = 'plotly_white',
        title= 'Habitantes Por Centro Poblado',
        title_font_size = 24)
    fig_2.update_yaxes(title_text="Numero de Habitantes", secondary_y=False)
    st.plotly_chart(fig_2,use_container_width=True)

    #Grafica Grupos Edades
    Fig3 = pd.read_excel('Hogares.xlsx',sheet_name='Fig3')
    fig_3 = px.bar(Fig3, x='Rango de Edades', y =['Caracterización', 'Población por Omision'], barmode = 'overlay', labels={'pop': 'Numero de Habitantes'}, color_discrete_sequence=paleta_personalizada)
    fig_3.update_layout(
        template = 'plotly_white',
        title= 'Grandes Grupos de Edades',
        title_font_size = 24)
    fig_3.update_yaxes(title_text="Numero de Habitantes", secondary_y=False)
    st.plotly_chart(fig_3,use_container_width=True)

    #Grafica Discapacidades por Población
    Fig4 = pd.read_excel('Hogares.xlsx',sheet_name='Fig4')
    fig_4 = px.pie(Fig4, names='Tipos de discapacidad', values ='Caracterización', labels={'pop': 'Numero de Habitantes'},hole=.3)
    fig_4.update_layout(
        template = 'plotly_white',
        title= 'Discapacidades por Población',
        title_font_size = 24)
    fig_4.add_trace(go.Pie(
        rotation=45))
    st.plotly_chart(fig_4,use_container_width=True)
