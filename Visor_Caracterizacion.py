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
from streamlit_folium import folium_static

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

tab1,tab2,tab3=st.tabs(['Mapa Detallado','Mapa General' ,'Graficas'])

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
    mapa = folium.Map(location=[9.661436,-73.746817], zoom_start=15)
    id= list(Fichas['Identificacion'])
    latitud = list(Fichas['Gps latitud'])
    longitud = list(Fichas['Gps longitud'])
    i= 0
    FastMarkerCluster(data=zip(latitud, longitud,id),name='Poblacion Total').add_to(mapa)
    marker_cluster = MarkerCluster()
    #marker_Cluster_Todos = MarkerCluster()
    #Mc_Fichas_Todos = MarkerCluster()
    columnas = ['Ficha No.','Identificacion','Gps latitud', 'Gps longitud', 'Color_Externo', 'Grupo_Vulnerable', 'Limitante', 'Clase_Encuestado']
    Fichas_P= Fichas[[*columnas]]
    Fichas_P = Fichas_P.loc[(Fichas_P['Clase_Encuestado']) == ('A')]
    for index, row in Fichas_P.iterrows():
        #Identificacion= id[i]
        #Gps_Lat=latitud[i]
        #Gps_Lon=longitud[i]
        vector=[]
        vector=row['Limitante'].split(" - ")
        Len_Vector = len(vector)
        columnas = ['Ficha No.', 'Dirección','Tipo_ID','Identificacion','Nombres Completos', 'Apellidos Completos', 'Edad_C', 'Sexos_C', 'Grupo_Vulnerable', 'Limitante']
        html = Fichas[[*columnas]]
        html = html.loc[(html['Ficha No.']) == row['Ficha No.']]
        html = html.to_html(classes="table") #table-striped table-hover table-condensed table-responsive
        popup = folium.Popup(html)
        #marker_Cluster_Todos.add_child(folium.Marker(location=[Gps_Lat,Gps_Lon], name=Identificacion, popup=popup,))
        match (Len_Vector):
            case 1:
                folium.CircleMarker(location=[row['Gps latitud'],row['Gps longitud']], tags = [row['Grupo_Vulnerable'], row['Limitante']],
                    popup=popup,
                    radius=3,
                    fill=True,
                    color=row['Color_Externo'],
                    fill_color=row['Color_Externo'], 
                    fill_opacity=1).add_to(mapa)
            case 2:
                v0=vector[0]
                v1=vector[1]
                folium.CircleMarker(location=[row['Gps latitud'],row['Gps longitud']], tags = [row['Grupo_Vulnerable'], v0, v1],
                    popup=popup,
                    radius=3,
                    fill=True,
                    color=row['Color_Externo'],
                    fill_color=row['Color_Externo'], 
                    fill_opacity=1).add_to(mapa)
    folium.plugins.Fullscreen(
        position="topright",
        title="Pantalla completa",
        title_cancel="Cancelar",
        force_separate_button=True,
    ).add_to(mapa)
   #folium_static(mapa, height=600, width=2000)
    st_folium(mapa, height=500,width=500, returned_objects=[])


with tab3:
    st.dataframe(Fichas,use_container_width=True)
    folium_static(mapa, height=600, width=2000)
    Condicion_Valores= Fichas.groupby('Grupo_Vulnerable')['Grupo_Vulnerable'].agg(len)
    

   # fig1 =Condicion_Valores.plot.barh(title='Grupos Vulnerables', template='simple_white',color={'Rrom y Población LGTBI':'olive','Desplazado por la Violencia':'red','Afrocolombiano':'green','Desplazado por desastres naturales':'blue', 'Indígenas': 'lightgray','Madre cabeza de familia': 'pink', 'Adulto Mayor':'orange','Expresidiario':'ligthgreen', 'Reinsertado':'darkgreen'})

    #Sexo_Valores=Fichas.groupby('Sexos_C')['Sexos_C'].agg(len)
    #fig2=Sexo_Valores.plot.bar(title='Distribucion Poblacional Por Sexo', template='simple_white',color={'Mujer':'red','Hombre':'green','ND':'lightgray'})

    #st.plotly_chart(fig1,use_container_width=True)
    #st.plotly_chart(fig2,use_container_width=True)

    """   Capa_Todos = folium.FeatureGroup(name='Poblacion Total',show=False)
   Capa_Todos.add_child(Mc_Fichas_Todos)
   mapa.add_child(Capa_Todos)

    BuscaCodigo_Miembro = Search(
        layer=Capa_Todos,
        geom_type='Point',
        placeholder="Buscar Por ID",
        search_zoom=60,
        collapsed = True,
        search_label = "name",
    ).add_to(mapa)

    Grupo_Poblacional = ['Afrocolombiano','Adulto Mayor','Madre cabeza de familia','Desplazado por la Violencia','Indígenas','Rrom y Población LGTBI','Desplazado por desastres naturales', 'Expresidiario', 'Reinsertado']
    TagFilterButton(Grupo_Poblacional).add_to(mapa)

    Limitante = ['Discapacidad Orgánica','Discapacidad Mental','Discapacidad Motora','Discapacidad Sensorial','Discapacidad Nula','Pluridiscapacidad']
    TagFilterButton(Limitante).add_to(mapa)

    folium.plugins.Fullscreen(
        position="topright",
        title="Pantalla completa",
        title_cancel="Cancelar",
        force_separate_button=True,
    ).add_to(mapa)

    folium.TileLayer('CartoDB Positron').add_to(mapa)
    folium.LayerControl().add_to(mapa)"""
