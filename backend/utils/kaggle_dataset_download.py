import kagglehub

# Download latest version
path = kagglehub.dataset_download("maltegrosse/8-m-spotify-tracks-genre-audio-features")

print("Path to dataset files:", path)