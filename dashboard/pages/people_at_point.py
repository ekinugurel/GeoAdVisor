import streamlit as st
import pandas as pd
import folium
from shapely.geometry import Point
import geopandas as gpd
import matplotlib.pyplot as plt
from pygris import tracts

import tradeAreaProcessing as tap


st.title('Last Stop Analysis')

token = ''

tapper = tap.tradeAreasPreprocessing(token=token,
                                    od = 'destination',
                                    geoFilterType = 'circle',
                                    radius = '0.2km',
                                    points = f'{37.734622}|{-122.471603}',
                                    providerType = 'consumer',
                                    startDateTime = '%3E%3D2023-06-01T02%3A31',
                                    endDateTime = '%3C%3D2023-06-15T02%3A31')

# Get df based on chosen destination
df = tapper.read_data()
df = tapper.create_dataframe(df)
df = tapper.separate_coordinates(df)
df = tapper.add_temporal_vars(df)
trips_gdf = tapper.get_trip_geometry(df)
ca_tiger = tapper.downloadShapefile()
intersected_trips = tapper.intersectedTrips(trips_gdf, ca_tiger)

# read in files
geojson_location = "./dashboard/pages/sf-tracts-2020-GEOID.geojson"
census_data = "/Users/ekinokos2/Library/CloudStorage/OneDrive-UW/GeoAdVisor/census_data/census_data_clean.csv"

# Load the GeoJSON file into a GeoDataFrame and csv into df
gdf = gpd.read_file(geojson_location)
census_df = pd.read_csv(census_data, dtype={"tract": str})

# Filter out invalid geometries
gdf = gdf[gdf.is_valid]

# Initialize class
cf = census_finder.censusFinder(gdf, census_df)
tract_no = cf.get_census_tract_info(37.734622, -122.471603)
demographics = cf.lookup_demographics(tract_no)







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

selected_coordinates = [df.loc[selected_index, ‘Latitude’], df.loc[selected_index, ‘Longitude’]]

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

