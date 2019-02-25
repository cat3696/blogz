from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
# Imports for timestamps and password hashing utilities.
from datetime import datetime
from hashutils import make_pw_hash, check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogzword@localhost:3306/blogz'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key = 'as8d7f98a!@qw546era#$#@$'
db = SQLAlchemy(app)


class Blog(db.Model):
#amend to add owner_id
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(400))
    body = db.Column(db.String(2000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    pub_date = db.Column(db.DateTime)
#amend blog constructor  to take user object 
    def __init__(self, title, body, owner, pub_date=None):
        self.title = title
        self.body = body
        self.owner = owner
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date

 #Create user class with id, username, password, blogs
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    username = db.Column(db.String(60), unique=True)
    password = db.Column(db.String(85))
    blogs = db.relationship('Blog',backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = make_pw_hash(password)
 # Required so that user is allowed to visit specific routes prior to logging in.
# Redirects to login  once encountering a page without permission.
@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'home']
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

        if user and check_pw_hash(password, user.password):
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
    username_error = ""
    password_error = ""
    verify_error = ""
    if request.method == 'POST':

        user_name = request.form['username']
        user_password = request.form['password']
        user_password_validate = request.form['verify']

        if not user_name or not user_password or not user_password_validate:
            print('All fields must be filled in', 'error')
            return render_template('signup.html', username_error= "Incorrect username or username doesn't meet 3 character requirement.")

        if user_password != user_password_validate:
            return render_template('signup.html', verify_error= "Passwords must match.")

        if len(user_password) < 3 and len(user_name) < 3:
           
            return render_template('signup.html', password_error = "Password must be at least 3 characters.")

        if len(user_password) < 3:
           return render_template('signup.html', password_error = "Password must be at least 3 characters.")

        if len(user_name) < 3:
           return render_template('signup.html', username_error= "Incorrect username or username doesn't meet 3 character requirement.")
            
        existing_user = User.query.filter_by(username=user_name).first()

        if not existing_user: 
            # creating a new user
            user_new = User(user_name, user_password) 
            # adds new user
            db.session.add(user_new)
            # commits new objects to the database
            db.session.commit()
            # adds username to this session so they will stay logged in
            session['username'] = user_name
            print('New user created', 'success')
            return redirect('/newpost')
        else:
            print('Error, there is an existing user with the same username', 'error')
            return render_template('signup.html')
    else:
            return render_template('signup.html')


  #return render_template('signup.html')
# Required so that user is allowed to visit specific routes prior to logging in.
# Redirects to login page once encountering a page without permission.

@app.route('/blog', methods=['POST', 'GET'])
def show_blog():
    blog_id = request.args.get('id')
    user_id = request.args.get('userid')
    # posts = Blog.query.all()
    # Recent blog posts order to top.
    posts = Blog.query.order_by(Blog.pub_date.desc())

    if blog_id:
        post = Blog.query.filter_by(id=blog_id).first()
        return render_template("single_post.html", title=post.title, body=post.body, user=post.owner.username, pub_date=post.pub_date, user_id=post.owner_id)
    if user_id:
        entries = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('user.html', entries=entries)

    return render_template('blog.html', posts=posts)

    
@app.route('/newpost', methods=['POST', 'GET'])
def create_new_post():
    if request.method == 'GET':
        return render_template('newpost.html', title="New Entry")

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()
        new_blog = Blog(blog_title, blog_body, owner)


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
            blog = Blog.query.all()
            return render_template('newpost.html', title="Build a Blog", blog=blog,
                blog_title=blog_title, title_error=title_error, 
                blog_body=blog_body, body_error=body_error)
# Logout - deletes current user session, redirects to index.
@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

if __name__ == '__main__':
    app.run()