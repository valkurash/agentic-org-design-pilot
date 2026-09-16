// Validates full ISO-8601 format with time and timezone.
function isValidISO8601(value) {
  return /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/.test(value);
}

module.exports = { isValidISO8601 };
