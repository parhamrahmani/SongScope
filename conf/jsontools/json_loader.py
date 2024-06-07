import json


def load_data(json_path):
    # Load your data from a file or any other source
    with open(json_path, 'r') as file:
        data = json.load(file)
    return data
