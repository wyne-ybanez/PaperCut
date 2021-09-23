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


@app.route('/')
@app.route('/get_posts')
def get_posts():
    """ 
    Displays Header Image.
    Displays posts onto page.
    Set posts limit to 5 per page.
    Skip determined by (page number - 1 * 5).
    Paginates page according to length of data.
    """
    # Variables
    header_img = True
    search_called = False
    POSTS_PER_PAGE = 5
    page = request.args.get('page', 1, type=int)
    SKIP_POSTS = (page - 1) * POSTS_PER_PAGE

    posts = list(mongo.db.posts.find().sort(
        'date', -1).skip(SKIP_POSTS).limit(POSTS_PER_PAGE))
    posts_data = list(mongo.db.posts.find())
    users = list(mongo.db.users.find())

    # Assign Genre Name to Genre ID
    for post in posts:
        genre_name = mongo.db.genres.find_one(
            {"_id": ObjectId(post["genre_id"])})["genre_name"]
        post['genre_name'] = genre_name

    genres = list(mongo.db.genres.find().sort('genre_name', 1))
    return render_template("index.html", posts=posts, posts_data=posts_data,
                           header_img=header_img, genres=genres, page=page, 
                           users=users, search_called=search_called)


@app.route('/search', methods=['GET', 'POST'])
def search():
    """
    Allows user to search for specific posts.
    Lets the site know when a search function
    is called to remove pagination feature.
    """
    query = request.form.get('query')
    users = list(mongo.db.users.find())
    genres = list(mongo.db.genres.find())
    posts = list(mongo.db.posts.find(
        {'$text': {'$search': query}}).sort([('date', -1), ('edit_date', -1)]))
    header_img = True
    search_called = True

    # Attach Genre name to Genre ID.
    for post in posts:
        genre_name = mongo.db.genres.find_one(
            {"_id": ObjectId(post["genre_id"])})["genre_name"]
        post['genre_name'] = genre_name

    return render_template('index.html', posts=posts, genres=genres, 
                           users=users, header_img=header_img, 
                           search_called=search_called)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Check if username already exists
    If it does, send user back to registration form
    If username is new, register new username into DB
    Put new user into session cookie
    """
    if request.method == 'POST':
        existing_user = mongo.db.users.find_one(
            {'username': request.form.get('username').lower()}
        )

        if existing_user:
            flash('Username already exists')
            return redirect(url_for('register'))

        register = {
            'username': request.form.get('username').lower(),
            'password': generate_password_hash(request.form.get('password')),
        }
        mongo.db.users.insert_one(register)

        session['user'] = request.form.get('username').lower()
        flash('Registration Successful!')
        return redirect(url_for('profile', username=session['user']))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Check if username exists in db.
    Check if hashed password matches with username.
    Flash messages to indicate successful or failed login.
    """
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
                    "profile", username=session['user']))
            else:
                flash('Incorrect Username and/or Password')
                return redirect(url_for("login"))

        else:
            flash('Incorrect Username and/or Password')
            return redirect(url_for("login"))

    return render_template('login.html')


@app.route('/search_profile/<user_id>', methods=['GET', 'POST'])
def search_profile(user_id):
    """
    Researching user and see
    their status and posts.
    """
    user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    users = list(mongo.db.users.find())
    posts = list(mongo.db.posts.find({'created_by': user['username']}))

    # Attach Genre name to Genre ID.
    for post in posts:
        genre_name = mongo.db.genres.find_one(
            {"_id": ObjectId(post["genre_id"])})["genre_name"]
        post['genre_name'] = genre_name

    return render_template("profile.html", user=user, posts=posts,
                           users=users)


@app.route('/profile/<username>', methods=['GET', 'POST'])
def profile(username):
    """
    Profile page for user.
    Taking user's username from DB.
    Use session cookie to identify user.
    """
    user = mongo.db.users.find_one({'username': session['user']})
    posts = mongo.db.posts.find({'created_by': user['username']})
    users = list(mongo.db.users.find())
    if session['user']:
        return render_template("profile.html", user=user, 
                               posts=posts, users=users)
    return redirect(url_for('login'))


@app.route('/edit_profile/<user_id>', methods=['GET', 'POST'])
def edit_profile(user_id):
    """
    Allows users to edit their profiles.
    Allows users to add bios to profile.
    """
    if request.method == 'POST':
        edit = request.form.get('status')
        avatar = request.form.get('avatar')
        mongo.db.users.update({'_id': ObjectId(user_id)}, {
                              '$set': {'status': edit, 'avatar': avatar}})
        flash('Profile Successfully Updated')

    username = mongo.db.users.find_one({'username': session['user']})
    user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
    return render_template('edit_profile.html', user=user, username=username)


@app.route('/delete_profile/<user_id>')
def delete_profile(user_id):
    """
    Deletes Profile and user's posts from db.
    Logs User out after account deletion.
    Keeps admin logged in.
    """
    mongo.db.users.remove({'_id': ObjectId(user_id)})
    admin_user = mongo.db.users.find_one({'admin': 'true'})
    user = session['user']
    posts = mongo.db.posts.find()

    # Delete User's posts after account deletion
    for post in posts:
        if post['created_by'] == user:
            mongo.db.posts.remove({'created_by': session['user']})
            flash('Account Successfully Deleted')
            return redirect(url_for('logout'))
        elif user == 'admin':
            flash('User Successfully Deleted')
            return redirect(url_for('get_posts'))

    if admin_user:
        flash('User Successfully Deleted')
        return redirect(url_for('get_posts'))
    return redirect(url_for('logout'))


@app.route('/logout')
def logout():
    """
    Remove User's session cookie
    """
    flash('You have been logged out')
    session.pop('user')
    return redirect(url_for('login'))


@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    """ Allows registered user to add a post. A flash message
    is shown if the post is successful. Inserts data
    into database. Redirects user to home page.
    """
    today = datetime.date.today()
    if request.method == 'POST':
        post = {
            'genre_id': request.form.get('genre'),
            'post_title': request.form.get('post_title'),
            'book': request.form.get('book'),
            'link': request.form.get('link'),
            'review': request.form.get('review'),
            'date': today.strftime('%d %B, %Y'),
            'created_by': session['user']
        }
        mongo.db.posts.insert_one(post)
        flash('Post Successfully Added')
        return redirect(url_for('get_posts'))

    genres = mongo.db.genres.find().sort('genre_name', 1)
    return render_template('add_post.html', genres=genres)


@app.route('/show_post/<post_id>')
def show_post(post_id):
    """
    Show post to reader.
    Change Genre ID to matching Genre Name.
    """
    post = mongo.db.posts.find_one({'_id': ObjectId(post_id)})

    # Attach Genre Name to Genre ID
    genre_name = mongo.db.genres.find_one(
        {"_id": ObjectId(post["genre_id"])})["genre_name"]
    post['genre_id'] = genre_name
    return render_template('review.html', post=post)


@app.route('/edit_post/<post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    """
    Allows creator to edit their post
    Flash message displays for successful edit
    """

    edit_date = datetime.date.today()
    if request.method == 'POST':
        edit = {
            'genre_id': request.form.get('genre'),
            'post_title': request.form.get('post_title'),
            'book': request.form.get('book'),
            'link': request.form.get('link'),
            'review': request.form.get('review'),
            'created_by': session['user'],
            'edit_date': edit_date.strftime('%d %B, %Y')
        }
        mongo.db.posts.update({'_id': ObjectId(post_id)}, edit)
        flash('Post Successfully Updated')

    genres = mongo.db.genres.find().sort('genre_name', 1)
    post = mongo.db.posts.find_one({'_id': ObjectId(post_id)})
    return render_template('edit_post.html', post=post, genres=genres)


@app.route('/delete_post/<post_id>')
def delete_post(post_id):
    """
    Deletes Post as long as
    request comes from the author or
    from an admin.
    """
    mongo.db.posts.remove({'_id': ObjectId(post_id)})
    flash('Post Successfully Deleted')
    return redirect(url_for('get_posts'))


@app.route('/dashboard')
def dashboard():
    """
    Check if user is an admin
    Displays no. of users.
    Displays no. of posts.
    Action buttons for genre manipulation.
    """
    genres = list(mongo.db.genres.find().sort('genre_name', 1))
    admin_user = mongo.db.users.find({'username': session['user'],
                                      'admin': 'true'})

    if admin_user:
        total_users = mongo.db.users.count_documents({})
        total_posts = mongo.db.posts.count_documents({})
        return render_template('dashboard.html', genres=genres,
                               total_users=total_users,
                               total_posts=total_posts)
    return render_template('404.html')


@app.route('/add_genre', methods=['GET', 'POST'])
def add_genre():
    """
    Allows admin to add a new genre.
    Genre name will derive from the form.
    Flash message used to indicate successful change.
    Redirects admin to the dashboard.
    """
    if request.method == 'POST':
        genre = {
            'genre_name': request.form.get('genre_name')
        }
        mongo.db.genres.insert_one(genre)
        flash('New Genre Added')
        return redirect(url_for('dashboard'))

    return render_template("add_genre.html")


@app.route('/edit_genre/<genre_id>', methods=['GET', 'POST'])
def edit_genre(genre_id):
    """
    Allows admin to edit an existing genre.
    Genre name will derive from the form which
    will update the data in the db.
    Flash message used to indicate successful change.
    Redirects admin to the dashboard.
    """
    if request.method == 'POST':
        submit = {
            'genre_name': request.form.get('genre_name')
        }
        mongo.db.genres.update({'_id': ObjectId(genre_id)}, submit)
        flash('Genre Successfully Updated')
        return redirect(url_for('dashboard'))

    genre = mongo.db.genres.find_one({'_id': ObjectId(genre_id)})
    return render_template('edit_genre.html', genre=genre)


@app.route('/delete_genre/<genre_id>')
def delete_genre(genre_id):
    """
    Deletes genre from website. Removes genre from database.
    Deletes Posts with the associated genre.
    Flash message to indicate successful deletion.
    Redirects admin to dashboard.
    """
    mongo.db.genres.remove({'_id': ObjectId(genre_id)})
    mongo.db.posts.remove({'genre_id': genre_id})
    flash('Genre Successfully Deleted')
    return redirect(url_for('dashboard'))


@app.errorhandler(404)
def not_found_error(error):
    """
    Route to handle 404 error
    """
    return render_template('404.html', error=error), 404


@app.errorhandler(500)
def internal_error(error):
    """
    Route to handle 500 error
    """
    return render_template('500.html', error=error), 500


if 'DEVELOPMENT' in os.environ:
    if __name__ == '__main__':
        app.run(host=os.environ.get('IP'),
                port=int(os.environ.get('PORT')),
                debug=True)
else:
    if __name__ == '__main__':
        app.run(host=os.environ.get('IP'),
                port=int(os.environ.get('PORT')),
                debug=False)
