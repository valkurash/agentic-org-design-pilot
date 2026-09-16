# store_writer.py

import json

class StoreWriter:
    def __init__(self, filepath='data/store.json'):
        self.filepath = filepath

    def write_data(self, data):
        """Writes data to the store in a controlled way."""
        with open(self.filepath, 'w') as file:
            json.dump(data, file)
