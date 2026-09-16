const session = require('express-session');
// Import auth module session middleware if it exists
// Placeholder code to bind session

module.exports = session({
  secret: 'keyboard cat',
  resave: false,
  saveUninitialized: true,
  cookie: { secure: process.env.NODE_ENV === 'production' }
});
