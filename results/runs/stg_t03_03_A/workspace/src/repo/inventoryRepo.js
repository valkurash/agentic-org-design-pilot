const fs = require('fs');
const path = require('path');

class InventoryRepo {
  constructor() {
    this.storePath = path.join(__dirname, '../../data/store.json');
  }

  loadInventory() {
    const data = JSON.parse(fs.readFileSync(this.storePath, 'utf8'));
    return data.inventory || 0;
  }

  saveInventory(inventory) {
    const data = { inventory };
    fs.writeFileSync(this.storePath, JSON.stringify(data));
  }

  adjustInventory(delta) {
    const currentInventory = this.loadInventory();
    const newInventory = currentInventory + delta;
    this.saveInventory(newInventory);
    return newInventory;
  }
}

module.exports = InventoryRepo;
