// Utility to validate full ISO-8601 date-time strings
function isValidISODateTime(value) {
    // This regex checks for a standard ISO-8601 date-time format with optional milliseconds
    return /^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,3})?([+-]\d{2}:\d{2}|Z))$/.test(value);
}

module.exports = { isValidISODateTime };
