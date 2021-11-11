from fastapi.testclient import TestClient
import main
import pytest
from test.comments_test import сreate_user_for_test, delete_user
from test.posts_test import create_post, delete_post


@pytest.fixture(scope="module")
def client():
    with TestClient(main.app) as client:
        yield client


def test_likes_crud(client: TestClient):
    user_id, token = сreate_user_for_test()
    post_id = create_post(client, user_id)
    headers = {'Content-Type': 'application/json'}
    try:
        params = {'user_id': user_id}
        data = {'post_id': post_id}
        response = client.post(
            '/feed/like/create', json=data, params=params, headers=headers
        )
        assert response.status_code == 201
        response = client.get('/feed/like')
        assert response.status_code == 200
        response = client.delete(
            '/feed/like/delete', json=data, params=params, headers=headers
        )
        assert response.status_code == 200
    except Exception as e:
        raise e
    finally:
        delete_post(client, user_id, post_id)
        delete_user(user_id, token)
