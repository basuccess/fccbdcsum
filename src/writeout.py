# writeout.py

import json
import os
import pandas as pd
from tqdm import tqdm
from constant import STATES_AND_TERRITORIES, TECH_ABBR_MAPPING
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_state_info(state_abbr):
    for fips, abbr, name in STATES_AND_TERRITORIES:
        if abbr == state_abbr:
            return fips.zfill(2), abbr, name.replace(' ', '_')  # Ensure FIPS code is zero-padded and spaces are replaced by underscores
    raise ValueError(f"State abbreviation {state_abbr} not found in STATES_AND_TERRITORIES")

def load_county_mapping(base_dir):
    county_mapping = {}
    file_path = os.path.join(base_dir, 'USA_FCC-bdc', 'resources', 'county_adjacency2024.txt')
    logging.info(f"Loading county mapping from {file_path}")
    try:
        with open(file_path, 'r') as f:
            for line in f:
                if line.startswith("County Name"):
                    continue
                parts = line.strip().split('|')
                county_name = parts[0]
                county_geoid = parts[1]
                state_fips = county_geoid[:2]
                county_mapping[county_geoid] = (state_fips, county_name)
        logging.info("County mapping loaded successfully")
    except FileNotFoundError as e:
        logging.error(f"County adjacency file not found: {e}")
        raise
    return county_mapping

def transform_bdc_locations(bdc_locations, county_mapping):
    provider_map = {}

    for location in bdc_locations:
        try:
            tech_abbr = location['technology']
            holding_company = location['brand_name']
            provider_id = location['provider_id']
            max_download_speed = location['max_advertised_download_speed']
            max_upload_speed = location['max_advertised_upload_speed']
            low_latency = location['low_latency']
            location_type = location['business_residential_code']
            block_geoid = location['block_geoid']
            county_geoid = block_geoid[:5]
            state_fips, county_name = county_mapping.get(county_geoid, (None, None))

            if state_fips is None:
                continue

            state_name = next((name for fips, abbr, name in STATES_AND_TERRITORIES if fips == state_fips), None)
            if state_name is None:
                continue

            state_key = f"{state_name}, {state_fips}"
            county_key = f"{county_name}, {state_fips}"

            if holding_company not in provider_map:
                provider_map[holding_company] = {
                    "provider_id": provider_id,
                    "states": {}
                }

            state_data = provider_map[holding_company]["states"].setdefault(state_key, {
                "counties": {}
            })

            county_data = state_data["counties"].setdefault(county_key, {
                "total_locations": 0,
                "technologies": {}
            })

            tech_data = county_data["technologies"].setdefault(f"{TECH_ABBR_MAPPING.get(tech_abbr, 'Unknown')}, {tech_abbr}", {
                "total_locations": 0,
                "R": {
                    "total_locations": 0,
                    "locations": []
                },
                "B": {
                    "total_locations": 0,
                    "locations": []
                },
                "X": {
                    "total_locations": 0,
                    "locations": []
                }
            })

            county_data["total_locations"] += 1
            tech_data["total_locations"] += 1
            loc_data = tech_data[location_type]
            loc_data["total_locations"] += 1

            # Check if a location with the same speeds and latency already exists
            existing_location = next((loc for loc in loc_data["locations"] if loc["max_download_speed"] == max_download_speed and loc["max_upload_speed"] == max_upload_speed and loc["low_latency"] == low_latency), None)
            if existing_location:
                existing_location["count"] += 1
            else:
                loc_data["locations"].append({
                    "count": 1,
                    "max_download_speed": max_download_speed,
                    "max_upload_speed": max_upload_speed,
                    "low_latency": low_latency
                })
        except KeyError as e:
            logging.error(f"Missing key in BDC location data: {e}")
            continue

    return provider_map

def read_existing_json(base_dir):
    output_dir = os.path.join(base_dir, 'USA_FCC-bdc')
    latest_file = None
    latest_date = None

    logging.info(f"Reading existing JSON files from {output_dir}")
    try:
        for filename in os.listdir(output_dir):
            if filename.startswith("fccbdcsum_") and filename.endswith(".json"):
                file_date = datetime.strptime(filename[10:18], '%m%d%Y')
                if latest_date is None or file_date > latest_date:
                    latest_date = file_date
                    latest_file = filename

        if latest_file:
            with open(os.path.join(output_dir, latest_file), 'r') as f:
                logging.info(f"Loading existing data from {latest_file}")
                return json.load(f)
    except FileNotFoundError as e:
        logging.warning(f"No existing JSON files found: {e}")
    return {}

def write_consolidated_json(bdc_data, base_dir, output_dir=None):
    county_mapping = load_county_mapping(base_dir)
    provider_map = read_existing_json(base_dir)

    logging.info("Starting to process BDC data")
    for _, row in tqdm(bdc_data.iterrows(), desc="Processing records"):
        provider_data = transform_bdc_locations([row], county_mapping)
        for provider, data in provider_data.items():
            if provider not in provider_map:
                provider_map[provider] = data
            else:
                for state_key, state_data in data["states"].items():
                    provider_state_data = provider_map[provider]["states"].setdefault(state_key, {
                        "counties": {}
                    })
                    for county, county_data in state_data["counties"].items():
                        provider_county_data = provider_state_data["counties"].setdefault(county, {
                            "total_locations": 0,
                            "technologies": {}
                        })
                        provider_county_data["total_locations"] += county_data["total_locations"]
                        for tech, tech_data in county_data["technologies"].items():
                            provider_tech_data = provider_county_data["technologies"].setdefault(tech, {
                                "total_locations": 0,
                                "R": {
                                    "total_locations": 0,
                                    "locations": []
                                },
                                "B": {
                                    "total_locations": 0,
                                    "locations": []
                                },
                                "X": {
                                    "total_locations": 0,
                                    "locations": []
                                }
                            })
                            provider_tech_data["total_locations"] += tech_data["total_locations"]
                            for loc_type in ["R", "B", "X"]:
                                if loc_type in tech_data:
                                    existing_tech_data = provider_tech_data[loc_type]
                                    new_tech_data = tech_data[loc_type]
                                    
                                    # Update total locations
                                    existing_tech_data["total_locations"] += new_tech_data["total_locations"]
                                    
                                    # Update locations list
                                    for new_loc in new_tech_data["locations"]:
                                        existing_location = next(
                                            (loc for loc in existing_tech_data["locations"] 
                                             if (loc["max_download_speed"] == new_loc["max_download_speed"] and 
                                                 loc["max_upload_speed"] == new_loc["max_upload_speed"] and 
                                                 loc["low_latency"] == new_loc["low_latency"])),
                                            None
                                        )
                                        if existing_location:
                                            existing_location["count"] += new_loc["count"]
                                        else:
                                            existing_tech_data["locations"].append(new_loc)

    # Create output directory if it doesn't exist
    if output_dir is None:
        output_dir = os.path.join(base_dir, 'USA_FCC-bdc')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Write the consolidated JSON file
    output_file = os.path.join(output_dir, f"fccbdcsum_{datetime.now().strftime('%m%d%Y')}.json")
    with open(output_file, 'w') as f:
        json.dump(provider_map, f, indent=2)
    
    logging.info(f"Consolidated JSON file written to: {output_file}")

# Example usage
# bdc_data = pd.read_csv('/path/to/bdc_data.csv')  # Load your BDC data here
# base_dir = '/Users/thouweling/Documents/1000 - Code/1010 - Python/fccbdcsum'
# write_consolidated_json(bdc_data, base_dir)