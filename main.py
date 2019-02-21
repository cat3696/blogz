from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
# Imports for timestamps and password hashing utilities.
from datetime import datetime
from hashutils import make_pw_hash, check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogzword@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):
#amend to add owner_id
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(400))
    body = db.Column(db.String(2000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    pub_date = db.Column(db.DateTime)
#amend blog constructor  to take user object 
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner
    if pub_date = dtatetime.utc.now()
    self.pub_date = pub_date

#Create user class with id, username, password, blogs
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    username = db.Column(db.String(60), unique=True)
    password = db.Column(db.String(85))
    blogs = db.relationship('blog',backref='owner')

    def _init_(self, username, password):
        self.usernme = username
        self.pw_hash = make_pw_hash(password)
 
 # Required so that user is allowed to visit specific routes prior to logging in.
# Redirects to login page once encountering a page without permission.
@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'home', 'static']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    #blogs = Blog.query.all()
    #return render_template('blog.html', title="Build a Blog", blogs=blogs)
    users = User.query.all()
    return render_template('home.html', users=users)

# Create login route - validation and verification of user information in database.
@app.route('/login', methods=['POST','GET'])
def login():
    username_error = ""
    password_error = ""

    if request.method == 'POST':
        password = request.form['password']
        username = request.form['username']
        user = User.query.filter_by(username=username).first()

        if user and check_pw_hash(password, user.pw_hash):
            session['username'] = username
            return redirect('/newpost')
        if not user:
            return render_template('login.html', username_error="Username does not exist.")
        else:
            return render_template('login.html', password_error="Your username or password was incorrect.")

    return render_template('login.html')

# Creat signup route - validation and verification of input.
@app.route("/signup", methods=['POST', 'GET'])
def signup():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            verify = request.form['verify']
            exist = User.query.filter_by(username=username).first()

            username_error = ""
            password_error = ""
            verify_error = ""

        if username == "":
            username_error = "Please enter a username."
        elif len(username) <= 3 or len(username) > 20:
            username_error = "Username must be between 3 and 20 characters long."
        elif " " in username:
            username_error = "Username cannot contain any spaces."
        if password == "":
            password_error = "Please enter a password."
        elif len(password) <= 3:
            password_error = "Password must be greater than 3 characters long."
        elif " " in password:
            password_error = "Password cannot contain any spaces."
        if password != verify or verify == "":
            verify_error = "Passwords do not match."
        if exist:
            username_error = "Username already taken."
        # If fields are good, continue to creating session with new username and password.
        if len(username) > 3 and len(password) > 3 and password == verify and not exist:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        else:
            return render_template('signup.html',
            username=username,
            username_error=username_error,
            password_error=password_error,
            verify_error=verify_error
            )

    return render_template('signup.html')
# Required so that user is allowed to visit specific routes prior to logging in.
# Redirects to login page once encountering a page without permission.

@app.route('/blog', methods=['POST', 'GET'])
def show_blog():
    
    if request.args:
        blog_id = request.args.get('id')
        blogs = Blog.query.filter_by(id=blog_id).all()
        return render_template('single_post.html', blogs=blogs)

    else:
        blogs = Blog.query.all()
        return render_template('blog.html', title="Build a Blog", blogs=blogs)

    
@app.route('/newpost', methods=['POST', 'GET'])
def create_new_post():
    if request.method == 'GET':
        return render_template('new_post.html', title="New Entry")

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        new_blog = Blog(blog_title, blog_body)
        owner = user.query.filter_by(username=session['username']).first()

        title_error = ''
        body_error = ''

        if len(blog_title) == 0:
            title_error = "Every entry needs a title, Love!"
        if len(blog_body) == 0:
            body_error = "Please write your post."

        if not title_error and not body_error:
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id={0}'.format(new_blog.id))
        
        else:
            blogs = Blog.query.all()
            return render_template('new_post.html', title="Build a Blog", blogs=blogs,
                blog_title=blog_title, title_error=title_error, 
                blog_body=blog_body, body_error=body_error)
# Logout - deletes current user session, redirects to index.
@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

if __name__ == '__main__':
    app.run()