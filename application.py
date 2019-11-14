#!/usr/bin/python3

import os

from flask import Flask, session, render_template, request, redirect, url_for, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


app = Flask(__name__)
app.secret_key = '301289'

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/login", methods=['GET', 'POST'])
def login_page():
    if request.method == 'GET':
        return render_template("login.html")
    
    if request.method == 'POST':
        uname = request.form.get("username")
        pswd = request.form.get("password")
        validate_username = "Select * from users where username=:uname"
        validate_user = "Select * from users where username=:uname and password=:pswd"

        if (uname or pswd) is "":
            return render_template("login.html", message="Username/Password can not be empty, both fields are required to login.")
    
        if db.execute(validate_username, {"uname":uname}).rowcount == 0:
            return render_template("login.html", message="Invalid username. Please provide correct credentials to login.")
    
        if db.execute(validate_user, {"uname":uname, "pswd":pswd}).rowcount == 0:
            return render_template("login.html", message="Invalid password. Please provide correct credentials to login.")
        
        session['username'] = uname
        return redirect(url_for('books'))

@app.route("/logout")
def logout():
    session.pop('username', None)
    return render_template('index.html')

@app.route("/user-registration", methods=["GET","POST"])
def registration():
    if request.method == "GET":
        return render_template("error.html", message="Please go to home page to register or login.")

    # Reusable queries
    username_check_query = "Select * from users where username = :uname"
    register_query = "Insert into users (username, password, email) values(:uname,:pswd,:emailId)"

    # Get information from the register form
    uname = request.form.get("username")
    pswd = request.form.get("password")
    emailId = request.form.get("email")

    if (uname or pswd) is "":
        return render_template("error.html", message="Username/Password can not be empty")

    if len(pswd) < 6:
        return render_template("error.html", message="Password length should be minimum 6 characters.")

    if db.execute(username_check_query, {"uname": uname}).rowcount == 0:
        db.execute(register_query, {"uname":uname, "pswd":pswd, "emailId": emailId})
        db.commit()
        return render_template("login.html", message="Successfully registered. Login to read or submit book reviews.")
    else:
        flash("Username already exists!")
        return render_template("error.html", message="Username already exists. Please try a different username.") 

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query:
        flash("You did not search for anything")
        return redirect(url_for('books'))
    elif query:
        q = '%'+ query +'%'
        dbQuery = db.execute('select * from book where title ilike :query or isbn ilike :query or author ilike :query order by id limit 10', {"query": q})
        res = dbQuery.fetchall()
    return render_template('search.html', books=res)

@app.route("/books")
def books():
    if 'username' in session:
        uname = session['username']
        books = db.execute("Select * from book").fetchall()
        return render_template("books.html", books=books, message="Welcome "+ uname)

    return render_template('error.html', message="Please login to access books.")

@app.route("/book/<int:book_id>")
def book(book_id):
    if 'username' in session:
        uname = session['username']
        book = db.execute("select * from book where id=:id",{"id":book_id}).fetchone()
        if book is None:
            return render_template("error.html", message="Book ID doesn't exist.")
        return render_template("book.html", book=book)
    return render_template('error.html', message="Please login to access books.")

# @app.route("/user/<int:user_id>")
# def profile(user_id):
#     pass

# def main():
#     books = db.execute("select * from book where title ilike '%woman%';").fetchall()
#     for book in books:
#         print(f"{book.title}")