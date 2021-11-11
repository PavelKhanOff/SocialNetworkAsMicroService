from app.database import async_session
from app.posts.post_dal import PostDAL


async def get_post_dal():
    async with async_session() as session:
        async with session.begin():
            yield PostDAL(session)
