import os
from flask import (
    Flask,
    flash,
    render_template,
    redirect,
    request,
    session,
    url_for,
)
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

    return render_template(
        "homepage.html", themes=themes, next_page=request.full_path
    )


@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query", "")
    is_query = query.replace(" ", "")
    if not is_query:
        flash("Please enter a search value")
        return redirect(url_for("render_homepage"))

    query_quotes = list(mongo.db.quotes.find({"$text": {"$search": query}}))

    for quote in query_quotes:
        quote["id"] = str(quote["_id"])

    all_comments = list(mongo.db.comments.find())

    return render_template(
        "search_results.html",
        query_quotes=query_quotes,
        query=query,
        all_comments=all_comments,
        next_page=request.full_path,
    )


@app.route("/browse_themes/<theme_name>")
def browse_themes(theme_name):
    theme_quotes = list(mongo.db.quotes.find({"theme": theme_name}))

    for quote in theme_quotes:
        quote["id"] = str(quote["_id"])

    all_comments = list(mongo.db.comments.find())

    return render_template(
        "browse_themes.html",
        theme_quotes=theme_quotes,
        theme_name=theme_name,
        all_comments=all_comments,
        next_page=request.full_path,
    )


@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()}
        )

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                existing_user["password"], request.form.get("password")
            ):
                session["user"] = request.form.get("username").lower()
                flash("Welcome {}".format(request.form.get("username")))

                return redirect(url_for("render_homepage"))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")

    return redirect(url_for("render_homepage"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        password = request.form.get("password")
        confirm_password = request.form.get("confirm-password")
        # passwrod must not contain whitespace
        no_white_pw = password.replace(" ", "")
        if no_white_pw == "":
            flash("Password must not contain whitespace")
            return redirect(url_for("render_homepage"))
        if no_white_pw != password:
            flash("Password must not contain whitespace")
            return redirect(url_for("render_homepage"))
        # Passwords must match
        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for("render_homepage"))
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()}
        )

        if existing_user:
            flash("Username already exists")

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password")),
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("render_homepage"))

    return redirect(url_for("render_homepage"))


@app.route("/logout")
def logout():
    # remove user from session cookie
    flash("You have been logged out")
    session.pop("user")

    return redirect(url_for("render_homepage"))


@app.route("/add_quote", methods=["GET", "POST"])
def add_quote():
    themes = mongo.db.themes.find().sort("theme", 1)
    if request.method == "POST":
        new_theme = request.form.get("new_theme", None)
        if new_theme:
            # Do not allow just whitespace
            is_new_theme = new_theme.replace(" ", "")
            if is_new_theme == "":
                flash("Please enter a theme value")
                return redirect(url_for("add_quote"))
            # Do not re add new theme to the database if it does actually exist (user error)
            is_it_new = list(mongo.db.themes.find({"theme": new_theme}))
            if len(is_it_new) == 0:
                mongo.db.themes.insert_one({"theme": new_theme.capitalize()})
        theme = new_theme or request.form.get("theme")

        # Book must not be just whitespace
        book = request.form.get("book")
        is_book = book.replace(" ", "")
        if is_book == "":
            flash("Book must have a vlaue")
            return redirect(url_for("add_quote"))

        # Quote must not be just whitespace
        is_text = request.form.get("text").replace(" ", "")
        if is_text == "":
            flash("Quote text must have a value")
            return redirect(url_for("add_quote"))

        quote = {
            "theme": theme.capitalize(),
            "book": request.form.get("book").capitalize(),
            "chapter": request.form.get("chapter"),
            "start_verse": request.form.get("start_verse"),
            "end_verse": request.form.get("end_verse"),
            "text": request.form.get("text").capitalize(),
            "added_by": session["user"],
        }

        # Prevent addition of duplicate quotes
        quote_already = list(mongo.db.quotes.find(quote))
        if len(quote_already) > 0:
            flash(
                """This quote has already been added for this theme.
                  Post a different quote."""
            )
            return redirect(url_for("add_quote"))

        mongo.db.quotes.insert_one(quote)
        flash("Quote Successfully Added")
        return redirect(url_for("my_quotes"))

    return render_template(
        "add_quote.html", themes=themes, next_page=request.full_path
    )


@app.route("/edit_quote/<quote_id>", methods=["GET", "POST"])
def edit_quote(quote_id):
    quote = mongo.db.quotes.find_one({"_id": ObjectId(quote_id)})
    themes = mongo.db.themes.find().sort("theme", 1)
    old_theme = quote["theme"]

    if request.method == "POST":
        new_theme = request.form.get("new_theme", None)

        if new_theme:
            # check if new theme is just whitespace
            is_new_theme = new_theme.replace(" ", "")
            if is_new_theme == "":
                flash("Please enter a theme value")
                return render_template(
                    "edit_quote.html", quote=quote, themes=themes
                )
            # Check if new theme added is actually new and if not don't readd 
            # to database
            is_it_new = list(mongo.db.themes.find({"theme": new_theme}))
            if len(is_it_new) == 0:
                mongo.db.themes.insert_one({"theme": new_theme.capitalize()})

        theme = new_theme.capitalize() or request.form.get("theme")

        # Book must not be just whitespace
        book = request.form.get("book")
        is_book = book.replace(" ", "")
        if is_book == "":
            flash("Book must have a vlaue")
            return render_template(
                "edit_quote.html", quote=quote, themes=themes
            )

        # Quote text must not be just whitespace
        is_text = request.form.get("text").replace(" ", "")
        if is_text == "":
            flash("Quote text must have a value")
            return render_template(
                "edit_quote.html", quote=quote, themes=themes
            )

        submit = {
            "theme": theme.capitalize(),
            "book": request.form.get("book").capitalize(),
            "chapter": request.form.get("chapter"),
            "start_verse": request.form.get("start_verse"),
            "end_verse": request.form.get("end_verse"),
            "text": request.form.get("text").capitalize(),
            "added_by": session["user"],
        }

        # Prevent addition of duplicate quotes
        quote_already = list(mongo.db.quotes.find(submit))
        if len(quote_already) > 0:
            flash("""The edited quote already exists for this theme.""")
            return render_template(
                "edit_quote.html", quote=quote, themes=themes
            )

        mongo.db.quotes.update({"_id": ObjectId(quote_id)}, submit)
        flash("Quote Successfully Updated")
        # Check if there are any more quotes with the same theme
        # as the theme that has been changed.  GET OLD THEME  If not, delete
        # the old theme from the themes collection.
        old_theme_quotes = list(mongo.db.quotes.find({"theme": old_theme}))
        if len(old_theme_quotes) == 0:
            mongo.db.themes.remove({"theme": old_theme})

        return redirect(url_for("my_quotes"))

    return render_template("edit_quote.html", quote=quote, themes=themes)


@app.route("/my_quotes")
def my_quotes():
    my_quotes = list(mongo.db.quotes.find({"added_by": session["user"]}))
    for quote in my_quotes:
        quote["id"] = str(quote["_id"])

    all_comments = list(mongo.db.comments.find())

    return render_template(
        "my_quotes.html",
        my_quotes=my_quotes,
        all_comments=all_comments,
        next_page=request.full_path,
    )


@app.route("/comment/<quote_id>", methods=["POST"])
def comment(quote_id):
    redirect_url = request.args.get("next", url_for("my_comments"))

    comment_input = request.form.get("comment")
    # check if comment has whitespace
    is_comment_input = comment_input.replace(" ", "")
    if is_comment_input == "":
        flash("Comment must have a value")

        return redirect(redirect_url)

    comment = {
        "comment": comment_input.capitalize(),
        "quote_id": quote_id,
        "comment_by": session["user"],
    }

    # check if user has already made this comment and prevent
    # duplication if so
    comment_already = list(mongo.db.comments.find(comment))
    if len(comment_already) > 0:
        flash(
            """You have already made this comment for
                this quote previously"""
        )
        return redirect(redirect_url)

    mongo.db.comments.insert_one(comment)
    flash("Thanks for commenting")

    return redirect(redirect_url)


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

    return redirect(url_for("my_quotes"))


@app.route("/my_comments")
def my_comments():

    all_quotes = list(mongo.db.quotes.find())
    my_comments = list(mongo.db.comments.find())

    commented_quotes = []

    for quote in all_quotes:
        d = {"quote": quote, "comments": []}

        for comment in my_comments:
            if comment["quote_id"] == str(quote["_id"]):
                d["comments"].append(comment)

        if len(d["comments"]) > 0:
            commented_quotes.append(d)

    return render_template(
        "my_comments.html",
        commented_quotes=commented_quotes,
        next_page=request.full_path,
    )


@app.route("/edit_comment/<quote_id>, <comment_id>", methods=["GET", "POST"])
def edit_comment(quote_id, comment_id):
    if request.method == "POST":
        edited_comment = request.form.get("edit_comment")
        # Prevent comment that is only whitespace
        is_edited_comment = edited_comment.replace(" ", "")
        if is_edited_comment == "":
            flash("Edited comment must have a value")
            return redirect(url_for("my_comments"))

        submit = {
            "comment": edited_comment.capitalize(),
            "quote_id": quote_id,
            "comment_by": session["user"],
        }

        # check if user has already made this comment and prevent
        # duplication if so
        comment_already = list(mongo.db.comments.find(submit))
        if len(comment_already) > 0:
            flash(
                """You have already made this edited comment
                  for this quote previously"""
            )
            return redirect(url_for("my_comments"))

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

    return render_template(
        "admin.html",
        all_quotes=all_quotes,
        all_comments=all_comments,
        next_page=request.full_path,
    )


if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP"), port=int(os.environ.get("PORT")), debug=True
    )
