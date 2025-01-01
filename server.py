from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import datetime
import smtplib
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date
import os
from dotenv import load_dotenv

load_dotenv()
# Load environment variables
my_email = os.getenv('my_email')
my_password = os.getenv('password')


app = Flask(__name__)
ckeditor = CKEditor(app)
app.config['CKEDITOR_CONFIG'] = {'toolbar': 'Full',
                                 'height': 500}
csrf = CSRFProtect(app)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
Bootstrap5(app)


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'

db = SQLAlchemy(model_class=Base)
db.init_app(app)

# create database model
class BlogPost(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

class Addblog(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


@app.route('/')
def index():
    # Query the database for all the posts. Convert the data to a python list.
    result = db.session.execute(db.select(BlogPost))
    post = result.scalars().all()
    current_year = datetime.datetime.now().year
    return render_template('index.html', post=post, year=current_year)



@app.route("/post/<int:post_id>")  # Route to display all posts
def show_post(post_id):
    # Retrieve a BlogPost from the database based on the post_id
    requested_post = db.get_or_404(BlogPost, post_id)
    current_year = datetime.datetime.now().year
    return render_template("post.html", post=requested_post, year=current_year)




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


# route for adding a new blog post
@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    current_year = datetime.datetime.now().year
    form = Addblog()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=form.author.data,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_post.html', form=form, year=current_year)

# route for editing a blog post
@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    current_year = datetime.datetime.now().year
    post = db.get_or_404(BlogPost, post_id)
    form = Addblog(obj=post)
    if form.validate_on_submit():
        post.title = form.title.data
        post.subtitle = form.subtitle.data
        post.body = form.body.data
        post.img_url = form.img_url.data
        post.author = form.author.data
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_post.html', form=form, post=post, year=current_year)

# route for deleting a blog post
@app.route('/delete_post/<int:post_id>', methods=['GET', 'POST'])
def delete_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)


