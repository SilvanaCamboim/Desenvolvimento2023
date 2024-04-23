import streamlit as st
from streamlit_folium import folium_static
import folium
import geopandas as gpd
import pandas as pd
import plotly.express as px

# Carregamento dos dados
url_bairros = 'https://raw.githubusercontent.com/SilvanaCamboim/Desenvolvimento2023/main/bairros.geojson'
url_estacionamentos = 'https://raw.githubusercontent.com/SilvanaCamboim/Desenvolvimento2023/main/estacionamentos.geojson'
polygons = gpd.read_file(url_bairros)
points = gpd.read_file(url_estacionamentos)

# Configuração da página
PAGE_CONFIG = {"page_title":"Aplicação de Mapas com Pandas", "page_icon":":smiley:", "layout":"centered"}
st.set_page_config(**PAGE_CONFIG)

def main():
    # Cria uma dropdown para escolher a regional
    regionais = polygons['NM_REGIONA'].unique()
    regional_selecionada = st.sidebar.selectbox('Escolha a regional', regionais)

    # Filtra os bairros por regional selecionada
    bairros_filtrados = polygons[polygons['NM_REGIONA'] == regional_selecionada]

    # Conta pontos dentro de cada polígono filtrado
    pts_in_polys = []
    for i, poly in bairros_filtrados.iterrows():
        pts_in_this_poly = points[points.within(poly.geometry)]
        pts_in_polys.append(len(pts_in_this_poly))

    bairros_filtrados['num_pto'] = pts_in_polys

    # Slidebar para filtrar pelo número de estacionamentos
    num_estacionamentos = st.sidebar.slider("Número de estacionamentos", int(bairros_filtrados['num_pto'].min()), int(bairros_filtrados['num_pto'].max()), (int(bairros_filtrados['num_pto'].min()), int(bairros_filtrados['num_pto'].max())))
    
    # Filtra os bairros pelo número de estacionamentos
    bairros_finais = bairros_filtrados[bairros_filtrados['num_pto'].between(num_estacionamentos[0], num_estacionamentos[1])]

    # Plota o histograma
    f = px.histogram(bairros_finais, x="num_pto", title="Distribuição de Estacionamentos")
    f.update_xaxes(title="Estacionamentos")
    f.update_yaxes(title="Número")
    st.plotly_chart(f)

    # Mapa com Folium
    m = folium.Map(location=[-25.5, -49.3], tiles='Stamen Terrain', zoom_start=11)
    folium.Choropleth(
        geo_data=bairros_finais.to_json(),
        name='estacionamentos por bairro',
        data=bairros_finais,
        columns=['OBJECTID', 'num_pto'],
        key_on='feature.properties.OBJECTID',
        fill_color='YlGn',
        legend_name='Estacionamentos por bairro'
    ).add_to(m)
    folium.LayerControl().add_to(m)
    folium_static(m)

if __name__ == '__main__':
    main()
