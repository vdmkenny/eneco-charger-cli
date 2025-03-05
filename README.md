# Eneco eMobility CLI

A Python script to query charging station data from the Eneco eMobility API. The script allows you to search for charging stations around a specified location (by address or coordinate) with filtering options and displays detailed, color-coded information including clickable links to Google Maps and owner websites.

## Installation

1. **Clone the repository**
2. `pip install -r requirements.txt`

## Usage

Run the script with either an address or a coordinate.

Example usage:

- Search by Address:

```
python chargers.py --address "Rooigemlaan 2 Gent"
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

Example output:

```
python3 chargers.py --address "Rooigemlaan 2 Gent" --range 0.1
Station Name: Allego BEALLEGO000337 ⚡⚡
Address: Rooigemlaan 2, 9000 Gent
Coordinates: lat=51.05421329, lng=3.69822672 (Distance: 0.11 km)
Access Type: Public
Owner: Allego
Usage: 2/7 sockets
EVSEs:
  - EVSE ID: BEALLEGO0002711
    Status: AVAILABLE ✓
    Connectors:
       * ID: 1, Standard: IEC_62196_T2_COMBO, Format: CABLE, Max Power: 150.0 kW
  - EVSE ID: BEALLEGO0002712
    Status: AVAILABLE ✓
    Connectors:
       * ID: 2, Standard: IEC_62196_T2_COMBO, Format: CABLE, Max Power: 150.0 kW
  - EVSE ID: BEALLEGO0002721
    Status: AVAILABLE ✓
    Connectors:
       * ID: 1, Standard: IEC_62196_T2_COMBO, Format: CABLE, Max Power: 150.0 kW
  - EVSE ID: BEALLEGO0002722
    Status: CHARGING ✗
    Connectors:
       * ID: 2, Standard: CHADEMO, Format: CABLE, Max Power: 50.0 kW
  - EVSE ID: BEALLEGO0002723
    Status: CHARGING ✗
    Connectors:
       * ID: 3, Standard: IEC_62196_T2_COMBO, Format: CABLE, Max Power: 150.0 kW
  - EVSE ID: BEALLEGO0003371
    Status: AVAILABLE ✓
    Connectors:
       * ID: 1, Standard: IEC_62196_T2_COMBO, Format: CABLE, Max Power: 300.0 kW
  - EVSE ID: BEALLEGO0003372
    Status: AVAILABLE ✓
    Connectors:
       * ID: 2, Standard: IEC_62196_T2_COMBO, Format: CABLE, Max Power: 300.0 kW
--------------------------------------------------
Station Name: Allego BEALLEGO000336 ⚡⚡
Address: Rooigemlaan 2, 9000 Gent
Coordinates: lat=51.05426334, lng=3.69815265 (Distance: 0.11 km)
Access Type: Public
Owner: Allego
Usage: 0/2 sockets
EVSEs:
  - EVSE ID: BEALLEGO0003361
    Status: AVAILABLE ✓
    Connectors:
       * ID: 1, Standard: IEC_62196_T2_COMBO, Format: CABLE, Max Power: 300.0 kW
  - EVSE ID: BEALLEGO0003362
    Status: AVAILABLE ✓
    Connectors:
       * ID: 2, Standard: IEC_62196_T2_COMBO, Format: CABLE, Max Power: 300.0 kW
--------------------------------------------------
```
