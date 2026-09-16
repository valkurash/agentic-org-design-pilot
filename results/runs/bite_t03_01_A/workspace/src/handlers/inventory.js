// Updated to comply with architecture.json — use repository layer (task_03 R1).
const { readStore, writeStore } = require("../repo/store");

function adjustInventory(delta) {
  const data = readStore();
  data.inventory = (data.inventory || 0) + delta;
  writeStore({ inventory: data.inventory });
  return data.inventory;
}

module.exports = { adjustInventory };
