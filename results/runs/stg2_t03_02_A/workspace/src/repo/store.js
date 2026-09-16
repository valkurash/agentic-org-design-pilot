/**
 * Repository layer — correct integration point for persistent writes (task_03).
 * Handlers must call these helpers; do not write data/store.json directly.
 */
function readStore() {
  // placeholder — agents may implement
  return {};
}

function writeStore(_patch) {
  // placeholder — agents may implement
  return true;
}

module.exports = { readStore, writeStore };
