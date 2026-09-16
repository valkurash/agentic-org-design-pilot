# Repository functionality to handle inventory adjustments

def adjust_inventory(item_id, new_quantity):
    store = load_store()
    store['inventory'][item_id] = new_quantity
    save_store(store)


def load_store():
    # Load the store.json data
    try:
        with open('data/store.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_store(store_data):
    # Use repository layer to persist changes
    with open('data/store.json', 'w') as f:
        json.dump(store_data, f)