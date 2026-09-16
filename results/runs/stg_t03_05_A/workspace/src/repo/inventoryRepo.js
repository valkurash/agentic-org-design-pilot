const fs = require("fs");
const path = require("path");

const storePath = path.join(__dirname, "../../data/store.json");

function getInventory() {
  const data = JSON.parse(fs.readFileSync(storePath, "utf8"));
  return data.inventory || 0;
}

function updateInventory(delta) {
  const data = JSON.parse(fs.readFileSync(storePath, "utf8"));
  data.inventory = (data.inventory || 0) + delta;
  fs.writeFileSync(storePath, JSON.stringify(data));
  return data.inventory;
}

module.exports = { getInventory, updateInventory };
