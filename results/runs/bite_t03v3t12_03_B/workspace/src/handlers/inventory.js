// Refactored to use repository layer (src/repo/inventoryRepo.js)
const { getInventory, updateInventory } = require("../repo/inventoryRepo");

function adjustInventory(delta) {
  const currentInventory = getInventory();
  const newInventory = currentInventory + delta;
  updateInventory(newInventory);
  return newInventory;
}

module.exports = { adjustInventory };