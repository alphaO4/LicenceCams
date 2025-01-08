import requests
import json
from concurrent.futures import ThreadPoolExecutor

# Scans a single camera's stream availability for a given IP address.
def scan_camera(ip, port, max_cameras):
    found_streams = []
    for cam_num in range(max_cameras):
        # Construct the URL for the camera stream
        url = f"http://{ip}:{port}/cam{cam_num}color"
        try:
            with requests.get(url, stream=True, timeout=5) as response:
                # Stop scanning if a 404 error with specific content is encountered
                if response.status_code == 404:
                    error_content = response.text.strip()
                    print(f"Cam not found at: {url} | Error: {error_content}")
                    if "Not found your stream" in error_content:
                        break
                else:
                    # Add the URL to the list if the stream is active
                    print(f"Active cam found at: {url}")
                    found_streams.append(url)
        except requests.RequestException as e:
            # Handle any connection-related exceptions
            print(f"Error accessing {url}: {e}")
            break
    return found_streams

# Concurrently scans all cameras for multiple IP addresses.
def scan_cameras(ip_list):
    port = 8080
    max_cameras = 100  # Maximum number of cameras to scan per IP
    all_streams = []

    # Use a thread pool to handle multiple IPs concurrently
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(scan_camera, ip, port, max_cameras) for ip in ip_list]
        for future in futures:
            all_streams.extend(future.result())

    return all_streams

# Retrieves infrared (IR) camera streams based on the URLs of active streams.
def get_ir_cams(urls):
    found_ir_streams = []

    def process_url(infra_url):
        try:
            with requests.get(infra_url, stream=True, timeout=5) as response:
                # Add the IR URL to the list if the stream is active
                if response.status_code != 404:
                    print(f"Active IR cam found at: {infra_url}")
                    found_ir_streams.append(infra_url)
                else:
                    print(f"IR cam not found at: {infra_url}")
        except requests.RequestException as e:
            # Ignore connection errors for individual URLs
            print(f"Error accessing {infra_url}: {e}")

    # Use a thread pool to process IR streams concurrently
    with ThreadPoolExecutor() as executor:
        executor.map(lambda url: process_url(f"{url[:-5]}ir"), urls)

    return found_ir_streams

# Creates a VLC-compatible playlist file from a list of stream URLs.
def create_vlc_playlist(stream_urls, output_file):
    with open(output_file, 'w') as playlist:
        # Write the M3U playlist header
        playlist.write("#EXTM3U\n")
        for url in stream_urls:
            # Add each stream to the playlist
            playlist.write(f"#EXTINF:-1,{url}\n")
            playlist.write(f"{url}\n")
    print(f"VLC playlist created at {output_file}")

if __name__ == "__main__":
    # Load the list of IPs from a JSON file
    with open("cams.json", "r") as file:
        data = json.load(file)
        # Extract IPs from the JSON structure
        ip_list = [entry["http"]["host"] for entry in data if "http" in entry and "host" in entry["http"]]

    # Scan for active color streams
    found_streams = scan_cameras(ip_list)

    if found_streams:
        # Create a playlist for color streams
        create_vlc_playlist(found_streams, "streams_playlist.m3u")
        # Scan for IR streams based on the active color streams
        ir_files = get_ir_cams(found_streams)
        # Create a playlist for IR streams
        create_vlc_playlist(ir_files, "ir_streams_playlist.m3u")
    else:
        print("No streams found.")
