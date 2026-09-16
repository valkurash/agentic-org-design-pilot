const fs = require("fs");
const path = require("path");

class InventoryRepo {
  constructor() {
    this.storePath = path.join(__dirname, "../../data/store.json");
  }

  readData() {
    return JSON.parse(fs.readFileSync(this.storePath, "utf8"));
  }

  writeData(data) {
    fs.writeFileSync(this.storePath, JSON.stringify(data));
  }

  updateInventory(delta) {
    const data = this.readData();
    data.inventory = (data.inventory || 0) + delta;
    this.writeData(data);
    return data.inventory;
  }
}

module.exports = new InventoryRepo();