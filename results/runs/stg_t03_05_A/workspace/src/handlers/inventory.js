const { updateInventory } = require("../repo/inventoryRepo.js");

function adjustInventory(delta) {
  return updateInventory(delta);
}

module.exports = { adjustInventory };