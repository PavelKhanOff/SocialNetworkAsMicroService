from fastapi.testclient import TestClient
import main
import pytest
import requests
from test.comments_test import сreate_user_for_test, delete_user


@pytest.fixture(scope="module")
def client():
    with TestClient(main.app) as client:
        yield client


def create_post(client, user_id):
    params = {'user_id': user_id}
    data = {"title": "string", "description": "string", "image": "string"}
    response = client.post('/feed/post/create', json=data, params=params)
    post_id = response.json().get('id')
    return post_id


def delete_post(client, user_id, post_id):
    params = {'user_id': user_id}
    client.delete(f'/feed/post/{post_id}', params=params)


def test_posts_crud(client: TestClient):
    user_id, token = сreate_user_for_test()
    print(user_id, token)
    try:
        params = {'user_id': user_id}
        data = {"title": "string", "description": "string", "image": "string"}
        response = client.post('/feed/post/create', json=data, params=params)
        post_id = response.json().get('id')
        assert response.status_code == 201
        response = client.get('/feed/posts/')
        assert response.status_code == 200
        response = client.get(f'/feed/post/{post_id}')
        assert response.status_code == 200
        data_updated = {"title": "updated", "description": "string", "image": "string"}
        response = client.patch(
            f'/feed/post/{post_id}/update', json=data_updated, params=params
        )
        assert response.status_code == 200
        response = client.delete(f'/feed/post/{post_id}', params=params)
        assert response.status_code == 200
        response = client.get(f'/feed/post/{post_id}/likes')
        assert response.status_code == 200
    except requests.exceptions.ConnectionError:
        print('sa')
    finally:
        delete_user(user_id, token)
