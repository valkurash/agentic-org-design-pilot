const InventoryRepo = require('../repo/inventoryRepo');

const inventoryRepo = new InventoryRepo();

function adjustInventory(delta) {
  return inventoryRepo.adjustInventory(delta);
}

module.exports = { adjustInventory };