const fs = require("fs");
const path = require("path");

const storePath = path.join(__dirname, "../../data/store.json");

function readStore() {
  const data = JSON.parse(fs.readFileSync(storePath, "utf8"));
  return data;
}

function writeStore(patch) {
  const data = readStore();
  const updatedData = { ...data, ...patch };
  fs.writeFileSync(storePath, JSON.stringify(updatedData));
  return updatedData;
}

module.exports = { readStore, writeStore };
