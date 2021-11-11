import json
import requests
from requests import exceptions
from app.config import (
    MIDDLEWARE_URL_CHECK_USER,
    MIDDLEWARE_URL_CHECK_HOMEWORK,
    MIDDLEWARE_URL_CHECK_COURSE,
    MIDDLEWARE_URL_CHECK_LESSON,
    MIDDLEWARE_URL_GET_USERS_FOLLOWINGS,
    MIDDLEWARE_URL_CHECK_ACHIEVEMENTS,
    MIDDLEWARE_URL_GET_COURSE_OBJ,
    MIDDLEWARE_URL_GET_USER_OBJ,
    MIDDLEWARE_URL_SEND_NOTIFICATIONS,
    MIDDLEWARE_URL_GET_USERS_FOLLOWERS,
    MIDDLEWARE_GET_SUPERUSER_TOKEN
)

import httpx


async def checker_user(url):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, timeout=8)
            response.raise_for_status()
        # response = requests.post(url=url, params=params, timeout=8)
    except httpx.HTTPError as exc:
        return exc
    except Exception as e:
        return e
    return json.loads(response.text).get('message')


async def checker(url, params):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, params=params, timeout=8)
            response.raise_for_status()
        # response = requests.post(url=url, params=params, timeout=8)
    except httpx.HTTPError as exc:
        return exc
    except Exception as e:
        return e
    return json.loads(response.text).get('message')


async def check_user(user_id):
    url = f'{MIDDLEWARE_URL_CHECK_USER}/{user_id}'
    return await checker_user(url)


async def check_course(course_id):
    url = MIDDLEWARE_URL_CHECK_COURSE
    params = {'course_id': course_id}
    return await checker(url, params)


async def check_lesson(lesson_id):
    url = MIDDLEWARE_URL_CHECK_LESSON
    params = {'lesson_id': lesson_id}
    return await checker(url, params)


async def check_homework(homework_id):
    url = MIDDLEWARE_URL_CHECK_HOMEWORK
    params = {'homework_id': homework_id}
    return await checker(url, params)


async def get_users_followings(user_id):
    url = f'{MIDDLEWARE_URL_GET_USERS_FOLLOWINGS}/{user_id}'
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, timeout=8)
            response.raise_for_status()
    except httpx.HTTPError as e:
        raise e
    except Exception as e:
        raise e
    return response.json()


async def get_users_name_and_followers(user_id):
    url = f'{MIDDLEWARE_URL_GET_USERS_FOLLOWERS}/{user_id}'
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, timeout=8)
            response.raise_for_status()
    except httpx.HTTPError as e:
        raise e
    except Exception as e:
        raise e
    return response.json()


async def add_achievements(user_id, comment_dal):
    comments = await comment_dal.get_user_comments_achievements(user_id)
    url = MIDDLEWARE_URL_CHECK_ACHIEVEMENTS
    if len(comments) >= 100000:
        params = {'user_id': user_id, 'quantity': 100000}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url=url, params=params, timeout=8)
                response.raise_for_status()
        except httpx.HTTPError as e:
            raise e
        except Exception as e:
            raise e
        return response.json()
    if len(comments) >= 10000:
        params = {'user_id': user_id, 'quantity': 10000}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url=url, params=params, timeout=8)
                response.raise_for_status()
        except httpx.HTTPError as e:
            raise e
        except Exception as e:
            raise e
        return response.json()
    if len(comments) >= 1000:
        params = {'user_id': user_id, 'quantity': 1000}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url=url, params=params, timeout=8)
                response.raise_for_status()
        except exceptions.ConnectionError as e:
            raise e
        except Exception as e:
            raise e
        return response.json()
    return 'ok'


def get_course(course_id):
    url = f'{MIDDLEWARE_URL_GET_COURSE_OBJ}/{course_id}'
    try:
        response = requests.post(url=url, timeout=8)
    except exceptions.ConnectionError as e:
        raise e
    except Exception as e:
        raise e
    return response.json()


def get_user(user_id):
    url = f'{MIDDLEWARE_URL_GET_USER_OBJ}/{user_id}'
    try:
        response = requests.post(url=url, timeout=8)
    except exceptions.ConnectionError as e:
        raise e
    except Exception as e:
        raise e
    return response.json()


async def get_token():
    url = f'{MIDDLEWARE_GET_SUPERUSER_TOKEN}'
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url=url, timeout=8)
            response.raise_for_status()
    except httpx.HTTPError as e:
        raise e
    except Exception as e:
        raise e
    return response.json()


async def send_post_notifications(user_id):
    url = MIDDLEWARE_URL_SEND_NOTIFICATIONS
    name_and_receivers = await get_users_name_and_followers(user_id)
    authorization = await get_token()
    headers = {'Authorization': f'Bearer {authorization}'}
    data = {
        'notification_type': 'Post',
        'title': 'Новое сообщение',
        'text': f'Новая публикация у {name_and_receivers[0]["username"]}',
        'user_id': user_id,
        'receivers': name_and_receivers[1]
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, json=data, headers=headers, timeout=8)
            response.raise_for_status()
    except httpx.HTTPError as e:
        raise e
    except Exception as e:
        raise e
    return response.json()


async def send_comments_notifications(user_id):
    url = MIDDLEWARE_URL_SEND_NOTIFICATIONS
    name_and_receivers = await get_users_name_and_followers(user_id)
    authorization = await get_token()
    headers = {'Authorization': f'Bearer {authorization}'}
    data = {
        'notification_type': 'Comment',
        'title': 'Новый комментарий',
        'text': f'{name_and_receivers[0]["username"]} оставил новый комментарий',
        'user_id': user_id,
        'receivers': name_and_receivers[1]
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, json=data, headers=headers, timeout=8)
            response.raise_for_status()
    except httpx.HTTPError as e:
        raise e
    except Exception as e:
        raise e
    return response.json()


async def send_like_notifications(user_id, post):
    url = MIDDLEWARE_URL_SEND_NOTIFICATIONS
    name_and_receivers = await get_users_name_and_followers(user_id)
    authorization = await get_token()
    headers = {'Authorization': f'Bearer {authorization}'}
    data = {
        'notification_type': 'Like',
        'title': 'Like',
        'text': f'{name_and_receivers[0]["username"]} поставил лайк {post.title}',
        'user_id': str(user_id),
        'receivers': [str(post.user_id)]
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, json=data, headers=headers, timeout=8)
            response.raise_for_status()
    except httpx.HTTPError as e:
        raise e
    except Exception as e:
        raise e
    return response.json()
