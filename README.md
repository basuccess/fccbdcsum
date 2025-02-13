# FCC Broadband Data Consolidation

This project consolidates broadband service data for US states and territories into a single JSON file. The output JSON file contains data aggregated by provider, state, and county, with details on service technology types and speeds.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/fccbdcsum.git
    cd fccbdcsum
    ```

2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

To run the script, use the following command:

```sh
python src/main.py -d /path/to/base/dir -s FL IL -o /path/to/output/dir

## Options

- '-d', '--base-dir', type=str, default=os.getcwd(), help='Base directory for data files'
- '-s', '--state', type=str, nargs='*', default=[state[1] for state in STATES_AND_TERRITORIES], help='State abbreviation(s) to process'
- '--log-file', type=str, nargs='?', const='fccbdcsum_log.log', help='Log file path'
- '-o', '--output-dir', type=str, help='Output directory for data files'
- '-v', '--version', action='version', version='%(prog)s 1.0', help='Print version and exit'

```
fccbdcsum
├── src
│   ├── constant.py        # Contains constants for the project
│   ├── prepdata.py        # Functions to prepare data for processing
│   ├── readin.py          # Functions to read input data files
│   ├── writeout.py        # Functions to write output to geopackage
│   └── main.py            # Main entry point for the project
data
│   └── USA_FCC-bdc
│       └── resources      # Directory for required resource files
├── requirements.txt       # Lists project dependencies
├── setup.py               # Packaging and metadata for the project
└── README.md              # Project documentation
```

## Functionality

1. **Data Preparation**: The project prepares lookup tables and dataframes for efficient processing of broadband service data.
2. **Data Reading**: It checks for the existence of required files and reads in the necessary data from FCC BDC and tabblock20 shapefiles.
3. **Data Merging**: The project merges broadband service locations with census block data based on geographic identifiers.
4. **Output Generation**: Finally, it outputs the processed data into a json file.

## Requirements

Ensure you have the necessary dependencies installed by running:

```
pip install -r requirements.txt
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
