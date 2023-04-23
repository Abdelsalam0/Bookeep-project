from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests
import ast
from forms import LoginForm, RegisterForm, BookForm



app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.app_context().push()
db = SQLAlchemy(app)
Bootstrap(app)


class Book(UserMixin, db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250))
    author = db.Column(db.String(250))
    description = db.Column(db.String(250))
    page_count = db.Column(db.String)
    category = db.Column(db.String(250))

    img_url = db.Column(db.String(250))


class User(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250))
    password = db.Column(db.String(250))
    name = db.Column(db.String(250))
    books = relationship('Book', secondary='user_books', backref='users') # this is like a list of books related to the user


user_books = db.Table(
    'user_books',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('book_id', db.Integer, db.ForeignKey('books.id'))
)


db.create_all()


login_manager = LoginManager()
login_manager.init_app(app)


def search_books(query):
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": query,
        "maxResults": 40,
        "printType": "books"
    }
    response = requests.get(url, params=params)
    data = response.json()
    books = []

    for item in data["items"]:
        book = {
            "title": item["volumeInfo"].get("title"),
            "authors": item["volumeInfo"].get("authors"),
            "description": item["volumeInfo"].get("description"),
            "category": item["volumeInfo"].get('categories'),
            'pages': item["volumeInfo"].get('pageCount'),
            "thumbnail": item["volumeInfo"].get("imageLinks", {}).get("thumbnail", "")
        }
        books.append(book)

    return books


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(int(user_id))


@app.route("/", methods=["GET", "POST"])
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    else:
        return redirect(url_for('profile'))


@app.route('/selectbooks', methods=['GET', "POST"])
@login_required
def select():
    if request.method == 'POST':
        books_selected = request.form.getlist('books')
        books_selected = [ast.literal_eval(book) for book in books_selected]

        for book in books_selected:

            title = str(book.get('title'))
            author = book.get('authors')[0]
            description = str(book.get('description'))
            page_count = book.get('pages')
            if book.get('category') is None:
                category = 'None'
            else:
                category = book.get('category')[0]

            img_url = book.get('thumbnail')
            new_book = Book(
                title=title,
                author=author,
                description=description,
                page_count=page_count,
                category=category,
                img_url=img_url
            )
            current_user.books.append(new_book)
            db.session.add(new_book)
            db.session.commit()
        return redirect(url_for('profile', user_id=current_user.id, current_user=current_user))


@app.route('/bookdetails')
def bookdetails():
    book_id = request.args.get('id')
    book = Book.query.get(book_id)
    return render_template('bookdetails.html', book=book)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = generate_password_hash(password=form.password.data,salt_length=8)


        new_user = User(
            name=name,
            email=email,
            password=password
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = db.session.query(User).filter_by(email=email).first()
        print(user.id)
        if user and check_password_hash(user.password, password=password):
            login_user(user)
            return redirect(url_for('profile'))

    return render_template('login.html', form=form, current_user=current_user)


@app.route('/profile/', methods=['GET', 'POST'])
@login_required
def profile():
    # user = db.session.query(User).filter_by(id=user_id).first()
    books = current_user.books
    print(type(current_user))
    num_books = len(books)
    form = BookForm()
    if form.validate_on_submit():
        query = form.title.data
        books = search_books(query)

        return render_template("selectbooks.html", books=books)

    return render_template('profile.html', books=books, form=form, num_books=num_books, current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/delete', methods=['GET', 'POST'])
def delete():
    selected_books = request.form.getlist('books')
    selected_books = [ast.literal_eval(book) for book in selected_books]
    print(selected_books)
    if request.method == 'POST':
        for i in selected_books:
            book_id = i
            book_to_delete = Book.query.get(book_id)
            db.session.delete(book_to_delete)
            db.session.commit()
    return redirect(url_for('profile',  current_user=current_user))


if __name__ == "__main__":
    app.run(debug=True)