from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
import datetime
from flask_login import LoginManager


# Delete this code:
# import requests
# posts = requests.get("https://api.npoint.io/43644ec4f0013682fc0d").json()

login_manager = LoginManager()
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    # Run only the first time to set up the table
    # db.create_all()
    # db.session.commit()

# CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


# WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField('Body', validators=[DataRequired()])
    # body = StringField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


class RegistrationForm(FlaskForm):
    id = db.Column(db.Integer, primary_key=True)
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password = StringField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")


@app.route('/register', methods=["GET", "POST"])
def register():
    users = db.session.query(Users).all()
    form = RegistrationForm()
    if request.method == "POST":
        new_user = Users(
            username=request.form['username'],
            email=request.form['email'],
            password=request.form['password'],
        )
        print(new_user.id, new_user.username, new_user.email, new_user.password)
        db.session.add(new_user)
        db.session.commit()
        message = "You're now registered!"
        return redirect(url_for('register', message=message))
    return render_template('registration.html', form=form, users=users)


@app.route('/author', methods=["GET"])
def author_profile(author_id):
    print(author_id)
    return render_template('author.html', author=author_id)


@app.route('/', methods=["GET"])
def get_all_posts():
    users = db.session.query(Users).all()
    posts = db.session.query(BlogPost).all()
    return render_template("index.html", all_posts=posts, users=users)


@app.route("/post/<int:index>")
def show_post(index):
    requested_post = BlogPost.query.get(index)
    return render_template("post.html", post=requested_post, post_id=index)


@app.route("/new-post", methods=["GET", "POST"])
def new_post():
    new_blog_post_form = CreatePostForm()
    if request.method == "POST":
        new_blog_post = BlogPost(
            title=request.form['title'],
            subtitle=request.form['subtitle'],
            author=request.form['author'],
            img_url=request.form['img_url'],
            body=request.form['body'],
            date=datetime.datetime.now().strftime("%A %d %B %Y %H:%M"),
        )
        db.session.add(new_blog_post)
        db.session.commit()
        print(new_post)
        return redirect(url_for('get_all_posts'))
    return render_template('make-post.html', form=new_blog_post_form)


@app.route('/<int:post_id>', methods=["GET", "POST"])
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        body=post.body,
        author=post.author,
        img_url=post.img_url,
    )
    if request.method == "POST":
        print("validated!!!!!")
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.author = edit_form.author.data
        post.img_url = edit_form.img_url.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for('show_post', index=post.id))
    return render_template("edit.html", form=edit_form)


@app.route('/delete/<post_id>')
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True)


