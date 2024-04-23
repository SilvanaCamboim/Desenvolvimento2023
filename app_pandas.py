import streamlit as st
from streamlit_folium import folium_static
import folium
import geopandas as gpd
import pandas as pd
import plotly.express as px
import requests
from io import StringIO

url_bairros = 'https://raw.githubusercontent.com/SilvanaCamboim/Desenvolvimento2023/main/bairros.geojson'
url_estacionamentos = 'https://raw.githubusercontent.com/SilvanaCamboim/Desenvolvimento2023/main/estacionamentos.geojson'

# Usando geopandas para ler diretamente das URLs
try:
    bairros = gpd.read_file(url_bairros)
    estacionamentos = gpd.read_file(url_estacionamentos)
    print("Arquivos lidos com sucesso!")
except Exception as e:
    print(f"Erro ao ler os arquivos GeoJSON: {e}")

# Check if the request was successful
for response in responses:
    if response.status_code == 200:
        # Read the GeoJSON file using geopandas
        polygons = gpd.read_file(response_bairros)
        points = gpd.read_file(response_estacionamentos)
    else:
        st.error(f"Error: {response.status_code} - Could not download the GeoJSON file.")

PAGE_CONFIG = {"page_title":"Aplicação de Mapas com Pandas","page_icon":":smiley:","layout":"centered"}
st.set_page_config(**PAGE_CONFIG)

def main():
   # Essa cópia é feita pois os pontos serão designados aos polígonos dos bairros
  pts = points.copy()
  pts_in_polys = []

  # Conta quantos pontos há em cada polígono
  for i, poly in polygons.iterrows():
    pts_in_this_poly = []
    for j, pt in pts.iterrows():
        if poly.geometry.contains(pt.geometry):
            pts_in_this_poly.append(pt.geometry)
            pts = pts.drop([j])
    pts_in_polys.append(len(pts_in_this_poly))
  # Adiciona o número de pontos ao data frame dos polígonos
  polygons['num_pto'] = gpd.GeoSeries(pts_in_polys)
  st.title("Criar aplicações com dados e mapas")
  st.subheader("Dados dos Estacionamentos por bairros em Curitiba")
	#Tabela com os dados sumarizados
  st.table(polygons.describe())
	# Cria a barra para a definição do número de estacionamentos no histograma
  values = st.sidebar.slider("Número de estacionamentos", float(polygons.num_pto.min()), 400., (10., 50.))
  f = px.histogram(polygons.query(f"num_pto.between{values}", engine='python'), x="num_pto", title="Distribuição de Estacionamentos")
  f.update_xaxes(title="Estacionamentos")
  f.update_yaxes(title="Número")
  st.plotly_chart(f) 
	#chama o mapa usando o Folium
  with st.echo():
    m = folium.Map (location = [-25.5,-49.3],tiles = 'Stamen Terrain',zoom_start =  13)
    bins = list(polygons['num_pto'].quantile([0, 0.25, 0.5, 0.75, 1]))
    folium.Choropleth(
       geo_data=polygons,
        name='estacionamentos por bairro',
        columns=['OBJECTID', 'num_pto'],
        data=polygons,
        key_on='feature.properties.OBJECTID',
        fill_color='YlGn',
        legend_name='estacionamentos por bairro',
        bins=bins,
        reset=True
       ).add_to(m)
    folium.LayerControl().add_to(m)
		#passa o folium para o streamlit
    folium_static(m)
    
if __name__ == '__main__':
    main()
