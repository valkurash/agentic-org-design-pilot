// Adjusted to use repository layer (task_03 fix)
const path = require("path");
const { readStore, writeStore } = require(path.join(__dirname, "../../src/repo/store.js"));

function adjustInventory(delta) {
  const data = readStore();
  data.inventory = (data.inventory || 0) + delta;
  writeStore(data);
  return data.inventory;
}

module.exports = { adjustInventory };
