import base64
import os
from json import dumps

import requests

from constants import MESSAGES_LIMIT
from tests.lib import client, test_db_media, test_db


def test_list_messages(test_db):
    token = client.post("account/reg", data=dumps({"login": "username", "password": "password"})).json()["token"]
    _ = [client.post("message", data=dumps({"text": f"text {i}"}), headers={"AuthToken": token}) for i in range(50)]

    response = client.get("messages")
    assert response.status_code == 200
    assert response.json() == [{'text': f'text {i}', 'id': i + 1, 'user_id': 1} for i in range(MESSAGES_LIMIT)]

    response = client.get(f"messages?limit={MESSAGES_LIMIT + 2}")
    assert response.status_code == 200
    assert response.json() == [{'text': f'text {i}', 'id': i + 1, 'user_id': 1} for i in range(MESSAGES_LIMIT + 2)]

    response = client.get("messages?offset=3")
    assert response.status_code == 200
    assert response.json() == [{'text': f'text {i + 3}', 'id': i + 4, 'user_id': 1} for i in range(MESSAGES_LIMIT)]

    response = client.get(f"messages?offset=2&limit={MESSAGES_LIMIT + 3}")
    assert response.status_code == 200
    assert response.json() == [{'text': f'text {i + 2}', 'id': i + 3, 'user_id': 1} for i in range(MESSAGES_LIMIT + 3)]


def test_get_message_success(test_db):
    token = client.post("account/reg", data=dumps({"login": "username", "password": "password"})).json()["token"]

    client.post("message", data=dumps({"text": "test text"}), headers={"AuthToken": token})

    response = client.get("message?message_id=1")
    assert response.status_code == 200
    assert response.json() == {'text': 'test text', 'id': 1, 'user_id': 1, 'url': None, 'files': []}


def test_get_message_error_message_not_found(test_db):
    response = client.get("message?message_id=1")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Message not found'}


def test_create_message_success_text(test_db):
    token = client.post("account/reg", data=dumps({"login": "username", "password": "password"})).json()["token"]

    response = client.post("message", data=dumps({"text": "test text"}), headers={"AuthToken": token})
    assert response.status_code == 200
    assert response.json() == {'text': 'test text', 'id': 1, 'user_id': 1, 'url': None, 'files': []}


def test_create_message_success_files(test_db_media):
    token = client.post("account/reg", data=dumps({"login": "username", "password": "password"})).json()["token"]

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

    response = client.post("message", data=dumps({"files": files_to_send}), headers={"AuthToken": token})
    assert response.status_code == 200
    data = response.json()

    # compare files
    for number, file in enumerate(data["files"]):
        with open(os.path.join(os.curdir, "media", file['url'].split('/')[-1]), "rb") as server_file:
            assert base64.b64encode(server_file.read()).decode() == files_to_send[number]["value"]

    del data["files"]
    # compare other data
    assert data == {'text': None, 'id': 1, 'user_id': 1, 'url': None}


def test_create_message_success_url(test_db_media):
    token = client.post("account/reg", data=dumps({"login": "username", "password": "password"})).json()["token"]

    resp = client.post("message", data=dumps({"url": "https://www.opengraph.xyz"}), headers={"AuthToken": token})
    assert resp.status_code == 200
    data = resp.json()

    # compare image
    with open(os.path.join(os.curdir, "media", data["url"]["image"].split('/')[-1]), "rb") as server_file:
        assert server_file.read() == requests.get("https://www.opengraph.xyz/og-opengraph-v2.png").content

    del data["url"]["image"]
    # compare other data
    assert data == {'text': None, 'id': 1, 'user_id': 1, 'files': [],
                    'url': {'id': 1, 'title': 'OpenGraph - Preview Social Media Share and Generate Metatags'}}


def test_create_message_error_empty(test_db):
    token = client.post("account/reg", data=dumps({"login": "username", "password": "password"})).json()["token"]

    response = client.post("message", data=dumps({}), headers={"AuthToken": token})
    assert response.status_code == 404
    assert response.json() == {'detail': 'Must be text or files or url'}


def test_create_message_error_user_not_found(test_db):
    response = client.post("message", data=dumps({"text": "test text"}), headers={"AuthToken": "1"})
    assert response.status_code == 404
    assert response.json() == {'detail': 'User not found'}


def test_delete_message_success(test_db):
    token = client.post("account/reg", data=dumps({"login": "username", "password": "password"})).json()["token"]

    client.post("message", data=dumps({"text": "test text"}), headers={"AuthToken": token})

    response = client.delete("message?message_id=1", headers={"AuthToken": token})
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_delete_message_error_no_message(test_db):
    token = client.post("account/reg", data=dumps({"login": "username", "password": "password"})).json()["token"]

    response = client.delete("message?message_id=1", headers={"AuthToken": token})
    assert response.status_code == 404
    assert response.json() == {"detail": "Message not found"}


def test_delete_message_error_bad_user(test_db):
    token = client.post("account/reg", data=dumps({"login": "username", "password": "password"})).json()["token"]
    bad_token = client.post("account/reg", data=dumps({"login": "bad_user", "password": "password"})).json()["token"]

    client.post("message", data=dumps({"text": "test text"}), headers={"AuthToken": token})

    response = client.delete("message?message_id=1", headers={"AuthToken": bad_token})
    assert response.status_code == 404
    assert response.json() == {"detail": "This user dont has access to message"}


def test_like_success(test_db):
    token = client.post("account/reg", data=dumps({"login": "username", "password": "password"})).json()["token"]

    client.post("message", data=dumps({"text": "test text"}), headers={"AuthToken": token})

    for i in range(1, 4):
        response = client.post("message/like?message_id=1", headers={"AuthToken": token})
        assert response.status_code == 200
        assert response.json() == {'like': bool(i % 2)}


def test_like_success_like_different_for_others(test_db):
    token_1 = client.post("account/reg", data=dumps({"login": "username_1", "password": "password"})).json()["token"]
    token_2 = client.post("account/reg", data=dumps({"login": "username_2", "password": "password"})).json()["token"]

    client.post("message", data=dumps({"text": "test text"}), headers={"AuthToken": token_1})

    assert client.post("message/like?message_id=1", headers={"AuthToken": token_1}).json() == {'like': True}
    assert client.post("message/like?message_id=1", headers={"AuthToken": token_2}).json() == {'like': True}
    assert client.post("message/like?message_id=1", headers={"AuthToken": token_1}).json() == {'like': False}


def test_like_error_bad_message(test_db):
    token = client.post("account/reg", data=dumps({"login": "username", "password": "password"})).json()["token"]

    response = client.post("message/like?message_id=1", headers={"AuthToken": token})
    assert response.status_code == 404
    assert response.json() == {"detail": "Message not found"}


def test_like_error_bad_user(test_db):
    token = client.post("account/reg", data=dumps({"login": "username", "password": "password"})).json()["token"]
    client.post("message", data=dumps({"text": "test text"}), headers={"AuthToken": token})

    response = client.post("message/like?message_id=1", headers={"AuthToken": ""})
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}
