const { readStore, writeStore } = require("../repo/store");

function adjustInventory(delta) {
  const data = readStore();
  data.inventory = (data.inventory || 0) + delta;
  writeStore(data);  // Assuming writeStore handles serialization and writing to store
  return data.inventory;
}

module.exports = { adjustInventory };