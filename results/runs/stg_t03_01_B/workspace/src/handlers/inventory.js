const repo = require("../repo/store");

function adjustInventory(delta) {
  const data = repo.readStore();
  data.inventory = (data.inventory || 0) + delta;
  repo.writeStore(data);
  return data.inventory;
}

module.exports = { adjustInventory };