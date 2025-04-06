from flask import Flask, render_template, request, redirect, url_for, flash, abort
# import requests
import datetime
import smtplib
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text
from flask_wtf import FlaskForm, CSRFProtect
from flask_ckeditor import CKEditor, CKEditorField
# from flask_gravatar import Gravatar
from datetime import date
import os
from dotenv import load_dotenv
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm, Addblog, CommentForm
from functools import wraps



load_dotenv()
# Load environment variables
my_email = os.getenv('my_email')
my_password = os.getenv('password')


app = Flask(__name__)
ckeditor = CKEditor(app)
app.config['CKEDITOR_CONFIG'] = {'toolbar': 'Full',
                                 'height': 500}
login_manager = LoginManager()
login_manager.init_app(app)
csrf = CSRFProtect(app)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
Bootstrap5(app)


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
# app.config['SQLALCHEMY_BINDS'] = {'users': 'sqlite:///users.db'}



db = SQLAlchemy(model_class=Base)
db.init_app(app)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))
    posts = db.relationship("BlogPost", back_populates="author")
    comments = db.relationship("Comment", back_populates="user", cascade="all, delete-orphan")


class Comment(db.Model):
    __tablename__ = 'comments'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('users.id'))
    text: Mapped[str] = mapped_column(Text, nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    post_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('blog_posts.id'))
    posts = db.relationship("BlogPost", back_populates="comments")
    user = db.relationship("User", back_populates="comments")


# create database model
class BlogPost(db.Model):
    __tablename__ = 'blog_posts'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('users.name'))
    author = relationship("User", back_populates="posts")
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    comments = relationship("Comment", back_populates="posts")


with app.app_context():
    db.create_all()  # Create the database tables


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

# gravatar = Gravatar(app,
#                     size=100,
#                     rating='g',
#                     default='retro',
#                     force_default=False,
#                     force_lower=False,
#                     use_ssl=False,
#                     base_url=None)


@app.route('/')
def index():
    # Query the database for all the posts. Convert the data to a python list.
    posts = BlogPost.query.all()
    # post = db.session.execute(db.select(BlogPost)).scalars().all()
    current_year = datetime.datetime.now().year
    return render_template('index.html', post=posts, year=current_year)


@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    current_year = datetime.datetime.now().year
    comment_form = CommentForm()

    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to log in to comment.")
            return redirect(url_for('login'))

        user = User.query.get(current_user.id)
        new_comment = Comment(
            author_id=current_user.id,
            text=comment_form.body.data,
            post_id=post_id,
            date=date.today().strftime("%B %d, %Y"),
            user=user
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('show_post', post_id=post_id))

    # Get comments with user data in a single query
    comments = (
        db.session.query(Comment, User)
        .join(User, Comment.author_id == User.id)
        .filter(Comment.post_id == post_id)
        .all()
    )
    return render_template("post.html", post=requested_post, year=current_year, form=comment_form, comments=comments)


@app.route('/register', methods=['GET', 'POST'])
def register():
    current_year = datetime.datetime.now().year
    register_form = RegisterForm()
    if request.method == 'POST':
        if register_form.validate_on_submit():
            # Check if the user already exists in the database
            existing_user = User.query.filter_by(email=register_form.email.data).first()
            existing_user_name = User.query.filter_by(name=register_form.name.data).first()
            if existing_user or existing_user_name:
                # User already exists, show an error message
                flash("User already exists. Please log in.")
                error_message = "User already exists. Please log in."  # Error message
                return render_template('register.html', form=register_form, year=current_year, error=error_message)
            else:
                # Create a new user and add it to the database
                new_user = User(
                    name=register_form.name.data,
                    email=register_form.email.data,
                    password=generate_password_hash(register_form.password.data, method='pbkdf2:sha256', salt_length=8)
                )
                db.session.add(new_user)
                db.session.commit()
                # Log in the user after successful registration
                login_user(new_user)
                return redirect(url_for('index'))
        # else:
        #     error_message = "All fields are required."  # Error message
        #     return render_template('register.html', form=register_form, year=current_year, error=error_message)
    return render_template('register.html', form=register_form, year=current_year)


@app.route('/login', methods=['GET', 'POST'])
def login():
    current_year = datetime.datetime.now().year
    login_form = LoginForm()
    if request.method == 'POST':
        if login_form.validate_on_submit():
            # Check if the user exists in the database
            user = db.session.execute(db.select(User).where(User.email == login_form.email.data)).scalar()
            if user:
                # Check if the password is correct
                if check_password_hash(user.password, login_form.password.data):
                    login_user(user)
                    return redirect(url_for('index'))
                else:
                    flash("Incorrect password. Please try again.")
                    error_message = "Incorrect password. Please try again."  # Error message
                    return render_template('login.html', form=login_form, year=current_year, error=error_message)
            else:
                register_link = url_for('register')
                flash(f"<span style='color:red;'>User does not exist. Please </span><a class='registered-link' href='{register_link}'><span style='color:blue; font-weight:bold;'>register</span></a>")
                error_message = "User does not exist. Please register."  # Error message
                return render_template('login.html', form=login_form, year=current_year, error=error_message)
        else:
            flash("All fields are required.")
            error_message = "All fields are required."  # Error message
            return render_template('login.html', form=login_form, year=current_year, error=error_message)
    return render_template('login.html', form=login_form, year=current_year)


@app.route('/about')
def about():
    current_year = datetime.datetime.now().year
    return render_template('about.html', year=current_year)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    current_year = datetime.datetime.now().year
    if request.method == 'POST':
        name = request.form['name']  # Use .get() to avoid KeyError
        email = request.form['email']
        phone = request.form['phone']
        message = request.form['message']

        if name and phone and email and message:  # Check if required fields have data
            # # send email to myself
            # wire_message = f"Name: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {message}"
            # with smtplib.SMTP('smtp.gmail.com', 587) as connection:
            #     connection.starttls()
            #     connection.login(user=my_email, password=my_password)
            #     connection.sendmail(from_addr='my_email',
            #                         to_addrs='jekuthielnnamdi@yahoo.com',
            #                         msg=f"Subject:A visitor from my blog\n\n{wire_message}")

            # ... (your code to send email or store data)
            return render_template('contact.html', year=current_year, msg_sent=True)

        else:
            error_message = "All fields are required."  # Error message
            return render_template('contact.html', year=current_year, msg_sent=False, error=error_message)
    return render_template('contact.html', year=current_year, msg_sent=False)


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and current_user.id == 1:
            return f(*args, **kwargs)
        else:
            return abort(403) #redirect(url_for('index'))
    return decorated_function



# route for adding a new blog post
@app.route('/add_post', methods=['GET', 'POST'])
@login_required
@admin_only
def add_post():
    current_year = datetime.datetime.now().year
    form = Addblog()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_post.html', form=form, year=current_year)


# route for editing a blog post
@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
@admin_only
def edit_post(post_id):
    current_year = datetime.datetime.now().year
    post = db.get_or_404(BlogPost, post_id)
    form = Addblog(obj=post)
    if form.validate_on_submit():
        post.title = form.title.data
        post.subtitle = form.subtitle.data
        post.body = form.body.data
        post.img_url = form.img_url.data
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_post.html', form=form, post=post, year=current_year)

# route for deleting a blog post
@app.route('/delete_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
@admin_only
def delete_post(post_id):
    post = db.get_or_404(BlogPost, post_id, description="Post not found")  # Check if post exists
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
