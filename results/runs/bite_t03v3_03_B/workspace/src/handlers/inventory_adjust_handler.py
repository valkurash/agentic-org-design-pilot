from repo.inventory_repo import InventoryRepo

def adjust_inventory(item_id, quantity_adjustment):
    inventory_repo = InventoryRepo()
    inventory_repo.update_inventory(item_id, quantity_adjustment)
