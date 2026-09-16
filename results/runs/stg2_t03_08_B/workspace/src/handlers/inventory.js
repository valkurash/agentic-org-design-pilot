const { readStore, writeStore } = require("../repo/store");

function adjustInventory(delta) {
  // Read the current store data
  const data = readStore();
  // Adjust inventory value
  data.inventory = (data.inventory || 0) + delta;
  // Write back the store data
  writeStore(data);
  return data.inventory;
}

module.exports = { adjustInventory };