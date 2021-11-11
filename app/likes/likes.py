from fastapi import APIRouter, Depends, status, Header
from app.likes import schemas
from pydantic import UUID4
from fastapi.responses import JSONResponse
from typing import Optional
from fastapi_pagination.ext.async_sqlalchemy import paginate
from app.additional_functions import check_user
from app.pagination import CustomPage as Page
from app.likes.dependencies import get_like_dal
from app.likes.like_dal import LikeDAL
from app.auth.jwt_decoder import decode
from app.additional_functions import send_like_notifications

router = APIRouter(tags=['Likes'])


@router.get('/feed/like', response_model=Page[schemas.LikeOut], status_code=200)
async def get_likes(
    user_id: Optional[UUID4] = None,
    post_id: Optional[int] = None,
    like_dal: LikeDAL = Depends(get_like_dal),
):
    q = await like_dal.get_like(post_id, user_id)
    if user_id:
        if await check_user(user_id) == "False":
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": "Пользователя не существует"},
            )
        return await paginate(like_dal.db_session, q)
    if post_id:
        return await paginate(like_dal.db_session, q)
    return await paginate(like_dal.db_session, q)


@router.post('/feed/like')
async def like(
    request: schemas.Like,
    authorization: Optional[str] = Header(None),
    like_dal: LikeDAL = Depends(get_like_dal),
):
    user_id = await decode(authorization)
    if user_id is None:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "Auth Failed"},
        )
    if await check_user(user_id) == "False":
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "Пользователя не существует"},
        )
    check_post = await like_dal.get_post(request.post_id)
    if not check_post:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "Поста не существует"},
        )
    checker = await like_dal.like(post_id=request.post_id, user_id=user_id)
    message = "Лайк убран"
    if checker:
        message = "Лайк добавлен"
        await send_like_notifications(user_id, check_post)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": message},
    )
