from json import dumps

from tests.lib import client, test_db


def test_reg_success(test_db):
    response = client.post("account/reg", data=dumps({"login": "username", "password": "password"}))
    assert response.status_code == 200
    assert "token" in response.json()


def test_reg_error_already_reg(test_db):
    client.post("account/reg", data=dumps({"login": "username", "password": "password"}))
    response = client.post("account/reg", data=dumps({"login": "username", "password": "password"}))
    assert response.status_code == 400
    assert response.json() == {"detail": "Login already registered"}


def test_login_success(test_db):
    client.post("account/reg", data=dumps({"login": "username", "password": "password"}))
    response = client.post("account/login", data=dumps({"login": "username", "password": "password"}))
    assert response.status_code == 200
    assert "token" in response.json()


def test_login_error_no_user(test_db):
    response = client.post("account/login", data=dumps({"login": "username", "password": "password"}))
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_login_error_bad_password(test_db):
    client.post("account/reg", data=dumps({"login": "username", "password": "password"}))
    response = client.post("account/login", data=dumps({"login": "username", "password": "bad_password"}))
    assert response.status_code == 404
    assert response.json() == {"detail": "Bad password"}

