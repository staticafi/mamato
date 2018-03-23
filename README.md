# benchexec-results-viewer
Reimplementation of satt-frontend in python that should be easily integrable with benchexec

## Usage

The main script is `brv.py`.

### Importing benchexec XMLs to database

To import benchexec results to database for viewing:

`./brv.py [FILE.xml]`

### Starting web interface locally

To start a webserver at http://localhost:3000 that displays results from database:

`./brv.py`

## Development

The easiest way to install dependencies is:

`pip install -r requirements.txt`
