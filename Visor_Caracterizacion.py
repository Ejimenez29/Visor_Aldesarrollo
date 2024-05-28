# Proyecto Navegador de Mapas Python

#Librerias
pip install "folium"
import streamlit as st
import folium
from folium import plugins # Puntos en el mapa
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster #Agrupa los Puntos espaciales
import pandas as pd
pd.options.plotting.backend = "plotly"
import numpy as np
from folium.plugins import TagFilterButton
import xyzservices.providers as xyz
from folium.plugins import Search
import plotly.graph_objs as go

APP_TITLE = 'VISOR DE DATOS'
APP_SUB_TITLE = 'PROYECTO DE CARACTERIZACION FUNDACION ALDESARROLLO'

#import dash_table_experiments as dt

def main():
    st.set_page_config(APP_TITLE)
    st.title(APP_TITLE)
    st.caption(APP_SUB_TITLE)

if __name__ == "__main__":
   main()

#Add the Stadia Maps Stamen Toner provider details via xyzservices
tile_provider = xyz.Stadia.StamenTerrain

#Update the URL to include the API key placeholder
tile_provider["url"] = tile_provider["url"] + "?api_key={api_key}"

#Update the URL to include the API key placeholder
tile_provider["url"] = tile_provider["url"] + "?api_key={api_key}"

#Puntos Espaciales
Fichas = pd.read_excel('C:/Caracterizacion/Hogares.xlsx',sheet_name='Fichas')
Fichas.fillna(0)

#Deploy Map----------------------------------------------------------------
mapa = folium.Map(location=[9.661436,-73.746817],
                   zoom_start=12)

#Create the folium TileLayer, specifying the API key
folium.TileLayer(
    tiles=tile_provider.build_url(api_key='888731e2-27a6-4c90-93ee-c978439590a9'),
    attr=tile_provider.attribution,
    name=tile_provider.name,
    max_zoom=tile_provider.max_zoom,
    detect_retina=True
).add_to(mapa)

#Capa del Cluster-------------------------------------------------------

codigo = list(Fichas['ID Diligenciamiento'])
id_a = list(Fichas['Número de documento de identidad']) #Identificacion del Titular
id_b = list(Fichas['Identificacion B']) #Identificacion del Miembro del Hogar
nombres_a=list(Fichas['Nombre Completos A'])
apellidos_a=list(Fichas['Apellidos Completos A'])
nombres_b=list(Fichas['Nombre Completos B']) #Nombres Completos Miembro del Hogar
apellidos_b=list(Fichas['Apellidos Completos B']) #Apellidos Completos Miembro del Hogar
latitud = list(Fichas['Gps latitud'])
longitud = list(Fichas['Gps longitud'])
color_e= list(Fichas['Color_Externo'])
grupo_vulnerable = list(Fichas['Grupo_Vulnerable'])
grupo_vulnerable_2 = list(Fichas['Grupo_Vulnerable_2'])
limitante=list(Fichas['Limitante'])
iconos = list(Fichas['Icono'])
prefx = list(Fichas['Prefix'])
clase_e = list(Fichas['Clase_Encuestado']) #Tipo de Encuestado
i = int(0)

#Crear Cluster para Busqueda

Mc_Fichas = MarkerCluster()

for cod, doc_a, nom_a, ape_a, doc_b, nom_b, ape_b, lat, lon, c_e, g_v, g_v2, limit, ico, pref, clas_e in zip(codigo, id_a, nombres_a, apellidos_a, id_b, nombres_b, apellidos_b, latitud, longitud, color_e, grupo_vulnerable, grupo_vulnerable_2, limitante, iconos, prefx, clase_e):
   Condicion=[1]
   if [clas_e] == Condicion:
      Mc_Fichas.add_child(folium.Marker(location=[lat,lon], name=[doc_a], tags = [g_v, g_v2, limit],
        icon=folium.Icon(color=c_e,
                           #icon_color=c_i,
                           icon=ico,
                           prefix=pref)))
      
Mc_Fichas_Todos = MarkerCluster()

for cod, doc_a, nom_a, ape_a, doc_b, nom_b, ape_b, lat, lon, c_e, g_v, g_v2, limit, ico, pref, clas_e in zip(codigo, id_a, nombres_a, apellidos_a, id_b, nombres_b, apellidos_b, latitud, longitud, color_e, grupo_vulnerable, grupo_vulnerable_2, limitante, iconos, prefx, clase_e):
   Mc_Fichas_Todos.add_child(folium.Marker(location=[lat,lon], name=[doc_b], tags = [g_v, g_v2, limit],
                           icon=folium.Icon(color=c_e,
                           #icon_color=c_i,
                           icon=ico,
                           prefix=pref)))

# Agregar los Clusters a la Capa
    
Capa_Fichas = folium.FeatureGroup(name='Fichas_Vulnerabilidad',show=True)
Mc_Fichas.add_to(Capa_Fichas)
mapa.add_child(Capa_Fichas)

Capa_Fichas_Todos = folium.FeatureGroup(name='Fichas_Poblacional',show=False)
Mc_Fichas_Todos.add_to(Capa_Fichas_Todos)
mapa.add_child(Capa_Fichas_Todos)

# Agregar Buscador en el mapa

BuscaCodigo = Search(
    layer=Capa_Fichas,
    geom_type='Point',
    placeholder="Buscar Titular Ficha",
    search_zoom=40,
    collapsed = False,
    search_label = "name"
).add_to(mapa)

BuscaCodigo_Miembro = Search(
    layer=Capa_Fichas_Todos,
    geom_type='Point',
    placeholder="Buscar Miembro Hogar",
    search_zoom=40,
    collapsed = False,
    search_label = "name"
).add_to(mapa)

# Agregar Marcardores

for cod, doc_a, nom_a, ape_a, doc_b, nom_b, ape_b, lat, lon, c_e, g_v, g_v2, limit, ico, pref, clas_e in zip(codigo, id_a, nombres_a, apellidos_a, id_b, nombres_b, apellidos_b, latitud, longitud, color_e, grupo_vulnerable, grupo_vulnerable_2, limitante, iconos, prefx, clase_e):
   vector=[]
   vector=limit.split(" - ")
   Len_Vector = len(vector)
   Condicion=[1]
   if [clas_e] == Condicion:
         match (Len_Vector):
            case 1:
               columnas = ['ID Diligenciamiento','Tipo_ID','Identificacion','Nombres Completos', 'Apellidos Completos', 'Edad_C', 'Sexos_C', 'Grupo_Vulnerable']
               html = Fichas[[*columnas]]
               html = html.loc[(html['ID Diligenciamiento']) == (cod)]
               html = html.to_html(classes="table") #table-striped table-hover table-condensed table-responsive
               popup = folium.Popup(html)
               folium.CircleMarker(location=[lat,lon], name=[doc_a], tags = [g_v, g_v2,limit],
                  popup=popup,
                  radius=3,
                  fill=True,
                  color=[c_e],
                  fill_color=[c_e], 
                  fill_opacity=1).add_to(mapa)
            case 2:
               v0=vector[0]
               v1=vector[1]
               columnas = ['ID Diligenciamiento','Tipo_ID','Identificacion','Nombres Completos', 'Apellidos Completos', 'Edad_C', 'Sexos_C', 'Grupo_Vulnerable']
               html = Fichas[[*columnas]]
               html = html.loc[(html['ID Diligenciamiento']) == (cod)]
               html = html.to_html(classes="table") #table-striped table-hover table-condensed table-responsive
               popup = folium.Popup(html)
               folium.CircleMarker(location=[lat,lon], name=[doc_a], tags = [g_v, g_v2,v0,v1],
                  popup=popup,
                  radius=3,
                  fill=True,
                  color=[c_e],
                  fill_color=[c_e], 
                  fill_opacity=1).add_to(mapa)           
            case 3:
               v0=vector[0]
               v1=vector[1]
               v2=vector[2]
               columnas = ['ID Diligenciamiento','Tipo_ID','Identificacion','Nombres Completos', 'Apellidos Completos', 'Edad_C', 'Sexos_C', 'Grupo_Vulnerable']
               html = Fichas[[*columnas]]
               html = html.loc[(html['ID Diligenciamiento']) == (cod)]
               html = html.to_html(classes="table") #table-striped table-hover table-condensed table-responsive
               popup = folium.Popup(html)
               folium.CircleMarker(location=[lat,lon], name=[doc_a], tags = [g_v, g_v2,v0,v1,v2],
                  popup=popup,
                  radius=3,
                  fill=True,
                  color=[c_e],
                  fill_color=[c_e], 
                  fill_opacity=1).add_to(mapa)
            case 4:
               v0=vector[0]
               v1=vector[1]
               v2=vector[2]
               v3=vector[3]
               columnas = ['ID Diligenciamiento','Tipo_ID','Identificacion','Nombres Completos', 'Apellidos Completos', 'Edad_C', 'Sexos_C', 'Grupo_Vulnerable']
               html = Fichas[[*columnas]]
               html = html.loc[(html['ID Diligenciamiento']) == (cod)]
               html = html.to_html(classes="table") #table-striped table-hover table-condensed table-responsive
               popup = folium.Popup(html)
               folium.CircleMarker(location=[lat,lon], name=[doc_a], tags = [g_v, g_v2,v0,v1,v2,v3],
                  popup=popup,
                  radius=3,
                  fill=True,
                  color=[c_e],
                  fill_color=[c_e], 
                  fill_opacity=1).add_to(mapa)            
            case 5:
               v0=vector[0]
               v1=vector[1]
               v2=vector[2]
               v3=vector[3]
               v4=vector[4]
               columnas = ['ID Diligenciamiento','Tipo_ID','Identificacion','Nombres Completos', 'Apellidos Completos', 'Edad_C', 'Sexos_C', 'Grupo_Vulnerable']
               html = Fichas[[*columnas]]
               html = html.loc[(html['ID Diligenciamiento']) == (cod)]
               html = html.to_html(classes="table") #table-striped table-hover table-condensed table-responsive
               popup = folium.Popup(html)
               folium.CircleMarker(location=[lat,lon], name=[doc_a], tags = [g_v, g_v2,v0,v1,v2,v3,v4],
                  popup=popup,
                  radius=3,
                  fill=True,
                  color=[c_e],
                  fill_color=[c_e], 
                  fill_opacity=1).add_to(mapa)            
            case 6:
               v0=vector[0]
               v1=vector[1]
               v2=vector[2]
               v3=vector[3]
               v4=vector[4]
               v5=vector[5]
               columnas = ['ID Diligenciamiento','Tipo_ID','Identificacion','Nombres Completos', 'Apellidos Completos', 'Edad_C', 'Sexos_C', 'Grupo_Vulnerable']
               html = Fichas[[*columnas]]
               html = html.loc[(html['ID Diligenciamiento']) == (cod)]
               html = html.to_html(classes="table") #table-striped table-hover table-condensed table-responsive
               popup = folium.Popup(html)
               folium.CircleMarker(location=[lat,lon], name=[doc_a], tags = [g_v, g_v2,v0,v1,v2,v3,v4,v5],
                  popup=popup,
                  radius=3,
                  fill=True,
                  color=[c_e],
                  fill_color=[c_e], 
                  fill_opacity=1).add_to(mapa)
            case 7:
               v0=vector[0]
               v1=vector[1]
               v2=vector[2]
               v3=vector[3]
               v4=vector[4]
               v5=vector[5]
               v6=vector[6]
               columnas = ['ID Diligenciamiento','Tipo_ID','Identificacion','Nombres Completos', 'Apellidos Completos', 'Edad_C', 'Sexos_C', 'Grupo_Vulnerable']
               html = Fichas[[*columnas]]
               html = html.loc[(html['ID Diligenciamiento']) == (cod)]
               html = html.to_html(classes="table") #table-striped table-hover table-condensed table-responsive
               popup = folium.Popup(html)
               folium.CircleMarker(location=[lat,lon], name=[doc_a], tags = [g_v, g_v2,v0,v1,v2,v3,v4,v5,v6],
                  popup=popup,
                  radius=3,
                  fill=True,
                  color=[c_e],
                  fill_color=[c_e], 
                  fill_opacity=1).add_to(mapa)

#Capas del Mapa-----------------------------------------------------

folium.TileLayer('CartoDB Positron').add_to(mapa)
folium.LayerControl(position='topleft').add_to(mapa)

#Grupos de Caracterizacion

Grupo_Poblacional = ['Afrocolombiano','Adulto Mayor','Madre cabeza de familia','Desplazado por la Violencia','Indígenas','Rrom y Población LGTBI','Ninguno', 'Desplazado por desastres naturales', 'Expresidiario', 'Reinsertado']
TagFilterButton(Grupo_Poblacional).add_to(mapa)

#Grupos de Vulnerabilidades

Limitante = ['Bañarse, vestirse o alimentarse por sí mismo','Dificultad para salir a la calle sin ayuda o compañía','Entender o aprender','Hablar','Moverse o caminar por sí mismo','Oír','Ver','Ninguna de las anteriores']
TagFilterButton(Limitante).add_to(mapa)

#Desplegar Mapa

st_map = st_folium(mapa, width=2000, height=450)

#Desplegar Graficas

Condicion_Valores= Fichas.groupby('Grupo_Vulnerable')['Grupo_Vulnerable'].agg(len)
fig =Condicion_Valores.plot.barh(title='Grupos Vulnerables', template='simple_white',color={'Rrom y Población LGTBI':'darkcyan','Desplazado por la Violencia':'red','Afrocolombiano':'green','Desplazado por desastres naturales':'blue', 'Indígenas': 'lightgray','Madre cabeza de familia': 'pink', 'Adulto Mayor':'orange','Expresidiario':'ligthgreen', 'Reinsertado':'darkgreen'})

Sexo_Valores=Fichas.groupby('Sexos_C')['Sexos_C'].agg(len)
fig2=Sexo_Valores.plot.bar(title='Distribucion Poblacional Por Sexo', template='simple_white',color={'Mujer':'red','Hombre':'green','ND':'lightgray'})

Vulnerable = st.sidebar.plotly_chart(fig)
Vulnerable = st.sidebar.plotly_chart(fig2)
