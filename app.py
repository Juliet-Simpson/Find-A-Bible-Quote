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

# This works
@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    query_quotes = list(mongo.db.quotes.find({"$text": {"$search": query}}))

    for quote in query_quotes:
        quote_id = str(quote["_id"])
        theme_quote_comments = list(mongo.db.comments.find({
            "quote_id": quote_id}))

    return render_template("search_results.html",
    query_quotes=query_quotes, query=query,
    theme_quote_comments=theme_quote_comments)

# this doesn't
@app.route("/browse_themes/<theme_name>")
def browse_themes(theme_name):
    theme_quotes = list(mongo.db.quotes.find({
        "theme": theme_name}))
        
# Got the whole rendering comments bit to do here also
    for quote in theme_quotes:
        quote_id = str(quote["_id"])
        theme_quote_comments = list(mongo.db.comments.find({
            "quote_id": quote_id}))
    
    return render_template("browse_themes.html",
        theme_quotes=theme_quotes, theme_name=theme_name, theme_quote_comments=theme_quote_comments)

# Working version
# @app.route("/browse_themes/<theme_name>")
# def browse_themes(theme_name):
#     theme_quotes = list(mongo.db.quotes.find({
#         "theme": theme_name}))
    
# # Got the whole rendering comments bit to do here also
#     return render_template("browse_themes.html",
#         theme_quotes=theme_quotes, theme_name=theme_name)



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
    quote = mongo.db.quotes.find_one({"_id": ObjectId(quote_id)})
    themes = mongo.db.themes.find().sort("theme", 1)
    # Commented out code is not working
    # old_theme = mongo.db.themes.find_one({"quote_id": str(quote_id)})
    if request.method == "POST":
        new_theme = request.form.get("new_theme", None)
        if new_theme:
            mongo.db.themes.insert_one({"theme": new_theme})

        # Check if there are any more quotes with the same theme
        # as the theme that has been changed.  GET OLD THEME  If not, delete 
        # the theme from the themes collection.

        # old_theme_quotes = list(mongo.db.quotes.find({"theme": old_theme}))
        # if len(old_theme_quotes) == 0:
        #     mongo.db.themes.remove({"theme": old_theme})

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
 
    return render_template("edit_quote.html", quote=quote, themes=themes)


# # SHOWS NONE OF THE COMMENTS (FILTERING ATTEMPTED)

@app.route("/my_quotes")
def my_quotes():
    my_quotes = list(mongo.db.quotes.find({
        "added_by": session["user"]}))

    for quote in my_quotes:
        quote_id = str(quote["_id"])
        quote_comments = list(mongo.db.comments.find({
            "quote_id": quote_id}))
    
    return render_template("my_quotes.html", my_quotes=my_quotes,
            quote_comments=quote_comments)

# SHOWS ALL THE COMMENTS NO FILTERING(NO ATTEMPT TO)
# @app.route("/my_quotes")
# def my_quotes():
#     my_quotes = list(mongo.db.quotes.find({
#         "added_by": session["user"]}))

#     quote_comments = list(mongo.db.comments.find())

#     return render_template("my_quotes.html", my_quotes=my_quotes,
#         quote_comments=quote_comments)


@app.route("/comment/<quote_id>,", methods=['GET', 'POST'])
def comment(quote_id):   
    if request.method == "POST":
        comment = {
            "comment": request.form.get("comment").capitalize(),
            "quote_id": quote_id,
            "comment_by": session["user"]
        }
        mongo.db.comments.insert_one(comment)
        flash("Thanks for commenting")
    return my_quotes()


@app.route("/delete_quote/<quote_id>, <delete_theme>")
def delete_quote(quote_id, delete_theme):
    mongo.db.quotes.remove({"_id": ObjectId(quote_id)})
    flash("Quote Successfully Deleted")

# Check if there are any more quotes with the same theme
# as the quote that has been deleted.  If not, delete 
# the theme from the themes collection.
    
    deleted_theme_quotes = list(mongo.db.quotes.find({"theme": delete_theme}))
    if len(deleted_theme_quotes) == 0:
        mongo.db.themes.remove({"theme": delete_theme})
    return my_quotes()


@app.route("/my_comments")
def my_comments():
    return render_template("my_comments.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
