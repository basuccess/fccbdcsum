import os
import argparse
import logging
import pandas as pd
from constant import STATES_AND_TERRITORIES
from prepdata import prepare_data, load_holder_mapping
from readin import read_data
from writeout import write_consolidated_json

def setup_logging(log_file, base_dir):
    if log_file is not None:
        log_file_path = os.path.join(base_dir, log_file)
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filename=log_file_path, filemode='w')
    else:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_arguments():
    parser = argparse.ArgumentParser(description='Build consolidated broadband service data for US states and territories.')
    parser.add_argument('-d', '--base-dir', type=str, default=os.getcwd(), help='Base directory for data files')
    parser.add_argument('-s', '--state', type=str, nargs='*', default=[state[1] for state in STATES_AND_TERRITORIES], help='State abbreviation(s) to process')
    parser.add_argument('--log-file', type=str, nargs='?', const='fccbdcsum_log.log', help='Log file path')
    parser.add_argument('-o', '--output-dir', type=str, help='Output directory for data files')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0', help='Print version and exit')
    return parser.parse_args()

def main():
    args = parse_arguments()
    setup_logging(args.log_file, args.base_dir)
    
    base_dir = args.base_dir
    output_dir = args.output_dir
    states_to_process = args.state

    logging.info(f'Starting processing for states: {states_to_process} in base directory: {base_dir}')
    
    holder_mapping = load_holder_mapping(base_dir)
    logging.debug(f"Holder mapping loaded: {holder_mapping}")

    for state in states_to_process:
        logging.info(f'Processing state: {state}')
        try:
            prepare_data(base_dir, state)
            bdc_data = read_data(base_dir, state)
            logging.debug(f"BDC data for {state}: {bdc_data}")
            logging.info(f'Finished processing BDC files for state: {state}')
            write_consolidated_json(bdc_data, base_dir, output_dir)
            logging.info('Processing completed.')
        except FileExistsError as e:
            logging.warning(f"Skipping state {state}: {e}")
        except Exception as e:
            logging.error(f"Error processing state {state}: {e}", exc_info=True)   

if __name__ == '__main__':
    main()