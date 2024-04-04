import gpxpy
import pandas as pd
from geopy.distance import geodesic
import os

# Minimum and maximum speed values in km/h
MIN_SPEED = 3
MAX_SPEED = 45

gpx_folder = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "gps")
dfs = []

# Iterate through all GPX files in the folder
for gpx_path in os.listdir(gpx_folder):
    if not gpx_path.endswith(".gpx"):
        continue
    with open(
        os.path.join(os.path.dirname(__file__), "..", "data", "raw", "gps", gpx_path),
        encoding="utf-8",
    ) as f:
        gpx = gpxpy.parse(f)

    # Convert to a dataframe one point at a time.
    points = []
    prev_point = None
    for segment in gpx.tracks[0].segments:
        for p in segment.points:
            if prev_point is not None:
                distance = geodesic(
                    (prev_point.latitude, prev_point.longitude),
                    (p.latitude, p.longitude),
                ).kilometers
                time_diff = (
                    p.time - prev_point.time
                ).total_seconds() / 3600  # Convert seconds to hours
                speed = (
                    distance / time_diff if time_diff != 0 else 0
                )  # Avoid division by zero
            else:
                speed = 0  # Speed for the first point is set to 0
            points.append(
                {
                    "time": p.time,
                    "latitude": p.latitude,
                    "longitude": p.longitude,
                    "elevation": p.elevation,
                    "speed": speed,
                }
            )
            prev_point = p

    df = pd.DataFrame.from_records(points)

    # filter out points with speed greater than 100 km/h and lower than 0 km/h
    df = df[(df["speed"] >= MIN_SPEED) & (df["speed"] <= MAX_SPEED)]

    dfs.append(df)

# Concatenate all DataFrames
df = pd.concat(dfs)

if not os.path.exists(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "data",
        "gps_combined",
    )
):
    os.makedirs(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "data",
            "gps_combined",
        )
    )


# Export the DataFrame to csv
df.to_csv(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "data",
        "gps_combined",
        "gps_combined_data.csv",
    ),
    index=False,
)
