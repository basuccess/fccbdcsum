# merge.py

import pandas as pd
import geopandas as gpd
import json
from tqdm import tqdm
from constant import TECH_ABBR_MAPPING
from prepdata import load_holder_mapping

def get_tech_abbr(tech_code):
    return TECH_ABBR_MAPPING.get(tech_code, "Unknown")

def get_holder_name(provider_id, holder_mapping):
    return holder_mapping.get(provider_id, "Unknown")

def merge_data(tabblock_df, bdc_df, holder_mapping):
    # Convert tabblock_df to GeoJSON format
    tabblock_geojson = json.loads(tabblock_df.to_json())

    # Set up tqdm for pandas
    tqdm.pandas()

    # Add tech_abbr to BDC data
    bdc_df['tech_abbr'] = bdc_df['technology'].progress_map(get_tech_abbr)
    print("Finished adding tech_abbr")

    # Add holding_company to BDC data
    bdc_df['holding_company'] = bdc_df['provider_id'].progress_map(lambda x: get_holder_name(x, holder_mapping))
    print("Finished adding holding_company")

    # Group BDC data
    grouped_bdc = bdc_df.groupby(['block_geoid', 'technology', 'tech_abbr', 'provider_id', 'holding_company', 'brand_name', 'location_id']).agg({
        'max_advertised_download_speed': 'max',
        'max_advertised_upload_speed': 'max',
        'low_latency': 'max',
        'business_residential_code': 'max'
    }).reset_index()
    print("Finished grouping BDC data")

    # Create a dictionary to map block_geoid to bdc_locations
    bdc_locations_dict = {}
    for block_geoid, group in tqdm(grouped_bdc.groupby('block_geoid'), desc="Creating bdc_locations_dict"):
        bdc_locations_dict[block_geoid] = group.to_dict(orient='records')
    print("Finished creating bdc_locations_dict")

    # Merge BDC data with tabblock GeoJSON
    for feature in tqdm(tabblock_geojson['features'], desc="Merging records"):
        geoid20 = feature['properties']['GEOID20']
        feature['properties']['bdc_locations'] = bdc_locations_dict.get(geoid20, [])
    print("Finished merging records")

    return tabblock_geojson