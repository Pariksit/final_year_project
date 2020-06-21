from datetime import datetime
from flaskblog import db
from flaskblog import login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(20),unique=True,nullable=False)
    email=db.Column(db.String(120),unique=True,nullable=False)
    username=db.Column(db.String(20),unique=True,nullable=False)
    image_file=db.Column(db.String(20),nullable=False,default='default.jpg')
    password=db.Column(db.String(60),nullable=False)
    fav_actor=db.Column(db.String(60),nullable=False)
    fav_director=db.Column(db.String(60),nullable=False)
    fav_genre=db.Column(db.String(60),nullable=False)
    fav_movie=db.Column(db.String(60),nullable=False)
    watchlist=db.Column(db.String(60),nullable=True)
    posts = db.relationship('Post',backref='author',lazy=True)

    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.image_file}','{self.username}','{self.fav_actor}','{self.fav_director}','{self.fav_genre}','{self.fav_movie}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

usr=User(username='Pariksit',
    email='Pariksit@gmail.com',
    password='Password',
    fav_actor='Ryan Gosling',
    fav_director='Martin',
    fav_genre='Thriller',
    fav_movie='Godfather')
