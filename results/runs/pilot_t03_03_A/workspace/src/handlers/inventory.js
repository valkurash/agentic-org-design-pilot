// Refactored to use repository layer (task_03 R1 resolution)
const { getInventory, updateInventory } = require("../repo/inventoryRepo");

function adjustInventory(delta) {
  const currentInventory = getInventory();
  const newInventory = currentInventory + delta;
  updateInventory(newInventory);
  return newInventory;
}

module.exports = { adjustInventory };
