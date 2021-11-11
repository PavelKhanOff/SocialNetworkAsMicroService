from app.database import async_session
from app.likes.like_dal import LikeDAL


async def get_like_dal():
    async with async_session() as session:
        async with session.begin():
            yield LikeDAL(session)
