import json

STORE_PATH = 'data/store.json'

class StoreHandler:
    @staticmethod
    def write_store(data):
        """Writes data to the persistent store via repo layer."""
        with open(STORE_PATH, 'w') as f:
            json.dump(data, f)

    @staticmethod
    def read_store():
        """Reads data from the persistent store via repo layer."""
        with open(STORE_PATH, 'r') as f:
            return json.load(f)
