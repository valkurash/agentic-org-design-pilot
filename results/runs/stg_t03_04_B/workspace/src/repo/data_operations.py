# src/repo/data_operations.py

import json
from typing import Any, Dict

STORE_PATH = 'data/store.json'

def read_store() -> Dict[str, Any]:
    with open(STORE_PATH, 'r') as file:
        return json.load(file)

def write_store(data: Dict[str, Any]) -> None:
    with open(STORE_PATH, 'w') as file:
        json.dump(data, file)

def update_inventory(item_id: str, adjustment: int) -> None:
    store_data = read_store()
    if 'inventory' in store_data:
        store_data['inventory'][item_id] = store_data['inventory'].get(item_id, 0) + adjustment
    else:
        store_data['inventory'] = {item_id: adjustment}
    write_store(store_data)

# The `update_inventory` function can be called by handlers to adjust inventory levels.