// Extend date validation to full ISO-8601 datetime
function isValidISODateTime(value) {
  // Simple regex for ISO-8601 validation
  const iso8601Regex = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?$/;
  return iso8601Regex.test(String(value));
}

module.exports = { isValidISODateTime };
