import geopandas as gpd
from shapely.geometry import Point

# Location of the GeoJSON file
geojson_location = "./dashboard/pages/sf-tracts-2020-GEOID.geojson"

# Load the GeoJSON file into a GeoDataFrame
gdf = gpd.read_file(geojson_location)

# Filter out invalid geometries
gdf = gdf[gdf.is_valid]

def get_census_tract_info(latitude, longitude):
    # Create a Point object from the provided coordinates
    point = Point(longitude, latitude)

    # Perform the spatial query to find which polygon contains the point
    for index, row in gdf.iterrows():
        if row['geometry'].contains(point):
            return {
                "TRACTCE20": row['TRACTCE20'],
                "GEOID": row['GEOID'],
            }
    return {"TRACTCE20": None, "GEOID": None}

# Example usage
latitude = 37.7749  # Replace with actual latitude
longitude = -122.4194  # Replace with actual longitude
census_tract_info = get_census_tract_info(latitude, longitude)

if census_tract_info:
    print(f"Census Tract Info: {census_tract_info}")
else:
    print("Could not determine the census tract for the provided coordinates.")