import logging
from .client import BinanceFuturesClient

logger = logging.getLogger(__name__)

class OrderService:
    def __init__(self):
        self.client = BinanceFuturesClient()

    def get_balance(self):
        """Return USDT balance dict."""
        return self.client.get_account_balance()

    def place_market_order(self, symbol: str, side: str, quantity: float) -> dict:
        return self.client.place_order(
            symbol=symbol,
            side=side,
            type="MARKET",
            quantity=quantity,
        )

    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float) -> dict:
        return self.client.place_order(
            symbol=symbol,
            side=side,
            type="LIMIT",
            quantity=quantity,
            price=price,
            timeInForce="GTC",
        )

    def place_stop_market_order(self, symbol: str, side: str, quantity: float, stop_price: float) -> dict:
        """Place a STOP_MARKET order — triggers a market order when stopPrice is hit."""
        return self.client.place_order(
            symbol=symbol,
            side=side,
            type="STOP_MARKET",
            quantity=quantity,
            stopPrice=stop_price,
        )

    def place_take_profit_market_order(self, symbol: str, side: str, quantity: float, stop_price: float) -> dict:
        """Place a TAKE_PROFIT_MARKET order — closes position at profit when stopPrice is hit."""
        return self.client.place_order(
            symbol=symbol,
            side=side,
            type="TAKE_PROFIT_MARKET",
            quantity=quantity,
            stopPrice=stop_price,
        )
