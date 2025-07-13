# Ehh.py

import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

def add_coordinates(df):
    """
    Add 'lat' and 'lon' columns to df by geocoding the 'name' field.
    """
    geolocator = Nominatim(user_agent="fishing_planner")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

    # helper to geocode one name
    def lookup(name):
        # include “Idaho, USA” to narrow the search
        loc = geocode(f"{name}, Idaho, USA")
        if loc:
            return pd.Series([loc.latitude, loc.longitude])
        else:
            return pd.Series([None, None])

    coords = df['name'].apply(lookup)
    coords.columns = ['lat', 'lon']
    return pd.concat([df, coords], axis=1)

if __name__ == "__main__":
    # 1. Load your water-bodies list
    df = pd.read_csv('waters_list.csv')  # must be in the same folder

    # 2. Geocode and append lat/lon
    df_with_coords = add_coordinates(df)

    # 3. Save out the new CSV
    df_with_coords.to_csv('waters_with_coords.csv', index=False)

    print("Saved waters_with_coords.csv with the following head:")
    print(df_with_coords.head())
