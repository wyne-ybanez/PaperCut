import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import datetime
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_posts")
def get_posts():
    posts = list(mongo.db.posts.find())
    return render_template("posts.html", posts=posts)


@app.route("/register", methods=["GET", "POST"])
def register():
    '''
      Check if username already exists
      If it does, send user back to registration form
      If username is new, register new username into DB
      Put new user into session cookie
    '''
    if request.method == 'POST':
        existing_user = mongo.db.users.find_one(
            {'username': request.form.get('username').lower()}
        )

        if existing_user: 
            flash('Username already exists')
            return redirect(url_for('register'))
    
        register = {
            'username': request.form.get('username').lower(),
            'password': generate_password_hash(request.form.get('password'))
        }
        mongo.db.users.insert_one(register)

        session['user'] = request.form.get('username').lower()
        flash('Registration Successful!')
        return redirect(url_for('profile', username=session['user']))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    '''
    Check if username exists in db
    Check if hashed password matches with username
    '''
    if request.method == 'POST':
        existing_user = mongo.db.users.find_one(
            {'username': request.form.get('username').lower()})

        if existing_user:
            if check_password_hash(
                existing_user['password'], request.form.get('password')):
                    session['user'] = request.form.get('username').lower()
                    flash('Welcome, {}'.format(
                        request.form.get('username')))
                    return redirect(url_for(
                            "profile", username=session["user"]))
            else:
                flash('Incorrect Username and/or Password')
                return redirect(url_for("login"))

        else:
            flash('Incorrect Username and/or Password')
            return redirect(url_for("login"))

    return render_template('login.html')


@app.route('/profile/<username>', methods=['GET','POST'])
def profile(username):
    '''
    Create profile page for user
    Taking user's username from DB
    Use session cookie to identify user
    '''
    username = mongo.db.users.find_one(
        {'username': session['user']})['username']

    if session['user']:
        return render_template('profile.html', username=username)

    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    '''
    Remove User's session cookie
    '''
    flash('You have been logged out')
    session.pop('user')
    return redirect(url_for('login'))


@app.route('/add_post', methods=['GET','POST'])
def add_post():
    ''' 
    Adds a post 
    Sends Data to DB
    '''
    today = datetime.date.today()
    if request.method == 'POST':
        post = {
            'genre_name': request.form.get('genre_name'),
            'post_title': request.form.get('post_title'),
            'book': request.form.get('book'),
            'review': request.form.get('review'),
            'date': today.strftime('%d %B, %Y'),
            'created_by': session['user']
        }
        mongo.db.posts.insert_one(post)
        flash('Post Successfully Added')
        return redirect(url_for('get_posts'))

    genres = mongo.db.genres.find().sort('genre_name',1)
    return render_template('add_post.html', genres=genres)


@app.route('/show_post/<post_id>')
def show_post(post_id):
    '''
    Show post to reader
    '''
    post = mongo.db.posts.find_one({'_id': ObjectId(post_id)})
    return render_template('review.html', post=post)


@app.route('/edit_post/<post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    ''' 
    Edits Post 
    Updates Database Info
    '''
    edit_date = datetime.date.today()
    if request.method == 'POST':
        edit = {
            'genre_name': request.form.get('genre_name'),
            'post_title': request.form.get('post_title'),
            'book': request.form.get('book'),
            'review': request.form.get('review'),
            'created_by': session['user'],
            'edit_date': edit_date.strftime('%d %B, %Y')
        }
        mongo.db.posts.update({'_id': ObjectId(post_id)}, edit)
        flash('Post Successfully Updated')

    post = mongo.db.posts.find_one({'_id': ObjectId(post_id)})
    genres = mongo.db.genres.find().sort('genre_name', 1)
    return render_template('edit_post.html', post=post, genres=genres)


@app.route('/delete_post/<post_id>')
def delete_post(post_id):
    mongo.db.posts.remove({'_id': ObjectId(post_id)})
    flash('Post Deleted')
    return redirect(url_for('get_posts'))


@app.route('/dashboard')
def dashboard():
    total_users = mongo.db.users.count_documents({})
    print(total_users)
    genres = list(mongo.db.genres.find().sort('genre_name', 1))
    return render_template('dashboard.html', genres=genres, total_users=total_users)


if __name__ == '__main__':
    app.run(host=os.environ.get('IP'),
            port=int(os.environ.get('PORT')),
            debug=True)
