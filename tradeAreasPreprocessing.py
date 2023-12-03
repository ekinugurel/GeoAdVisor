import pandas as pd
import requests
import geopandas as gpd
from shapely.geometry import LineString
from pygris import tracts
import shapely

class tradeAreasPreprocessing():
    def __init__(self, token, od, geoFilterType, radius, points, providerType,
                 startDateTime, endDateTime):
        self.token = token
        self.od = od
        self.geoFilterType = geoFilterType
        self.radius = radius
        self.points = points
        self.providerType = providerType
        self.startDateTime = startDateTime
        self.endDateTime = endDateTime

    def read_data(self):
        """
        Read data from endpoint_url
        """
        data = requests.get(f'https://api.iq.inrix.com/v1/trips?od={self.od}&geoFilterType={self.geoFilterType}&radius={self.radius}&points={self.points}&providerType={self.providerType}&startDateTime={self.startDateTime}&endDateTime={self.endDateTime}', headers={'Authorization': f"Bearer {self.token}"}).json()
        return data

    def create_dataframe(self, data):
        """
        Create dataframe from data
        """
        df = pd.DataFrame.from_dict(data['data'])
        return df
    
    def separate_coordinates(self, df):
        """
        Separate coordinates from dataframe
        """
        df['start_lat'] = df['startLoc'].apply(lambda x: x.split(',')[0]).astype(float)
        df['start_lon'] = df['startLoc'].apply(lambda x: x.split(',')[1]).astype(float)
        df['end_lat'] = df['endLoc'].apply(lambda x: x.split(',')[0]).astype(float)
        df['end_lon'] = df['endLoc'].apply(lambda x: x.split(',')[1]).astype(float)
        return df
    
    def get_trip_geometry(self, response_df, crs='EPSG:4326'):
        start_pts = gpd.points_from_xy(response_df['startLoc'].str.split(',').str[1], response_df['startLoc'].str.split(',').str[0])
        end_pts = gpd.points_from_xy(response_df['endLoc'].str.split(',').str[1], response_df['endLoc'].str.split(',').str[0])
        trip_lines = [shapely.geometry.LineString([start_pt, end_pt]) for start_pt, end_pt in zip(start_pts, end_pts)]
        trips_gdf = gpd.GeoDataFrame(response_df, geometry=trip_lines, crs=crs)
        return trips_gdf[['tripId','geometry']]

    def create_linestring(self, df):
        """
        Create linestring from coordinates
        """
        df['geometry'] = df.apply(lambda x: LineString([(x['start_lon'], x['start_lat']), (x['end_lon'], x['end_lat'])]), axis=1)
        return df
    
    def add_temporal_vars(self, df):
        """
        Add temporal variables to dataframe
        """
        df['startDateTime'] = pd.to_datetime(df['startDateTime'], format='%Y-%m-%dT%H:%M:%S.%fZ')
        df['endDateTime'] = pd.to_datetime(df['endDateTime'], format='%Y-%m-%dT%H:%M:%S.%fZ')
        df['duration'] = (df['endDateTime'] - df['startDateTime']).dt.total_seconds()
        df['day'] = df['startDateTime'].dt.day
        df['month'] = df['startDateTime'].dt.month
        df['year'] = df['startDateTime'].dt.year
        df['dow'] = df['startDateTime'].dt.dayofweek
        df['start_hour'] = df['startDateTime'].dt.hour
        df['end_hour'] = df['endDateTime'].dt.hour
        df['start_date'] = df['startDateTime'].dt.date
        df['end_date'] = df['endDateTime'].dt.date
        df['weekend'] = df['dow'].apply(lambda x: 1 if x >= 5 else 0)
        return df
    
    def add_mode(self, df):
        """
        Add mode to dataframe using tripMeanSpeedKPH
        """ 
        mode = []
        if df['tripMeanSpeedKPH'] <= 10 and df['tripMeanSpeedKPH'] > 0:
            mode.append('walk')
        elif df['tripMeanSpeedKPH'] <= 20 and df['tripMeanSpeedKPH'] > 10:
            mode.append('bike')
        elif df['tripMeanSpeedKPH'] <= 30 and df['tripMeanSpeedKPH'] > 20:
            mode.append('bus')
        elif df['tripMeanSpeedKPH'] > 30:
            mode.append('car')

        df['mode'] = mode
        return df
    
    def poly_locate_line_points(self, line_geo, poly_geo):
        if line_geo.intersects(poly_geo):
            intersection = line_geo.intersection(poly_geo)
            first_point = intersection.boundary.geoms[0]
            last_point = intersection.boundary.geoms[-1]
            res = (line_geo.project(first_point)*111111, line_geo.project(last_point)*111111)
            return res
        else:
            return None
        
    def downloadShapefile(self, state = "CA", year=2020, epsg='4326', county='075'):
        """
        Download shapefile of San Francisco County
        """
        ca_tiger = tracts(state=state, cache=True, year=year).to_crs(epsg=epsg)
        ca_tiger = ca_tiger[ca_tiger['COUNTYFP']==county]
        return ca_tiger[['GEOID','geometry']]
    
    def intersectedTrips(self, trip_geo_lookup, sf_geo_lookup):
        """
        Find intersected trips
        """
        intersected_trips = gpd.sjoin(trip_geo_lookup, sf_geo_lookup, how='inner', predicate='intersects')[['tripId','GEOID']].sort_values(['tripId','GEOID'])
        intersected_trips = pd.merge(intersected_trips, sf_geo_lookup, on='GEOID', how='inner')
        intersected_trips = pd.merge(intersected_trips, trip_geo_lookup, on='tripId', how='inner')
        intersected_trips['line_locs'] = intersected_trips.apply(lambda x: self.poly_locate_line_points(x['geometry_x'], x['geometry_y']), axis=1)
        return intersected_trips    