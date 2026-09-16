const fs = require('fs');
const path = require('path');

function adjustInventory(delta) {
  const storePath = path.join(__dirname, '../../data/store.json');
  const data = JSON.parse(fs.readFileSync(storePath, 'utf8'));
  data.inventory = (data.inventory || 0) + delta;
  fs.writeFileSync(storePath, JSON.stringify(data));
  return data.inventory;
}

module.exports = { adjustInventory };