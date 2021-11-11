from fastapi import APIRouter, Depends, status, Header
from app.posts import schemas
from app.likes.schemas import LikeOut
from typing import Optional
from fastapi_pagination.ext.async_sqlalchemy import paginate
from fastapi.responses import JSONResponse
from fastapi_pagination.paginator import paginate as paginate_list
from pydantic import UUID4
from app.additional_functions import (
    check_user,
    get_users_followings,
    check_course,
)
from app.pagination import CustomPage as Page
from elastic import es
from app.posts.dependencies import get_post_dal
from app.posts.post_dal import PostDAL
from app.likes.like_dal import LikeDAL
from app.likes.dependencies import get_like_dal
from app.redis.redis import redis_cache
from app.auth.jwt_decoder import decode
from http import HTTPStatus
from starlette.responses import Response
from app.additional_functions import send_post_notifications

router = APIRouter(tags=['Posts'])


@router.get('/feed/posts', response_model=Page[schemas.PostOut], status_code=200)
async def get_all_posts(
    user_id: Optional[UUID4] = None,
    post_dal: PostDAL = Depends(get_post_dal),
    like_dal: LikeDAL = Depends(get_like_dal),
    title: Optional[str] = None,
    authorization: Optional[str] = Header(None),
):
    request_user_id = await decode(authorization)
    posts = await post_dal.get_all_posts()
    if user_id:
        ids = await get_users_followings(user_id)
        followers_count = len(ids)
        if followers_count != 0:
            subs_post = [post for post in posts if str(post.user_id) in ids]
            if len(subs_post) > 0:
                for post in subs_post:
                    like = await like_dal.get_like_by_id(post.id, request_user_id)
                    bookmark = await post_dal.get_book_mark(
                        user_id=request_user_id, post_id=post.id
                    )
                    if like:
                        post.is_liked = True
                    if bookmark:
                        post.is_bookmarked = True
                return paginate_list(subs_post)
    if title:
        posts = await post_dal.get_posts_by_title(title)
    for post in posts:
        like = await like_dal.get_like_by_id(post.id, request_user_id)
        if like:
            post.is_liked = True
        bookmark = await post_dal.get_book_mark(
            user_id=request_user_id, post_id=post.id
        )
        if bookmark:
            post.is_bookmarked = True
    return paginate_list(posts)


@router.get(
    '/feed/posts/suggested', response_model=Page[schemas.PostOut], status_code=200
)
async def get_suggested_posts(
    post_dal: PostDAL = Depends(get_post_dal),
    like_dal: LikeDAL = Depends(get_like_dal),
    authorization: Optional[str] = Header(None),
):
    request_user_id = await decode(authorization)
    ids = []
    if request_user_id:
        ids = await get_users_followings(request_user_id)
        ids.append(request_user_id)
    posts = await post_dal.get_all_posts_order_by_popularity(ids)
    for post in posts:
        like = await like_dal.get_like_by_id(post.id, request_user_id)
        if like:
            post.is_liked = True
        bookmark = await post_dal.get_book_mark(
            user_id=request_user_id, post_id=post.id
        )
        if bookmark:
            post.is_bookmarked = True
    return paginate_list(posts)


@router.get('/feed/post/{post_id}', response_model=schemas.PostOut, status_code=200)
async def get_post(
    post_id: int,
    post_dal: PostDAL = Depends(get_post_dal),
    authorization: Optional[str] = Header(None),
    like_dal: LikeDAL = Depends(get_like_dal),
):
    post = await post_dal.get_post(post_id)
    if not post:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Такого поста не найдено"},
        )
    request_user_id = await decode(authorization)
    like = await like_dal.get_like_by_id(post.id, request_user_id)
    if like:
        post.is_liked = True
    bookmark = await post_dal.get_book_mark(user_id=request_user_id, post_id=post.id)
    if bookmark:
        post.is_bookmarked = True
    return post


@router.post('/feed/post/create', status_code=201)
async def create_post(
    request: schemas.Post,
    post_dal: PostDAL = Depends(get_post_dal),
    authorization: Optional[str] = Header(None),
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
    if check_current_user == "False":
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
    new_post = await post_dal.create_post(
        request.title, request.description, user_id, request.course_id
    )
    await send_post_notifications(user_id)
    try:
        body = {
            "title": request.title,
            "description": request.description,
            "user_id": user_id,
            "id": new_post.id,
        }
        await es.index(index="posts", id=new_post.id, body=body)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": f"Ошибка в сохранение elastic search: {e}"},
        )
    count_posts = await post_dal.count_posts(user_id)
    await redis_cache.hset(f"user:{user_id}", mapping={"posts_count": count_posts})
    return new_post


@router.patch('/feed/post/{post_id}', status_code=202)
async def update_post(
    request: schemas.UpdatePost,
    post_id: int,
    post_dal: PostDAL = Depends(get_post_dal),
    authorization: Optional[str] = Header(None),
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
    update_dict = request.dict(exclude_unset=True)
    post = await post_dal.get_post(post_id)
    if not post:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Пост не найден"},
        )
    if str(post.user_id) != str(user_id):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "Вы не являетесь автором"},
        )
    body = {
        "doc": {
            "title": request.title,
            "description": request.description,
            "user_id": user_id,
            "id": post.id,
        }
    }
    try:
        await es.update(index='posts', doc_type='_doc', id=post.id, body=body)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": f"Ошибка в апдейте elastic search: {e}"},
        )
    return await post_dal.update_post(post_id, update_dict)


@router.delete('/feed/post/{post_id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_post(
    post_id: int,
    authorization: Optional[str] = Header(None),
    post_dal: PostDAL = Depends(get_post_dal),
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
    post = await post_dal.get_post(post_id)
    if not post:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Поста не существует"},
        )
    if str(post.user_id) != str(user_id):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "Вы не являетесь автором"},
        )
    try:
        await es.delete(index='posts', doc_type='_doc', id=post.id)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": f"Ошибка при удалении поста: {e}"},
        )
    await post_dal.delete_post(post_id)
    count_posts = await post_dal.count_posts(user_id)
    await redis_cache.hset(f"user:{user_id}", mapping={"posts_count": count_posts})
    return Response(status_code=204)


@router.get('/feed/post/{post_id}/likes', response_model=Page[LikeOut], status_code=200)
async def get_post_likes(post_id: int, post_dal: PostDAL = Depends(get_post_dal)):
    post = await post_dal.get_post_with_likes(post_id)
    if not post:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "Поста не существует"},
        )
    return paginate_list(post.likes)


@router.get('/feed/bookmark', response_model=Page[schemas.PostOut])
async def get_bookmarks_of_user(
    post_dal: PostDAL = Depends(get_post_dal),
    authorization: Optional[str] = Header(None),
    like_dal: LikeDAL = Depends(get_like_dal),
):
    request_user_id = await decode(authorization)
    posts = await post_dal.get_book_marks_of_user(user_id=request_user_id)
    for post in posts:
        like = await like_dal.get_like_by_id(post.id, request_user_id)
        if like:
            post.is_liked = True
        bookmark = await post_dal.get_book_mark(
            user_id=request_user_id, post_id=post.id
        )
        if bookmark:
            post.is_bookmarked = True
    return paginate_list(posts)


@router.post('/feed/bookmark')
async def book_mark(
    post_id: int,
    post_dal: PostDAL = Depends(get_post_dal),
    authorization: Optional[str] = Header(None),
):
    request_user_id = await decode(authorization)
    if not request_user_id:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "Auth Failed"},
        )
    check_bookmark = await post_dal.book_mark(post_id=post_id, user_id=request_user_id)
    message = "Пост убран из избранных"
    if check_bookmark:
        message = "Пост добавлен в избранное"
    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": message})
