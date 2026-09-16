from src.repo.inventory_adjust import adjust_inventory

def handle_inventory_adjustment_request(request):
    item_id = request.get('item_id')
    quantity = request.get('quantity')
    result = adjust_inventory(item_id, quantity)
    return result