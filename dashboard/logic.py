import numpy as np
import pandas as pd
# import geopandas as gpd


def process_request(classification, time=None):
    '''

    :param classification:
    :param time:

    :return: A mxn matrix where m is number of census tracts and n is advertisement score
    '''
    # todo process the data in this file and modules imported here
    map_data = pd.DataFrame(
        np.random.randn(100000, 2) / [50, 50] + [37.76, -122.4],
        columns=['lat', 'lon'])
    return map_data
