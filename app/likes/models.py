from app.database import Base
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    DateTime,
)
from app.custom_fields import GUID
from sqlalchemy.sql import func


class Like(Base):
    __tablename__ = 'Likes'
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(
        DateTime(timezone=True), nullable=True, server_default=func.now()
    )
    user_id = Column(GUID, nullable=False)
    post_id = Column(Integer, ForeignKey("Posts.id"))
