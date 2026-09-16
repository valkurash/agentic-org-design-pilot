const { v4: uuidv4 } = require('uuid');

class Todo {
  constructor(title, description, completed = false) {
    this.id = uuidv4();
    this.title = title;
    this.description = description;
    this.completed = completed;
    this.created_at = new Date();
    this.updated_at = new Date();
  }

  update(title, description, completed) {
    this.title = title ?? this.title;
    this.description = description ?? this.description;
    this.completed = completed ?? this.completed;
    this.updated_at = new Date();
  }
}

module.exports = Todo;
