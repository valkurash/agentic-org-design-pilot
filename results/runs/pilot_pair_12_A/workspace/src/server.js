const express = require('express');
const bodyParser = require('body-parser');

const todosController = require('./todos/todosController');

const app = express();
app.use(bodyParser.json());

app.use(todosController);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
