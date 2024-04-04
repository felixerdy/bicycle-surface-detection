# Bicycle Surface Detection

This project aims to label acceleration values from the MPU6050 sensor and GPS data recorded using Komoot with surface data from OpenStreetMap.

## Installation

It is recommended to use the provided devcontainer to run the project. The devcontainer is based on the official Python image and includes all necessary dependencies. To use the devcontainer, you need to have Docker and Visual Studio Code installed.

## Usage

### Data Collection
Setup an ESP32 with the provided Arduino sketch in `arduino/acceleration_csv/acceleration_csv.ino`. The ESP32 will collect acceleration data and save it to a CSV file. It will also connect to a WiFi network and get the time from an NTP server.

While the ESP32 is collecting data, record a GPX file using Komoot. The GPX file will contain the GPS data.

### Data Storage
After collecting the data, save the CSV files and the GPX files to the `data/raw` directory

### Data Processing
Run the following scripts to process the data:
- `python src/0_prepare_sensor_data.py` to process the acceleration data
- `python src/1_prepare_gps_data.py` to process the GPS data
- `python src/2_gps_data_chunks.py` to chunk the GPS data and label it with surface data
- `python src/3_create_ml_data.py` to combine sensor and GPS data to create the final dataset for the machine learning model

## Inspect your Data
To inspect the data, you can use the `data/gps_combined/gps_combined_labeled.csv` file. Visit [Kepler.gl](https://kepler.gl/) and upload the file to visualize the data.