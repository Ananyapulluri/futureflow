import logging
import os
from binance.client import Client
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class BinanceFuturesClient:
    def __init__(self):
        api_key = os.getenv("BINANCE_API_KEY")
        api_secret = os.getenv("BINANCE_API_SECRET")

        if not api_key or not api_secret:
            raise RuntimeError("Missing Binance API credentials in .env")

        self.client = Client(
            api_key=api_key,
            api_secret=api_secret,
            testnet=True
        )

        # FIX: Use the correct Futures testnet base URL (fapi path)
        self.client.FUTURES_TESTNET_URL = "https://testnet.binancefuture.com/fapi"

        logger.info("Binance Futures Testnet client initialized")

    def place_order(self, **kwargs):
        logger.info(f"Placing order request: {kwargs}")
        try:
            response = self.client.futures_create_order(**kwargs)
            logger.info(f"Order response: {response}")
            return response
        except Exception:
            logger.exception("Binance API error")
            raise

    def get_account_balance(self):
        """Fetch USDT balance from Futures testnet account."""
        try:
            balances = self.client.futures_account_balance()
            for b in balances:
                if b["asset"] == "USDT":
                    return {
                        "asset": "USDT",
                        "balance": float(b["balance"]),
                        "availableBalance": float(b["availableBalance"]),
                    }
            return {"asset": "USDT", "balance": 0.0, "availableBalance": 0.0}
        except Exception:
            logger.exception("Failed to fetch account balance")
            raise
