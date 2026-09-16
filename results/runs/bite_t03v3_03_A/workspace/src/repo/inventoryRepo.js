const fs = require("fs");
const path = require("path");

function getInventory() {
  const storePath = path.join(__dirname, "../../data/store.json");
  const data = JSON.parse(fs.readFileSync(storePath, "utf8"));
  return data.inventory || 0;
}

function updateInventory(newInventory) {
  const storePath = path.join(__dirname, "../../data/store.json");
  const data = JSON.parse(fs.readFileSync(storePath, "utf8"));
  data.inventory = newInventory;
  fs.writeFileSync(storePath, JSON.stringify(data));
  return data.inventory;
}

module.exports = { getInventory, updateInventory };
