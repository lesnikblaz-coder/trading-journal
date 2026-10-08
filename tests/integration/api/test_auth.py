# HELPERS
DEFAULT_EMAIL = "test@example.com"
DEFAULT_PASSWORD = "password123"

LOGIN_URL = "/auth/login"
REGISTER_URL = "/auth/register"
REFRESH_URL = "/auth/refresh"
LOGOUT_URL = "/auth/logout"
PROTECTED_URL = "/trading-systems"

async def register_user(
        client,
        email: str = DEFAULT_EMAIL,
        password: str = DEFAULT_PASSWORD,
):
    return await client.post(
        url=REGISTER_URL,
        json={
            "email": email,
            "password": password
        }
    )


# TESTS
async def test_register_success(client):
    response = await register_user(client)

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "Bearer"
    assert "refresh_cookie" in response.cookies


async def test_register_duplicate_email(client):
    # first registration -> success
    await register_user(client)

    # second registration, using the same email -> duplication error
    response = await register_user(client)

    assert response.status_code == 409

async def test_login_success(client):
    await register_user(client)

    response = await client.post(
        url=LOGIN_URL,
        json={
            "email": DEFAULT_EMAIL,
            "password": DEFAULT_PASSWORD,
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert  "access_token" in data
    assert data["token_type"] == "Bearer"
    assert "refresh_cookie" in response.cookies

async def test_login_wrong_password(client):
    await register_user(client)

    response = await client.post(
        url=LOGIN_URL,
        json={
            "email": DEFAULT_EMAIL,
            "password": "incorrect_password"
        },
    )

    assert response.status_code == 401

async def test_login_unknown_email(client):
    response = await client.post(
        url=LOGIN_URL,
        json={
            "email": "doesnotexist@example.com",
            "password": DEFAULT_PASSWORD,
        },
    )

    assert response.status_code == 401

async def test_refresh_success(client):
    await register_user(client)

    login_response = await client.post(
        url=LOGIN_URL,
        json={
            "email": DEFAULT_EMAIL,
            "password": DEFAULT_PASSWORD,
        }
    )

    old_access_token = login_response.json()["access_token"]

    response = await client.post(url=REFRESH_URL)

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "Bearer"

    assert data["access_token"] != old_access_token

    assert "refresh_cookie" in response.cookies

async def test_refresh_rotates_cookie(client):
    await register_user(client)

    login_response = await client.post(
        url=LOGIN_URL,
        json={
            "email": DEFAULT_EMAIL,
            "password": DEFAULT_PASSWORD
        }
    )

    assert login_response.status_code == 200

    old_refresh_token = client.cookies.get("refresh_cookie")

    assert old_refresh_token is not None

    refresh_response = await client.post(url=REFRESH_URL)

    assert refresh_response.status_code == 200

    new_refresh_token = client.cookies.get("refresh_cookie")

    assert new_refresh_token is not None
    assert new_refresh_token != old_refresh_token


# test that old token cannot be reused
# make a separate client and manually give it the old cookie
async def test_old_refresh_token_is_rejected(client):
    await register_user(client)

    await client.post(
        url=LOGIN_URL,
        json={
            "email": DEFAULT_EMAIL,
            "password": DEFAULT_PASSWORD
        }
    )

    old_refresh_token = client.cookies.get("refresh_cookie")

    assert old_refresh_token is not None

    response = await client.post(url=REFRESH_URL)

    assert response.status_code == 200

    # a different client represents someone still
    # holding the old refresh token
    from httpx import AsyncClient, ASGITransport
    from app.main import app

    old_token_client = AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        cookies={
            "refresh_cookie": old_refresh_token
        }
    )

    try:
        response = await old_token_client.post(url=REFRESH_URL)

        assert response.status_code == 401

    finally:
        await old_token_client.aclose()

async def test_logout(client):
    await register_user(client)

    await client.post(
        url=LOGIN_URL,
        json={
            "email": DEFAULT_EMAIL,
            "password": DEFAULT_PASSWORD
        }
    )

    assert client.cookies.get("refresh_cookie") is not None

    response = await client.post(url=LOGOUT_URL)

    assert response.status_code == 204

async def test_logout_revokes_refresh_token(client):
    await register_user(client)

    await client.post(
        url=LOGIN_URL,
        json={
            "email": DEFAULT_EMAIL,
            "password": DEFAULT_PASSWORD
        }
    )

    assert client.cookies.get("refresh_cookie") is not None

    response = await client.post(url=LOGOUT_URL)

    assert response.status_code == 204

    refresh_response = await client.post(url=REFRESH_URL)

    assert refresh_response.status_code == 401

async def test_authenticated_request(client):
    await register_user(client)

    login_response = await client.post(
        url=LOGIN_URL,
        json={
            "email": DEFAULT_EMAIL,
            "password": DEFAULT_PASSWORD
        }
    )

    access_token = login_response.json()["access_token"]

    response = await client.get(
        url=PROTECTED_URL,
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

async def test_protected_endpoint_requires_authentication(client):
    response = await client.get(url=PROTECTED_URL)

    assert response.status_code == 401

async def test_invalid_access_token(client):
    response = await client.get(
        url=PROTECTED_URL,
        headers={
            "Authorization": "Bearer definitely-not-a-real-token"
        }
    )

    assert response.status_code == 401