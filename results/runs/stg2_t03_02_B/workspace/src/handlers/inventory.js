const { writeStore, readStore } = require("../repo/store");

function adjustInventory(delta) {
  const data = readStore();
  const updatedInventory = (data.inventory || 0) + delta;
  writeStore({ inventory: updatedInventory });
  return updatedInventory;
}

module.exports = { adjustInventory };