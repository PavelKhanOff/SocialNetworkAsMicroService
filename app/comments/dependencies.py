from app.database import async_session
from app.comments.comment_dal import CommentDAL


async def get_comment_dal():
    async with async_session() as session:
        async with session.begin():
            yield CommentDAL(session)
