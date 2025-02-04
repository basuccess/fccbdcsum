import os
import argparse
import logging
from constant import STATES_AND_TERRITORIES
from prepdata import prepare_data, load_holder_mapping
from readin import read_data
from merge import merge_data
from writeout import write_geojson_and_convert_to_gpkg

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_arguments():
    parser = argparse.ArgumentParser(description='Build broadband service geopackage files for US states and territories.')
    parser.add_argument('-d', '--base-dir', type=str, default=os.getcwd(), help='Base directory for data files')
    parser.add_argument('-s', '--state', type=str, nargs='*', default=[state[1] for state in STATES_AND_TERRITORIES], help='State abbreviation(s) to process')
    parser.add_argument('-o', '--output-dir', type=str, help='Output directory for data files')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0', help='Print version and exit')
    return parser.parse_args()

def main():
    setup_logging()
    args = parse_arguments()
    
    base_dir = args.base_dir
    output_dir = args.output_dir
    states_to_process = args.state

    logging.info(f'Starting processing for states: {states_to_process} in base directory: {base_dir}')
    
    holder_mapping = load_holder_mapping(base_dir)

    for state in states_to_process:
        logging.info(f'Processing state: {state}')
        prepare_data(base_dir, state)
        tabblock_data = read_data(base_dir, state)
        bdc_data = read_data(base_dir, state, bdc=True)
        logging.info(f'Finished processing BDC files for state: {state}')
        merged_data = merge_data(tabblock_data, bdc_data, holder_mapping)
        write_geojson_and_convert_to_gpkg(merged_data, base_dir, state, output_dir)

    logging.info('Processing completed.')

if __name__ == '__main__':
    main()