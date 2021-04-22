from .base import Base
from sqlalchemy import Column, Integer, String, orm, DateTime, ForeignKey
from sqlalchemy.orm import relationship


class Post(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    text = Column(String)
    date = Column(DateTime)
    likes = Column(Integer, default=0)

    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User")

    def __lt__(self, post):
        if self.date > post.date:
            return True
        elif self.date == post.date and self.likes > post.likes:
            return True
        else:
            return False

    def __eq__(self, post):
        if post.text == self.text and post.name == self.name and post.date == self.date:
            return True
        else:
            return False

    def __repr__(self):
        return f'<Post(title={self.name}, text={self.text}, date={self.date})>'

    def __str__(self):
        return f'<Post(title={self.name}, text={self.text}, date={self.date})>'
