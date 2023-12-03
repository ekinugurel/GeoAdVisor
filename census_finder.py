import geopandas as gpd
from shapely.geometry import Point
import pandas as pd

class censusFinder():
    def __init__(self, gdf, census_data):
        self.gdf = gdf
        self.census_data = census_data

    def get_census_tract_info(self, latitude, longitude):
        # Create a Point object from the provided coordinates
        point = Point(longitude, latitude)

        # Perform the spatial query to find which polygon contains the point
        for index, row in self.gdf.iterrows():
            if row['geometry'].contains(point):
                return row['TRACTCE20']
        return "No census tract found for the given coordinates."

    # lookup demographics in census data from tract numbere
    def lookup_demographics(self, tract_no):
        #print(str(self.census_data['tract'].iloc[0]))
        tract_demographics = self.census_data[self.census_data['tract']==tract_no]
        return tract_demographics

    

# def main():
#     # read in files
#     geojson_location = "/Users/ekinokos2/Library/CloudStorage/OneDrive-UW/GeoAdVisor/sf-tracts-2020-clipped.geojson"
#     census_data = "/Users/ekinokos2/Library/CloudStorage/OneDrive-UW/GeoAdVisor/census_data/census_data_clean.csv"

#     # Load the GeoJSON file into a GeoDataFrame and csv into df
#     gdf = gpd.read_file(geojson_location)
#     census_df = pd.read_csv(census_data, dtype={"tract": str})

#     # Filter out invalid geometries
#     gdf = gdf[gdf.is_valid]

#     # Example usage
#     latitude = 37.7749  # Replace with actual latitude
#     longitude = -122.4194  # Replace with actual longitude
#     census_tract_info = get_census_tract_info(latitude, longitude, gdf)

#     if census_tract_info:
#         print(f"Census Tract Info: {census_tract_info}")
#         demographics = lookup_demographics(census_df, census_tract_info["TRACTCE20"])
#         print(demographics)
#     else:
#         print("Could not determine the census tract for the provided coordinates.")

# main()