from typing import List, Optional
from pydantic import BaseModel, UUID4
from typing import Any


class Like(BaseModel):
    post_id: int


class LikeOut(Like):
    user_id: Any
    post_id: int

    class Config:
        orm_mode = True
