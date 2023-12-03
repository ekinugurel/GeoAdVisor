import streamlit as st
import pandas as pd
import folium
from shapely.geometry import Point
import geopandas as gpd
import matplotlib.pyplot as plt
from pygris import tracts
import requests

import census_finder as cf
import tradeAreaProcessing as tap


st.title('Last Stop Analysis')
HASH_TOKEN = 'aGp0NmJvd2RkYnxiQ1pCZFdkZ2t5NVE1Y3NNSFRxTk0yOWdKYVNPS2dTdDhrVTdtZzJq'
APP_ID = 'hjt6bowddb'
TOKEN_URL = 'https://api.iq.inrix.com/auth/v1/appToken'
def get_token():
    #Pass in the app_id and hash_token as query parameters
    params = {'appId': APP_ID,
    'hashToken': HASH_TOKEN}
    response = requests.get(TOKEN_URL, params=params)
    response.raise_for_status() # Raise HTTPError for bad responses
    data = response.json()
    token = data['result']['token']
    return token, response.status_code

token, status_code = get_token()
ev_df = pd.read_csv('charger_loc.csv')

st.map(data=ev_df, latitude='Latitude', longitude='Longitude', color=None, size=None, zoom=None, use_container_width=True)

# Get user point
selected_marker = st.selectbox('Select Marker', ev_df['Station Name'].tolist())
selected_index = ev_df.index[ev_df['Station Name'] == selected_marker].tolist()[0]
selected_lon = ev_df.loc[selected_index, 'Longitude']
selected_lat = ev_df.loc[selected_index, 'Latitude']

if selected_marker:
    st.write(f"You selected station: {selected_marker}")
    st.write(f"Charger Provider: {ev_df.loc[selected_index, 'EV Network']}")
    if ev_df.loc[selected_index, 'EV Level2 EVSE Num'] > 0:
        st.write(f"Number of L2 Chargers: {int(ev_df.loc[selected_index, 'EV Level2 EVSE Num'])}")
    if ev_df.loc[selected_index, 'EV DC Fast Count'] > 0:
        st.write(f"Number of L3 Chargers: {int(ev_df.loc[selected_index, 'EV DC Fast Count'])}")
    st.write(f"Access: {ev_df.loc[selected_index, 'Access Code']}")
  
    st.write(f"Charger Provider: {ev_df.loc[selected_index, 'EV Network']}")
    st.write(f"Access: {ev_df.loc[selected_index, 'Access Code']}")

# Load data and fill in map
tapper = tap.tradeAreasPreprocessing(token=token,
                                    od = 'destination',
                                    geoFilterType = 'circle',
                                    radius = '0.2km',
                                    points = f'{selected_lat}|{selected_lon}',
                                    providerType = 'consumer',
                                    startDateTime = '%3E%3D2023-06-01T02%3A31',
                                    endDateTime = '%3C%3D2023-06-15T02%3A31')

# Get df based on chosen destination
df = tapper.read_data()
df = tapper.create_dataframe(df)
df = tapper.separate_coordinates(df)
df = tapper.add_temporal_vars(df)
# trips_gdf = tapper.get_trip_geometry(df)
ca_tiger = tapper.downloadShapefile()
# intersected_trips = tapper.intersectedTrips(trips_gdf, ca_tiger)

# read in files
geojson_location = "sf-tracts-2020-GEOID.geojson"
census_data = "census_data_clean.csv"

# Load the GeoJSON file into a GeoDataFrame and csv into df
gdf = gpd.read_file(geojson_location)
census_df = pd.read_csv(census_data, dtype={"tract": str})
# Get the origin tracts for the trips
df['startLoc']
trip_tract_info = [cf.get_census_tract_info(lat,lon)['TRACTCE20'] for lat,lon in zip(df['startLoc'].str.split(',').str[0], df['startLoc'].str.split(',').str[1])]
df['home_tract'] = trip_tract_info
df = pd.merge(df, census_df, left_on='home_tract', right_on='tract')

st.title('Histogram of pct_nonwhite')
st.write("Histogram")
fig, ax = plt.subplots()
ax.hist(df['pct_nonwhite'])
st.pyplot(fig)
# st.plotly_chart(df['pct_nonwhite'], use_container_width=True)


# Sample data
# data = {
#     'ID': ['Monkey', 'B'],
#     'Latitude': ['33.772815', '33.829216'],
#     'Longitude': ['-84.39043', '-86.92847']
# }