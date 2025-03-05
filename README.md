# Chargers

A Python script to query charging station data from the Eneco eMobility API. The script allows you to search for charging stations around a specified location (by address or coordinate) with filtering options and displays detailed, color-coded information including clickable links to Google Maps and owner websites.

## Installation

1. **Clone the repository**
2. `pip install -r requirements.txt`

## Usage

Run the script with either an address or a coordinate.

Examples:

- Search by Address:

```
python chargers.py --address "1600 Amphitheatre Parkway, Mountain View, CA"
```

- Search by Coordinate:

```
    python chargers.py --coordinate 50.9401 4.0516
```

Additional Options:
```
    --range: Range in kilometers around the center (default: 0.1 km).
    --min-speed: Minimum charging speed in kW (default: 1).
    --max-speed: Maximum charging speed in kW (default: 999).
    --available-now: Only include stations with at least one available plug (filters out full charging stations).
```
