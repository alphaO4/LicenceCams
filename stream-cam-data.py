import re
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime
import socket

# Parse for make, model, and manufacturer using regex
metadata_pattern = re.compile(r'"MakerName": "(.*?)","ModelName": "(.*?)"')
license_plate_pattern = re.compile(r'[A-Z0-9]{1,7}')  # Basic example for license plates

# Define the host and port
host = "166.152.44.55"
port = 5002

# Create a socket connection
try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(f"Connecting to {host}:{port}...")
        s.connect((host, port))
        print("Connection established.")

        # Continuously receive data
        buffer = b""
        while True:
            data = s.recv(4096)
            if not data:
                break
            buffer += data

            # Extract metadata
            try:
                metadata_match = metadata_pattern.search(buffer.decode(errors="ignore"))
                if metadata_match:
                    maker_name = metadata_match.group(1)
                    model_name = metadata_match.group(2)
                    print(f"Maker: {maker_name}, Model: {model_name}")
                #else:
                #    print("Metadata not found in the stream.")
            except Exception as e:
                print(f"Error extracting metadata: {e}")

            # Attempt to process image from buffer
            try:
                image = Image.open(io.BytesIO(buffer))

                # Add current timestamp to the image
                draw = ImageDraw.Draw(image)
                font = ImageFont.load_default()  # Load default font
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                draw.text((10, 10), timestamp, fill="white", font=font)

                # Show and save the image
                image.show()
                image.save("live_image_with_timestamp.png")
                print("Image processed and saved.")
                break
            except Exception:
                # If an image isn't successfully created, continue receiving more data
                pass
except Exception as ex:
    print(f"An error occurred: {ex}")