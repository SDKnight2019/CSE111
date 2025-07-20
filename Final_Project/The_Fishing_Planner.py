import math
import datetime
import csv
import requests

USER_GEAR_CSV = "/home/sdknight2019/Public/Developer/CSE111/Final_Project/user_gear.csv"
def load_user_gear(filename):
    """Load user's available gear from a CSV file. Returns a dict by type and a flat set of names."""
    gear_by_type = {"rod": {}, "lure": {}, "accessory": {}}
    gear_names = set()
    try:
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                gtype = row["type"].strip().lower()
                name = row["name"].strip().lower()
                details = row["details"].strip()
                gear_by_type.setdefault(gtype, {})[name] = details
                gear_names.add(name)
    except FileNotFoundError:
        print(f"Warning: {filename} not found. No user gear loaded.")
    return gear_by_type, gear_names
def prompt_bait_and_gear_method(selected_methods):
    """Prompt user for bait preference and (if needed) gear method. Returns (bait_preference, gear_method)."""
    while True:
        print("\nDo you have a two-pole permit? (y/n): ", end='')
        two_pole_input = input().strip().lower()
        if two_pole_input in ('y', 'n'):
            two_pole = two_pole_input == 'y'
            break
        else:
            print("Please enter 'y' for yes or 'n' for no.")
    bait_types = ["moving", "still"]
    bait_preference = []
    if two_pole:
        print("\nYou have a two-pole permit. Please select bait preference for each pole.")
        for pole_num in range(1, 3):
            print(f"\nPole {pole_num}:")
            for idx, bait in enumerate(bait_types, 1):
                print(f"  {idx}. {bait.title()} Bait")
            while True:
                try:
                    bait_choice = int(input(f"Enter the number for your bait preference for pole {pole_num} (1-{len(bait_types)}): ").strip())
                    if 1 <= bait_choice <= len(bait_types):
                        bait_preference.append(bait_types[bait_choice - 1])
                        break
                    else:
                        print(f"Please enter a number between 1 and {len(bait_types)}.")
                except Exception:
                    print("Invalid input. Please enter a valid number.")
    else:
        print("\nDo you prefer moving or still bait?")
        for idx, bait in enumerate(bait_types, 1):
            print(f"  {idx}. {bait.title()} Bait")
        while True:
            try:
                bait_choice = int(input(f"Enter the number for your bait preference (1-{len(bait_types)}): ").strip())
                if 1 <= bait_choice <= len(bait_types):
                    bait_preference = [bait_types[bait_choice - 1]]
                    break
                else:
                    print(f"Please enter a number between 1 and {len(bait_types)}.")
            except Exception:
                print("Invalid input. Please enter a valid number.")
    if len(selected_methods) > 1:
        print("\nYou selected multiple fishing methods. Which one(s) do you want gear recommendations for?")
        for idx, method in enumerate(selected_methods, 1):
            print(f"  {idx}. {method.title()}")
        while True:
            try:
                gear_method_choices = input(f"Enter the number(s) for your preferred method(s) for gear (comma separated, e.g. 1,2): ").strip()
                selected_indices = [int(x) for x in gear_method_choices.split(',') if x.strip().isdigit() and 1 <= int(x.strip()) <= len(selected_methods)]
                if selected_indices:
                    gear_methods = [selected_methods[i-1] for i in selected_indices]
                    break
                else:
                    print(f"Please enter at least one valid number between 1 and {len(selected_methods)}.")
            except Exception:
                print("Invalid input. Please enter valid numbers separated by commas.")
    else:
        gear_methods = [selected_methods[0]]
    return bait_preference, gear_methods, two_pole

def load_fishing_spots(filename):
    """Load fishing spots from a CSV file."""
    spots = []
    try:
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    lat = float(row["lat"]) if row["lat"] else None
                    lon = float(row["lon"]) if row["lon"] else None
                except Exception:
                    lat, lon = None, None
                species = [s.strip().lower() for s in row["species"].split(';')] if "species" in row and row["species"] else []
                spot = {
                    "name": row["name"],
                    "location": row["location_desc"],
                    "latitude": lat,
                    "longitude": lon,
                    "species": species
                }
                spots.append(spot)
    except FileNotFoundError:
        print(f"Warning: {filename} not found. No spots loaded.")
    return spots

def get_nws_weather(lat, lon, day_offset=0):
    """Fetch weather data from the National Weather Service API for given coordinates and day offset (0-6)."""
    headers = {"User-Agent": "FishingPlanner/1.0 (your_email@example.com)"}
    try:
        points_url = f"https://api.weather.gov/points/{lat},{lon}"
        points_resp = requests.get(points_url, headers=headers, timeout=10)
        points_resp.raise_for_status()
        forecast_url = points_resp.json()["properties"]["forecast"]
        forecast_resp = requests.get(forecast_url, headers=headers, timeout=10)
        forecast_resp.raise_for_status()
        periods = forecast_resp.json()["properties"]["periods"]
        period_index = min(day_offset * 2, len(periods) - 1)
        period = periods[period_index]
        weather = {
            "temperature": period["temperature"],
            "wind": period["windSpeed"],
            "cloud_cover": period["shortForecast"].lower()
        }
        return weather
    except Exception as e:
        print(f"NWS weather fetch failed: {e}. Skipping this spot.")
        return None

def get_weather_conditions(lat=None, lon=None, day_offset=0):
    """Get weather conditions for a specific day offset using NWS live data only."""
    if lat is not None and lon is not None:
        return get_nws_weather(lat, lon, day_offset=day_offset)
    print("Live weather unavailable for this location. Skipping.")
    return None

def score_conditions(spot, weather, target_species):
    """Score a fishing spot based on weather, target species, and fishing method, out of 110 points."""
    score = 0
    if isinstance(target_species, list):
        if any(any(ts in s for ts in target_species) for s in spot["species"]):
            score += 40
    else:
        if any(target_species in s for s in spot["species"]):
            score += 40

    temp = weather["temperature"]
    if 65 <= temp <= 70:
        score += 30
    elif 60 <= temp <= 64 or 71 <= temp <= 75:
        score += 25
    elif 55 <= temp <= 59 or 76 <= temp <= 80:
        score += 15
    elif 50 <= temp <= 54 or 81 <= temp <= 85:
        score += 5

    cloud = weather["cloud_cover"]
    if "partly cloudy" in cloud:
        score += 10
    elif "cloudy" in cloud:
        score += 7
    elif "clear" in cloud:
        score += 5
    elif "rain" in cloud or "showers" in cloud:
        score += 2

    wind_str = weather.get("wind", "0 mph")
    try:
        wind_val = int(wind_str.split()[0])
    except Exception:
        wind_val = 0
    if wind_val <= 5:
        score += 10
    elif wind_val <= 10:
        score += 7
    elif wind_val <= 15:
        score += 4
    elif wind_val <= 20:
        score += 2

    if "rain" in cloud or "showers" in cloud:
        score += 2  
    elif "snow" in cloud:
        score += 1

    if hasattr(spot, 'fishing_method_score'):
        score += spot.fishing_method_score
    elif 'fishing_method_score' in spot:
        score += spot['fishing_method_score']

    return min(score, 110)

def recommend_gear(spot, weather, target_species, fishing_method=None, bait_preference=None):
    """Recommend gear based on spot, weather, species, fishing method, and bait preference, using only user's available gear."""
    temp = weather.get("temperature", 65)
    cloud = weather.get("cloud_cover", "")
    wind = weather.get("wind", "0 mph")
    try:
        wind_val = int(wind.split()[0])
    except Exception:
        wind_val = 0
    location = (spot.get("location") or "") + " " + (spot.get("name") or "")
    location = location.lower()
    if any(w in location for w in ["lake", "reservoir", "pond"]):
        water_type = "still"
    elif any(w in location for w in ["river", "stream", "creek"]):
        water_type = "moving"
    else:
        water_type = "unknown"

    rods_used = recommend_gear.rods_used if hasattr(recommend_gear, 'rods_used') else set()
    gear = []

    bait_type_map = {
        'spinner': 'moving', 'spinners': 'moving', 'spoon': 'moving', 'spoons': 'moving', 'crankbait': 'moving', 'chatterbait': 'moving', 'fly': 'moving', 'rooster tail': 'moving', 'double spinner': 'moving',
        'hook': 'still', 'hooks': 'still', 'circle hooks': 'still', 'soft plastic': 'still', 'soft plastics': 'still', 'slip sinker rig': 'still', 'sinker weights': 'still', 'drifting rig': 'still',
        'rain jacket': 'accessory', 'heavier line (12-15lb)': 'accessory', '8-10lb line': 'accessory', 'waders': 'accessory', 'wading boots': 'accessory', 'float tube': 'accessory', 'fins': 'accessory', 'life jacket': 'accessory', 'shore rod holder': 'accessory', 'longer rod (7-9ft)': 'accessory', 'steel leader': 'accessory', 'slow retrieve': 'accessory'
    }
    if fishing_method == "shore":
        if bait_preference != "moving":
            gear.append("shore rod holder")
        if water_type == "still":
            gear.append("longer rod (7-9ft)")
    elif fishing_method == "wading":
        gear.append("waders")
        gear.append("wading boots")
    elif fishing_method == "float tube":
        gear.append("float tube")
        gear.append("fins")
        gear.append("life jacket")

    user_gear = recommend_gear.user_gear
    user_gear_names = recommend_gear.user_gear_names

    def add_gear(item):
        key = item.lower()
        keys_to_try = [key]
        if key.endswith('s'):
            keys_to_try.append(key[:-1])
        else:
            keys_to_try.append(key + 's')
        found = False
        for k in keys_to_try:
            if k in user_gear["lure"]:
                gear.append(user_gear["lure"][k])
                found = True
                break
            elif k in user_gear["accessory"]:
                gear.append(user_gear["accessory"][k])
                found = True
                break
            elif k in user_gear_names:
                gear.append(k)
                found = True
                break
        if not found:
            print(f"[Warning] You do not have '{item}' in your gear list.")

    def add_rod(rod_type):
        key = rod_type.lower()
        rod_name = user_gear["rod"].get(key, rod_type)
        if key in user_gear["rod"] and rod_name not in rods_used:
            gear.append(rod_name)
            rods_used.add(rod_name)
        elif key in user_gear_names and rod_type not in rods_used:
            gear.append(rod_type)
            rods_used.add(rod_type)
        elif key in user_gear["rod"] and rod_name in rods_used:
            pass
        elif key in user_gear_names and rod_type in rods_used:
            pass
        else:
            print(f"[Warning] You do not have '{rod_type}' rod in your gear list.")

    ts_list = target_species if isinstance(target_species, list) else [target_species]
    group = None
    for g in ["bass", "trout", "walleye", "catfish", "pike"]:
        if any(g in ts for ts in ts_list):
            group = g
            break
    lure_candidates = []
    def add_lure_candidate(item):
        key = item.lower()
        keys_to_try = [key]
        if key.endswith('s'):
            keys_to_try.append(key[:-1])
        else:
            keys_to_try.append(key + 's')
        # Determine bait type
        bait_type = bait_type_map.get(key, None)
        # Only add if bait_type matches bait_preference, or is accessory
        if bait_preference in ('moving', 'still'):
            if bait_type == bait_preference or bait_type == 'accessory':
                for k in keys_to_try:
                    if k in user_gear["lure"] and user_gear["lure"][k] not in lure_candidates:
                        lure_candidates.append(user_gear["lure"][k])
                    elif k in user_gear["accessory"] and user_gear["accessory"][k] not in lure_candidates:
                        lure_candidates.append(user_gear["accessory"][k])
                    elif k in user_gear_names and k not in lure_candidates:
                        lure_candidates.append(k)
        else:
            # If bait_preference is not set, allow all
            for k in keys_to_try:
                if k in user_gear["lure"] and user_gear["lure"][k] not in lure_candidates:
                    lure_candidates.append(user_gear["lure"][k])
                elif k in user_gear["accessory"] and user_gear["accessory"][k] not in lure_candidates:
                    lure_candidates.append(user_gear["accessory"][k])
                elif k in user_gear_names and k not in lure_candidates:
                    lure_candidates.append(k)

    if group == "bass":
        if water_type == "still":
            add_rod("medium-heavy")
            if temp >= 70:
                add_lure_candidate("chatterbait")
            else:
                add_lure_candidate("spinner")
        elif water_type == "moving":
            add_rod("medium")
            add_lure_candidate("soft plastic")
        else:
            add_rod("medium")
            add_lure_candidate("spinner")
        if wind_val > 10:
            add_lure_candidate("heavier line (12-15lb)")
        else:
            add_lure_candidate("8-10lb line")
        if bait_preference == "moving":
            add_lure_candidate("crankbait")
        elif bait_preference == "still":
            add_lure_candidate("soft plastic")
    elif group == "trout":
        if water_type == "moving":
            add_rod("fly")
            add_lure_candidate("fly")
        elif water_type == "still":
            add_rod("ultralight")
            if temp < 60:
                add_lure_candidate("hook")
            else:
                add_lure_candidate("spoon")
        else:
            add_rod("light")
            add_lure_candidate("spinner")
        if wind_val > 10:
            add_lure_candidate("spoon")
        if bait_preference == "moving":
            add_lure_candidate("spinner")
        elif bait_preference == "still":
            add_lure_candidate("hook")
    elif group == "walleye":
        add_rod("medium")
        if water_type == "still":
            add_lure_candidate("soft plastic")
        else:
            add_lure_candidate("crankbait")
        if temp < 55:
            add_lure_candidate("slow retrieve")
        if bait_preference == "moving":
            add_lure_candidate("crankbait")
        elif bait_preference == "still":
            add_lure_candidate("hook")
    elif group == "catfish":
        add_rod("medium-heavy")
        add_lure_candidate("circle hooks")
        add_lure_candidate("hook")
        if water_type == "moving":
            add_lure_candidate("sinker weights")
        if bait_preference == "moving":
            add_lure_candidate("drifting rig")
        elif bait_preference == "still":
            add_lure_candidate("slip sinker rig")
    elif group == "pike":
        add_rod("medium-heavy")
        add_lure_candidate("steel leader")
        add_lure_candidate("spoon")
        if bait_preference == "moving":
            add_lure_candidate("spinner")
        elif bait_preference == "still":
            add_lure_candidate("soft plastic")
    else:
        if water_type == "still":
            add_rod("medium")
            add_lure_candidate("hook")
        elif water_type == "moving":
            add_rod("light")
            add_lure_candidate("spinner")
        else:
            add_rod("medium")
            add_lure_candidate("hook")
        if bait_preference == "moving":
            add_lure_candidate("spinner")
        elif bait_preference == "still":
            add_lure_candidate("hook")
    if "rain" in cloud or "showers" in cloud:
        add_lure_candidate("rain jacket")
    gear.extend(lure_candidates[:3])
    return gear

def average_spot_score(spot, target_species, start_day, trip_length):
    """Average the spot's score over the trip duration (start_day to start_day+trip_length-1)."""
    total_score = 0
    valid_days = 0
    for offset in range(start_day, start_day + trip_length):
        weather = get_weather_conditions(spot['latitude'], spot['longitude'], day_offset=offset)
        if weather:
            total_score += score_conditions(spot, weather, target_species)
            valid_days += 1
    if valid_days == 0:
        return None
    return total_score / valid_days

def fishing_method_possible(spot, fishing_method):
    """Return True if the fishing method is likely possible at the spot, based on keywords."""
    location = (spot.get("location") or "") + " " + (spot.get("name") or "")
    location = location.lower()
    if fishing_method == "shore":
        return True
    elif fishing_method == "wading":
        return any(w in location for w in ["river", "stream", "creek", "shallow", "wade", "access"])
    elif fishing_method == "float tube":
        return any(w in location for w in ["lake", "pond", "reservoir", "float tube", "launch"])
    return False

def get_weekday_offset(target_weekday):
    """Return the number of days from today to the next target_weekday (0=Monday, 6=Sunday)."""
    today = datetime.datetime.now().date()
    today_weekday = today.weekday() 
    days_of_week = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    try:
        target_index = days_of_week.index(target_weekday.lower())
    except ValueError:
        return 0 
    offset = (target_index - today_weekday) % 7
    return offset

def main():
    print("Welcome to The Fishing Planner!")
    spots = load_fishing_spots("/home/sdknight2019/Public/Developer/CSE111/Final_Project/waters_with_coords.csv")
    user_gear, user_gear_names = load_user_gear(USER_GEAR_CSV)
    recommend_gear.user_gear = user_gear
    recommend_gear.user_gear_names = user_gear_names
    if not spots:
        print("No fishing spots available. Exiting.")
        return
    if not any(user_gear.values()) or not user_gear_names:
        print("Warning: Your gear list is empty. Gear recommendations will be limited or unavailable.")

    print("\nHow would you like to fish? (You can select multiple methods, e.g. 1,2)")
    fishing_methods = ["shore", "wading", "float tube"]
    for idx, method in enumerate(fishing_methods, 1):
        print(f"  {idx}. {method.title()}")
    while True:
        try:
            method_choices = input(f"Enter the number(s) for your fishing method(s), separated by commas (1-{len(fishing_methods)}): ").strip()
            selected_indices = [int(x) for x in method_choices.split(',') if x.strip().isdigit() and 1 <= int(x.strip()) <= len(fishing_methods)]
            if selected_indices:
                selected_methods = [fishing_methods[i-1] for i in selected_indices]
                break
            else:
                print(f"Please enter at least one valid number between 1 and {len(fishing_methods)}.")
        except Exception:
            print("Invalid input. Please enter valid numbers separated by commas.")

    for spot in spots:
        if any(fishing_method_possible(spot, m) for m in selected_methods):
            spot['fishing_method_score'] = 10
        else:
            spot['fishing_method_score'] = 0

    main_groups_order = [
        "bass", "catfish", "chub", "dace", "grayling", "perch", "sculpin", "shiner", "sucker", "trout", "walleye", "whitefish", "salmon", "steelhead"
    ]
    species_map = {}
    for spot in spots:
        for s in spot["species"]:
            if not s:
                continue
            common_name = s.split('(')[0].strip()
            if not common_name:
                continue
            name_lower = common_name.lower()
            if "steelhead" in name_lower:
                main_group = "steelhead"
            elif "salmon" in name_lower and "trout" not in name_lower:
                main_group = "salmon"
            else:
                parts = common_name.split()
                if len(parts) > 1 and parts[-1] in main_groups_order:
                    main_group = parts[-1]
                elif parts[0] in main_groups_order:
                    main_group = parts[0]
                else:
                    continue
            if main_group not in species_map:
                species_map[main_group] = set()
            species_map[main_group].add(common_name)
    print("\nAvailable main fish groups:")
    display_groups = [g for g in main_groups_order]
    for idx, group in enumerate(display_groups, 1):
        print(f"  {idx}. {group.title()}")

    while True:
        try:
            group_choice = int(input(f"\nEnter the number of the main group you want to target (1-{len(display_groups)}): ").strip())
            if 1 <= group_choice <= len(display_groups):
                main_group = display_groups[group_choice - 1]
                break
            else:
                print(f"Please enter a number between 1 and {len(display_groups)}.")
        except Exception:
            print("Invalid input. Please enter a valid number.")
    subtypes = sorted(species_map.get(main_group, []))
    def is_illegal_species(name):
        return "bull trout" in name.lower()

    def needs_salmon_permit(name):
        return "salmon" in name.lower()

    def needs_steelhead_permit(name):
        return "steelhead" in name.lower()

    if main_group in ["salmon", "steelhead"]:
        species_name = main_group
        if not subtypes:
            subtypes = [main_group]
        if is_illegal_species(species_name):
            print("\nFishing for Bull Trout is illegal and cannot be selected. Please choose another species.")
            return
        if needs_salmon_permit(species_name):
            has_salmon = input("\nDo you have a salmon permit? (y/n): ").strip().lower() == 'y'
            if not has_salmon:
                print("You must have a salmon permit to fish for salmon. Please choose another species.")
                return
        if needs_steelhead_permit(species_name):
            has_steelhead = input("\nDo you have a steelhead permit? (y/n): ").strip().lower() == 'y'
            if not has_steelhead:
                print("You must have a steelhead permit to fish for steelhead. Please choose another species.")
                return
        target_species = [species_name]
        print(f"Selected: {species_name.title()}")
    elif len(subtypes) == 1:
        if is_illegal_species(subtypes[0]):
            print("\nFishing for Bull Trout is illegal and cannot be selected. Please choose another species.")
            return
        if needs_salmon_permit(subtypes[0]):
            has_salmon = input("\nDo you have a salmon permit? (y/n): ").strip().lower() == 'y'
            if not has_salmon:
                print("You must have a salmon permit to fish for salmon. Please choose another species.")
                return
        if needs_steelhead_permit(subtypes[0]):
            has_steelhead = input("\nDo you have a steelhead permit? (y/n): ").strip().lower() == 'y'
            if not has_steelhead:
                print("You must have a steelhead permit to fish for steelhead. Please choose another species.")
                return
        target_species = [subtypes[0]]
        print(f"Selected: {subtypes[0].title()}")
    elif not subtypes:
        print(f"\nNo sub-species found for {main_group.title()}. Please choose another group.")
        return
    else:
        print(f"\nAvailable {main_group.title()} species:")
        for idx, subtype in enumerate(subtypes, 1):
            label = subtype.title()
            if is_illegal_species(subtype):
                label += " (ILLEGAL TO FISH)"
            print(f"  {idx}. {label}")
        while True:
            try:
                sub_choices = input(f"\nEnter the number(s) of the {main_group.title()} species you want to target (comma separated, e.g. 1,3): ").strip()
                selected_indices = [int(x) for x in sub_choices.split(',') if x.strip().isdigit() and 1 <= int(x.strip()) <= len(subtypes)]
                if selected_indices:
                    selected_species = [subtypes[i-1] for i in selected_indices]
                    illegal_selected = [s for s in selected_species if is_illegal_species(s)]
                    if illegal_selected:
                        print(f"\nFishing for {', '.join(s.title() for s in illegal_selected)} is illegal and cannot be selected. Please choose only legal species.")
                        continue
                    salmon_needed = [s for s in selected_species if needs_salmon_permit(s)]
                    steelhead_needed = [s for s in selected_species if needs_steelhead_permit(s)]
                    if salmon_needed:
                        has_salmon = input("\nYou selected salmon species. Do you have a salmon permit? (y/n): ").strip().lower() == 'y'
                        if not has_salmon:
                            print("You must have a salmon permit to fish for salmon. Please choose only species you are permitted to fish for.")
                            continue
                    if steelhead_needed:
                        has_steelhead = input("\nYou selected steelhead species. Do you have a steelhead permit? (y/n): ").strip().lower() == 'y'
                        if not has_steelhead:
                            print("You must have a steelhead permit to fish for steelhead. Please choose only species you are permitted to fish for.")
                            continue
                    target_species = selected_species
                    break
                else:
                    print(f"Please enter at least one valid number between 1 and {len(subtypes)}.")
            except Exception:
                print("Invalid input. Please enter valid numbers separated by commas.")

    today = datetime.datetime.now().date()
    today_weekday = today.weekday()
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    print("\nWhat day of the week do you want to start your trip?")
    for i in range(7):
        day_idx = (today_weekday + i) % 7
        label = days_of_week[day_idx]
        if i == 0:
            label += " (Today)"
        elif i == 1:
            label += " (Tomorrow)"
        print(f"  {i+1}. {label}")
    while True:
        try:
            weekday_num = int(input(f"Enter the number for your start day (1-7): ").strip())
            if 1 <= weekday_num <= 7:
                start_day = weekday_num - 1
                weekday_input = days_of_week[(today_weekday + start_day) % 7].lower()
                break
            else:
                print("Please enter a number between 1 and 7.")
        except Exception:
            print("Invalid input. Please enter a valid number.")
    print(f"You will be fishing in {start_day} day(s) from today.")
    try:
        trip_length = int(input("How many days will your trip be? (1-7): ").strip())
        if not (1 <= trip_length <= 7):
            print("Please enter a number between 1 and 7. Defaulting to 1.")
            trip_length = 1
    except Exception:
        print("Invalid input. Defaulting to 1.")
        trip_length = 1
    if start_day + trip_length > 7:
        print("Trip exceeds available forecast range. Adjusting trip length.")
        trip_length = 7 - start_day
    while True:
        show_top_input = input("Show the top 5 spots? (y/n): ").strip().lower()
        if show_top_input in ('y', 'n'):
            show_top = show_top_input == 'y'
            break
        else:
            print("Please enter 'y' for yes or 'n' for no.")
    end_day = start_day + trip_length - 1
    if show_top:
        scored_spots = []
        for spot in spots:
            if spot['latitude'] is None or spot['longitude'] is None:
                continue
            avg_score = average_spot_score(spot, target_species, start_day, trip_length)
            if avg_score is not None:
                scored_spots.append((avg_score, spot))
        scored_spots.sort(reverse=True, key=lambda x: x[0])
        print(f"\nThe top spots for fishing from day {start_day} to day {end_day} are:")
        for i, (avg_score, spot) in enumerate(scored_spots[:5], 1):
            print(f"{i}. {spot['name']} (Avg Score: {avg_score:.2f}) | Location: {spot['location']} | Lat: {spot['latitude']} | Lon: {spot['longitude']}")
        if not scored_spots:
            print("No suitable fishing spots found for your criteria with live weather.")
            return

        while True:
            try:
                spot_choice = int(input(f"\nEnter the number of the spot you want details for (1-{min(5, len(scored_spots))}): ").strip())
                if 1 <= spot_choice <= min(5, len(scored_spots)):
                    best_spot = scored_spots[spot_choice - 1][1]
                    best_avg_score = scored_spots[spot_choice - 1][0]
                    break
                else:
                    print(f"Please enter a number between 1 and {min(5, len(scored_spots))}.")
            except Exception:
                print("Invalid input. Please enter a valid number.")

        bait_preference, gear_methods, two_pole = prompt_bait_and_gear_method(selected_methods)
        print(f"\nThe top place for fishing from day {start_day} to day {end_day} is: {best_spot['name']} (Avg Score: {best_avg_score:.2f})")
        print(f"Location: {best_spot['location']} | Lat: {best_spot['latitude']} | Lon: {best_spot['longitude']}")
        print(f"(Weather and gear recommendations are based on the first day of your trip.)")
        weather = get_weather_conditions(best_spot['latitude'], best_spot['longitude'], day_offset=start_day)
        if weather:
            print(f"Forecasted weather at {best_spot['name']} (Day {start_day}): {weather}")
            for gear_method in gear_methods:
                if two_pole:
                    rods_used = set()
                    for pole_num, bait in enumerate(bait_preference, 1):
                        recommend_gear.rods_used = rods_used
                        gear = recommend_gear(best_spot, weather, target_species, gear_method, bait)
                        print(f"Recommended gear for {gear_method.title()} (Pole {pole_num}, {bait.title()} Bait): {', '.join(gear)}")
                        print(f"Top 3 lures/baits for Pole {pole_num} ({bait.title()}): {', '.join([g for g in gear if g not in ['shore rod holder', 'longer rod (7-9ft)', 'waders', 'wading boots', 'float tube', 'fins', 'life jacket', 'heavier line (12-15lb)', '8-10lb line', 'rain jacket']][:3])}")
                    if hasattr(recommend_gear, 'rods_used'):
                        del recommend_gear.rods_used
                else:
                    gear = recommend_gear(best_spot, weather, target_species, gear_method, bait_preference[0])
                    print(f"Recommended gear for {gear_method.title()}: {', '.join(gear)}")
                    print(f"Top 3 lures/baits: {', '.join([g for g in gear if g not in ['shore rod holder', 'longer rod (7-9ft)', 'waders', 'wading boots', 'float tube', 'fins', 'life jacket', 'heavier line (12-15lb)', '8-10lb line', 'rain jacket']][:3])}")
        return
 
    best_spot = None
    best_avg_score = -math.inf
    for spot in spots:
        if spot['latitude'] is None or spot['longitude'] is None:
            continue
        avg_score = average_spot_score(spot, target_species, start_day, trip_length)
        if avg_score is not None and avg_score > best_avg_score:
            best_avg_score = avg_score
            best_spot = spot

    bait_preference, gear_methods, two_pole = prompt_bait_and_gear_method(selected_methods)

    if best_spot:
        print(f"The top place for fishing from day {start_day} to day {end_day} is: {best_spot['name']} (Avg Score: {best_avg_score:.2f})")
        print(f"Location: {best_spot['location']} | Lat: {best_spot['latitude']} | Lon: {best_spot['longitude']}")
        print(f"(Weather and gear recommendations are based on the first day of your trip.)")
        weather = get_weather_conditions(best_spot['latitude'], best_spot['longitude'], day_offset=start_day)
        if weather:
            print(f"Forecasted weather at {best_spot['name']} (Day {start_day}): {weather}")
            for gear_method in gear_methods:
                if two_pole:
                    rods_used = set()
                    for pole_num, bait in enumerate(bait_preference, 1):
                        recommend_gear.rods_used = rods_used
                        gear = recommend_gear(best_spot, weather, target_species, gear_method, bait)
                        print(f"Recommended gear for {gear_method.title()} (Pole {pole_num}, {bait.title()} Bait): {', '.join(gear)}")
                        print(f"Top 3 lures/baits for Pole {pole_num} ({bait.title()}): {', '.join([g for g in gear if g not in ['shore rod holder', 'longer rod (7-9ft)', 'waders', 'wading boots', 'float tube', 'fins', 'life jacket', 'heavier line (12-15lb)', '8-10lb line', 'rain jacket']][:3])}")
                    if hasattr(recommend_gear, 'rods_used'):
                        del recommend_gear.rods_used
                else:
                    gear = recommend_gear(best_spot, weather, target_species, gear_method, bait_preference[0])
                    print(f"Recommended gear for {gear_method.title()}: {', '.join(gear)}")
                    print(f"Top 3 lures/baits: {', '.join([g for g in gear if g not in ['shore rod holder', 'longer rod (7-9ft)', 'waders', 'wading boots', 'float tube', 'fins', 'life jacket', 'heavier line (12-15lb)', '8-10lb line', 'rain jacket']][:3])}")
    else:
        print("No suitable fishing spot found for your criteria with live weather.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("\nAn unexpected error occurred. Please check your input files and try again.")
        print(f"Error details: {e}")