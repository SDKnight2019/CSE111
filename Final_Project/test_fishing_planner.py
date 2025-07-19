import io
import csv
from The_Fishing_Planner import (
    load_fishing_spots,
    score_conditions,
    average_spot_score,
    recommend_gear
)

mock_weather = {
    "temperature": 70,
    "wind": "5 mph",
    "cloud_cover": "partly cloudy"
}

mock_spot = {
    "name": "Test Lake",
    "location": "Test County",
    "latitude": 44.0,
    "longitude": -111.0,
    "species": ["rainbow trout", "bass"]
}

def test_load_fishing_spots():
    csv_content = """name,location_desc,lat,lon,species
Test Lake,Test County,44.0,-111.0,Rainbow Trout;Bass
"""
    with open("test_spots.csv", "w") as f:
        f.write(csv_content)
    spots = load_fishing_spots("test_spots.csv")
    assert len(spots) == 1
    assert spots[0]["name"] == "Test Lake"
    assert "rainbow trout" in spots[0]["species"]
    print("test_load_fishing_spots passed.")

def test_score_conditions():
    score = score_conditions(mock_spot, mock_weather, "trout")
    assert score >= 10  
    print("test_score_conditions passed.")

def test_average_spot_score():
    import The_Fishing_Planner
    The_Fishing_Planner.get_weather_conditions = lambda lat, lon, day_offset=0: mock_weather
    avg = average_spot_score(mock_spot, "trout", 0, 3)
    assert avg >= 10
    print("test_average_spot_score passed.")

def test_recommend_gear():
    gear = recommend_gear(mock_spot, mock_weather, "trout")
    assert "fly rod" in gear
    print("test_recommend_gear passed.")

if __name__ == "__main__":
    test_load_fishing_spots()
    test_score_conditions()
    test_average_spot_score()
    test_recommend_gear()
    print("All tests passed.")