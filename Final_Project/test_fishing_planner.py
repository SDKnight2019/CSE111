import io
import csv
from The_Fishing_Planner import (
    load_fishing_spots,
    score_conditions,
    average_spot_score,
    recommend_gear,
    fishing_method_possible,
    get_weekday_offset,
    prompt_bait_and_gear_method
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
Test River,Test Valley,45.0,-112.0,Trout;Catfish
"""
    with open("test_spots.csv", "w") as f:
        f.write(csv_content)
    spots = load_fishing_spots("test_spots.csv")
    assert len(spots) == 2
    assert spots[0]["name"] == "Test Lake"
    assert "rainbow trout" in spots[0]["species"]
    assert spots[1]["name"] == "Test River"
    assert "catfish" in spots[1]["species"]
    print("test_load_fishing_spots passed.")

def test_score_conditions():
    score = score_conditions(mock_spot, mock_weather, "trout")
    assert score >= 10
    spot2 = dict(mock_spot)
    spot2["species"] = ["walleye"]
    score2 = score_conditions(spot2, mock_weather, "trout")
    assert score2 < score
    weather2 = dict(mock_weather)
    weather2["wind"] = "30 mph"
    score3 = score_conditions(mock_spot, weather2, "trout")
    assert score3 < score
    print("test_score_conditions passed.")

def test_average_spot_score():
    import The_Fishing_Planner
    The_Fishing_Planner.get_weather_conditions = lambda lat, lon, day_offset=0: mock_weather
    avg = average_spot_score(mock_spot, "trout", 0, 3)
    assert avg >= 10
    print("test_average_spot_score passed.")

def test_recommend_gear():
    recommend_gear.user_gear = {
        "rod": {"fly": "fly rod", "ultralight": "ultralight rod", "medium": "medium rod", "medium-heavy": "medium-heavy rod"},
        "lure": {"fly": "fly", "spinner": "spinner", "spoon": "spoon", "chatterbait": "chatterbait", "soft plastic": "soft plastic", "crankbait": "crankbait", "hook": "hook"},
        "accessory": {"waders": "waders", "wading boots": "wading boots", "float tube": "float tube", "fins": "fins", "life jacket": "life jacket", "shore rod holder": "shore rod holder"}
    }
    recommend_gear.user_gear_names = set([
        "fly rod", "ultralight rod", "medium rod", "medium-heavy rod", "fly", "spinner", "spoon", "chatterbait", "soft plastic", "crankbait", "hook",
        "waders", "wading boots", "float tube", "fins", "life jacket", "shore rod holder"
    ])
    gear = recommend_gear(mock_spot, mock_weather, "trout", fishing_method="wading", bait_preference="moving")
    assert any("fly" in g or "rod" in g for g in gear)
    spot2 = dict(mock_spot)
    spot2["species"] = ["bass"]
    spot2["location"] = "Test Lake"
    weather2 = dict(mock_weather)
    weather2["temperature"] = 80
    gear2 = recommend_gear(spot2, weather2, "bass", fishing_method="shore", bait_preference="still")
    assert any("rod" in g for g in gear2)
    spot3 = dict(mock_spot)
    spot3["species"] = ["catfish"]
    spot3["location"] = "Test River"
    gear3 = recommend_gear(spot3, mock_weather, "catfish", fishing_method="wading", bait_preference="still")
    assert any("hook" in g for g in gear3)
    print("test_recommend_gear passed.")

def test_fishing_method_possible():
    spot = {"name": "Lakeview", "location": "Big Lake"}
    assert fishing_method_possible(spot, "shore")
    assert not fishing_method_possible(spot, "wading")
    assert fishing_method_possible(spot, "float tube")
    spot2 = {"name": "Creekside", "location": "Shallow Creek"}
    assert fishing_method_possible(spot2, "wading")
    print("test_fishing_method_possible passed.")

def test_get_weekday_offset():
    import datetime
    today = datetime.datetime.now().date()
    today_name = today.strftime("%A").lower()
    assert get_weekday_offset(today_name) == 0
    assert 0 <= get_weekday_offset("sunday") <= 6
    print("test_get_weekday_offset passed.")

def test_prompt_bait_and_gear_method():
    assert callable(prompt_bait_and_gear_method)
    print("test_prompt_bait_and_gear_method exists.")

if __name__ == "__main__":
    test_load_fishing_spots()
    test_score_conditions()
    test_average_spot_score()
    test_recommend_gear()
    test_fishing_method_possible()
    test_get_weekday_offset()
    test_prompt_bait_and_gear_method()
    print("All tests passed.")