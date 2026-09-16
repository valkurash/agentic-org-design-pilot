// Fix: route via src/repo/.
const { updateInventory } = require("../repo/inventoryRepo");

function adjustInventory(delta) {
  return updateInventory(delta);
}

module.exports = { adjustInventory };