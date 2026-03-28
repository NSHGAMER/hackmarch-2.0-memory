from flask import Flask
from models import db, User
from routes import routes
from auth import auth
from scheduler import start_scheduler
from flask_login import LoginManager
import os
import openai
from email_utils import send_email

app = Flask(__name__)
app.secret_key = "secret"

# 📁 FIXED DATABASE PATH (always in project folder)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, "database.db")

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# 🔐 LOGIN MANAGER
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 🔗 REGISTER ROUTES
app.register_blueprint(routes)
app.register_blueprint(auth)

# ✅ SAFE DATABASE CREATION (NO DELETE, NO ERROR)
with app.app_context():
    db.create_all()
    print("Database ready ✅")

# ⏰ START SCHEDULER
start_scheduler()

@app.route("/test-email")
def test_email():
    send_email("your_email@gmail.com", "Test", "Working 🚀")
    return "Sent"

@app.route('/verify/<token>')
def verify(token):
    return f"✅ Reminder acknowledged for token: {token}"

# 🚀 RUN APP
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)