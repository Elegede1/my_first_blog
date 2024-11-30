from flask import Flask, render_template
import requests
import datetime



def get_blog_posts():
    url = "https://api.npoint.io/461fddd6b230791ec84d"
    response = requests.get(url)
    response.raise_for_status()
    all_posts = response.json()
    return all_posts


app = Flask(__name__)

@app.route('/')
def index():
    current_year = datetime.datetime.now().year
    all_posts = get_blog_posts()
    return render_template('index.html', posts=all_posts, year=current_year)


@app.route('/post/<int:post_id>')
def post(post_id):
    current_year = datetime.datetime.now().year
    all_posts = get_blog_posts()

    # find the specific post based on the post_id
    selected_post = None
    for post in all_posts:
        if post["id"] == post_id:
            selected_post = post
            break
    return render_template('post.html', post=selected_post, year=current_year)

@app.route('/about')
def about():
    current_year = datetime.datetime.now().year
    return render_template('about.html', year=current_year)

@app.route('/contact')
def contact():
    current_year = datetime.datetime.now().year
    return render_template('contact.html', year=current_year)

if __name__ == '__main__':
    app.run(debug=True)