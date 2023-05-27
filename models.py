from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime

db = SQLAlchemy()

class Follow(db.Model):
  __tablename__ = 'follows'
  follower_id = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key=True)
  followed_id = db.Column(db.Integer, db.ForeignKey('User.id'), primary_key=True)
  
class User(db.Model):
  __tablename__ = 'User'
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(20), unique=True, nullable=False)
  password= db.Column(db.String(100), nullable=False)
  posts = db.relationship('Post', backref='author')
  followed = db.relationship('Follow', foreign_keys=[Follow.follower_id])
  followers = db.relationship('Follow', foreign_keys=[Follow.followed_id])


class Post(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(120), nullable=False)
  date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
  content = db.Column(db.Text(500), nullable=False)
  image = db.Column(db.String(100))
  creator= db.Column(db.String(20), nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)