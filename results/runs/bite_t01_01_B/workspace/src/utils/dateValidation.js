// existing shared date helpers — FROZEN, do not edit
// Validates calendar dates only (YYYY-MM-DD).
// No time-of-day, no timezone/offset support.
function isValidDate(value) {
  return /^\d{4}-\d{2}-\d{2}$/.test(String(value));
}
module.exports = { isValidDate };
