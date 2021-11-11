from fastapi import APIRouter, Depends
from app.posts.dependencies import get_post_dal
from app.posts.post_dal import PostDAL
from app.files.file_dal import FileDAL
from app.files.dependencies import get_file_dal
from fastapi.responses import JSONResponse
from app.files.schemas import FileIn


router = APIRouter(tags=['Middleware'])


@router.get("/feed/middleware/post/check/{post_id}")
async def check_exists(post_id: int, post_dal: PostDAL = Depends(get_post_dal)):
    return await post_dal.check_post(post_id)


@router.get("/feed/middleware/post/check")
async def check_post_exists(
    post_id: int, user_id: str, post_dal: PostDAL = Depends(get_post_dal)
):
    return await post_dal.check_post_exists(post_id=post_id, user_id=user_id)


@router.get("/feed/middleware/post/{post_id}")
async def get_post(post_id: int, post_dal: PostDAL = Depends(get_post_dal)):
    return await post_dal.get_post(post_id)


@router.post('/feed/middleware/upload/image', status_code=200)
async def upload_image(request: FileIn, file_dal: FileDAL = Depends(get_file_dal)):
    await file_dal.upload_image(request)
    return JSONResponse(content="Successfully added Post image")
