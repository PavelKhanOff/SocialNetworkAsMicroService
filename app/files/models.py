from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
)
from app.database import Base
from sqlalchemy.orm import relationship


class File(Base):
    __tablename__ = 'Files'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50), nullable=False)
    url = Column(String(500), nullable=True, default='file_default.png')
    post_id = Column(Integer, ForeignKey("Posts.id"))
    key = Column(String(500), nullable=False)
