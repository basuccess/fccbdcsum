# writeout.py

import json
import os
import geopandas as gpd
from tqdm import tqdm
from constant import STATES_AND_TERRITORIES

def get_state_info(state_abbr):
    for fips, abbr, name in STATES_AND_TERRITORIES:
        if abbr == state_abbr:
            return fips.zfill(2), abbr, name.replace(' ', '_')  # Ensure FIPS code is zero-padded and spaces are replaced by underscores
    raise ValueError(f"State abbreviation {state_abbr} not found in STATES_AND_TERRITORIES")

def transform_bdc_locations(bdc_locations):
    tech_map = {}
    location_ids = set()
    location_max_speeds = {}
    relevant_techs = {"Copper", "Cable", "Fiber"}

    for location in bdc_locations:
        tech_abbr = location['tech_abbr']
        holding_company = location['holding_company']
        location_id = location['location_id']
        max_download_speed = location['max_advertised_download_speed']
        
        location_ids.add(location_id)
        
        if tech_abbr in relevant_techs:
            if location_id not in location_max_speeds:
                location_max_speeds[location_id] = max_download_speed
            else:
                location_max_speeds[location_id] = max(location_max_speeds[location_id], max_download_speed)

        if tech_abbr not in tech_map:
            tech_map[tech_abbr] = {
                'holding_company': [],
                'locations': [],
                'provider_id': [],
                'brand_name': [],
                'technology': location['technology'],
                'technology_description': tech_abbr,
                'max_advertised_download_speed': [],
                'max_advertised_upload_speed': [],
                'low_latency': [],
                'business_residential_code': []
            }
        if holding_company not in tech_map[tech_abbr]['holding_company']:
            tech_map[tech_abbr]['holding_company'].append(holding_company)
            tech_map[tech_abbr]['locations'].append(0)
            tech_map[tech_abbr]['provider_id'].append(location['provider_id'])
            tech_map[tech_abbr]['brand_name'].append(location['brand_name'])
            tech_map[tech_abbr]['max_advertised_download_speed'].append(max_download_speed)
            tech_map[tech_abbr]['max_advertised_upload_speed'].append(location['max_advertised_upload_speed'])
            tech_map[tech_abbr]['low_latency'].append(location['low_latency'])
            tech_map[tech_abbr]['business_residential_code'].append(location['business_residential_code'])
        index = tech_map[tech_abbr]['holding_company'].index(holding_company)
        tech_map[tech_abbr]['locations'][index] += 1

    unserved_count = sum(1 for speed in location_max_speeds.values() if speed < 25 or speed is None)
    underserved_count = sum(1 for speed in location_max_speeds.values() if 25 <= speed < 100)
    served_count = sum(1 for speed in location_max_speeds.values() if speed >= 100)
    
    return tech_map, len(location_ids), unserved_count, underserved_count, served_count

def write_geojson_and_convert_to_gpkg(merged_data, base_dir, state_abbr, output_dir=None):
    fips, abbr, name = get_state_info(state_abbr)
    if output_dir is None:
        state_dir = f"{fips}_{abbr}_{name}"
        output_dir = os.path.join(base_dir, 'USA_FCC-bdc', state_dir)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    geojson_file = os.path.join(output_dir, f"{fips}_{abbr}_BB.geojson")
    gpkg_file = os.path.join(output_dir, f"{fips}_{abbr}_BB.gpkg")
    
    # Transform the bdc_locations field and add summary fields
    for feature in merged_data['features']:
        if 'bdc_locations' in feature['properties']:
            tech_map, total_locations, unserved_count, underserved_count, served_count = transform_bdc_locations(feature['properties']['bdc_locations'])
            feature['properties'].update(tech_map)
            feature['properties']['Total_Locations'] = total_locations
            feature['properties']['Unserved'] = unserved_count
            feature['properties']['Underserved'] = underserved_count
            feature['properties']['Served'] = served_count
            del feature['properties']['bdc_locations']
    
    # Convert the merged data to a GeoDataFrame
    gdf = gpd.GeoDataFrame.from_features(merged_data['features'])
    
    # Ensure the CRS is set to EPSG:4269 - NAD83
    gdf.set_crs("EPSG:4269", inplace=True)
    
    # Simplify geometries if necessary
    # gdf['geometry'] = gdf['geometry'].simplify(tolerance=0.001, preserve_topology=True)
    
    # Write the GeoJSON file with progress indication and indentation
    with open(geojson_file, 'w') as f:
        json.dump(merged_data, f, indent=2)
    
    print(f"GeoJSON file written to: {geojson_file}")
    
    # Delete the existing GeoPackage file if it exists
    if os.path.exists(gpkg_file):
        os.remove(gpkg_file)
    
    # Write the GeoDataFrame to a new GeoPackage file
    gdf.to_file(gpkg_file, driver="GPKG", layer=f"{fips}_{abbr}_BB")
    
    print(f"GeoPackage file written to: {gpkg_file}")