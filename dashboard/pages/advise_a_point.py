import streamlit as st
import pandas as pd
import folium
from shapely.geometry import Point
import geopandas as gpd
import matplotlib.pyplot as plt
from pygris import tracts

import census_finder as cf
import tradeAreaProcessing as tap

st.title('Digital Advertisement Use Case 📊')

token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhcHBJZCI6ImhqdDZib3dkZGIiLCJ0b2tlbiI6eyJpdiI6IjdhNDE3MjYwNWVlOGIwMDYzOTQ3YjAxNzhkY2Q0N2NlIiwiY29udGVudCI6ImU3NzdmMGEzZWY4MDc3MDg2MDIxZGMzZWIyNDA2MmM5NTM0NTViMDVmNTk3NTlhMjZkYzZkMmJjNDNlNTUxOGRkMWMxMjIwZGNhNGRlOTg0ODc3NTk0MjEwMGZiYjA4NjAzOTM3YjM3YjM1NmJkZGM0MjAwYjFhNjQ4MTgyZDU5MTQ5ZTA3MTYyZDA5NDk5MWVkMWNkODU3MjRiYjQ3ZTBiYWFkYzdhYzc3ODQzZGIzNzQ0Y2YzNmQ2MTI0Y2IzNzRkNDc3ODJjZTVkYWE1N2VlMTdjODc2YmZmZDVjNzE4OWM3ZDc1ZjkyYTJlMjU2YzhmN2E1YjFiNzU0OWRhOWZkNTc3OWJjNWM0MWQ4MDZhZTEwY2I0OTdhMDZiMDRjYzJiMzY3YmJhYjRhNzE4ZmU2ODZmMWJmZWFkYjA2NmU5ZDdlMmZhZWJkMDQwY2M2OTkzYTA3MzlhNTgxY2RkYzk2YWI1OTMwM2ZkZGU2ZjAzYTdjZjdjZWI4MjI5MDU3N2RhYzc1Nzc1NjY4ZTFhMDhlMzI5OWUxZmUwYmZhOWZjZGM0ZmUzZTA3YTkwNTViMDAyNjc5YTVhOTZmNzBlNmJhMDI5NjEzZjlkNWFmNTgyMWRjY2FjY2EwMTVkY2UxM2IwODY4ODU4NzNlNWVmYWFhOGZkOTBjMmIyYTNmZjdlZTg5NzU3NmMzZmRlNzhmYmU5MDA5OWYwMjVlODQ4NGJkZjI3OGRmZGYxN2ZmZDczYTRlMGRjMDY5NWNiZTZhZDQ3OWVkZDkxNGQyMGU5NGUzYjcwMmZjNDZjZWNmN2MzYWJhNzZlODA5N2JjMzYwZGU0YzdhZGJkNGM1OWZiZjZjMDViMTNkNDIxMGUzZTBlNDUwM2E3In0sInNlY3VyaXR5VG9rZW4iOnsiaXYiOiI3YTQxNzI2MDVlZThiMDA2Mzk0N2IwMTc4ZGNkNDdjZSIsImNvbnRlbnQiOiJmNjc3ZjhmOGNmYTU3ZjAwMTc2NWYwMWVhODcwNTFiYTcyNjA0NTAxZjFjYzZkZmQ1YWQxYTJmZDc4YmUxOGVjYzRlZTVjNDRhNTVhZjc5Nzg1M2JhYjFmIn0sImp0aSI6IjUzYWFhNjA4LTg4MDAtNDU4NS05Y2FiLWE4OWY2NzljODhiZCIsImlhdCI6MTcwMTU4ODY0MSwiZXhwIjoxNzAxNTkyMjQxfQ.n6rxPC1sS6YW-LGDfP8w2gbjoGJ87lzmwKcgF_PKdio'
df = pd.read_csv('./dashboard/pages/charger_loc.csv')


# Function to initialize map
def init_map(center=[37.76, -122.4], zoom_start=12, map_type="OpenStreetMap"):
    return folium.Map(location=center, zoom_start=zoom_start, tiles=map_type)

# Function to create a GeoDataFrame from a DataFrame
def create_point_map(df):
    df[['Latitude', 'Longitude']] = df[['Latitude', 'Longitude']].apply(pd.to_numeric, errors='coerce')
    df['coordinates'] = df.apply(lambda row: Point(row.Longitude, row.Latitude), axis=1)
    gdf = gpd.GeoDataFrame(df, geometry='coordinates')
    return gdf

# Function to plot markers on the Folium map
def plot_from_df(df, folium_map):
    gdf = create_point_map(df)
    for i, row in gdf.iterrows():
        popup_message = f"Station Name: {row['Station Name']}"  # Customize the popup message here
        folium.Marker([row['Latitude'], row['Longitude']], popup=folium.Popup(popup_message, parse_html=True)).add_to(folium_map)
    return folium_map

# Initialize the map and plot markers
m = init_map()
m = plot_from_df(df, m)

# Display the map in Streamlit
st.write(m)

# Load data and fill in map
tapper = tap.tradeAreasPreprocessing(token=token,
                                    od = 'destination',
                                    geoFilterType = 'circle',
                                    radius = '0.2km',
                                    points = f'{33.772815}|{-84.39043}',
                                    providerType = 'consumer',
                                    startDateTime = '%3E%3D2023-06-01T02%3A31',
                                    endDateTime = '%3C%3D2023-06-15T02%3A31')
df = pd.read_csv('./dashboard/pages/origin_demographics.csv')

# Load the GeoJSON file into a GeoDataFrame and csv into df
geojson_location = "./dashboard/pages/sf-tracts-2020-GEOID.geojson"
census_data = "./dashboard/pages/census_data_clean.csv"
gdf = gpd.read_file(geojson_location)
census_df = pd.read_csv(census_data, dtype={"tract": str})

# # Get df based on chosen destination
# df = tapper.read_data()
# df = tapper.create_dataframe(df)
# df = tapper.separate_coordinates(df)
# df = tapper.add_temporal_vars(df)
trips_gdf = tapper.get_trip_geometry(df)
df = df.drop(columns='tripId')
trips_gdf = pd.concat([trips_gdf, df], axis=1)
ca_tiger = tapper.downloadShapefile()
intersected_trips = tapper.intersectedTrips(trips_gdf, ca_tiger[['geometry','GEOID']], sample_n=10000)



# Sample data
# data = {
#     'ID': ['Monkey', 'B'],
#     'Latitude': ['33.772815', '33.829216'],
#     'Longitude': ['-84.39043', '-86.92847']
# }