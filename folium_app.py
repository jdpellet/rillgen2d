import streamlit as st
import folium
from streamlit_folium import folium_static
import pandas as pd

# Create a folium map
m = folium.Map(location=[45.5236, -122.6750])

# Create a marker
folium.Marker(
    location=[45.5236, -122.6750],
    popup="Welcome to <b>PORTLAND</b>",
).add_to(m)

# Display the map in Streamlit
folium_static(m)