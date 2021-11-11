from typing import Optional

from pydantic import BaseModel


class FileIn(BaseModel):
    url: str
    title: str
    key: str
    post_id: int


class FileOut(BaseModel):
    id: int
    url: Optional[str] = None
    title: str
    key: Optional[str] = None

    class Config:
        orm_mode = True
