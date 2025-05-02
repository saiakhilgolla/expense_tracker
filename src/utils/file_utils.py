import json

def load_config(file_path):
    with open(file_path, "r") as file:
        config = json.load(file)
    return config

def is_csv_file(file_path):
    """Validate if the file is a CSV file."""
    return file_path.endswith(".csv")