import argparse
import math
import sys
import requests
from datetime import datetime, timezone
from colorama import init, Fore, Style
from geopy.geocoders import Nominatim

init(autoreset=True)

def geocode_address(address):
    geolocator = Nominatim(user_agent="charging_station_locator")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    else:
        print(Fore.RED + "Error: Address not found.")
        sys.exit(1)

def compute_bounds(lat, lon, search_range_km):
    lat_delta = search_range_km / 111.0
    lon_delta = search_range_km / (111.0 * math.cos(math.radians(lat)))
    north = lat + lat_delta
    south = lat - lat_delta
    east = lon + lon_delta
    west = lon - lon_delta
    return {
        "northWest": [north, west],
        "northEast": [north, east],
        "southEast": [south, east],
        "southWest": [south, west]
    }

def get_charging_stations(bounds, available_now=False, speed_range=[1, 999]):
    url = "https://www.eneco-emobility.com/api/chargemap/search-polygon"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Content-Type": "application/json",
        "Origin": "https://www.eneco-emobility.com",
        "DNT": "1",
        "Sec-GPC": "1",
        "Connection": "keep-alive",
        "Referer": "https://www.eneco-emobility.com/chargemap",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers"
    }
    payload = {
        "bounds": bounds,
        "filters": {
            "availableNow": available_now,
            "isAllowed": False,
            "speed": speed_range,
            "connectorTypes": []
        },
        "zoomLevel": 17
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(Fore.RED + "Error fetching charging station data: " + str(e))
        sys.exit(1)

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2)**2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(dlon/2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def get_station_max_power_kw(station):
    max_kw = 0
    for evse in station.get("evses", []):
        for connector in evse.get("connectors", []):
            mp = connector.get("maxPower", None)
            if mp is not None:
                try:
                    kw = int(mp) / 1000
                    if kw > max_kw:
                        max_kw = kw
                except ValueError:
                    continue
    return max_kw

def get_relative_time(last_updated_str):
    try:
        # Truncate microseconds to 6 digits if necessary.
        if "." in last_updated_str:
            base, frac = last_updated_str.split(".", 1)
            digits = ""
            tz_offset = ""
            for ch in frac:
                if ch.isdigit():
                    digits += ch
                else:
                    tz_offset = frac[len(digits):]
                    break
            digits = digits[:6]
            last_updated_str = f"{base}.{digits}{tz_offset}"
        last_updated = datetime.fromisoformat(last_updated_str)
        now = datetime.now(timezone.utc)
        diff = now - last_updated.astimezone(timezone.utc)
        days = diff.days
        hours, remainder = divmod(diff.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        parts = []
        if days > 0:
            parts.append(f"{days} days")
        if hours > 0 or days > 0:
            parts.append(f"{hours} hours")
        parts.append(f"{minutes} minutes")
        return " ".join(parts)
    except Exception:
        return "N/A"

def format_google_maps_link(address, lat, lon):
    url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
    return f"\033]8;;{url}\033\\{address}\033]8;;\033\\"

def display_station_info(stations, query_lat, query_lon):
    for station in stations:
        station_max_kw = get_station_max_power_kw(station)
        if station_max_kw > 300:
            emoji = Fore.YELLOW + " ⚡⚡⚡" + Style.RESET_ALL
        elif station_max_kw > 100:
            emoji = Fore.YELLOW + " ⚡⚡" + Style.RESET_ALL
        elif station_max_kw > 50:
            emoji = Fore.YELLOW + " ⚡" + Style.RESET_ALL
        else:
            emoji = ""
        coords = station.get("coordinates", {})
        station_lat = coords.get("lat", None)
        station_lon = coords.get("lng", None)
        distance_str = (f"{haversine_distance(query_lat, query_lon, station_lat, station_lon):.2f} km"
                        if station_lat is not None and station_lon is not None else "N/A")
        print(Fore.CYAN + Style.BRIGHT + f"Station Name: {station.get('name', 'N/A')}{emoji}")
        addr = station.get("address", {})
        address_text = f"{addr.get('streetAndHouseNumber', 'N/A')}, {addr.get('postcode', '')} {addr.get('city', '')}"
        clickable_address = format_google_maps_link(address_text, station_lat, station_lon) if station_lat and station_lon else address_text
        print(Style.BRIGHT + f"Address: {clickable_address}")
        print(f"Coordinates: lat={station_lat}, lng={station_lon} (Distance: {distance_str})")
        
        access_type = station.get("accessType", "N/A")
        if access_type.lower() == "public":
            access_color = Fore.GREEN
        else:
            access_color = Fore.YELLOW
        print("Access Type: " + access_color + access_type + Style.RESET_ALL)
        
        owner = station.get("owner", {})
        owner_name = owner.get("name", station.get("ownerName", "N/A"))
        owner_website = owner.get("website", None)
        if owner_website:
            clickable_owner = f"\033]8;;{owner_website}\033\\{owner_name}\033]8;;\033\\"
        else:
            clickable_owner = owner_name
        print("Owner: " + Fore.MAGENTA + clickable_owner + Style.RESET_ALL)
        
        evses = station.get("evses", [])
        total = len(evses)
        occupied = sum(1 for evse in evses if evse.get("status", "").upper() != "AVAILABLE")
        if total > 0:
            if occupied == total:
                usage_color = Fore.RED
            elif occupied == 0:
                usage_color = Fore.GREEN
            else:
                usage_color = Fore.YELLOW
            print(Style.BRIGHT + f"Usage: {usage_color}{occupied}/{total}{Style.RESET_ALL} sockets")
        print(Style.BRIGHT + "EVSEs:")
        for evse in evses:
            status = evse.get("status", "N/A")
            last_updated_str = evse.get("lastUpdated")
            relative_time = f"({get_relative_time(last_updated_str)})" if last_updated_str else ""
            if status.upper() == "AVAILABLE":
                status_color = Fore.GREEN
                free_icon = Fore.GREEN + "✓" + Style.RESET_ALL
            else:
                status_color = Fore.RED
                free_icon = Fore.RED + "✗" + Style.RESET_ALL
            # Status line now: "Status: AVAILABLE (4 hours 27 minutes) ✓"
            print(f"  - EVSE ID: {evse.get('evseId', 'N/A')}")
            print(f"    Status: {status_color}{status} {relative_time} {free_icon}{Style.RESET_ALL}")
            print("    Connectors:")
            for connector in evse.get("connectors", []):
                max_power = connector.get("maxPower", "N/A")
                if max_power != "N/A":
                    try:
                        max_power_kw = int(max_power) / 1000
                        max_power_str = f"{max_power_kw} kW"
                    except ValueError:
                        max_power_str = max_power
                else:
                    max_power_str = max_power
                print(f"       * ID: {connector.get('id', 'N/A')}, Standard: {connector.get('standard', 'N/A')}, "
                      f"Format: {connector.get('format', 'N/A')}, Max Power: {max_power_str}")
        print("-" * 50)

def main():
    parser = argparse.ArgumentParser(
        description="Find charging stations around a given location. Charging speed parameters are in kW."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--address', type=str, help="Address to search around (e.g., '1600 Amphitheatre Parkway, Mountain View, CA').")
    group.add_argument('--coordinate', nargs=2, metavar=('LAT', 'LON'), type=float,
                       help="Latitude and Longitude (e.g., --coordinate 50.9401 4.0516).")
    parser.add_argument('--range', type=float, default=0.1, help="Range in kilometers around the center (default: 0.1 km).")
    parser.add_argument('--min-speed', type=int, default=1, help="Minimum charging speed in kW (default: 1).")
    parser.add_argument('--max-speed', type=int, default=999, help="Maximum charging speed in kW (default: 999).")
    parser.add_argument('--available-now', action='store_true', default=False,
                        help="Only include stations with at least one available plug (filter out full charging stations).")
    args = parser.parse_args()
    
    if args.address:
        query_lat, query_lon = geocode_address(args.address)
    else:
        query_lat, query_lon = args.coordinate

    bounds = compute_bounds(query_lat, query_lon, args.range)
    speed_range = [args.min_speed, args.max_speed]
    stations = get_charging_stations(bounds, available_now=args.available_now, speed_range=speed_range)
    
    stations = sorted(
        stations,
        key=lambda s: haversine_distance(query_lat, query_lon,
                                         s.get("coordinates", {}).get("lat", query_lat),
                                         s.get("coordinates", {}).get("lng", query_lon))
    )
    
    if stations:
        display_station_info(stations, query_lat, query_lon)
    else:
        print("No station data available.")

if __name__ == '__main__':
    main()

