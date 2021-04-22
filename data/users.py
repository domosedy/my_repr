from sqlalchemy import Column, Integer, String, orm, ForeignKey, Table
from sqlalchemy.orm import relationship
from .base import Base
from hashlib import md5
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

likes = Table('likes', Base.metadata,
              Column('user_id', Integer, ForeignKey('users.id')),
              Column('post_id', Integer, ForeignKey('posts.id')))

followers = Table('followers', Base.metadata,
                  Column('follower_id', Integer, ForeignKey('users.id')),
                  Column('followed_id', Integer, ForeignKey('users.id')))
'''class Followers(Base):
    __tablename__ = 'followers'
    id = Column(Integer, primary_key=True)
    followed_id = Column(Integer, ForeignKey('users.id'))
    follower_id = Column(Integer, ForeignKey('users.id'))
'''


class User(Base, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nickname = Column(String)
    hashed_password = Column(String)
    about = Column(String, default='')
    email = Column(String)
    follows = Column(Integer, default=0)
    '''follows = Column(Integer, default=0)
    followers = relationship('User', back_populates='user')
    followings = relationship('User', back_populates='user')'''

    news = relationship('Post', back_populates='user')
    liked = relationship('Post', secondary=likes)
    followed = relationship('User', secondary=followers,
                            primaryjoin=(followers.c.follower_id == id),
                            secondaryjoin=(
                                followers.c.followed_id == id),
                            backref='followers')

    def avatar(self, size):
        digest = md5(self.nickname.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def follow(self, user):
        if user in self.followed:
            self.followed.remove(user)
            user.follows -= 1
        else:
            self.followed.append(user)
            user.follows += 1

    def like(self, post):
        if post not in self.liked:
            self.liked.append(post)
            post.likes += 1
        else:
            self.liked.remove(post)
            post.likes -= 1

    def __repr__(self):
        return "<User(name='%s', about='%s')>" % (self.nickname, self.about)

    def __str__(self):
        return "<User(name='%s', about='%s')>" % (self.nickname, self.about)
