from httpx import AsyncClient

REGISTER_PAYLOAD = {
    "email": "auth@example.com",
    "password": "hunter2hunter2",
    "display_name": "Auth Test",
    "timezone": "Europe/Tallinn",
}


async def test_register_returns_token_pair(client: AsyncClient) -> None:
    response = await client.post("/auth/register", json=REGISTER_PAYLOAD)

    assert response.status_code == 201
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body


async def test_register_duplicate_email_rejected(client: AsyncClient) -> None:
    await client.post("/auth/register", json=REGISTER_PAYLOAD)
    response = await client.post("/auth/register", json=REGISTER_PAYLOAD)

    assert response.status_code == 409


async def test_login_success(client: AsyncClient) -> None:
    await client.post("/auth/register", json=REGISTER_PAYLOAD)

    response = await client.post(
        "/auth/login",
        json={"email": REGISTER_PAYLOAD["email"], "password": REGISTER_PAYLOAD["password"]},
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


async def test_login_wrong_password_rejected(client: AsyncClient) -> None:
    await client.post("/auth/register", json=REGISTER_PAYLOAD)

    response = await client.post(
        "/auth/login",
        json={"email": REGISTER_PAYLOAD["email"], "password": "wrong password"},
    )

    assert response.status_code == 401


async def test_refresh_returns_new_token_pair(client: AsyncClient) -> None:
    register = await client.post("/auth/register", json=REGISTER_PAYLOAD)
    refresh_token = register.json()["refresh_token"]

    response = await client.post("/auth/refresh", json={"refresh_token": refresh_token})

    assert response.status_code == 200
    assert "access_token" in response.json()


async def test_refresh_rejects_access_token(client: AsyncClient) -> None:
    register = await client.post("/auth/register", json=REGISTER_PAYLOAD)
    access_token = register.json()["access_token"]

    response = await client.post("/auth/refresh", json={"refresh_token": access_token})

    assert response.status_code == 401


async def test_me_unauthorised_without_token(client: AsyncClient) -> None:
    response = await client.get("/auth/me")

    assert response.status_code in (401, 403)
