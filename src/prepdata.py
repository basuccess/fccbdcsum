# prepdata.py

import os
import re
import logging
import pandas as pd
from constant import STATES_AND_TERRITORIES, BDC_US_PROVIDER_FILE_PATTERN

def prepare_lookup_tables():
    # Prepare dictionaries for quick lookup
    state_dict = {abbr: (fips, name) for fips, abbr, name in STATES_AND_TERRITORIES}
    return state_dict

def load_holder_mapping(base_dir):
    logging.info(f"Preparing holder mapping data.")
    resources_dir = os.path.join(base_dir, 'USA_FCC-bdc', 'resources')
    if not os.path.exists(resources_dir):
        raise FileNotFoundError(f"Resources directory not found: {resources_dir}")
    
    # Find all files matching the pattern
    files = [f for f in os.listdir(resources_dir) if re.match(BDC_US_PROVIDER_FILE_PATTERN, f)]
    if not files:
        raise FileNotFoundError(f"No files matching pattern {BDC_US_PROVIDER_FILE_PATTERN} found in: {resources_dir}")
    
    # Sort files by the date found in group 1 of the pattern match
    files.sort(key=lambda f: re.search(BDC_US_PROVIDER_FILE_PATTERN, f).group(1), reverse=True)
    
    # Use the most recent file
    most_recent_file = files[0]
    holder_mapping_file = os.path.join(resources_dir, most_recent_file)
    
    holder_mapping_df = pd.read_csv(holder_mapping_file)
    holder_mapping = dict(zip(holder_mapping_df['provider_id'], holder_mapping_df['holding_company']))
    return holder_mapping

def prepare_dataframes():
    # Prepare dataframe for storing FCC-BDC features
    fcc_bdc_df = pd.DataFrame()
    return fcc_bdc_df

def check_directory_structure(base_dir):
    # Check if the required directory structure exists
    required_dirs = [
        os.path.join(base_dir, 'USA_FCC-bdc'),
        os.path.join(base_dir, 'USA_FCC-bdc', 'resources')
    ]

    for directory in required_dirs:
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Required directory does not exist: {directory}")

def prepare_data(base_dir, state):
    logging.info(f"Preparing data for state: {state}")
    # Function to prepare data
    check_directory_structure(base_dir)
    lookup_tables = prepare_lookup_tables()
    fcc_bdc_df = prepare_dataframes()
    # Additional data preparation logic can be added here
    return fcc_bdc_df