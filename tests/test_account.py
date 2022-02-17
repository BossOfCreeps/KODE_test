import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_reg_success(async_client: AsyncClient) -> None:
    response = await async_client.post("account/reg", json={"login": "username", "password": "password"})
    assert response.status_code == 200
    assert "token" in response.json()


async def test_reg_error_already_reg(async_client: AsyncClient):
    await async_client.post("account/reg", json={"login": "username", "password": "password"})
    response = await async_client.post("account/reg", json={"login": "username", "password": "password"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Login already registered"}


async def test_login_success(async_client: AsyncClient):
    await async_client.post("account/reg", json={"login": "username", "password": "password"})
    response = await async_client.post("account/login", json={"login": "username", "password": "password"})
    assert response.status_code == 200
    assert "token" in response.json()


async def test_login_error_no_user(async_client: AsyncClient):
    response = await async_client.post("account/login", json={"login": "username", "password": "password"})
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


async def test_login_error_bad_password(async_client: AsyncClient):
    await async_client.post("account/reg", json={"login": "username", "password": "password"})
    response = await async_client.post("account/login", json={"login": "username", "password": "bad_password"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Bad password"}
