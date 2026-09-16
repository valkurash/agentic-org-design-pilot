const { v4: uuidv4 } = require('uuid');

class TodoItem {
  constructor(userId, title, description) {
    this.id = uuidv4();
    this.user_id = userId;
    this.title = title;
    this.description = description;
    this.is_complete = false;
    this.created_at = new Date();
    this.updated_at = new Date();
  }

  update(title, description, isComplete) {
    this.title = title || this.title;
    this.description = description || this.description;
    this.is_complete = isComplete !== undefined ? isComplete : this.is_complete;
    this.updated_at = new Date();
  }
}

module.exports = TodoItem;