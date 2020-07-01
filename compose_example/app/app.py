import os
from flask import Flask, render_template, request, url_for, redirect
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient('mongodb://mongo:27017/')
db = client.book_db
books = db.books

@app.route('/')
def list_games():
    all_books = books.find()

    return render_template('base.html', books=all_books)

@app.route('/create', methods=['POST'])
def create_game():
    new_book = {
        'title': request.form['title'],
        'author': request.form['author']
    }

    books.insert_one(new_book)

    return redirect(url_for('list_games'))

if __name__ == '__main__':
    debug = os.environ.get('DEBUG', False)
    app.run(debug=debug, host='0.0.0.0')
