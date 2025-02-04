# Broadband Geopackage Project

This project is designed to build broadband service geopackage files for each US state and territory. It processes data from the FCC BDC and census tabblock20 shapefiles to create a structured output suitable for geographic information systems (GIS).

## Project Structure

```
catfccbdc
├── src
│   ├── constant.py        # Contains constants for the project
│   ├── prepdata.py        # Functions to prepare data for processing
│   ├── readin.py          # Functions to read input data files
│   ├── merge.py           # Functions to merge data based on geographic identifiers
│   ├── writeout.py        # Functions to write output to geopackage
│   └── main.py            # Main entry point for the project
├── data
│   ├── USA_FCC-bdc        # Directory for FCC BDC state broadband data
│   ├── USA_Census         # Directory for tabblock20 shapefiles
│   └── USA_FCC-bdc
│       └── resources      # Directory for required resource files
├── requirements.txt       # Lists project dependencies
├── setup.py               # Packaging and metadata for the project
└── README.md              # Project documentation
```

## Usage

To run the project, use the following command:

```
python src/main.py [options]
```

### Options

- `-d` or `--base-dir`: Specify the base directory (default is the current working directory).
- `-s` or `--state`: Specify a state abbreviation or a list of state abbreviations to process (default is to process all states).
- `-h` or `--help`: Print help/usage information and exit.
- `-v` or `--version`: Print the version of the project and exit.

## Functionality

1. **Data Preparation**: The project prepares lookup tables and dataframes for efficient processing of broadband service data.
2. **Data Reading**: It checks for the existence of required files and reads in the necessary data from FCC BDC and tabblock20 shapefiles.
3. **Data Merging**: The project merges broadband service locations with census block data based on geographic identifiers.
4. **Output Generation**: Finally, it outputs the processed data into geopackage files for each specified state.

## Requirements

Ensure you have the necessary dependencies installed by running:

```
pip install -r requirements.txt
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
