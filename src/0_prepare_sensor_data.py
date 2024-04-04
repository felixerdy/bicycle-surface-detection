import os
import pandas as pd

# Directory containing CSV files
directory = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "sensor")

# List to hold DataFrames
dfs = []

# Iterate through CSV files in the directory
for filename in os.listdir(directory):
    if filename.endswith(".csv"):
        # Read CSV into DataFrame
        df = pd.read_csv(os.path.join(directory, filename))

        # Append DataFrame to the list
        dfs.append(df)

# Concatenate all DataFrames into one
combined_df = pd.concat(dfs, ignore_index=True)

if not os.path.exists(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "data",
        "sensor_combined",
    )
):
    os.makedirs(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "data",
            "sensor_combined",
        )
    )

# Export the combined DataFrame to Parquet
combined_df.to_csv(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "data",
        "sensor_combined",
        "sensor_combined_data.csv",
    ),
    index=False,
)
