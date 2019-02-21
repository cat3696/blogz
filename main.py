from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy


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
#amend blog constructor  to take user object 
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

#Create user class with id, username, password, blogs
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    username = db.column(db.String(60), unique=True)
    password = db.Column(db.String(85))
    blogs = db.relationship('blog',backref='owner')

    def _init_(self, username, password):
        self.usernme = username
        self.password = password
    
    def _repr_(self):
        return str(self.username) 

@app.route('/')
def index():
    blogs = Blog.query.all()
    return render_template('blog.html', title="Build a Blog", blogs=blogs)

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

if __name__ == '__main__':
    app.run()