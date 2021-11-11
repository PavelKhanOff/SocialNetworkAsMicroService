from sqlalchemy.orm import Session
from app.files.models import File


class FileDAL:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def upload_image(self, request):
        new_file = File(
            key=request.key,
            url=request.url,
            title=request.title,
            post_id=request.post_id,
        )
        self.db_session.add(new_file)
        await self.db_session.flush()
