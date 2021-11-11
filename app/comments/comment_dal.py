from typing import List, Optional

from sqlalchemy import update, delete
from sqlalchemy.future import select
from sqlalchemy.orm import Session


from app.comments.models import Comment
from app.posts.models import Post


class CommentDAL:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def create_comment(
        self,
        text,
        user_id,
        course_id: Optional[int] is None,
        lesson_id: Optional[int] is None,
        homework_id: Optional[int] is None,
        post_id: Optional[int] is None,
    ):

        new_comment = Comment(
            text=text,
            user_id=user_id,
            course_id=course_id,
            lesson_id=lesson_id,
            homework_id=homework_id,
            post_id=post_id,
        )
        self.db_session.add(new_comment)
        await self.db_session.flush()
        return new_comment

    async def get_all_comments(self):
        q = select(Comment).order_by(Comment.id)
        return q

    async def get_user_comments(self, user_id):
        q = select(Comment).filter(Comment.user_id == user_id)
        return q

    async def get_user_comments_achievements(self, user_id):
        q = await self.db_session.execute(
            select(Comment).filter(Comment.user_id == user_id)
        )
        return q.scalars().all()

    async def get_course_comments(self, course_id):
        q = select(Comment).filter(Comment.course_id == course_id)
        return q

    async def get_lesson_comments(self, lesson_id):
        q = select(Comment).filter(Comment.lesson_id == lesson_id)
        return q

    async def get_homework_comments(self, homework_id):
        q = select(Comment).filter(Comment.homework_id == homework_id)
        return q

    async def get_post_comments(self, post_id):
        q = select(Comment).filter(Comment.homework_id == post_id)
        return q

    async def get_post(self, post_id):
        q = await self.db_session.execute(select(Post).filter(Post.id == post_id))
        return q.scalars().first()

    async def update_comment(self, comment_id, text):
        q = update(Comment).filter(Comment.id == comment_id)
        if text:
            q = q.values(text=text)
        q.execution_options(synchronize_session="fetch")
        await self.db_session.execute(q)
        return "обновлено"

    async def delete_comment(self, comment_id):
        stmt = delete(Comment).where(Comment.id == comment_id)
        await self.db_session.execute(stmt)
        return "удалено"

    async def get_comment(self, comment_id):
        q = await self.db_session.execute(
            select(Comment).filter(Comment.id == comment_id)
        )
        return q.scalars().first()
