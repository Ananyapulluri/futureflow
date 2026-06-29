import pytest
import json
from unittest.mock import patch, MagicMock
from app import app


MOCK_ORDER = {
    "orderId": 999,
    "status": "FILLED",
    "executedQty": "0.001",
    "avgPrice": "50000.00",
}

MOCK_BALANCE = {
    "asset": "USDT",
    "balance": 10000.0,
    "availableBalance": 8500.0,
}


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


class TestHealthEndpoint:
    def test_health_ok(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.get_json()["status"] == "ok"


class TestBalanceEndpoint:
    def test_balance_success(self, client):
        with patch("app.OrderService") as MockSvc:
            MockSvc.return_value.get_balance.return_value = MOCK_BALANCE
            r = client.get("/balance")
            assert r.status_code == 200
            data = r.get_json()
            assert data["success"] is True
            assert data["data"]["balance"] == 10000.0

    def test_balance_error(self, client):
        with patch("app.OrderService") as MockSvc:
            MockSvc.return_value.get_balance.side_effect = RuntimeError("creds missing")
            r = client.get("/balance")
            assert r.status_code == 500
            assert r.get_json()["success"] is False


class TestOrderEndpoint:
    def _post(self, client, body):
        return client.post("/order", data=json.dumps(body), content_type="application/json")

    def test_dry_run_market(self, client):
        r = self._post(client, {
            "symbol": "BTCUSDT", "side": "BUY",
            "type": "MARKET", "quantity": 0.001, "dry_run": True
        })
        assert r.status_code == 200
        data = r.get_json()
        assert data["dry_run"] is True
        assert data["order_preview"]["type"] == "MARKET"

    def test_dry_run_limit(self, client):
        r = self._post(client, {
            "symbol": "ETHUSDT", "side": "SELL",
            "type": "LIMIT", "quantity": 0.1, "price": 3000, "dry_run": True
        })
        assert r.status_code == 200
        assert r.get_json()["order_preview"]["price"] == 3000

    def test_market_order_live(self, client):
        with patch("app.OrderService") as MockSvc:
            MockSvc.return_value.place_market_order.return_value = MOCK_ORDER
            r = self._post(client, {
                "symbol": "BTCUSDT", "side": "BUY",
                "type": "MARKET", "quantity": 0.001
            })
            assert r.status_code == 200
            assert r.get_json()["data"]["orderId"] == 999

    def test_limit_order_live(self, client):
        with patch("app.OrderService") as MockSvc:
            MockSvc.return_value.place_limit_order.return_value = MOCK_ORDER
            r = self._post(client, {
                "symbol": "BTCUSDT", "side": "BUY",
                "type": "LIMIT", "quantity": 0.001, "price": 50000
            })
            assert r.status_code == 200

    def test_stop_market_order(self, client):
        with patch("app.OrderService") as MockSvc:
            MockSvc.return_value.place_stop_market_order.return_value = MOCK_ORDER
            r = self._post(client, {
                "symbol": "BTCUSDT", "side": "SELL",
                "type": "STOP_MARKET", "quantity": 0.001, "stop_price": 45000
            })
            assert r.status_code == 200

    def test_take_profit_order(self, client):
        with patch("app.OrderService") as MockSvc:
            MockSvc.return_value.place_take_profit_market_order.return_value = MOCK_ORDER
            r = self._post(client, {
                "symbol": "BTCUSDT", "side": "SELL",
                "type": "TAKE_PROFIT_MARKET", "quantity": 0.001, "stop_price": 60000
            })
            assert r.status_code == 200

    def test_invalid_side_returns_400(self, client):
        r = self._post(client, {
            "symbol": "BTCUSDT", "side": "HODL",
            "type": "MARKET", "quantity": 0.001
        })
        assert r.status_code == 400
        assert r.get_json()["success"] is False

    def test_limit_missing_price_returns_400(self, client):
        r = self._post(client, {
            "symbol": "BTCUSDT", "side": "BUY",
            "type": "LIMIT", "quantity": 0.001
        })
        assert r.status_code == 400

    def test_stop_market_missing_stop_price_returns_400(self, client):
        r = self._post(client, {
            "symbol": "BTCUSDT", "side": "SELL",
            "type": "STOP_MARKET", "quantity": 0.001
        })
        assert r.status_code == 400

    def test_missing_body_returns_400(self, client):
        r = client.post("/order")
        assert r.status_code == 400
