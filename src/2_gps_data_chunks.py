import pandas as pd
from geopy.distance import geodesic
import overpy
from geopy.distance import geodesic
import os

CHUNK_LENGTH = 50  # meters
OVERPASS_DEFAULT_AROUND_DISTANCE = 6
OVERPASS_HIGHWAY_AROUND_DISTANCE = 2

api = overpy.Overpass()

# Read the CSV file
df = pd.read_csv(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "data",
        "gps_combined",
        "gps_combined_data.csv",
    )
)


def calculate_distance(lat1, lon1, lat2, lon2):
    return geodesic((lat1, lon1), (lat2, lon2)).meters


def overpass_surface_type(line_string: list):
    # Query the Overpass API to get the surface type
    # result = api.query(
    #     f'way["highway"~"primary|secondary|tertiary|trunk|service|residential"](around:%s, %s);out;'
    #     % (OVERPASS_AROUND_DISTANCE, ",".join(map(str, line_string)))
    # )
    result = api.query(
        """
        relation[route=bicycle](around:{around}, {line});
        way[highway=cycleway](around:{around}, {line});
        way[highway=path][bicycle=designated](around:{around}, {line});
        way["highway"~"primary|secondary|tertiary|trunk|service|residential|path"](around:{highway_around}, {line});
        out body;
        """.format(
            around=OVERPASS_DEFAULT_AROUND_DISTANCE,
            highway_around=OVERPASS_HIGHWAY_AROUND_DISTANCE,
            line=",".join(map(str, line_string)),
        )
    )
    # # return one surface_type. try to prioritize bicycle ways (bicycle = designated) or cycleways.
    # # iterate over the ways and find ciclyeways or bicycle=designated
    for way in result.ways:
        if "bicycle" in way.tags and way.tags["bicycle"] == "designated":
            return way.tags["surface"]
        if "highway" in way.tags and way.tags["highway"] == "cycleway":
            return way.tags["surface"]
    # if no bicycle ways, return the first surface type
    # check if there is result.ways
    if len(result.ways) > 0:
        if "surface" not in result.ways[0].tags:
            return "unknown"
        return result.ways[0].tags["surface"]
    else:
        return "unknown"
    # surface_types = []
    # for way in result.ways:
    #     if "surface" in way.tags:
    #         surface_types.append(way.tags["surface"])
    # return surface_types


# Initialize variables
current_chunk = []
chunked_tracks = []
cumulative_distance = 0

# Iterate over the dataframe and split the track into chunks
for index, row in df.iterrows():
    if not current_chunk:
        current_chunk.append(row)
    else:
        prev_row = current_chunk[-1]
        distance = calculate_distance(
            prev_row["latitude"],
            prev_row["longitude"],
            row["latitude"],
            row["longitude"],
        )
        cumulative_distance += distance
        if cumulative_distance < CHUNK_LENGTH:
            current_chunk.append(row)
        else:
            chunked_tracks.append(current_chunk)
            current_chunk = [row]
            cumulative_distance = 0

# Append the last chunk
if current_chunk:
    chunked_tracks.append(current_chunk)

# Convert the chunks to dataframes
chunked_tracks_as_df = [
    pd.DataFrame(chunk, columns=df.columns) for chunk in chunked_tracks
]

dfs = []

if not os.path.exists(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "data",
        "gps_chunks",
    )
):
    os.makedirs(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "data",
            "gps_chunks",
        )
    )

for i, chunk in enumerate(chunked_tracks_as_df):
    # check if file exists
    if os.path.exists(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "data",
            "gps_chunks",
            f"chunk_{i}.csv",
        )
    ):
        print(f"Chunk {i} - Exists. Skipping.")
        continue

    # Get the surface type for the chunk
    line_string = []
    for row in chunk.iterrows():
        line_string.append(row[1]["latitude"])
        line_string.append(row[1]["longitude"])
    surface_type = overpass_surface_type(line_string)
    if surface_type == "unknown":
        print(f"Chunk {i} - Surface type: {surface_type}. Skipping.")
        continue
    print(f"Chunk {i} - Surface type: {surface_type}")
    chunk["surface_type"] = surface_type
    dfs.append(chunk)

    chunk.to_csv(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "data",
            "gps_chunks",
            f"chunk_{i}.csv",
        ),
        index=False,
    )

# Combine all the dataframes
if not dfs:
    print("No new chunks to process")
    exit()
combined_df = pd.concat(dfs, ignore_index=True)
combined_df.to_csv(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "data",
        "gps_combined",
        "gps_combined_labeled.csv",
    ),
    index=False,
)
