import re
from PIL import Image
import io
from datetime import datetime
import socket

# Define start bits and end of packet marker
start_bytes = b"\xbb\x0b\x00\x00"
jpeg_start = b"\xff\xd8"
jpeg_end = b"\xff\xd9"

# Regex for metadata
metadata_pattern = re.compile(
    r'"ColorName": "(.*?)",.*?"EngineTimeDelay": "(.*?)",.*?"MakerName": "(.*?)",.*?"ModelName": "(.*?)",.*?"NumSatellitesGPS": "(.*?)",.*?"UseCacheGPS": "(.*?)"'
)

# Define the host and port
host = "166.152.44.55"
port = 5002

# Helper function to save images
def save_image(data, timestamp):
    try:
        image = Image.open(io.BytesIO(data))
        filename = f"image_{timestamp}.jpg"
        image.save(filename)
        print(f"Image saved as {filename}")
    except Exception as e:
        print(f"Error saving image: {e}")

# Connect to the socket
try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(f"Connecting to {host}:{port}...")
        s.connect((host, port))
        print("Connection established.")

        buffer = b""
        while True:
            data = s.recv(26040)  # Increased buffer size to 64 KB
            if not data:
                print("No more data received. Closing connection.")
                break

            buffer += data

            # Process packets starting with start_bytes
            while start_bytes in buffer:
                start_idx = buffer.find(start_bytes)
                if start_idx == -1:
                    break  # No valid packet start found

                # Trim buffer to start_bytes
                buffer = buffer[start_idx:]
                # Look for a complete packet with image
                jpeg_start_idx = buffer.find(jpeg_start)
                jpeg_end_idx = buffer.find(jpeg_end) + 2

                print(buffer)
                if jpeg_start_idx != -1 and jpeg_end_idx != -1 and jpeg_end_idx > jpeg_start_idx:
                    # Extract and save the JPEG image
                    jpeg_data = buffer[jpeg_start_idx:jpeg_end_idx]
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    save_image(jpeg_data, timestamp)

                    # Remove the processed JPEG data from the buffer
                    buffer = buffer[jpeg_end_idx:]
                else:
                    # Incomplete packet, wait for more data
                    break

                # Extract metadata from the remaining buffer
                try:
                    decoded_data = buffer.decode(errors="ignore")
                    metadata_match = metadata_pattern.search(decoded_data)
                    if metadata_match:
                        color_name = metadata_match.group(1)
                        engine_time_delay = metadata_match.group(2)
                        maker_name = metadata_match.group(3)
                        model_name = metadata_match.group(4)
                        num_satellites = metadata_match.group(5)
                        use_cache = metadata_match.group(6)
                        print(
                            f"Metadata Found:\n"
                            f"  Color: {color_name}\n"
                            f"  EngineTimeDelay: {engine_time_delay}\n"
                            f"  Maker: {maker_name}\n"
                            f"  Model: {model_name}\n"
                            f"  NumSatellitesGPS: {num_satellites}\n"
                            f"  UseCacheGPS: {use_cache}"
                        )
                        # Clear the buffer after extracting metadata
                    else:
                        print("No metadata found.")
                except Exception as ex:
                    print(f"Error decoding metadata: {ex}")
                buffer = b""

except Exception as ex:
    print(f"An error occurred: {ex}")
