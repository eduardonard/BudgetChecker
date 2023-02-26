import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import datetime

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///progetto.db")

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    user_id = session["user_id"] 
    username = db.execute("SELECT username FROM users WHERE id = ?", user_id)[0]["username"]
    income_db = db.execute("SELECT amount, category, date, comment FROM transactions WHERE user_id = ? AND amount > 0 ORDER BY date DESC", user_id)
    liabilities_db = db.execute("SELECT amount, category, date, comment FROM transactions WHERE user_id = ? AND amount < 0 ORDER BY date DESC", user_id)
    incCategori = db.execute("SELECT category FROM categories WHERE user_id = ? AND type = 'income'",user_id)
    expCategori = db.execute("SELECT category FROM categories WHERE user_id = ? AND type = 'liability'",user_id)
    cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
    indes = render_template("index.html", income_db = income_db, liabilities_db = liabilities_db, cash = cash, incCategories=incCategori, expCategories = expCategori, username=username)
    if request.method == "GET":
        return indes
    elif request.method == "POST" and request.form.get("amount") != None:
        cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
        amount = request.form.get("amount")
        category = request.form.get("category")          
        date = request.form.get("date")
        comment = request.form.get("comment")
        how = request.form.get("how")
        if category == None:
            income_db = db.execute("SELECT amount, category, date FROM transactions WHERE user_id = ? AND amount > 0", user_id)
            liabilities_db = db.execute("SELECT amount, category, date FROM transactions WHERE user_id = ? AND amount < 0", user_id)
            cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
            flash("Must select category")
            return indes
        amount = int(amount)
        db.execute("INSERT INTO transactions (user_id, amount, category, date, comment) VALUES (?, ?, ?, ?, ?)", user_id, amount, category, date, comment)
        db.execute("UPDATE users SET cash = ? WHERE id = ?", cash + amount, user_id)
        cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
        income_db = db.execute("SELECT amount, category, date FROM transactions WHERE user_id = ? AND amount > 0", user_id)
        liabilities_db = db.execute("SELECT amount, category, date FROM transactions WHERE user_id = ? AND amount < 0", user_id)
    return redirect("/")


@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    user_id = session["user_id"]
    username = db.execute("SELECT username FROM users WHERE id = ?", user_id)[0]["username"]
    categori = db.execute("SELECT category FROM categories WHERE user_id = ?", user_id)
    transactions = db.execute("SELECT * FROM transactions WHERE user_id = ?", user_id)
    if request.method == "GET":
        return render_template("settings.html", categories = categori, transactions = transactions, username = username)
    elif request.method == "POST" and request.form.get("newCash") != None:
        db.execute("UPDATE users SET cash = ? WHERE id = ?", int(request.form.get("newCash")), user_id)
    elif request.method == "POST" and request.form.get("addCategory") != None:
        db.execute("INSERT INTO categories (category , type, user_id) VALUES (?, ?, ?)", request.form.get("addCategory"), request.form.get("addCategoryType"), user_id)
    elif request.method == "POST" and request.form.get("remCategory") != None:
        db.execute("DELETE FROM categories WHERE category = ?", request.form.get("remCategory"))
    elif request.method == "POST" and request.form.get("remTransaction") != None:
        db.execute("DELETE FROM transactions WHERE id = ?", request.form.get("remTransaction"))
    elif request.method == "POST":
        return redirect("/settings")
    return redirect("/settings")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("login.html",error="Invalid username and/or password")
        session["user_id"] = rows[0]["id"]
        return redirect("/")
    elif request.method == "GET":
        return render_template("login.html")

@app.route("/home")
def home():
    return render_template("homepage.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        verify = request.form.get("confirmation")

        if not username:
            return apology("Username required")

        if not password:
            return apology("Password required")

        if not verify:
            return apology("Password verification required")

        if password != verify:
            return apology("Passwords don't match, try again")

        hash = generate_password_hash(password)

        try:
            newUser = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
        except:
            return apology("Username exists")

        session["user_id"] = newUser

        return redirect("/")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("notfound.html")