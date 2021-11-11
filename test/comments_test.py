from fastapi.testclient import TestClient
import main
import requests
import pytest


@pytest.fixture(scope="module")
def client():
    with TestClient(main.app) as client:
        yield client


def сreate_user_for_test():
    data = {
        "email": "test_user2@user.com",
        "password": "string",
        "avatar": "default_avatar.jpeg",
        "username": "testuser2",
        "first_name": "string",
        "second_name": "string",
        "description": "string",
        "web_site": "string",
        "phone": "string",
        "gender": "string",
        "birth_date": "2021-08-05",
    }
    url = 'http://core-service:8000/core/auth/register'
    try:
        response = requests.post(url=url, json=data, timeout=8)
        user_id = response.json().get('id')
    except requests.exceptions.ConnectionError:
        return [False]
    except Exception:
        return [False]

    data_for_token = {'username': 'test_user2@user.com', 'password': 'string'}
    response_token = requests.post(
        'http://core-service:8000/core/auth/jwt/login', data=data_for_token
    )

    token = response_token.json().get('access_token')

    return user_id, token


def delete_user(user_id, token):
    headers = {'Authorization': 'Bearer ' + token}
    response = requests.delete(
        f'http://core-service:8000/core/user/{user_id}/delete', headers=headers
    )
    print(response.json())


def test_comment_crud(client: TestClient):
    user_id, token = сreate_user_for_test()
    print(user_id, token)
    try:
        params = {'user_id': user_id}
        data = {'text': '23213123', 'course_id': '1'}
        response = client.post('/feed/comment/create', json=data, params=params)
        comment_id = response.json().get('id')
        assert response.status_code == 201
        response = client.get('/feed/comment/')
        assert response.status_code == 200
        data_updated = {'text': 'updated', 'course_id': '1'}
        response = client.patch(
            f'/feed/comment/{comment_id}/update', json=data_updated, params=params
        )
        assert response.status_code == 202
        response = client.delete(
            f'/feed/comment/{comment_id}', json=data_updated, params=params
        )
        assert response.status_code == 200

    except Exception as e:

        raise e
    finally:
        delete_user(user_id, token)
