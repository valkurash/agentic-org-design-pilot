const Ajv = require('ajv');
const fs = require('fs');

const ajv = new Ajv();

function validateClaim(claim) {
  const schema = JSON.parse(fs.readFileSync('schemas/expense_claim.schema.json', 'utf8'));
  const validate = ajv.compile(schema);
  const valid = validate(claim);
  if (!valid) {
    throw new Error('Claim is invalid: ' + ajv.errorsText(validate.errors));
  }
  return valid;
}

module.exports = {
  validateClaim,
};