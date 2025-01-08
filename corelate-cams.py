import json

# Load playlists and deduplicate in a single script

def load_streams(file_path):
    with open(file_path, "r") as file:
        return [line.strip() for line in file if line.strip() and not line.startswith("#")]

def correlate_streams(color_streams, ir_streams):
    streams = []
    for color_stream in color_streams:
        ip = color_stream.split("/")[2].split(":")[0]  # Extract IP from URL
        ir_stream = next((ir for ir in ir_streams if ip in ir), None)
        if ir_stream:
            streams.append({
                "name": ip,
                "color_stream": color_stream,
                "ir_stream": ir_stream
            })
    return streams

def deduplicate_streams(streams):
    unique_streams = {}
    for entry in streams:
        if entry["name"] not in unique_streams:
            unique_streams[entry["name"]] = entry  # Retain the first entry per unique name
    return list(unique_streams.values())

def main():
    # Load streams
    color_streams = load_streams("streams_playlist.m3u")
    ir_streams = load_streams("ir_streams_playlist.m3u")

    # Correlate and deduplicate streams
    correlated_streams = correlate_streams(color_streams, ir_streams)
    unique_streams = deduplicate_streams(correlated_streams)

    # Save the deduplicated JSON file
    with open("sum-streams.json", "w") as file:
        json.dump(unique_streams, file, indent=4)

    print(f"Processing complete. {len(correlated_streams) - len(unique_streams)} duplicates removed.")

if __name__ == "__main__":
    main()
