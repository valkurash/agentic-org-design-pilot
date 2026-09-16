const { readStore, writeStore } = require('./store');

function adjustInventory(delta) {
  const data = readStore();
  data.inventory = (data.inventory || 0) + delta;
  writeStore({ inventory: data.inventory });
  return data.inventory;
}

module.exports = { adjustInventory };