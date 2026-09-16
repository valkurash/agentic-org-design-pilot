const fs = require('fs');

function validateClaim(claim, schema) {
  const Ajv = require('ajv');
  const ajv = new Ajv();
  const validate = ajv.compile(schema);
  const valid = validate(claim);
  if (!valid) {
    console.error(validate.errors);
    return false;
  }
  return true;
}

function loadSchema(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

module.exports = {
  validateClaim,
  loadSchema
};
