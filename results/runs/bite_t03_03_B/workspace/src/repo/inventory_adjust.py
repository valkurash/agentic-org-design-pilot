# repo layer for inventory adjustment
class InventoryAdjustRepo:
    def write_adjustment(data):
        with open('data/store.json', 'w') as store_file:
            json.dump(data, store_file)

