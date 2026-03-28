from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()


# ===============================
# 🔐 USER MODEL
# ===============================
class User(db.Model, UserMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # 🔗 Relationships
    lessons = db.relationship(
        "Lesson",
        backref="user",
        lazy=True,
        cascade="all, delete"
    )

    learnings = db.relationship(
        "Learning",
        backref="user",
        lazy=True,
        cascade="all, delete"
    )

    chats = db.relationship(
        "ChatMessage",
        backref="user",
        lazy=True,
        cascade="all, delete"
    )

    todos = db.relationship(
        "Todo",
        backref="user",
        lazy=True,
        cascade="all, delete"
    )


# ===============================
# 📚 LESSON MODEL
# ===============================
class Lesson(db.Model):
    __tablename__ = "lesson"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    sub_details = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    next_review = db.Column(db.DateTime)
    interval = db.Column(db.Integer, default=1)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False
    )


# ===============================
# 🤖 LEARNING MODEL
# ===============================
class Learning(db.Model):
    __tablename__ = "learning"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    summary = db.Column(db.Text)

    time_spent = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False
    )

    chats = db.relationship(
        "ChatMessage",
        backref="learning",
        lazy=True,
        cascade="all, delete"
    )


# ===============================
# 💬 CHAT MODEL
# ===============================
class ChatMessage(db.Model):
    __tablename__ = "chat_message"

    id = db.Column(db.Integer, primary_key=True)

    role = db.Column(db.String(10))  # "user" or "ai"
    message = db.Column(db.Text)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    learning_id = db.Column(db.Integer, db.ForeignKey("learning.id"))


# ===============================
# 📝 TODO MODEL
# ===============================
class Todo(db.Model):
    __tablename__ = "todo"

    id = db.Column(db.Integer, primary_key=True)

    task = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

class QuizAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    learning_id = db.Column(db.Integer, db.ForeignKey('learning.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    score = db.Column(db.Integer)
    total = db.Column(db.Integer)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    learning_id = db.Column(db.Integer, db.ForeignKey('learning.id'))

    minutes = db.Column(db.Integer)
    is_custom = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)