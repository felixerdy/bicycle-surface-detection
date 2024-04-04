import os
import pandas as pd

TIMESTAMP_FIELD = "Time"

# Acceleration data
sensor_data = os.path.join(
    os.path.dirname(__file__),
    "..",
    "data",
    "sensor_combined",
    "sensor_combined_data.csv",
)

# Directory containing CSV files
directory = os.path.join(os.path.dirname(__file__), "..", "data", "gps_chunks")

ml_directory = os.path.join(os.path.dirname(__file__), "..", "data", "ml_data")

if not os.path.exists(ml_directory):
    os.makedirs(ml_directory)

sensor_data_df = pd.read_csv(sensor_data)

sensor_data_df[TIMESTAMP_FIELD] = sensor_data_df[TIMESTAMP_FIELD].apply(
    lambda x: pd.to_datetime(x / 1000, unit="s")
)

dfs = []

# Iterate through CSV files in the directory
for filename in os.listdir(directory):
    if filename.endswith(".csv"):
        # Read CSV into DataFrame
        df = pd.read_csv(os.path.join(directory, filename))
        df["chunk_id"] = filename.split(".")[0].replace("chunk_", "")

        df["time"] = df["time"].apply(lambda x: pd.to_datetime(x).tz_localize(None))

        # get min and max time and filter the sensor data
        min_time = df["time"].min()
        max_time = df["time"].max()

        filtered_df = sensor_data_df[
            (sensor_data_df[TIMESTAMP_FIELD] >= min_time)
            & (sensor_data_df[TIMESTAMP_FIELD] <= max_time)
        ]
        filtered_df["chunk_id"] = filename.split(".")[0].replace("chunk_", "")
        filtered_df["surface_type"] = df.loc[1, "surface_type"]
        filtered_df["timestamp"] = pd.to_datetime(filtered_df[TIMESTAMP_FIELD])
        filtered_df = filtered_df.drop(columns=[TIMESTAMP_FIELD])
        filtered_df.to_csv(os.path.join(ml_directory, filename), index=False)
        dfs.append(filtered_df)

# Concatenate all DataFrames into one
# combined_df = pd.concat(dfs, ignore_index=True)
# combined_df.to_csv(os.path.join(ml_directory, "ml_combined_data.csv"), index=False)
