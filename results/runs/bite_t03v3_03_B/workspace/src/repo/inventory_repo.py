import json

class InventoryRepo:
    def __init__(self, store_path='data/store.json'):
        self.store_path = store_path

    def update_inventory(self, item_id, quantity_adjustment):
        # Read the current inventory data
        with open(self.store_path, 'r') as file:
            inventory_data = json.load(file)
        
        # Adjust the inventory
        inventory_data[item_id] = inventory_data.get(item_id, 0) + quantity_adjustment
        
        # Write back the adjusted inventory data
        with open(self.store_path, 'w') as file:
            json.dump(inventory_data, file)
