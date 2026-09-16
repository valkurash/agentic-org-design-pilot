// Violation fixed: Utilize repository layer for store writes
const { readStore, writeStore } = require("../repo/store");

function adjustInventory(delta) {
  const data = readStore();
  data.inventory = (data.inventory || 0) + delta;
  writeStore(data);
  return data.inventory;
}

module.exports = { adjustInventory };
