// Refactored to use repository layer (src/repo/store.js)
const { readStore, writeStore } = require("../repo/store");

function adjustInventory(delta) {
  const data = readStore();
  data.inventory = (data.inventory || 0) + delta;
  writeStore({ inventory: data.inventory });
  return data.inventory;
}

module.exports = { adjustInventory };
