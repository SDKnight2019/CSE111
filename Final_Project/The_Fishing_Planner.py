import math
import random
import datetime
import csv
import requests  # Now using live weather data

def load_fishing_spots(filename):
    """Load fishing spots from a CSV file, using name/location/lat/lon from the water bodies file."""
    spots = []
    try:
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                spot = {
                    "name": row["name"],
                    "location": row["location_desc"],
                    "latitude": float(row["lat"]),
                    "longitude": float(row["lon"]),
                    # No species info in this file, so leave as empty list or add logic if needed
                    "species": []
                }
                spots.append(spot)
    except FileNotFoundError:
        print(f"Warning: {filename} not found. No spots loaded.")
    return spots

def get_nws_weather(lat, lon):
    """Fetch weather data from the National Weather Service API for given coordinates."""
    headers = {"User-Agent": "FishingPlanner/1.0 (your_email@example.com)"}
    try:
        # Step 1: Get forecast URL for the point
        points_url = f"https://api.weather.gov/points/{lat},{lon}"
        points_resp = requests.get(points_url, headers=headers, timeout=10)
        points_resp.raise_for_status()
        forecast_url = points_resp.json()["properties"]["forecast"]
        # Step 2: Get the forecast
        forecast_resp = requests.get(forecast_url, headers=headers, timeout=10)
        forecast_resp.raise_for_status()
        periods = forecast_resp.json()["properties"]["periods"]
        # Use the first period (current/next)
        period = periods[0]
        weather = {
            "temperature": period["temperature"],
            "wind": period["windSpeed"],
            "cloud_cover": period["shortForecast"].lower()
        }
        return weather
    except Exception as e:
        print(f"NWS weather fetch failed: {e}. Using simulated weather.")
        return None

def get_weather_conditions(lat=None, lon=None):
    """Get weather conditions, using NWS live data only."""
    if lat is not None and lon is not None:
        weather = get_nws_weather(lat, lon)
        if weather:
            return weather
    print("Live weather unavailable for this location. Skipping.")
    return None

def score_conditions(spot, weather, target_species):
    """Score a fishing spot based on weather and target species."""
    score = 0
    # Add points if spot has target species
    if target_species in spot["species"]:
        score += 10
    # Adjust score based on weather (customize as needed)
    if 60 <= weather["temperature"] <= 75:
        score += 5
    if "cloud" in weather["cloud_cover"]:
        score += 2
    return score

def recommend_spot(spots, weather, target_species):
    """Recommend the best fishing spot based on scores."""
    best_spot = None
    best_score = -math.inf
    for spot in spots:
        score = score_conditions(spot, weather, target_species)
        if score > best_score:
            best_score = score
            best_spot = spot
    return best_spot, best_score

def recommend_gear(spot, weather, target_species):
    """Recommend gear based on spot, weather, and species."""
    # Placeholder logic
    if target_species == "bass":
        return ["spinnerbait", "medium rod"]
    elif target_species == "trout":
        return ["fly rod", "flies"]
    else:
        return ["basic rod", "worms"]

def main():
    print("Welcome to The Fishing Planner!")
    spots = load_fishing_spots("/home/sdknight2019/Public/Developer/CSE111/Final_Project/waters_with_coords_filtered.csv")
    if not spots:
        print("No fishing spots available. Exiting.")
        return
    target_species = input("Enter your target species (e.g., bass, trout): ").strip().lower()
    show_all = input("Show scores and recommended gear for all locations? (y/n): ").strip().lower() == 'y'
    # Use live weather for all locations if requested
    if show_all:
        print("\nScores and recommended gear for all locations (using live weather):")
        for spot in spots:
            weather = get_weather_conditions(spot['latitude'], spot['longitude'])
            if weather:
                score = score_conditions(spot, weather, target_species)
                gear = recommend_gear(spot, weather, target_species)
                print(f"{spot['name']}: Score {score} | Gear: {', '.join(gear)} | Weather: {weather}")
            else:
                print(f"{spot['name']}: Live weather unavailable. Skipping.")
        print()
    # Recommend spot based on live weather for all spots
    best_spot = None
    best_score = -math.inf
    best_weather = None
    for spot in spots:
        weather = get_weather_conditions(spot['latitude'], spot['longitude'])
        if weather:
            score = score_conditions(spot, weather, target_species)
            if score > best_score:
                best_score = score
                best_spot = spot
                best_weather = weather
    if best_spot:
        print(f"Recommended spot: {best_spot['name']} (Score: {best_score})")
        print(f"Location: {best_spot['location']} | Lat: {best_spot['latitude']} | Lon: {best_spot['longitude']}")
        print(f"Current weather at {best_spot['name']}: {best_weather}")
        gear = recommend_gear(best_spot, best_weather, target_species)
        print(f"Recommended gear: {', '.join(gear)}")
    else:
        print("No suitable fishing spot found for your criteria with live weather.")

if __name__ == "__main__":
    main()
