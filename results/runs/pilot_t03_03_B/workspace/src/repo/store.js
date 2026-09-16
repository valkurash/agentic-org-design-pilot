const fs = require("fs");
const path = require("path");

const storePath = path.join(__dirname, "../../data/store.json");

function readStore() {
  try {
    const data = fs.readFileSync(storePath, "utf8");
    return JSON.parse(data);
  } catch (error) {
    console.error("Error reading the store:", error);
    return {};
  }
}

function writeStore(patch) {
  try {
    const currentData = readStore();
    const newData = { ...currentData, ...patch };
    fs.writeFileSync(storePath, JSON.stringify(newData));
    return true;
  } catch (error) {
    console.error("Error writing to the store:", error);
    return false;
  }
}

module.exports = { readStore, writeStore };
