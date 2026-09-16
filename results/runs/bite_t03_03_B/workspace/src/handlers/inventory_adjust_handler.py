# handler for the inventory adjust endpoint
from src.repo.inventory_adjust import InventoryAdjustRepo

def handle_adjustment_request(request_data):
    adjustment_data = process_request_data(request_data)
    InventoryAdjustRepo.write_adjustment(adjustment_data)
    return {'status': 'success'}


def process_request_data(request_data):
    # For now, we just return the request_data
    return request_data
