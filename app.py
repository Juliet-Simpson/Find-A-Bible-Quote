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


# NO FILTERING
@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    query_quotes = list(mongo.db.quotes.find({"$text": {"$search": query}}))

    for quote in query_quotes:
        quote["id"] = str(quote["_id"])
        
    all_comments = list(mongo.db.comments.find())

    return render_template("search_results.html",
        query_quotes =query_quotes, query=query,
        all_comments =all_comments)


@app.route("/browse_themes/<theme_name>")
def browse_themes(theme_name):
    theme_quotes = list(mongo.db.quotes.find({
        "theme": theme_name}))

    for quote in theme_quotes:
        quote["id"] = str(quote["_id"])

    all_comments = list(mongo.db.comments.find())

    return render_template("browse_themes.html",
        theme_quotes=theme_quotes, theme_name=theme_name,
        all_comments=all_comments)


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
                        # FIX HERE, just want to return close modal
                    return render_template("base.html")
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                # FIX HERE, just want to return close modal
                return render_template("base.html")

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            # FIX HERE
            return render_template("base.html")
    # FIX HERE return what?
    return render_template("base.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        password = request.form.get("password")
        confirm_password = request.form.get("confirm-password")
        if password != confirm_password:
            flash("Passwords do not match.")
             # FIX HERE
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
        # FIX HERE
        return render_template("base.html")
    # FIX HERE
    return render_template("base.html")


@app.route("/logout")
def logout():
    # remove user from session cookie
    flash("You have been logged out")
    session.pop("user")
# HERE, modal reload current page, logout can happen from anywhere, may still want to see search results...
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
        return redirect(url_for("my_quotes"))

    return render_template("add_quote.html", themes=themes)


@app.route("/edit_quote/<quote_id>", methods=["GET", "POST"])
def edit_quote(quote_id):
    quote = mongo.db.quotes.find_one({"_id": ObjectId(quote_id)})
    themes = mongo.db.themes.find().sort("theme", 1)
    old_theme = quote["theme"]
    if request.method == "POST":
        new_theme = request.form.get("new_theme", None)
        if new_theme:
            mongo.db.themes.insert_one({"theme": new_theme})

        # Check if there are any more quotes with the same theme
        # as the theme that has been changed.  GET OLD THEME  If not, delete 
        # the old theme from the themes collection.
            old_theme_quotes = list(mongo.db.quotes.find({"theme": old_theme}))
            if len(old_theme_quotes) == 0:
                mongo.db.themes.remove({"theme": old_theme})

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
        return redirect(url_for("my_quotes"))
 
    return render_template("edit_quote.html", quote=quote, themes=themes)


@app.route("/my_quotes")
def my_quotes():
    my_quotes = list(mongo.db.quotes.find({
        "added_by": session["user"]}))
    for quote in my_quotes:
        quote["id"] = str(quote["_id"])

    all_comments = list(mongo.db.comments.find())

    return render_template("my_quotes.html", my_quotes=my_quotes,
        all_comments=all_comments)


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
    return redirect(url_for("my_quotes"))
    # Want to redirect url to current page.  Make sure comment loads though


@app.route("/delete_quote/<quote_id>, <delete_theme>")
def delete_quote(quote_id, delete_theme):
    mongo.db.quotes.remove({"_id": ObjectId(quote_id)})

    # Also delete comments from quote
    mongo.db.comments.remove({"quote_id": str(ObjectId(quote_id))})
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

    all_quotes = list(mongo.db.quotes.find())
    my_comments = list(mongo.db.comments.find())
        
    commented_quotes = []

    for quote in all_quotes:
        d = {
            "quote": quote,
            "comments": []
        }

        for comment in my_comments:
            if comment['quote_id'] == str(quote['_id']):
                d['comments'].append(comment)

        if len(d['comments']) > 0:
            commented_quotes.append(d)

    return render_template("my_comments.html",
    commented_quotes=commented_quotes)


@app.route("/edit_comment/<quote_id>, <comment_id>", methods=["GET", "POST"])
def edit_comment(quote_id, comment_id):
    if request.method == "POST":
        submit = {
            "comment": request.form.get("edit_comment").capitalize(),
            "quote_id": quote_id,
            "comment_by": session["user"]
        }
        mongo.db.comments.update({"_id": ObjectId(comment_id)}, submit)
        flash("Comment successfully edited")

    return redirect(url_for("my_comments"))


@app.route("/delete_comment/<comment_id>")
def delete_comment(comment_id):
    mongo.db.comments.remove({"_id": ObjectId(comment_id)})
    flash("Comment Successfully Deleted")

    return redirect(url_for("my_comments"))


@app.route("/admin")
def admin():
    all_quotes = list(mongo.db.quotes.find())
    all_comments = list(mongo.db.comments.find())

    for quote in all_quotes:
        quote["id"] = str(quote["_id"])

    return render_template("admin.html",
    all_quotes=all_quotes, all_comments=all_comments)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
