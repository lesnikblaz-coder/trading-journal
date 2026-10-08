from decimal import Decimal

from app import enums


TSYS_URL = "/trading-systems"
TRADE_URL = "/trades"

# TESTS
async def test_create_active_trade(
        client,
        test_user,
        trade_payload,
        trading_system,
        auth_headers
):
    trade = trade_payload()

    response = await client.post(
        url=f"{TSYS_URL}/{trading_system["id"]}{TRADE_URL}",
        headers=auth_headers(test_user.id),
        json=trade
    )

    assert response.status_code == 200

    data = response.json()

    # quantity correctness check
    _expected_quantity = (
            Decimal(trade["dollar_risk"])
            /
            abs((Decimal(trade["entry_price"]) - Decimal(trade["stop_loss_price"])))
    )

    assert data["quantity"] is not None
    assert Decimal(data["quantity"]) == _expected_quantity

    # status correctness check
    assert data["status"] == enums.TradeStatus.ACTIVE

    assert data["realized_pnl"] is None
    assert data["realized_pnl_percent"] is None
    assert data["result_r"] is None

async def test_create_closed_trade(
        client,
        test_user,
        trade_payload,
        trading_system,
        auth_headers
):
    trade = trade_payload(
        exit_price="110"
    )

    response = await client.post(
        url=f"{TSYS_URL}/{trading_system["id"]}{TRADE_URL}",
        headers=auth_headers(test_user.id),
        json=trade
    )

    assert response.status_code == 200

    data = response.json()

    assert data["exit_price"] == "110"

    assert data["status"] == enums.TradeStatus.CLOSED

    assert Decimal(data["realized_pnl"]) == Decimal("2000")
    assert Decimal(data["realized_pnl_percent"]) == Decimal("2")
    assert Decimal(data["result_r"]) == Decimal("2")

async def test_update_trade(
        client,
        test_user,
        trade_payload,
        trading_system,
        auth_headers
):
    # trade created with ACTIVE status
    trade = trade_payload()

    post_response = await client.post(
        url=f"{TSYS_URL}/{trading_system["id"]}{TRADE_URL}",
        headers=auth_headers(test_user.id),
        json=trade
    )

    assert post_response.status_code == 200

    data = post_response.json()
    trade_id = data["id"]

    assert data["status"] == enums.TradeStatus.ACTIVE

    # update trade with exit price so status is CLOSED
    patch_response = await client.patch(
        url=f"{TRADE_URL}/{trade_id}",
        headers=auth_headers(test_user.id),
        json={
            "exit_price": "110"
        }
    )

    assert patch_response.status_code == 200

    get_response = await client.get(
        url=f"{TRADE_URL}/{trade_id}",
        headers=auth_headers(test_user.id)
    )

    assert get_response.status_code == 200

    updated_data = get_response.json()

    assert updated_data["status"] == enums.TradeStatus.CLOSED
    assert Decimal(updated_data["exit_price"]) == Decimal("110")
    assert Decimal(updated_data["realized_pnl"]) == Decimal("2000")
    assert Decimal(updated_data["realized_pnl_percent"]) == Decimal("2")
    assert Decimal(updated_data["result_r"]) == Decimal("2")

async def test_delete_trade(
        client,
        test_user,
        trade_payload,
        trading_system,
        auth_headers
):
    trade = trade_payload()

    post_response = await client.post(
        url=f"{TSYS_URL}/{trading_system["id"]}{TRADE_URL}",
        headers=auth_headers(test_user.id),
        json=trade
    )

    assert post_response.status_code == 200

    data = post_response.json()
    trade_id = data["id"]

    delete_response = await client.delete(
        url=f"{TRADE_URL}/{trade_id}",
        headers=auth_headers(test_user.id)
    )

    assert delete_response.status_code == 204

    get_response = await client.get(
        url=f"{TRADE_URL}/{trade_id}",
        headers=auth_headers(test_user.id)
    )

    assert get_response.status_code == 404

# Verify User B cannot access, modify, or delete User A's trades
async def test_cross_user_authorization(
        client,
        test_user,
        test_user_b,
        trade_payload,
        trading_system,
        auth_headers
):
    user_a_headers = auth_headers(test_user.id)
    user_b_headers = auth_headers(test_user_b.id)

    trade = trade_payload()

    post_response = await client.post(
        url=f"{TSYS_URL}/{trading_system["id"]}{TRADE_URL}",
        headers=user_a_headers,
        json=trade
    )

    assert post_response.status_code == 200
    data = post_response.json()
    trade_id = data["id"]

    # User B tries retrieving User A's trade
    get_response = await client.get(
        url=f"{TRADE_URL}/{trade_id}",
        headers=user_b_headers
    )

    assert get_response.status_code == 404

    # User B tries updating User A's trade
    patch_response = await client.patch(
        url=f"{TRADE_URL}/{trade_id}",
        headers=user_b_headers,
        json={
            "symbol": "AMZN"
        }
    )

    assert patch_response.status_code == 404

    # User B tries deleting User A's trade
    delete_response = await client.delete(
        url=f"{TRADE_URL}/{trade_id}",
        headers=user_b_headers
    )

    assert delete_response.status_code == 404

    # Verify User A's trade is still intact
    owner_response = await client.get(
        url=f"{TRADE_URL}/{trade_id}",
        headers=user_a_headers
    )

    assert owner_response.status_code == 200
    assert owner_response.json()["symbol"] == trade["symbol"]

async def test_cross_user_trade_creation(
        client,
        test_user,
        test_user_b,
        trade_payload,
        trading_system,
        auth_headers
):
    user_b_headers = auth_headers(test_user_b.id)

    trade = trade_payload()

    # User B tries to create a trade inside User A's trading system
    post_response = await client.post(
        url=f"{TSYS_URL}/{trading_system["id"]}{TRADE_URL}",
        headers=user_b_headers,
        json=trade
    )

    assert post_response.status_code == 401