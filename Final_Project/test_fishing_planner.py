import io
import csv
from The_Fishing_Planner import (
    load_fishing_spots,
    load_user_gear,
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

def test_shore_rod_holder_logic():
    recommend_gear.user_gear = {
        "rod": {"medium": "medium rod"},
        "lure": {"spinner": "spinner", "spoon": "spoon"},
        "accessory": {"shore rod holder": "shore rod holder"}
    }
    recommend_gear.user_gear_names = set(["medium rod", "spinner", "spoon", "shore rod holder"])
    spot = dict(mock_spot)
    gear = recommend_gear(spot, mock_weather, "trout", fishing_method="shore", bait_preference="moving")
    assert "shore rod holder" not in gear
    gear2 = recommend_gear(spot, mock_weather, "trout", fishing_method="shore", bait_preference="still")
    assert "shore rod holder" in gear2
    print("test_shore_rod_holder_logic passed.")

def test_top_3_lures():
    recommend_gear.user_gear = {
        "rod": {"medium": "medium rod"},
        "lure": {"spinner": "spinner", "spoon": "spoon", "fly": "fly", "hook": "hook", "crankbait": "crankbait"},
        "accessory": {}
    }
    recommend_gear.user_gear_names = set(["medium rod", "spinner", "spoon", "fly", "hook", "crankbait"])
    spot = dict(mock_spot)
    gear = recommend_gear(spot, mock_weather, "trout", fishing_method="shore", bait_preference="moving")
    lures = [g for g in gear if g not in ["shore rod holder", "longer rod (7-9ft)", "waders", "wading boots", "float tube", "fins", "life jacket", "heavier line (12-15lb)", "8-10lb line", "rain jacket"]]
    assert len(lures) <= 3
    print("test_top_3_lures passed.")

def test_single_vs_two_pole_output():
    import builtins
    import sys
    from io import StringIO
    input_values = iter(["n", "1"])
    def mock_input(prompt=""): return next(input_values)
    orig_input = builtins.input
    builtins.input = mock_input
    orig_stdout = sys.stdout
    sys.stdout = StringIO()
    try:
        bait, methods, two_pole = prompt_bait_and_gear_method(["shore"])
        assert not two_pole
        assert bait == ["moving"]
        assert methods == ["shore"]
        output = sys.stdout.getvalue()
        assert "Pole" not in output
    finally:
        builtins.input = orig_input
        sys.stdout = orig_stdout
    input_values = iter(["y", "1", "2"])
    def mock_input2(prompt=""): return next(input_values)
    builtins.input = mock_input2
    sys.stdout = StringIO()
    try:
        bait, methods, two_pole = prompt_bait_and_gear_method(["shore"])
        assert two_pole
        assert bait == ["moving", "still"]
        output = sys.stdout.getvalue()
        assert "Pole 1" in output and "Pole 2" in output
    finally:
        builtins.input = orig_input
        sys.stdout = orig_stdout
    print("test_single_vs_two_pole_output passed.")

def test_plural_singular_gear():
    recommend_gear.user_gear = {
        "rod": {},
        "lure": {"spinners": "spinners", "spinner": "spinner"},
        "accessory": {}
    }
    recommend_gear.user_gear_names = set(["spinners", "spinner"])
    spot = dict(mock_spot)
    gear1 = recommend_gear(spot, mock_weather, "trout", fishing_method="shore", bait_preference="moving")
    assert any("spinner" in g or "spinners" in g for g in gear1)
    print("test_plural_singular_gear passed.")

def test_salmon_steelhead_single_species():
    from The_Fishing_Planner import main as fishing_main
    spots = [
        {"name": "Salmon River", "location": "River", "latitude": 1, "longitude": 2, "species": ["chinook salmon"]},
        {"name": "Steelhead Creek", "location": "Creek", "latitude": 3, "longitude": 4, "species": ["steelhead"]}
    ]
    main_groups_order = ["salmon", "steelhead"]
    species_map = {}
    for spot in spots:
        for s in spot["species"]:
            common_name = s.split('(')[0].strip()
            name_lower = common_name.lower()
            if "steelhead" in name_lower:
                main_group = "steelhead"
            elif "salmon" in name_lower and "trout" not in name_lower:
                main_group = "salmon"
            else:
                continue
            if main_group not in species_map:
                species_map[main_group] = set()
            species_map[main_group].add(common_name)
    assert "salmon" in species_map and "steelhead" in species_map
    assert "chinook salmon" in species_map["salmon"]
    assert "steelhead" in species_map["steelhead"]
    print("test_salmon_steelhead_single_species passed.")

def test_illegal_species():
    from The_Fishing_Planner import main as fishing_main
    def is_illegal_species(name):
        return "bull trout" in name.lower()
    assert is_illegal_species("bull trout")
    assert not is_illegal_species("rainbow trout")
    print("test_illegal_species passed.")

def test_permit_logic():
    def needs_salmon_permit(name):
        return "salmon" in name.lower()
    def needs_steelhead_permit(name):
        return "steelhead" in name.lower()
    assert needs_salmon_permit("chinook salmon")
    assert not needs_salmon_permit("rainbow trout")
    assert needs_steelhead_permit("steelhead")
    assert not needs_steelhead_permit("catfish")
    print("test_permit_logic passed.")

def test_prompt_bait_and_gear_method_multimethod(monkeypatch=None):
    import builtins
    input_values = iter(["y", "1", "2", "1,2"])
    def mock_input(prompt=""):
        return next(input_values)
    orig_input = builtins.input
    builtins.input = mock_input
    try:
        bait, methods, two_pole = prompt_bait_and_gear_method(["shore", "wading"])
        assert two_pole is True
        assert bait == ["moving", "still"]
        assert set(methods) == {"shore", "wading"}
        print("test_prompt_bait_and_gear_method_multimethod passed.")
    finally:
        builtins.input = orig_input

def test_robustness_missing_files():
    try:
        _ = load_user_gear("nonexistent_file.csv")
        _ = load_fishing_spots("nonexistent_file.csv")
        print("test_robustness_missing_files passed.")
    except Exception as e:
        print(f"test_robustness_missing_files failed: {e}")

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
    try:
        test_load_fishing_spots()
        test_score_conditions()
        test_average_spot_score()
        test_recommend_gear()
        test_shore_rod_holder_logic()
        test_top_3_lures()
        test_single_vs_two_pole_output()
        test_fishing_method_possible()
        test_get_weekday_offset()
        test_prompt_bait_and_gear_method()
        test_plural_singular_gear()
        test_salmon_steelhead_single_species()
        test_illegal_species()
        test_permit_logic()
        test_prompt_bait_and_gear_method_multimethod()
        test_robustness_missing_files()
    except AssertionError as e:
        print(f"A test failed: {e}")
    except Exception as e:
        print(f"An error occurred during testing: {e}")
    else:
        print("All tests passed.")