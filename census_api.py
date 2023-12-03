import pandas as pd
from census import Census
from us import states
import numpy as np

'''
census variables:
    'B19013_001E': 'Median Household Income',
    'B01001_001E': 'Total Population',
    'B01001_026E': 'Female Population',
    'B01001_002E': 'Male Population',
    'B01001_003E': 'Under 5 years',
    'B01001_004E': '5 to 9 years',
    'B01001_005E': '10 to 14 years',
    'B01001_006E': '15 to 19 years',
    'B01001_007E': '20 to 24 years',
    'B01001_008E': '25 to 29 years',
    'B01001_009E': '30 to 34 years',
    'B01001_010E': '35 to 39 years',
    'B01001_011E': '40 to 44 years',
    'B01001_012E': '45 to 49 years',
    'B01001_013E': '50 to 54 years',
    'B01001_014E': '55 to 59 years',
    'B01001_015E': '60 to 64 years',
    'B01001_016E': '65 to 69 years',
    'B01001_017E': '70 to 74 years',
    'B01001_018E': '75 to 79 years',
    'B01001_019E': '80 to 84 years',
    'B02001_002E': 'White alone',
    'B02001_003E': 'Black or African American alone',
    'B02001_004E': 'American Indian and Alaska Native alone',
    'B02001_005E': 'Asian alone',
    'B02001_006E': 'Native Hawaiian and Other Pacific Islander alone',
    'B02001_007E': 'Some other race alone',
    'B02001_008E': 'Two or more races',
    'B03001_003E': 'Hispanic or Latino (of any race)'
'''

# query the api to get demographics for all census tracts in SF
def census_api_query():
    # set API key
    c = Census("ed687f63ddd84e59decbac48b228eff4c5503cfd")

    # Specify the variables you want (median household income)
    variables = ('B19013_001E','B01001_001E','B01001_026E', 'B01001_002E',
                'B01001_001E', 'B01001_002E', 'B01001_003E', 'B01001_004E', 'B01001_005E', 'B01001_006E',
                'B01001_007E', 'B01001_008E', 'B01001_009E', 'B01001_010E', 'B01001_011E', 'B01001_012E',
                'B01001_013E', 'B01001_014E', 'B01001_015E', 'B01001_016E', 'B01001_017E', 'B01001_018E',
                'B01001_019E', 'B02001_002E', 'B02001_003E', 'B02001_004E', 'B02001_005E', 'B02001_006E',
                'B02001_007E', 'B02001_008E', 'B03001_003E')

    # Specify the geographic area (tracts in San Francisco County, California)
    geo_area = {'for': 'tract:*', 'in': 'state:{} county:075'.format(states.CA.fips)}

    # Make the API request
    response = c.acs5.get(variables, geo_area)

    df = pd.DataFrame(response)
    df = df.rename(columns={
        'B19013_001E': 'Median Household Income',
        'B01001_001E': 'Total Population',
        'B01001_026E': 'Female Population',
        'B01001_002E': 'Male Population',
        'B01001_003E': 'Under 5 years',
        'B01001_004E': '5 to 9 years',
        'B01001_005E': '10 to 14 years',
        'B01001_006E': '15 to 19 years',
        'B01001_007E': '20 to 24 years',
        'B01001_008E': '25 to 29 years',
        'B01001_009E': '30 to 34 years',
        'B01001_010E': '35 to 39 years',
        'B01001_011E': '40 to 44 years',
        'B01001_012E': '45 to 49 years',
        'B01001_013E': '50 to 54 years',
        'B01001_014E': '55 to 59 years',
        'B01001_015E': '60 to 64 years',
        'B01001_016E': '65 to 69 years',
        'B01001_017E': '70 to 74 years',
        'B01001_018E': '75 to 79 years',
        'B01001_019E': '80 to 84 years',
        'B02001_002E': 'White alone',
        'B02001_003E': 'Black or African American alone',
        'B02001_004E': 'American Indian and Alaska Native alone',
        'B02001_005E': 'Asian alone',
        'B02001_006E': 'Native Hawaiian and Other Pacific Islander alone',
        'B02001_007E': 'Some other race alone',
        'B02001_008E': 'Two or more races',
        'B03001_003E': 'Hispanic or Latino (of any race)'
    })

    return df

# convert #'s to percentages in df for sampling to population
def clean_api_data(df):
    clean_df = df[["tract", "Median Household Income"]]
    clean_df["total_pop"] = df["Total Population"]
    clean_df["pct_female"] = df["Female Population"]/df["Total Population"]
    clean_df["pct_male"] = df["Male Population"]/df["Total Population"]
    clean_df["pct_children"] = (df["Under 5 years"] + df["5 to 9 years"] + df["10 to 14 years"] + df["15 to 19 years"])/df["Total Population"]
    clean_df["pct_20-39"] = (df["20 to 24 years"] + df["25 to 29 years"] + df["30 to 34 years"] + df["35 to 39 years"])/df["Total Population"]
    clean_df["pct_39-64"] = (df["40 to 44 years"] + df["45 to 49 years"] + df["50 to 54 years"] + df["55 to 59 years"] + df["60 to 64 years"])/df["Total Population"]
    clean_df["pct_65+"] = (df["65 to 69 years"] + df["70 to 74 years"] + df["75 to 79 years"] + df["80 to 84 years"])/df["Total Population"]
    clean_df["pct_nonwhite"] = (df["Total Population"] - df["White alone"])/df["Total Population"]
    clean_df["pct_latine"] = df["Hispanic or Latino (of any race)"]/df["Total Population"]

    # replace negative median income values with nan
    clean_df["Median Household Income"] = clean_df["Median Household Income"].replace(-666666666, np.nan)

    clean_df.to_csv('/Users/kaitlynng/Desktop/Coding/GeoAdVisor/census_data/census_data_clean.csv', index=False)
    print("Success!")



def main():
    df = census_api_query()
    print(df)
    clean_api_data(df)

main()