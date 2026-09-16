// Updated to route via src/repo/ store.js (task_03 adjustment)
const { readStore, writeStore } = require("../repo/store");

function adjustInventory(delta) {
  const data = readStore();
  data.inventory = (data.inventory || 0) + delta;
  writeStore(data);
  return data.inventory;
}

module.exports = { adjustInventory };
