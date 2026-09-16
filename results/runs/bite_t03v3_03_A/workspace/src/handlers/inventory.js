const { getInventory, updateInventory } = require("../repo/inventoryRepo");

function adjustInventory(delta) {
  const currentInventory = getInventory();
  const newInventory = currentInventory + delta;
  return updateInventory(newInventory);
}

module.exports = { adjustInventory };