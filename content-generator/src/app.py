from flask import Flask, request, session, render_template, redirect, url_for, flash, g
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Post, Like, Comment
from main import AIContentBot
import os
from dotenv import load_dotenv
from functools import wraps

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///social_media.db'
db.init_app(app)

bot = AIContentBot()

@app.before_request
def load_user():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_user():
    return dict(current_user=g.user)

@app.route('/')
def index():
    if g.user is None:
        return redirect(url_for('login'))
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('signup'))
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        bot.add_user_interests(username, [])
        flash('Account created successfully', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash('Logged in successfully', 'success')
            return redirect(url_for('index'))
        flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

@app.route('/create_post', methods=['POST'])
@login_required
def create_post():
    prompt = request.form.get('prompt')
    success, result = bot.generate_and_check_content(prompt, g.user.username)
    
    if success:
        new_post = Post(content=result, user_id=g.user.id)
        db.session.add(new_post)
        db.session.commit()
        flash('Post created successfully', 'success')
    else:
        flash(result, 'error')
    
    return redirect(url_for('index'))

@app.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    like = Like.query.filter_by(user_id=g.user.id, post_id=post_id).first()
    if like:
        db.session.delete(like)
        db.session.commit()
        flash('Post unliked', 'success')
    else:
        new_like = Like(user_id=g.user.id, post_id=post_id)
        db.session.add(new_like)
        db.session.commit()
        flash('Post liked', 'success')
    return redirect(url_for('index'))

@app.route('/comment/<int:post_id>', methods=['POST'])
@login_required
def comment_post(post_id):
    content = request.form.get('content')
    success, result = bot.generate_and_check_content(content, g.user.username)
    
    if success:
        new_comment = Comment(content=result, user_id=g.user.id, post_id=post_id)
        db.session.add(new_comment)
        db.session.commit()
        flash('Comment added successfully', 'success')
    else:
        flash(result, 'error')
    
    return redirect(url_for('index'))

@app.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(Post.id.desc()).all()
    return render_template('profile.html', user=user, posts=posts)

@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User not found.', 'error')
        return redirect(url_for('index'))
    if user.id == g.user.id:
        flash('You cannot follow yourself!', 'error')
        return redirect(url_for('profile', username=username))
    g.user.follow(user)
    db.session.commit()
    flash(f'You are now following {username}!', 'success')
    return redirect(url_for('profile', username=username))

@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User not found.', 'error')
        return redirect(url_for('index'))
    if user.id == g.user.id:
        flash('You cannot unfollow yourself!', 'error')
        return redirect(url_for('profile', username=username))
    g.user.unfollow(user)
    db.session.commit()
    flash(f'You have unfollowed {username}.', 'success')
    return redirect(url_for('profile', username=username))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)