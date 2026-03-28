from flask import Blueprint, render_template, request, redirect, flash
from models import db, User
from flask_login import login_user, logout_user, login_required
import bcrypt

auth = Blueprint("auth", __name__)   # ✅ THIS LINE IS CRITICAL

@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"].encode("utf-8")

        # ✅ CHECK FIRST (THIS IS MISSING IN YOUR CODE)
        user_exists = User.query.filter_by(email=email).first()

        if user_exists:
            flash("⚠️ Email already registered. Please login.")
            return redirect("/login")

        # ✅ ONLY CREATE IF NOT EXISTS
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())

        new_user = User(email=email, password=hashed)

        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash("Something went wrong. Try again.")
            return redirect("/register")

        return redirect("/login")

    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"].encode("utf-8")

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.checkpw(password, user.password):
            login_user(user)
            return redirect("/dashboard")

        flash("Invalid credentials")

    return render_template("login.html")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")