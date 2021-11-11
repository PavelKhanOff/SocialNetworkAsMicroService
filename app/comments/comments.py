from fastapi import APIRouter, Depends, status, Header
from app.comments import schemas
from typing import Optional
from fastapi_pagination.ext.async_sqlalchemy import paginate
from fastapi.responses import JSONResponse
from pydantic import UUID4
from app.additional_functions import (
    check_user,
    check_course,
    check_homework,
    check_lesson,
)
from http import HTTPStatus
from starlette.responses import Response
from app.pagination import CustomPage as Page
from app.comments.comment_dal import CommentDAL
from app.comments.dependencies import get_comment_dal
from app.additional_functions import add_achievements
from app.auth.jwt_decoder import decode
from app.additional_functions import send_comments_notifications


router = APIRouter(tags=['Comments'])


@router.get('/feed/comment', response_model=Page[schemas.CommentOut], status_code=200)
async def show_comments(
    comment_dal: CommentDAL = Depends(get_comment_dal),
    user_id: Optional[str] = None,
    course_id: Optional[int] = None,
    homework_id: Optional[int] = None,
    lesson_id: Optional[int] = None,
    post_id: Optional[int] = None,
):
    if user_id:
        if await check_user(user_id) == "False":
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": "Пользователя не существует"},
            )
        comments = await comment_dal.get_user_comments(user_id)
        return await paginate(comment_dal.db_session, comments)
    if course_id:
        if await check_course(course_id) == "False":
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": "Курса не существует"},
            )
        comments = await comment_dal.get_course_comments(course_id)
        return await paginate(comment_dal.db_session, comments)
    if homework_id:
        if await check_homework(homework_id) == "False":
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": "Домашнего задания не существует"},
            )
        comments = await comment_dal.get_homework_comments(homework_id)
        return await paginate(comment_dal.db_session, comments)
    if lesson_id:
        if await check_lesson(lesson_id) == "False":
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": "Урока не существует"},
            )
        comments = await comment_dal.get_lesson_comments(lesson_id)
        return await paginate(comment_dal.db_session, comments)
    if post_id:
        if await comment_dal.get_post(post_id) is None:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": "Поста не существует"},
            )
        comments = await comment_dal.get_post_comments(post_id)
        return await paginate(comment_dal.db_session, comments)
    comments = await comment_dal.get_all_comments()
    return await paginate(comment_dal.db_session, comments)


@router.post('/feed/comment/create', status_code=201)
async def create_comment(
    request: schemas.Comment,
    authorization: Optional[str] = Header(None),
    comment_dal: CommentDAL = Depends(get_comment_dal),
):
    user_id = await decode(authorization)
    if user_id is None:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "Auth Failed"},
        )
    check_current_user = await check_user(user_id)
    if check_current_user not in ["True", "False"]:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": f"Что то пошло не так: {check_current_user}"},
        )
    if await check_user(user_id) == "False":
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Пользователя не существует"},
        )
    if request.course_id:
        if await check_course(request.course_id) == "False":
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": "Курса не существует"},
            )
    if request.lesson_id:
        if await check_lesson(request.lesson_id) == "False":
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": "Урока не существует"},
            )
    if request.homework_id:
        if await check_homework(request.homework_id) == "False":
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": "Домашнее задание не существует"},
            )
    if request.post_id:
        if await comment_dal.get_post(request.post_id) is None:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": "Поста не существует"},
            )
    new_comment = await comment_dal.create_comment(
        request.text,
        user_id,
        request.course_id,
        request.homework_id,
        request.lesson_id,
        request.post_id,
    )
    await send_comments_notifications(user_id)
    await add_achievements(user_id, comment_dal)
    return schemas.CommentOut.from_orm(new_comment)


@router.patch('/feed/comment/{comment_id}/update', status_code=202)
async def update_comment(
    comment_id: int,
    request: schemas.CommentUpdate,
    authorization: Optional[str] = Header(None),
    comment_dal: CommentDAL = Depends(get_comment_dal),
):
    user_id = await decode(authorization)
    if user_id is None:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "Auth Failed"},
        )
    if await check_user(user_id) == "False":
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Пользователя не существует"},
        )
    return await comment_dal.update_comment(comment_id, request.text)


@router.delete('/feed/comment/{comment_id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_comment(
    comment_id: int,
    authorization: Optional[str] = Header(None),
    comment_dal: CommentDAL = Depends(get_comment_dal),
):
    user_id = await decode(authorization)
    if user_id is None:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "Auth Failed"},
        )
    if await check_user(user_id) == "False":
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Пользователя не существует"},
        )
    check_comment = await comment_dal.get_comment(comment_id)
    if not check_comment:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Коммента не существует"},
        )
    return Response(status_code=204)
