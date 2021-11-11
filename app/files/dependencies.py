from app.database import async_session
from app.files.file_dal import FileDAL


async def get_file_dal():
    async with async_session() as session:
        async with session.begin():
            yield FileDAL(session)
