const inventoryRepo = require("../repo/inventoryRepo");

function adjustInventory(delta) {
  return inventoryRepo.updateInventory(delta);
}

module.exports = { adjustInventory };