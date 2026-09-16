/**
 * Repository layer — correct integration point for persistent writes (task_03).
 * Handlers must call these helpers; do not write data/store.json directly. Updated for inventory.
 */
const fs = require("fs");
const path = require("path");

const storePath = path.join(__dirname, "../../data/store.json");

function readStore() {
  const data = JSON.parse(fs.readFileSync(storePath, "utf8"));
  return data;
}

function writeStore(newData) {
  fs.writeFileSync(storePath, JSON.stringify(newData));
}

module.exports = { readStore, writeStore };
