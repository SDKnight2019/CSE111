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
    """Score a fishing spot based on weather and target species (partial match allowed)."""
    score = 0
    if any(target_species in s for s in spot["species"]):
        score += 10
    if 60 <= weather["temperature"] <= 75:
        score += 5
    if "cloud" in weather["cloud_cover"]:
        score += 2
    return score

def recommend_gear(spot, weather, target_species):
    """Recommend gear based on spot, weather, and species."""
    if target_species == "bass":
        return ["spinnerbait", "medium rod"]
    elif target_species == "trout":
        return ["fly rod", "flies"]
    else:
        return ["basic rod", "worms"]

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
    if not spots:
        print("No fishing spots available. Exiting.")
        return
    target_species = input("Enter your target species (e.g., bass, trout): ").strip().lower()
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday_input = input(f"What day of the week do you want to start your trip? ({'/'.join(days_of_week)}): ").strip().lower()
    start_day = get_weekday_offset(weekday_input)
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

    best_spot = None
    best_avg_score = -math.inf
    for spot in spots:
        if spot['latitude'] is None or spot['longitude'] is None:
            continue
        avg_score = average_spot_score(spot, target_species, start_day, trip_length)
        if avg_score is not None and avg_score > best_avg_score:
            best_avg_score = avg_score
            best_spot = spot
    if best_spot:
        print(f"The top place for fishing from day {start_day} to day {end_day} is: {best_spot['name']} (Avg Score: {best_avg_score:.2f})")
        print(f"Location: {best_spot['location']} | Lat: {best_spot['latitude']} | Lon: {best_spot['longitude']}")
        print(f"(Weather and gear recommendations are based on the first day of your trip.)")
        weather = get_weather_conditions(best_spot['latitude'], best_spot['longitude'], day_offset=start_day)
        if weather:
            print(f"Forecasted weather at {best_spot['name']} (Day {start_day}): {weather}")
            gear = recommend_gear(best_spot, weather, target_species)
            print(f"Recommended gear: {', '.join(gear)}")
    else:
        print("No suitable fishing spot found for your criteria with live weather.")

if __name__ == "__main__":
    main()
