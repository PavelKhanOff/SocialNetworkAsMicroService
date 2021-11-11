from app.database import Base
from sqlalchemy import Column, Integer, Text, select, ForeignKey
from app.custom_fields import GUID
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional


class Comment(Base):
    __tablename__ = 'Comments'
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text)
    course_id = Column(Integer, nullable=True)
    homework_id = Column(Integer, nullable=True)
    lesson_id = Column(Integer, nullable=True)
    user_id = Column(GUID, nullable=False)
    post_id = Column(Integer, ForeignKey("Posts.id"))

    @classmethod
    async def read_all(cls, session: AsyncSession):
        stmt = select(cls)
        stream = await session.stream(stmt.order_by(cls.id))
        async for row in stream:
            yield row.Comment
