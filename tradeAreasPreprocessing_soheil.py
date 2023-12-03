import pandas as pd
import requests
import geopandas as gpd
from shapely.geometry import LineString, MultiLineString
from pygris import tracts
import shapely
import googlemaps

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

    def get_inrix_route(self, wp_1, wp_2, departure_time=None):
        '''
        wp_1 and wp_2 are str(lat, long) points.

        departure_time: default: now, DepartureTime must be within nine months from the time of the API call, and must occur in the future.,
         format:YYYY-MM-DDTHH:MM:SSZ; for example 2009-04-04T13:42:41Z.
        '''
        auth_token = f'Bearer {self.token}'
        findRoute_url = 'https://api.iq.inrix.com/findRoute'
        format = 'json'
        routeOutputFields = 'P,summary'
        if departure_time is None:
            route = requests.get(findRoute_url, headers={'Authorization': auth_token},
                                 params={'wp_1': wp_1,
                                         'wp_2': wp_2,
                                         'format': format,
                                         'routeOutputFields': routeOutputFields})
        else:
            route = requests.get(findRoute_url, headers={'Authorization': auth_token},
                                 params={'wp_1': wp_1,
                                         'wp_2': wp_2,
                                         'format': format,
                                         'routeOutputFields': routeOutputFields,
                                         'departure_time': departure_time})
        data = route.json()
        print(data)
        # result = data['result']['trip']
        route = data['result']['trip']['routes'][0]
        out = {'travelTimeMinutes': route['travelTimeMinutes'],
               'averageSpeed': route['averageSpeed'],
               'totalDistance': route['totalDistance'],
               'points': route['points']['coordinates']}
        return out


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

    def get_multiline_trip_geometry(self, response_df, departure_time=None, crs='EPSG:4326'):
        start_pts = gpd.points_from_xy(response_df['startLoc'].str.split(',').str[1], response_df['startLoc'].str.split(',').str[0])
        end_pts = gpd.points_from_xy(response_df['endLoc'].str.split(',').str[1], response_df['endLoc'].str.split(',').str[0])
        # all_trip_points = [self.get_inrix_route(start_pt, end_pt, departure_time)['points'] for start_pt, end_pt in zip(start_pts, end_pts)]
        # all_trip_points = [self.get_google_route([str(start_pt), str(end_pt)], departure_time)['points'] for start_pt, end_pt in zip(start_pts, end_pts)]
        #[print([str(start_pt), str(end_pt)], departure_time) for start_pt, end_pt in zip(start_pts, end_pts)]
        all_trip_points = []
        trip_lines = []
        for start_pt, end_pt in zip(start_pts, end_pts):
            waypoint = [f'{start_pt.y},{start_pt.x}', f'{end_pt.y},{end_pt.x}']
            trip_points = get_google_route(waypoint, departure_time)['points']
            all_trip_points.append(trip_points)
            try:
                trip_lines.append(shapely.geometry.MultiLineString(trip_points))
            except:
                trip_lines.append(shapely.geometry.LineString(trip_points))
        trips_gdf = gpd.GeoDataFrame(response_df, geometry=trip_lines, crs=crs)
        return trips_gdf[['tripId', 'geometry']]
        
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
        intersected_trips['line_locs'] = intersected_trips.apply(lambda x: self.poly_locate_line_points(x['geometry_y'], x['geometry_x']), axis=1)
        return intersected_trips    

def get_google_route(waypoints, departure_time=None):
        with open('google_routing_api_key.txt', 'r') as f:
            API_KEY = f.read()
        gmaps = googlemaps.Client(key=API_KEY)
        #https://developers.google.com/maps/documentation/directions/get-directions
        # departure_time is time as an integer in seconds since midnight, January 1, 1970 UTC.
        # There should be no space between lat and long
        # waypoints = ['37.80300372563528,-122.42538202577136', '37.76799081681866,-122.41476498906668']
        
        travel_mode = "driving"
        if departure_time is None:
            directions_result = gmaps.directions(
                origin=waypoints[0],
                destination=waypoints[-1],
                waypoints=waypoints[1:-1],
                mode=travel_mode)
        else:
            directions_result = gmaps.directions(
                origin=waypoints[0],
                destination=waypoints[-1],
                waypoints=waypoints[1:-1],
                mode=travel_mode,
                departure_time=departure_time)

        duration = directions_result[0]['legs'][0]['duration']['text']
        distance = directions_result[0]['legs'][0]['distance']['text']
        points = []
        for step in directions_result[0]['legs'][0]['steps']:
            loc = step['start_location']
            points.append([loc['lng'], loc['lat']])
            
        last_loc =  directions_result[0]['legs'][0]['steps'][-1]['end_location']
        points.append([last_loc['lat'], last_loc['lng']])
        clean_result = {'distance':distance, 'duration':duration, 'points':points}
        # return directions_result, clean_result
        return clean_result