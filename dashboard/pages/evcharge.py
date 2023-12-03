import streamlit as st
import pandas as pd
import folium
from shapely.geometry import Point
import geopandas
import matplotlib.pyplot as plt

st.title('EV Chargers Use Case 🔋')

# Function to initialize map
def init_map(center=[37.76, -122.4], zoom_start=12, map_type="OpenStreetMap"):
    return folium.Map(location=center, zoom_start=zoom_start, tiles=map_type)

# Function to create a GeoDataFrame from a DataFrame
def create_point_map(df):
    df[['Latitude', 'Longitude']] = df[['Latitude', 'Longitude']].apply(pd.to_numeric, errors='coerce')
    df['coordinates'] = df.apply(lambda row: Point(row.Longitude, row.Latitude), axis=1)
    gdf = geopandas.GeoDataFrame(df, geometry='coordinates')
    return gdf

# Function to plot markers on the Folium map
def plot_from_df(df, folium_map):
    gdf = create_point_map(df)
    for i, row in gdf.iterrows():
        popup_message = f"Station Name: {row['Station Name']}"  # Customize the popup message here
        folium.Marker([row['Latitude'], row['Longitude']], popup=folium.Popup(popup_message, parse_html=True)).add_to(folium_map)
    return folium_map

# Sample data
# data = {
#     'ID': ['Monkey', 'B'],
#     'Latitude': ['33.772815', '33.829216'],
#     'Longitude': ['-84.39043', '-86.92847']
# }

# df = pd.DataFrame(data)
df = pd.read_csv('./charger_loc.csv')

# Initialize the map and plot markers
m = init_map()
m = plot_from_df(df, m)

# Display the map in Streamlit
st.write(m)

selected_marker = st.selectbox('Select Marker', df['Station Name'].tolist())
selected_index = df.index[df['Station Name'] == selected_marker].tolist()[0]

if selected_marker:
    st.write(f"You selected station: {selected_marker}")
    st.write(f"Charger Provider: {df.loc[selected_index, 'EV Network']}")
    if df.loc[selected_index, 'EV Level2 EVSE Num'] > 0:
        st.write(f"Number of L2 Chargers: {int(df.loc[selected_index, 'EV Level2 EVSE Num'])}")
    if df.loc[selected_index, 'EV DC Fast Count'] > 0:
        st.write(f"Number of L3 Chargers: {int(df.loc[selected_index, 'EV DC Fast Count'])}")
    st.write(f"Access: {df.loc[selected_index, 'Access Code']}")
  
    st.write(f"Charger Provider: {df.loc[selected_index, 'EV Network']}")
    st.write(f"Access: {df.loc[selected_index, 'Access Code']}")

