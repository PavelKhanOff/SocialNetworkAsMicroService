from typing import List, Optional

from sqlalchemy import update, desc, delete, func
from sqlalchemy.future import select
from sqlalchemy.orm import Session, selectinload
from pydantic import UUID4
from app.posts.models import Post, PostBookMark
from sqlalchemy.sql.expression import exists


class PostDAL:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def get_post(self, post_id):
        q = await self.db_session.execute(select(Post).filter_by(id=post_id))
        return q.scalars().first()

    async def check_post(self, post_id):
        q = await self.db_session.execute(
            exists(select(Post.id).filter_by(id=post_id)).select()
        )
        return q.scalar()

    async def check_post_exists(self, post_id: int, user_id: str):
        q = await self.db_session.execute(
            exists(select(Post.id).filter_by(id=post_id, user_id=user_id)).select()
        )
        return q.scalar()

    async def get_post_with_likes(self, post_id: int):
        q = await self.db_session.execute(
            select(Post).options(selectinload(Post.likes)).filter(Post.id == post_id)
        )
        return q.scalars().first()

    async def get_all_posts(self):
        q = await self.db_session.execute(select(Post).order_by(desc(Post.pub_date)))
        return q.scalars().unique().all()

    async def get_all_posts_order_by_popularity(self, users_followings):
        q = await self.db_session.execute(
            select(Post)
            .where(Post.user_id.notin_(users_followings))
            .order_by(desc(Post.likes_count))
        )
        return q.scalars().unique().all()

    async def get_all_posts_query(self):
        q = select(Post).order_by(desc(Post.pub_date))
        return q

    async def get_posts_by_title(self, title):
        q = await self.db_session.execute(
            select(Post)
            .filter(Post.title.like(f'{title}%'))
            .order_by(desc(Post.pub_date))
        )
        return q.scalars().all()

    async def get_posts_by_title_query(self, title):
        q = select(Post).filter(Post.title.like(f'{title}%'))
        return q

    async def create_post(
        self, title: str, description: str, user_id: UUID4, course_id: int
    ):
        new_post = Post(
            title=title,
            description=description,
            user_id=user_id,
            course_id=course_id,
        )
        self.db_session.add(new_post)
        await self.db_session.flush()
        return new_post

    async def update_post(self, post_id: int, updated_values):
        q = update(Post).where(Post.id == post_id)
        q = q.values(updated_values)
        q.execution_options(synchronize_session="fetch")
        await self.db_session.execute(q)
        return 'Обновлено'

    async def delete_post(self, post_id: int):
        q = delete(Post).where(Post.id == post_id)
        await self.db_session.execute(q)

    async def count_posts(self, user_id):
        q = await self.db_session.execute(
            select(func.count(Post.id)).filter_by(user_id=user_id)
        )
        return q.scalars().first()

    async def get_book_mark(self, user_id: UUID4, post_id: int):
        q = await self.db_session.execute(
            select(PostBookMark).filter(
                PostBookMark.post_id == post_id, PostBookMark.user_id == user_id
            )
        )
        return q.scalars().first()

    async def get_book_marks_of_user(self, user_id: UUID4):
        q = await self.db_session.execute(
            select(Post)
            .filter(
                Post.id.in_(
                    select(PostBookMark.post_id).filter(PostBookMark.user_id == user_id)
                )
            )
            .order_by(desc(Post.pub_date))
        )
        return q.scalars().all()

    async def book_mark(self, user_id: UUID4, post_id: int):
        if await self.get_book_mark(user_id, post_id):
            q = delete(PostBookMark).where(
                PostBookMark.post_id == post_id, PostBookMark.user_id == user_id
            )
            await self.db_session.execute(q)
            return False
        else:
            new_bookmark = PostBookMark(user_id=user_id, post_id=post_id)
            self.db_session.add(new_bookmark)
            await self.db_session.flush()
            return True
