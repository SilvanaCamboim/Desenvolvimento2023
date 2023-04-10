import streamlit as st
from streamlit_folium import folium_static
import folium

PAGE_CONFIG = {"page_title":"Aplicação de Mapas","page_icon":":smiley:","layout":"centered"}
st.set_page_config(**PAGE_CONFIG)

def main():
	st.title("Como adicionar mapas no StreamLit")
	st.subheader("Baseado num caderno do Colab")
	menu = ["Home","Mapa"]
	choice = st.sidebar.selectbox('Menu',menu)
	if choice == 'Home':
		st.subheader("Página Inicial 1")
	elif choice == 'Mapa':
		st.subheader("Visualizar Mapa")
		with st.echo():
			m = folium.Map (location = [-25.5,-49.3],tiles = 'Stamen Terrain', zoom_start =  11)
			folium_static(m)
	else: 
		st.subheader("")
if __name__ == '__main__':
	main()
