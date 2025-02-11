# readin.py

import os
import re
import logging
import pandas as pd
from tqdm import tqdm
from constant import BDC_FILE_PATTERN, STATES_AND_TERRITORIES

def get_state_info(state_abbr):
    for fips, abbr, name in STATES_AND_TERRITORIES:
        if abbr == state_abbr:
            return fips.zfill(2), abbr, name.replace(' ', '_')  # Ensure FIPS code is zero-padded and spaces are replaced by underscores
    raise ValueError(f"State abbreviation {state_abbr} not found in STATES_AND_TERRITORIES")

def check_required_files(base_dir, state_abbr):
    fips, abbr, name = get_state_info(state_abbr)
    state_dir = f"{fips}_{abbr}_{name}"
    
    bdc_dir = os.path.join(base_dir, 'USA_FCC-bdc', state_dir)

    if not os.path.exists(bdc_dir):
        raise FileNotFoundError(f"Required directory not found: {bdc_dir}")
    
    bdc_files = [f for f in os.listdir(bdc_dir) if re.match(BDC_FILE_PATTERN, f)]

    if not bdc_files:
        raise FileNotFoundError(f"No BDC files found in: {bdc_dir}")
    
    return bdc_files

def combine_bdc_files(base_dir, state_abbr):
    fips, abbr, name = get_state_info(state_abbr)
    state_dir = f"{fips}_{abbr}_{name}"
    
    bdc_dir = os.path.join(base_dir, 'USA_FCC-bdc', state_dir)
    bdc_files = [f for f in os.listdir(bdc_dir) if re.match(BDC_FILE_PATTERN, f)]
    
    logging.info(f"Processing BDC files: {bdc_files}")
    
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

def read_data(base_dir, state_abbr):
    check_required_files(base_dir, state_abbr)
    return combine_bdc_files(base_dir, state_abbr)