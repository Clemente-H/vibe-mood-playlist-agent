import kagglehub
import os
import shutil

# Define the destination directory for the database file
DESTINATION_DIR = os.path.join(os.path.dirname(__file__), "..", "data_spotify")
DESTINATION_FILE_NAME = "spotify.sqlite"

# Ensure the destination directory exists
os.makedirs(DESTINATION_DIR, exist_ok=True)

print("Downloading dataset from Kaggle...")
# Download latest version
download_path = kagglehub.dataset_download("maltegrosse/8-m-spotify-tracks-genre-audio-features")

print(f"Dataset downloaded to: {download_path}")

# Assuming the sqlite file is directly in the downloaded path
# We need to find the .sqlite file within the downloaded directory
sqlite_file_found = None
for root, _, files in os.walk(download_path):
    for file in files:
        if file.endswith(".sqlite"):
            sqlite_file_found = os.path.join(root, file)
            break
    if sqlite_file_found:
        break

if sqlite_file_found:
    destination_path = os.path.join(DESTINATION_DIR, DESTINATION_FILE_NAME)
    shutil.move(sqlite_file_found, destination_path)
    print(f"Moved '{sqlite_file_found}' to '{destination_path}'")
else:
    print("Error: No .sqlite file found in the downloaded dataset.")

print("Kaggle dataset download and setup complete.")