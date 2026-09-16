const { readStore, writeStore } = require("../repo/store");

function adjustInventory(delta) {
  const storeData = readStore();
  storeData.inventory = (storeData.inventory || 0) + delta;
  writeStore(storeData);
  return storeData.inventory;
}

module.exports = { adjustInventory };