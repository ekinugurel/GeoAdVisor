import geopandas as gpd
from shapely.geometry import Point
import pandas as pd



def get_census_tract_info(latitude, longitude, gdf):
    # Create a Point object from the provided coordinates
    point = Point(longitude, latitude)

    # Perform the spatial query to find which polygon contains the point
    for index, row in gdf.iterrows():
        if row['geometry'].contains(point):
            return {
                "TRACTCE20": row['TRACTCE20'],
            }
    return "No census tract found for the given coordinates."

# lookup demographics in census data from tract numbere
def lookup_demographics(census_data, tract_no):
    print(tract_no)
    print(str(census_data['tract'].iloc[0]))
    tract_demographics = census_data[census_data['tract']==tract_no]
    return tract_demographics

def main():
    # read in files
    geojson_location = "/Users/kaitlynng/Desktop/Coding/GeoAdVisor/sf-tracts-2020-clipped.geojson"
    census_data = "/Users/kaitlynng/Desktop/Coding/GeoAdVisor/census_data/census_data_clean.csv"

    # Load the GeoJSON file into a GeoDataFrame and csv into df
    gdf = gpd.read_file(geojson_location)
    census_df = pd.read_csv(census_data, dtype={"tract": str})

    # Filter out invalid geometries
    gdf = gdf[gdf.is_valid]

    # Example usage
    latitude = 37.7749  # Replace with actual latitude
    longitude = -122.4194  # Replace with actual longitude
    census_tract_info = get_census_tract_info(latitude, longitude, gdf)

    if census_tract_info:
        print(f"Census Tract Info: {census_tract_info}")
        demographics = lookup_demographics(census_df, census_tract_info["TRACTCE20"])
        print(demographics)
    else:
        print("Could not determine the census tract for the provided coordinates.")

main()