from typing import Optional
from pydantic import BaseModel


class Comment(BaseModel):
    text: str
    course_id: Optional[int] = None
    homework_id: Optional[int] = None
    lesson_id: Optional[int] = None
    post_id: Optional[int] = None


class CreateCommentSchema(BaseModel):
    text: str
    course_id: Optional[int] = None
    homework_id: Optional[int] = None
    lesson_id: Optional[int] = None
    post_id: Optional[int] = None


class CommentOut(Comment):
    id: int

    class Config:
        orm_mode = True


class CommentUpdate(BaseModel):
    text: str
