from app.database import Base
from app.custom_fields import GUID
from sqlalchemy.sql import func, select
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table

from app.additional_functions import get_course, get_user
from sqlalchemy.orm import relationship, column_property
from app.likes.models import Like
from app.comments.models import Comment
from app.files.models import File


class PostBookMark(Base):
    __tablename__ = "PostBookMarks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(GUID, nullable=False)
    post_id = Column(Integer, ForeignKey("Posts.id"))


class Post(Base):
    __tablename__ = 'Posts'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50), nullable=False)
    description = Column(Text)
    pub_date = Column(DateTime(timezone=True), nullable=True, server_default=func.now())
    images = relationship('File', lazy='joined', backref='post')
    user_id = Column(GUID, nullable=False)
    likes = relationship('Like', lazy="select", backref='post')
    course_id = Column(Integer, nullable=False)
    comments = relationship('Comment', lazy="select", backref='post')
    likes_count = column_property(
        select(func.count(Like.id))
        .where(Like.post_id == id)
        .correlate_except(Like)
        .scalar_subquery()
    )
    comments_count = column_property(
        select(func.count(Comment.id))
        .where(Comment.post_id == id)
        .correlate_except(Comment)
        .scalar_subquery()
    )

    def __init__(self, title: str, description: str, user_id, course_id: int):
        self.is_liked = False
        self.is_bookmarked = False
        self.title = title
        self.description = description

        self.user_id = user_id
        self.course_id = course_id

    @property
    def is_liked(self):
        return self._is_liked

    @is_liked.setter
    def is_liked(self, value):
        self._is_liked = value

    @property
    def is_bookmarked(self):
        return self._is_bookmarked

    @is_bookmarked.setter
    def is_bookmarked(self, value):
        self._is_bookmarked = value

    @property
    def course(self):
        course = get_course(self.course_id)
        return course

    @property
    def user(self):
        user = get_user(self.user_id)
        return user
