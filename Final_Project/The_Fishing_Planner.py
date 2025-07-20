"""
The Fishing Planner
-------------------
A command-line tool to help plan fishing trips by recommending the best spots and gear based on:
- User's available gear (from user_gear.csv)
- Fishing spots and species (from waters_with_coords.csv)
- Live weather data (from the National Weather Service API)
- User preferences (fishing method, target species, bait type)

Usage: Run the script and follow the prompts. Requires internet access for live weather.
"""
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
    print("\nDo you prefer moving or still bait?")
    bait_types = ["moving", "still"]
    for idx, bait in enumerate(bait_types, 1):
        print(f"  {idx}. {bait.title()} Bait")
    while True:
        try:
            bait_choice = int(input(f"Enter the number for your bait preference (1-{len(bait_types)}): ").strip())
            if 1 <= bait_choice <= len(bait_types):
                bait_preference = bait_types[bait_choice - 1]
                break
            else:
                print(f"Please enter a number between 1 and {len(bait_types)}.")
        except Exception:
            print("Invalid input. Please enter a valid number.")
    if len(selected_methods) > 1:
        print("\nYou selected multiple fishing methods. Which one do you want gear recommendations for?")
        for idx, method in enumerate(selected_methods, 1):
            print(f"  {idx}. {method.title()}")
        while True:
            try:
                gear_method_choice = int(input(f"Enter the number for your preferred method for gear (1-{len(selected_methods)}): ").strip())
                if 1 <= gear_method_choice <= len(selected_methods):
                    gear_method = selected_methods[gear_method_choice - 1]
                    break
                else:
                    print(f"Please enter a number between 1 and {len(selected_methods)}.")
            except Exception:
                print("Invalid input. Please enter a valid number.")
    else:
        gear_method = selected_methods[0]
    return bait_preference, gear_method
import math
import datetime
import csv
import requests

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
    # Species match: up to 40 points
    if any(target_species in s for s in spot["species"]):
        score += 40

    # Temperature: up to 30 points
    temp = weather["temperature"]
    if 65 <= temp <= 70:
        score += 30
    elif 60 <= temp <= 64 or 71 <= temp <= 75:
        score += 25
    elif 55 <= temp <= 59 or 76 <= temp <= 80:
        score += 15
    elif 50 <= temp <= 54 or 81 <= temp <= 85:
        score += 5

    # Cloud cover: up to 10 points
    cloud = weather["cloud_cover"]
    if "partly cloudy" in cloud:
        score += 10
    elif "cloudy" in cloud:
        score += 7
    elif "clear" in cloud:
        score += 5
    elif "rain" in cloud or "showers" in cloud:
        score += 2

    # Wind: up to 10 points (lower wind is better)
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

    # Precipitation: up to 10 points (if mentioned in cloud_cover)
    if "rain" in cloud or "showers" in cloud:
        score += 2  # already added above, so no extra
    elif "snow" in cloud:
        score += 1

    # Fishing method compatibility: up to 10 points
    if hasattr(spot, 'fishing_method_score'):
        score += spot.fishing_method_score
    elif 'fishing_method_score' in spot:
        score += spot['fishing_method_score']

    # Cap score at 110 (or 100 if you want to keep old max)
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
    # Determine water type
    if any(w in location for w in ["lake", "reservoir", "pond"]):
        water_type = "still"
    elif any(w in location for w in ["river", "stream", "creek"]):
        water_type = "moving"
    else:
        water_type = "unknown"

    gear = []
    # Add method-specific gear
    if fishing_method == "shore":
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

    # user_gear and user_gear_names must be passed as attributes on the function
    user_gear = recommend_gear.user_gear
    user_gear_names = recommend_gear.user_gear_names

    def add_gear(item):
        key = item.lower()
        if key in user_gear["lure"]:
            gear.append(user_gear["lure"][key])
        elif key in user_gear["accessory"]:
            gear.append(user_gear["accessory"][key])
        elif key in user_gear_names:
            gear.append(item)
        else:
            print(f"[Warning] You do not have '{item}' in your gear list.")

    def add_rod(rod_type):
        key = rod_type.lower()
        if key in user_gear["rod"]:
            gear.append(user_gear["rod"][key])
        elif key in user_gear_names:
            gear.append(rod_type)
        else:
            print(f"[Warning] You do not have '{rod_type}' rod in your gear list.")

    # Bass
    if "bass" in target_species:
        if water_type == "still":
            add_rod("medium-heavy")
            if temp >= 70:
                add_gear("chatterbait")
            else:
                add_gear("spinner")
        elif water_type == "moving":
            add_rod("medium")
            add_gear("soft plastic")
        else:
            add_rod("medium")
            add_gear("spinner")
        if wind_val > 10:
            gear.append("heavier line (12-15lb)")
        else:
            gear.append("8-10lb line")
        if bait_preference == "moving":
            add_gear("crankbait")
        elif bait_preference == "still":
            add_gear("soft plastic")
    # Trout
    elif "trout" in target_species:
        if water_type == "moving":
            add_rod("fly")
            if "cloud" in cloud:
                add_gear("fly")
            else:
                add_gear("fly")
        elif water_type == "still":
            add_rod("ultralight")
            if temp < 60:
                add_gear("hook")
            else:
                add_gear("spoon")
        else:
            add_rod("light")
            add_gear("spinner")
        if wind_val > 10:
            add_gear("spoon")
        if bait_preference == "moving":
            add_gear("spinner")
        elif bait_preference == "still":
            add_gear("hook")
    # Walleye
    elif "walleye" in target_species:
        add_rod("medium")
        if water_type == "still":
            add_gear("soft plastic")
        else:
            add_gear("crankbait")
        if temp < 55:
            gear.append("slow retrieve")
        if bait_preference == "moving":
            add_gear("crankbait")
        elif bait_preference == "still":
            add_gear("hook")
    # Catfish
    elif "catfish" in target_species:
        add_rod("medium-heavy")
        gear.append("circle hooks")
        add_gear("hook")
        if water_type == "moving":
            gear.append("sinker weights")
        if bait_preference == "moving":
            gear.append("drifting rig")
        elif bait_preference == "still":
            gear.append("slip sinker rig")
    # Pike
    elif "pike" in target_species:
        add_rod("medium-heavy")
        gear.append("steel leader")
        add_gear("spoon")
        if bait_preference == "moving":
            add_gear("spinner")
        elif bait_preference == "still":
            add_gear("soft plastic")
    # Default
    else:
        if water_type == "still":
            add_rod("medium")
            add_gear("hook")
        elif water_type == "moving":
            add_rod("light")
            add_gear("spinner")
        else:
            add_rod("medium")
            add_gear("hook")
        if bait_preference == "moving":
            add_gear("spinner")
        elif bait_preference == "still":
            add_gear("hook")
    # Add rain gear if needed
    if "rain" in cloud or "showers" in cloud:
        gear.append("rain jacket")
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

# Helper to determine if a fishing method is possible at a spot
def fishing_method_possible(spot, fishing_method):
    """Return True if the fishing method is likely possible at the spot, based on keywords."""
    location = (spot.get("location") or "") + " " + (spot.get("name") or "")
    location = location.lower()
    if fishing_method == "shore":
        # Assume shore fishing is possible at most places
        return True
    elif fishing_method == "wading":
        # Look for river, stream, creek, shallow, wade, access
        return any(w in location for w in ["river", "stream", "creek", "shallow", "wade", "access"])
    elif fishing_method == "float tube":
        # Look for lake, pond, reservoir, float tube, launch
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
    # Load user gear once
    user_gear, user_gear_names = load_user_gear(USER_GEAR_CSV)
    # Attach to recommend_gear for use in recommendations
    recommend_gear.user_gear = user_gear
    recommend_gear.user_gear_names = user_gear_names
    if not spots:
        print("No fishing spots available. Exiting.")
        return

    # Ask for fishing method first
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

    # Add fishing method compatibility score to each spot (score if any selected method is possible)
    for spot in spots:
        if any(fishing_method_possible(spot, m) for m in selected_methods):
            spot['fishing_method_score'] = 10
        else:
            spot['fishing_method_score'] = 0

    # ...existing code for species selection...
    # Group species by main group (e.g., 'trout') and allow user to select a main group, then a subspecies
    main_groups_list = [
        "trout", "bass", "perch", "catfish", "sunfish", "salmon", "carp", "sucker", "whitefish", "pike", "walleye", "crappie", "bluegill", "sturgeon", "shad", "bream", "pickerel", "muskellunge", "drum", "gar", "shiner", "chub", "dace", "minnow", "bullhead", "tilapia", "cod", "flounder", "halibut", "mackerel", "snapper", "grouper", "sheefish", "grayling", "smelt", "burbot", "rockfish", "sculpin", "stickleback", "perch", "shark", "ray", "eel", "lamprey"
    ]
    species_map = {}
    for spot in spots:
        for s in spot["species"]:
            if not s:
                continue
            # Only take the part before any '(' 
            common_name = s.split('(')[0].strip()
            if not common_name:
                continue
            parts = common_name.split()
            # Find main group by matching last word to main_groups_list
            if len(parts) > 1 and parts[-1] in main_groups_list:
                main_group = parts[-1]
            elif parts[0] in main_groups_list:
                main_group = parts[0]
            else:
                continue  # skip if not a recognized group
            if main_group not in species_map:
                species_map[main_group] = set()
            species_map[main_group].add(common_name)
    if not species_map:
        print("No species data found in spots. Exiting.")
        return

    main_groups = sorted(species_map.keys())
    print("\nAvailable main fish groups:")
    for idx, group in enumerate(main_groups, 1):
        print(f"  {idx}. {group.title()}")
    # User selects main group
    while True:
        try:
            group_choice = int(input(f"\nEnter the number of the main group you want to target (1-{len(main_groups)}): ").strip())
            if 1 <= group_choice <= len(main_groups):
                main_group = main_groups[group_choice - 1]
                break
            else:
                print(f"Please enter a number between 1 and {len(main_groups)}.")
        except Exception:
            print("Invalid input. Please enter a valid number.")
    subtypes = sorted(species_map[main_group])
    if len(subtypes) == 1:
        target_species = subtypes[0]
        print(f"Selected: {target_species.title()}")
    else:
        print(f"\nAvailable {main_group.title()} species:")
        for idx, subtype in enumerate(subtypes, 1):
            print(f"  {idx}. {subtype.title()}")
        while True:
            try:
                sub_choice = int(input(f"\nEnter the number of the {main_group.title()} species you want to target (1-{len(subtypes)}): ").strip())
                if 1 <= sub_choice <= len(subtypes):
                    target_species = subtypes[sub_choice - 1]
                    break
                else:
                    print(f"Please enter a number between 1 and {len(subtypes)}.")
            except Exception:
                print("Invalid input. Please enter a valid number.")
    # Number days of week by offset from today
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
    show_top = input("Show the top 5 spots? (y/n): ").strip().lower() == 'y'
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
        # Prompt user to select a spot for detailed recommendation
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
        # Continue to ask bait preference, then show weather and gear
        # Ask bait and gear method using helper
        bait_preference, gear_method = prompt_bait_and_gear_method(selected_methods)
        print(f"\nThe top place for fishing from day {start_day} to day {end_day} is: {best_spot['name']} (Avg Score: {best_avg_score:.2f})")
        print(f"Location: {best_spot['location']} | Lat: {best_spot['latitude']} | Lon: {best_spot['longitude']}")
        print(f"(Weather and gear recommendations are based on the first day of your trip.)")
        weather = get_weather_conditions(best_spot['latitude'], best_spot['longitude'], day_offset=start_day)
        if weather:
            print(f"Forecasted weather at {best_spot['name']} (Day {start_day}): {weather}")
            gear = recommend_gear(best_spot, weather, target_species, gear_method, bait_preference)
            print(f"Recommended gear: {', '.join(gear)}")
        return
    # Non-top-5 mode
    best_spot = None
    best_avg_score = -math.inf
    for spot in spots:
        if spot['latitude'] is None or spot['longitude'] is None:
            continue
        avg_score = average_spot_score(spot, target_species, start_day, trip_length)
        if avg_score is not None and avg_score > best_avg_score:
            best_avg_score = avg_score
            best_spot = spot

    # Ask for bait preference
    # Ask bait and gear method using helper
    bait_preference, gear_method = prompt_bait_and_gear_method(selected_methods)

    if best_spot:
        print(f"The top place for fishing from day {start_day} to day {end_day} is: {best_spot['name']} (Avg Score: {best_avg_score:.2f})")
        print(f"Location: {best_spot['location']} | Lat: {best_spot['latitude']} | Lon: {best_spot['longitude']}")
        print(f"(Weather and gear recommendations are based on the first day of your trip.)")
        weather = get_weather_conditions(best_spot['latitude'], best_spot['longitude'], day_offset=start_day)
        if weather:
            print(f"Forecasted weather at {best_spot['name']} (Day {start_day}): {weather}")
            gear = recommend_gear(best_spot, weather, target_species, gear_method, bait_preference)
            print(f"Recommended gear: {', '.join(gear)}")
    else:
        print("No suitable fishing spot found for your criteria with live weather.")

if __name__ == "__main__":
    main()