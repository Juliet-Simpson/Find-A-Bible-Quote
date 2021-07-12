import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/render_homepage")
def render_homepage():
    return render_template("homepage.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                        session["user"] = request.form.get("username").lower()
                        flash("Welcome {}".format(
                            request.form.get("username")))
                        return render_template("base.html")
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return render_template("base.html")

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return render_template("base.html")

    return render_template("base.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return render_template("base.html")
# HERE
    return render_template("base.html")


@app.route("/logout")
def logout():
    # remove user from session cookie
    flash("You have been logged out")
    session.pop("user")
# HERE
    return redirect(url_for("render_homepage"))


@app.route("/add_quote", methods=["GET", "POST"])
def add_quote():
    themes = mongo.db.themes.find().sort("theme", 1)
    if request.method == "POST":
        quote = {
            "theme": request.form.get("theme"),
            "book": request.form.get("book").capitalize(),
            "chapter": request.form.get("chapter"),
            "start_verse": request.form.get("start_verse"),
            "end_verse": request.form.get("end_verse"),
            "text": request.form.get("text").capitalize(),
            "added_by": session["user"]
        }
        mongo.db.quotes.insert_one(quote)
        flash("Quote Successfully Added")
        # return render_template("add_quote.html", themes=themes)
        return redirect(url_for("add_quote"))

    return render_template("add_quote.html", themes=themes)


@app.route("/edit_quote/<quote_id>", methods=["GET", "POST"])
def edit_quote(quote_id):
    themes = mongo.db.themes.find().sort("theme", 1)
    if request.method == "POST":
        submit = {
            "theme": request.form.get("theme"),
            "book": request.form.get("book").capitalize(),
            "chapter": request.form.get("chapter"),
            "start_verse": request.form.get("start_verse"),
            "end_verse": request.form.get("end_verse"),
            "text": request.form.get("text").capitalize(),
            "added_by": session["user"]
        }
        mongo.db.quotes.update({"_id": ObjectId(quote_id)}, submit)
        flash("Quote Successfully Updated")
        return my_quotes()

    quote = mongo.db.quotes.find_one({"_id": ObjectId(quote_id)})
    return render_template("edit_quote.html", quote=quote, themes=themes)


@app.route("/add_theme")
def add_theme():
    return


@app.route("/my_quotes")
def my_quotes():
    quotes = list(mongo.db.quotes.find())
    return render_template("my_quotes.html", quotes=quotes)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
