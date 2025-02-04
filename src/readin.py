# readin.py

import os
import re
import pandas as pd
import geopandas as gpd
from tqdm import tqdm
from constant import BDC_FILE_PATTERN, TABBLOCK20_FILE_PATTERN, STATES_AND_TERRITORIES

def get_state_info(state_abbr):
    for fips, abbr, name in STATES_AND_TERRITORIES:
        if abbr == state_abbr:
            return fips.zfill(2), abbr, name.replace(' ', '_')  # Ensure FIPS code is zero-padded and spaces are replaced by underscores
    raise ValueError(f"State abbreviation {state_abbr} not found in STATES_AND_TERRITORIES")

def check_required_files(base_dir, state_abbr):
    fips, abbr, name = get_state_info(state_abbr)
    state_dir = f"{fips}_{abbr}_{name}"
    
    bdc_dir = os.path.join(base_dir, 'USA_FCC-bdc', state_dir)
    tabblock_dir = os.path.join(base_dir, 'USA_Census', state_dir)

    if not os.path.exists(bdc_dir):
        raise FileNotFoundError(f"Required directory not found: {bdc_dir}")
    
    if not os.path.exists(tabblock_dir):
        raise FileNotFoundError(f"Required directory not found: {tabblock_dir}")

    bdc_files = [f for f in os.listdir(bdc_dir) if re.match(BDC_FILE_PATTERN, f)]
    tabblock_files = [f for f in os.listdir(tabblock_dir) if re.match(TABBLOCK20_FILE_PATTERN, f)]

    if not bdc_files:
        raise FileNotFoundError(f"No BDC files found in: {bdc_dir}")
    
    if not tabblock_files:
        raise FileNotFoundError(f"No Tabblock20 files found in: {tabblock_dir}")

    return bdc_files, tabblock_files

def combine_bdc_files(base_dir, state_abbr):
    fips, abbr, name = get_state_info(state_abbr)
    state_dir = f"{fips}_{abbr}_{name}"
    
    bdc_dir = os.path.join(base_dir, 'USA_FCC-bdc', state_dir)
    bdc_files = [f for f in os.listdir(bdc_dir) if re.match(BDC_FILE_PATTERN, f)]
    
    print(f"Processing BDC files: {bdc_files}")
    
    combined_df = pd.DataFrame()
    for i, bdc_file in enumerate(tqdm(bdc_files, desc="Processing BDC files")):
        file_path = os.path.join(bdc_dir, bdc_file)
        if bdc_file.endswith('.csv'):
            df = pd.read_csv(file_path, encoding='ISO-8859-1')  # Adjust encoding as needed
        elif bdc_file.endswith('.zip'):
            df = pd.read_csv(file_path, compression='zip', encoding='ISO-8859-1')  # Adjust encoding as needed
        
        combined_df = pd.concat([combined_df, df], ignore_index=True)
    
    # Ensure block_geoid is treated as a 15-digit ID
    combined_df['block_geoid'] = combined_df['block_geoid'].apply(lambda x: str(int(x)).zfill(15))
    
    # Select required fields
    combined_df = combined_df[['frn', 'provider_id', 'brand_name', 'location_id', 'technology', 
                               'max_advertised_download_speed', 'max_advertised_upload_speed', 
                               'low_latency', 'business_residential_code', 'state_usps', 
                               'block_geoid', 'h3_res8_id']]
    
    return combined_df

def read_tabblock20(base_dir, state_abbr):
    fips, abbr, name = get_state_info(state_abbr)
    state_dir = f"{fips}_{abbr}_{name}"
    
    tabblock_dir = os.path.join(base_dir, 'USA_Census', state_dir)
    tabblock_files = [f for f in os.listdir(tabblock_dir) if re.match(TABBLOCK20_FILE_PATTERN, f)]
    
    # Assuming there's only one tabblock file per state
    file_path = os.path.join(tabblock_dir, tabblock_files[0])
    tabblock_gdf = gpd.read_file(file_path)  # Read shapefile using geopandas
    
    # Ensure GEOID20 is treated as a 15-digit ID
    tabblock_gdf['GEOID20'] = tabblock_gdf['GEOID20'].apply(lambda x: str(x).zfill(15))
    
    # Indicate progress while iterating over the rows
    for _ in tqdm(tabblock_gdf.iterrows(), total=tabblock_gdf.shape[0], desc="Reading Tabblock Data"):
        pass
    
    return tabblock_gdf

def read_data(base_dir, state_abbr, bdc=False):
    check_required_files(base_dir, state_abbr)
    if bdc:
        return combine_bdc_files(base_dir, state_abbr)
    else:
        return read_tabblock20(base_dir, state_abbr)