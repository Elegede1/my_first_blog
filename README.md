# my_first_blog

This project implements a simple blog application using Flask, a Python web framework.  It leverages several extensions for enhanced functionality and styling:

* **Flask-Bootstrap:** Provides Bootstrap integration for responsive and visually appealing design.
* **Flask-CKEditor:** Integrates CKEditor, a rich text editor, for creating and editing blog posts with formatted content.
* **Flask-SQLAlchemy:** Simplifies database interactions using SQLAlchemy, an Object-Relational Mapper (ORM).
* **Flask-WTF:** Facilitates creating and handling web forms, including form validation and CSRF protection.

## Features

* **View Blog Posts:**  Users can view a list of blog posts on the home page, with titles, subtitles, authors, and dates.
* **Read Full Posts:** Clicking on a post title leads to the full post view, displaying the complete content and an image.
* **Create New Posts:**  Authenticated users (implementation not included in this example) can create new blog posts with titles, subtitles, rich text content (using CKEditor), author names, and image URLs.
* **Edit Existing Posts:**  Similar to creating posts, authenticated users can edit existing blog posts.
* **Delete Posts:** Authenticated users can delete blog posts.
* **Contact Form:**  A contact form allows visitors to send messages to the blog owner.  (Email sending functionality needs to be configured – commented out in the example code).
* **About Page:** A simple about page.


## Installation and Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-username/myblog-clean-blog-gh-pages.git
`

Create and Activate a Virtual Environment: (Recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install Dependencies:
pip install -r requirements.txt
Set Up the Database:
Create the posts.db file.
Run the migrations.
Set Environment Variables: Create a .env file in the root directory of your project and set the following environment variables replacing placeholders with your actual values.
SECRET_KEY=YOUR_SECRET_KEY
my_email=YOUR_EMAIL
password=YOUR_EMAIL_PASSWORD
Run the Application:
flask run
Usage
Navigate to http://127.0.0.1:5000/ in your web browser to view the blog.
Use the navigation links to access different sections of the blog.
Contributing
Contributions are welcome! If you find any issues or have suggestions for improvements, feel free to open an issue or submit a pull request.
License
This project is licensed under the MIT License.