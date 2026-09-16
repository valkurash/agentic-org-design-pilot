const fs = require("fs");
const path = require("path");

const storePath = path.join(__dirname, "../../data/store.json");

function getInventory() {
  const data = JSON.parse(fs.readFileSync(storePath, "utf8"));
  return data.inventory || 0;
}

function updateInventory(newInventory) {
  const data = JSON.parse(fs.readFileSync(storePath, "utf8"));
  data.inventory = newInventory;
  fs.writeFileSync(storePath, JSON.stringify(data));
}

module.exports = { getInventory, updateInventory };