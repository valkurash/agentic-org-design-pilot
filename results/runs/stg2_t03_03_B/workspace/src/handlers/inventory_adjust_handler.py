# Handler for adjusting inventory, uses repo layer
from src.repo.inventory_adjust_repo import adjust_inventory

def inventory_adjust_endpoint(request_data):
    return adjust_inventory(request_data)