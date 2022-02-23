import base64
import os

import pytest
import requests
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.crud import create_user, create_message
from constants import MESSAGES_LIMIT as LIMIT

pytestmark = pytest.mark.asyncio(asyncio_mode="strict")


async def test_list_messages(async_client: AsyncClient, db_session: AsyncSession) -> None:
    def pretty(messages: list) -> dict:
        return {'data': messages, 'messages_lem': 50}

    user_id, _ = await create_user(db_session, "username", "password")
    _ = [await create_message(db_session, user_id, text=f"text {i}") for i in range(50)]

    response = await async_client.get("messages")
    assert response.status_code == 200
    assert response.json() == pretty([{'text': f'text {i}', 'id': i + 1, 'user_id': 1} for i in range(LIMIT)])

    response = await async_client.get(f"messages?limit={LIMIT + 2}")
    assert response.status_code == 200
    assert response.json() == pretty([{'text': f'text {i}', 'id': i + 1, 'user_id': 1} for i in range(LIMIT + 2)])

    response = await async_client.get("messages?offset=3")
    assert response.status_code == 200
    assert response.json() == pretty([{'text': f'text {i + 3}', 'id': i + 4, 'user_id': 1} for i in range(LIMIT)])

    response = await async_client.get(f"messages?offset=2&limit={LIMIT + 3}")
    assert response.status_code == 200
    assert response.json() == pretty([{'text': f'text {i + 2}', 'id': i + 3, 'user_id': 1} for i in range(LIMIT + 3)])


async def test_get_message_success(async_client: AsyncClient, db_session: AsyncSession) -> None:
    user_id, _ = await create_user(db_session, "username", "password")
    await create_message(db_session, user_id, text="test text")

    response = await async_client.get("message/1")
    assert response.status_code == 200
    assert response.json() == {'text': 'test text', 'id': 1, 'user_id': 1, 'url': None, 'files': []}


async def test_get_message_error_message_not_found(async_client: AsyncClient, db_session: AsyncSession) -> None:
    response = await async_client.get("message/1")
    assert response.status_code == 401
    assert response.json() == {'detail': 'Message not found'}


async def test_create_message_success_text(async_client: AsyncClient, db_session: AsyncSession) -> None:
    _, token = await create_user(db_session, "username", "password")

    response = await async_client.post("message", json={"text": "text"}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {'text': 'text', 'id': 1, 'user_id': 1, 'url': None, 'files': []}


async def test_create_message_success_files(async_client: AsyncClient, db_session: AsyncSession) -> None:
    _, token = await create_user(db_session, "username", "password")

    # я привык запускать тесты из Pycharm, который запускает тесты из папки тестов, но общие тесты запускаются из корня
    if "tests" in os.listdir(os.curdir):
        path = os.path.join(os.curdir, "tests", "data")
    elif "data" in os.listdir(os.curdir):
        path = os.path.join(os.curdir, "data")
    else:
        assert False

    # я знаю про генераторы списков, но тут логика на мой взгляд слишком большая для него
    files_to_send = []
    for file in os.listdir(path):
        # вроде принято мокать работу с бинарными файлами, но мне не нравится когда проверяют полностью замоканный код,
        # при том, что можно просто положить маленький файл, чтобы проверить на нём и быть на 100% уверенным, что эта
        # часть кода работает
        with open(os.path.join(path, file), "rb") as file_object:
            files_to_send.append({"name": file, "value": base64.b64encode(file_object.read()).decode()})

    re = await async_client.post("message", json={"files": files_to_send}, headers={"Authorization": f"Bearer {token}"})
    assert re.status_code == 200
    data = re.json()

    # compare files
    for number, file in enumerate(data["files"]):
        with open(os.path.join(os.curdir, "media", file['url'].split('/')[-1]), "rb") as server_file:
            assert base64.b64encode(server_file.read()).decode() == files_to_send[number]["value"]

    del data["files"]
    # compare other data
    assert data == {'text': None, 'id': 1, 'user_id': 1, 'url': None}


async def test_create_message_success_url(async_client: AsyncClient, db_session: AsyncSession) -> None:
    _, token = await create_user(db_session, "username", "password")

    resp = await async_client.post("message", json={"url": "https://www.opengraph.xyz"},
                                   headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()

    # compare image
    with open(os.path.join(os.curdir, "media", data["url"]["image"].split('/')[-1]), "rb") as server_file:
        assert server_file.read() == requests.get("https://www.opengraph.xyz/og-opengraph-v2.png").content

    del data["url"]["image"]
    # compare other data
    assert data == {'text': None, 'id': 1, 'user_id': 1, 'files': [],
                    'url': {'id': 1, 'title': 'OpenGraph - Preview Social Media Share and Generate Metatags'}}


async def test_create_message_error_empty(async_client: AsyncClient, db_session: AsyncSession) -> None:
    _, token = await create_user(db_session, "username", "password")

    response = await async_client.post("message", json={}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert response.json() == {'detail': 'Must be text or files or url'}


async def test_create_message_error_user_not_found(async_client: AsyncClient, db_session: AsyncSession) -> None:
    response = await async_client.post("message", json={"text": "test text"}, headers={"Authorization": f"Bearer 1"})
    assert response.status_code == 401
    assert response.json() == {'detail': 'User not found'}


async def test_delete_message_success(async_client: AsyncClient, db_session: AsyncSession) -> None:
    user_id, token = await create_user(db_session, "username", "password")
    await create_message(db_session, user_id, text="test text")

    response = await async_client.delete("message/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_delete_message_error_no_message(async_client: AsyncClient, db_session: AsyncSession) -> None:
    _, token = await create_user(db_session, "username", "password")

    response = await async_client.delete("message/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Message not found"}


async def test_delete_message_error_bad_user(async_client: AsyncClient, db_session: AsyncSession) -> None:
    user_id, token = await create_user(db_session, "username_1", "password")
    _, bad_t = await create_user(db_session, "username_2", "password")
    await create_message(db_session, user_id, text="test text")

    response = await async_client.delete("message/1", headers={"Authorization": f"Bearer {bad_t}"})
    assert response.status_code == 404
    assert response.json() == {"detail": "This user dont has access to message"}


async def test_like_success(async_client: AsyncClient, db_session: AsyncSession) -> None:
    user_id, token = await create_user(db_session, "username", "password")
    await create_message(db_session, user_id, text="test text")

    for i in range(1, 4):
        is_dis = "" if bool(i % 2) else "dis"
        response = await async_client.post(f"message/{is_dis}like/1", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json() == {'like': bool(i % 2)}


async def test_like_success_like_different_for_others(async_client: AsyncClient, db_session: AsyncSession) -> None:
    user_id, t1 = await create_user(db_session, "username_1", "password")
    _, t2 = await create_user(db_session, "username_2", "password")
    await create_message(db_session, user_id, text="test text")

    assert (await async_client.post("message/like/1", headers={"Authorization": f"Bearer {t1}"})).json()['like']
    assert (await async_client.post("message/like/1", headers={"Authorization": f"Bearer {t2}"})).json()['like']
    assert not (await async_client.post("message/dislike/1", headers={"Authorization": f"Bearer {t1}"})).json()['like']


async def test_like_error_bad_message(async_client: AsyncClient, db_session: AsyncSession) -> None:
    _, token = await create_user(db_session, "username", "password")

    response = await async_client.post("message/like/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Message not found"}


async def test_like_error_bad_user(async_client: AsyncClient, db_session: AsyncSession) -> None:
    user_id, token = await create_user(db_session, "username", "password")
    await create_message(db_session, user_id, text="test text")

    response = await async_client.post("message/like/1", headers={"Authorization": "Bearer"})
    assert response.status_code == 401
    assert response.json() == {"detail": "User not found"}
