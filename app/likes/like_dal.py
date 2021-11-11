from typing import List, Optional

from sqlalchemy import update, desc, delete
from sqlalchemy.future import select
from sqlalchemy.orm import Session, selectinload
from pydantic import UUID4
from app.likes.models import Like
from app.posts.models import Post
from fastapi.responses import JSONResponse
from fastapi import status


class LikeDAL:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def get_like(self, post_id: int, user_id: UUID4):
        q = select(Like)
        if user_id:
            q = select(Like).filter(Like.user_id == user_id)
            return q
        if post_id:
            q = select(Like).filter(Like.post_id == post_id)
            return q
        return q

    async def get_like_by_id(self, post_id, user_id):
        q = await self.db_session.execute(
            select(Like).filter_by(post_id=post_id, user_id=user_id)
        )
        return q.scalars().first()

    async def like(self, post_id: int, user_id: UUID4):
        if await self.get_like_by_id(post_id=post_id, user_id=user_id):
            q = (
                delete(Like)
                .where(Like.post_id == post_id)
                .where(Like.user_id == user_id)
            )
            await self.db_session.execute(q)
            return False
        else:
            new_like = Like(post_id=post_id, user_id=user_id)
            self.db_session.add(new_like)
            await self.db_session.flush()
            return True

    async def get_post(self, post_id):
        post = await self.db_session.execute(select(Post).filter(Post.id == post_id))
        return post.scalars().first()
