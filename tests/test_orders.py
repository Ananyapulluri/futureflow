import pytest
from unittest.mock import MagicMock, patch
from bot.orders import OrderService


MOCK_ORDER_RESPONSE = {
    "orderId": 123456,
    "symbol": "BTCUSDT",
    "status": "FILLED",
    "executedQty": "0.001",
    "avgPrice": "50000.00",
}

MOCK_BALANCE_RESPONSE = [
    {"asset": "USDT", "balance": "10000.00", "availableBalance": "8500.00"},
    {"asset": "BNB",  "balance": "1.00",     "availableBalance": "1.00"},
]


@pytest.fixture
def mock_service():
    """OrderService with mocked BinanceFuturesClient."""
    with patch("bot.orders.BinanceFuturesClient") as MockClient:
        instance = MockClient.return_value
        instance.place_order.return_value = MOCK_ORDER_RESPONSE
        instance.get_account_balance.return_value = {
            "asset": "USDT",
            "balance": 10000.0,
            "availableBalance": 8500.0,
        }
        service = OrderService()
        service.client = instance
        yield service, instance


class TestOrderService:
    def test_place_market_order(self, mock_service):
        service, mock_client = mock_service
        result = service.place_market_order("BTCUSDT", "BUY", 0.001)
        mock_client.place_order.assert_called_once_with(
            symbol="BTCUSDT", side="BUY", type="MARKET", quantity=0.001
        )
        assert result["orderId"] == 123456
        assert result["status"] == "FILLED"

    def test_place_limit_order(self, mock_service):
        service, mock_client = mock_service
        result = service.place_limit_order("BTCUSDT", "SELL", 0.001, 52000)
        mock_client.place_order.assert_called_once_with(
            symbol="BTCUSDT", side="SELL", type="LIMIT",
            quantity=0.001, price=52000, timeInForce="GTC"
        )
        assert result["orderId"] == 123456

    def test_place_stop_market_order(self, mock_service):
        service, mock_client = mock_service
        result = service.place_stop_market_order("BTCUSDT", "SELL", 0.001, 45000)
        mock_client.place_order.assert_called_once_with(
            symbol="BTCUSDT", side="SELL", type="STOP_MARKET",
            quantity=0.001, stopPrice=45000
        )
        assert result["status"] == "FILLED"

    def test_place_take_profit_market_order(self, mock_service):
        service, mock_client = mock_service
        result = service.place_take_profit_market_order("BTCUSDT", "SELL", 0.001, 60000)
        mock_client.place_order.assert_called_once_with(
            symbol="BTCUSDT", side="SELL", type="TAKE_PROFIT_MARKET",
            quantity=0.001, stopPrice=60000
        )

    def test_get_balance(self, mock_service):
        service, mock_client = mock_service
        bal = service.get_balance()
        assert bal["asset"] == "USDT"
        assert bal["balance"] == 10000.0
        assert bal["availableBalance"] == 8500.0

    def test_place_order_propagates_exception(self, mock_service):
        service, mock_client = mock_service
        mock_client.place_order.side_effect = RuntimeError("API down")
        with pytest.raises(RuntimeError, match="API down"):
            service.place_market_order("BTCUSDT", "BUY", 0.001)
