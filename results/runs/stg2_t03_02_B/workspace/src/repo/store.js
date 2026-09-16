/**
 * Repository layer — correct integration point for persistent writes (task_03).
 * Handlers must call these helpers; do not write data/store.json directly.
 */

const fs = require("fs");
const path = require("path");

function readStore() {
  const storePath = path.join(__dirname, "../../data/store.json");
  const data = JSON.parse(fs.readFileSync(storePath, "utf8"));
  return data;
}

function writeStore(patch) {
  const storePath = path.join(__dirname, "../../data/store.json");
  const data = readStore();
  const updatedData = { ...data, ...patch };
  fs.writeFileSync(storePath, JSON.stringify(updatedData));
  return true;
}

module.exports = { readStore, writeStore };
