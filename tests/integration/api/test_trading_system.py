from uuid import UUID

from app.core import security


TSYS_URL = "/trading-systems"


def auth_headers(user_id: UUID):
    token = security.create_access_token(user_id)

    return {
        "Authorization": f"Bearer {token}"
    }


# TESTS
async def test_create_trading_system(
        client,
        system_payload,
        test_user
):
    response = await client.post(
        url=TSYS_URL,
        json=system_payload,
        headers=auth_headers(test_user.id)
    )

    assert response.status_code == 200, response.text

    data = response.json()

    assert data["name"] == system_payload["name"]
    assert data["description"] == system_payload["description"]

    assert data["user_id"] == str(test_user.id)

    assert "id" in data
    assert "created_at" in data

async def test_get_trading_systems(
        client,
        system_payload,
        test_user
):
    post_response = await client.post(
        url=TSYS_URL,
        json=system_payload,
        headers=auth_headers(test_user.id)
    )

    assert post_response.status_code == 200

    get_response = await client.get(
        url=TSYS_URL,
        headers=auth_headers(test_user.id)
    )

    assert get_response.status_code == 200

    data = get_response.json()

    assert len(data) == 1
    assert data[0]["id"] == post_response.json()["id"]

async def test_get_trading_system_by_id(
        client,
        system_payload,
        test_user
):
    post_response = await client.post(
        url=TSYS_URL,
        json=system_payload,
        headers=auth_headers(test_user.id)
    )

    assert post_response.status_code == 200

    post_data = post_response.json()
    system_id = post_data["id"]

    get_response = await client.get(
        url=f"{TSYS_URL}/{system_id}",
        headers=auth_headers(test_user.id)
    )

    assert get_response.status_code == 200

    get_data = get_response.json()
    assert get_data == post_data

async def test_update_trading_system(
        client,
        system_payload,
        test_user
):
    post_response = await client.post(
        url=TSYS_URL,
        json=system_payload,
        headers=auth_headers(test_user.id)
    )

    assert post_response.status_code == 200

    post_data = post_response.json()
    system_id = post_data["id"]

    # update the name
    patch_response = await client.patch(
        url=f"{TSYS_URL}/{system_id}",
        json={
            "name": "Updated System"
        },
        headers=auth_headers(test_user.id)
    )

    assert patch_response.status_code == 200

    patch_data = patch_response.json()

    assert patch_data["name"] == "Updated System"

    # get the system by id to check if it's set in the database
    get_response = await client.get(
        url=f"{TSYS_URL}/{system_id}",
        headers=auth_headers(test_user.id)
    )

    assert get_response.status_code == 200

    get_data = get_response.json()
    assert get_data["name"] == patch_data["name"]

async def test_delete_trading_system(
        client,
        system_payload,
        test_user
):
    post_response = await client.post(
        url=TSYS_URL,
        json=system_payload,
        headers=auth_headers(test_user.id)
    )

    assert post_response.status_code == 200

    post_data = post_response.json()
    system_id = post_data["id"]

    delete_response = await client.delete(
        url=f"{TSYS_URL}/{system_id}",
        headers=auth_headers(test_user.id)
    )

    assert delete_response.status_code == 204

    get_response = await client.get(
        url=TSYS_URL,
        headers=auth_headers(test_user.id)
    )

    assert get_response.status_code == 200
    assert not any(
        system["id"] == system_id
        for system in get_response.json()
    )

# verify that user B cannot retrieve, update or delete user A's system |-> cross user authorization
async def test_cross_user_authorization(
        client,
        test_user,
        test_user_b,
        system_payload
):
    user_a_headers = auth_headers(test_user.id)
    user_b_headers = auth_headers(test_user_b.id)

    post_response = await client.post(
        url=TSYS_URL,
        json=system_payload,
        headers=user_a_headers
    )

    assert post_response.status_code == 200

    post_data = post_response.json()
    system_id = post_data["id"]

    # User B tries retrieving User A's system
    get_response = await client.get(
        url=f"{TSYS_URL}/{system_id}",
        headers=user_b_headers
    )

    assert get_response.status_code == 404

    # User B tries updating User A's system
    patch_response = await client.patch(
        url=f"{TSYS_URL}/{system_id}",
        json={"name": "HACKED"},
        headers=user_b_headers
    )

    assert patch_response.status_code == 404

    # User B tries updating User A's system
    delete_response = await client.delete(
        url=f"{TSYS_URL}/{system_id}",
        headers=user_b_headers
    )

    assert delete_response.status_code == 404

    # Verify User A's system is still intact
    owner_response = await client.get(
        url=f"{TSYS_URL}/{system_id}",
        headers=user_a_headers
    )

    assert owner_response.status_code == 200
    assert owner_response.json()["name"] == system_payload["name"]