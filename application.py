#!/usr/bin/python3

import os

from flask import Flask, session, render_template, request, redirect, url_for, flash, jsonify
import requests
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from unicodedata import normalize
from datetime import datetime
import pprint
import random


app = Flask(__name__)
app.secret_key = '301289'
app.static_folder = 'static'

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
    message = ""
    if not query:
        flash("You did not search for anything")
        return redirect(url_for('books'))
    elif query:
        q = '%'+ query +'%'
        dbQuery = db.execute('select * from book where title ilike :query or isbn ilike :query or author ilike :query order by id limit 10', {"query": q})
        res = dbQuery.fetchall()
    if len(res)==0:
        message = "No books matching this query!"
    return render_template('search.html', books=res, message=message)

@app.route("/books")
def books():
    if 'username' in session:
        uname = session['username']
        books = db.execute("Select * from book").fetchall()
        x = random.randrange(0,5001,12)
        return render_template("books.html", books=books, message="Welcome "+ uname.capitalize(), num=x)

    return render_template('error.html', message="Please login to access books.")

@app.route("/book/<int:book_id>", methods=['GET', 'POST'])
def book(book_id):
    review_insert_query = "Insert into reviews (reviewer_id, book_isbn, rating, review_comment) values(:user_id, :book_isbn, :rating, :book_review)"
    reviews = []
    if 'username' in session:
        uname = session['username']
        book = db.execute("select * from book where id=:id",{"id":book_id}).fetchone()

        if book is None:
            return render_template("error.html", message="Book ID doesn't exist.")

        user_id = db.execute("select user_id from users where username=:uname",{"uname":uname}).fetchone()
        isbn = db.execute("select isbn from book where id=:id",{"id":book_id}).fetchone()

        for item in isbn:
            book_isbn = str(item)

        for item in user_id:
            user_id = str(item)

        book_review = str(request.form.get('review'))
        book_rating = request.form.get('rating')

        # Get good reads data
        data = [0, 0]
        try:
            goodreads_data = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "K0pOqH7V3rc9YKReYXz40g", "isbns": isbn}, timeout=3.05)
            response = goodreads_data.json()
            avg_rating = response["books"][0]["average_rating"]
            review_count = response["books"][0]["work_ratings_count"]
            data=[avg_rating,review_count]
        except Exception as e:
            print(e.message)

        # Getting details of reviews on the book
        reviews = db.execute("select * from reviews where book_isbn=:book_isbn", {"book_isbn":book_isbn}).fetchall()

        # Submitting the review
        if request.method == 'POST':
            try:
                if int(book_rating) == 0:
                    return render_template("book.html", book=book, reviews=reviews, data=data, message="Please select proper rating for submitting your review.")
                else:
                    db.execute(review_insert_query,{"user_id":int(user_id),"book_isbn":book_isbn, "rating": int(book_rating), "book_review":book_review})
                    db.commit()
            except Exception as e:
                return render_template('error.html', message="You can not submit more than one review on a book.")

        reviews = db.execute("select * from reviews where book_isbn=:book_isbn", {"book_isbn":book_isbn}).fetchall()
        return render_template("book.html", book=book, reviews=reviews, data=data)

    return render_template('error.html', message="Please login to access books.")

@app.route("/api/<string:book_isbn>")
def book_api(book_isbn):
      """Return details about a single flight."""

      # Make sure flight exists.
      book = db.execute("select * from book where isbn=:isbn",{"isbn":book_isbn}).fetchone()
      if book is None:
          return jsonify({"error": "Invalid Book ISBN"}), 404

      # Get all details from book.
      book_isbn = book.isbn
      reviews = db.execute("select * from reviews where book_isbn=:book_isbn", {"book_isbn":book_isbn}).fetchall()
      review_count = len(reviews)
      comments = []
      average_rating = 0.0
      for review in reviews:
          comments.append(review.review_comment)
          average_rating += review.rating

      if review_count > 0:
          average_rating /= review_count
      else:
          average_rating = 0.0

      return jsonify({
              "title": book.title,
              "author": book.author,
              "year": book.year,
              "isbn": book_isbn,
              "review_count": review_count,
              "average_score": average_rating
            })

# @app.route("/user/<int:user_id>")
# def profile(user_id):
#     pass

# def main():
#     books = db.execute("select * from book where title ilike '%woman%';").fetchall()
#     for book in books:
#         print(f"{book.title}")
