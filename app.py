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
@app.route("/render_homepage/<theme_name>")
def render_homepage():
    themes = list(mongo.db.themes.find().sort("theme", 1))
    return render_template("homepage.html", themes=themes)


@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    quotes = list(mongo.db.quotes.find({"$text": {"$search": query}}))
    return render_template("search_results.html", quotes=quotes, query=query)


@app.route("/browse_themes/<theme_name>")
def browse_themes(theme_name):
    theme_quotes = list(mongo.db.quotes.find({
        "theme": theme_name}))
    return render_template("browse_themes.html",
        theme_quotes=theme_quotes, theme_name=theme_name)


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
        password = request.form.get("password")
        confirm_password = request.form.get("confirm-password")
        if password != confirm_password:
            flash("Passwords do not match.")
            return render_template("base.html")
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
        new_theme = request.form.get("new_theme", None)
        if new_theme:
            mongo.db.themes.insert_one({"theme": new_theme})
            theme = new_theme or request.form.get("theme")
            quote = {
                "theme": theme,
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
            return my_quotes()

    return render_template("add_quote.html", themes=themes)


@app.route("/edit_quote/<quote_id>", methods=["GET", "POST"])
def edit_quote(quote_id):
    themes = mongo.db.themes.find().sort("theme", 1)
    if request.method == "POST":
        new_theme = request.form.get("new_theme", None)
        if new_theme:
            mongo.db.themes.insert_one({"theme": new_theme})
            theme = new_theme or request.form.get("theme")
            submit = {
                "theme": theme,
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
    # make a variable of each quotes object id to use for relating quote to comment
    # quote_id = mongo.db.quote.find({"_id": ObjectId(quote_id)})
    # **MATCH quote._id from quotes to quote_id value in comments
    # quote_comment = list(mongo.db.comments.find())
    my_quotes = list(mongo.db.quotes.find({"added_by": session["user"]}))
    # quote_comments = list(mongo.db.comments.find(comments.quote_id = quotes.quote_id))
    return render_template("my_quotes.html", my_quotes=my_quotes)


# @app.route("/comment")
# def comment():
#     if request.method == "POST":
#         comment = {
#             "comment": request.form.get("comment").capitalize(),
#             "quote_id": How DO WE GET THAT,
#             "comment_by": session["user"]
#         }
#         mongo.db.comments.insert_one(comment)

#     return (current template how???)


@app.route("/delete_quote/<quote_id>, <delete_theme>")
def delete_quote(quote_id, delete_theme):
    mongo.db.quotes.remove({"_id": ObjectId(quote_id)})
    flash("Quote Successfully Deleted")

# Check if there are any more quotes with the same theme
#  as the quote that has been deleted.  If not, delete 
# the theme from the themes collection.
    theme_text = delete_theme
    deleted_theme_quotes = list(mongo.db.quotes.find({"theme": theme_text}))
    if len(deleted_theme_quotes) == 0:
        mongo.db.themes.remove({"theme": theme_text})
    return my_quotes()


@app.route("/my_comments")
def my_comments():
    return render_template("my_comments.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
