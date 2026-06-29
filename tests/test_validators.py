import pytest
from bot.validators import (
    validate_side, validate_order_type,
    validate_quantity, validate_price, validate_stop_price,
    VALID_SIDES, VALID_ORDER_TYPES,
)

# ── validate_side ──────────────────────────────────────────
class TestValidateSide:
    def test_buy_lowercase(self):
        assert validate_side("buy") == "BUY"

    def test_sell_uppercase(self):
        assert validate_side("SELL") == "SELL"

    def test_mixed_case(self):
        assert validate_side("Buy") == "BUY"

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="side must be one of"):
            validate_side("HOLD")

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            validate_side("")


# ── validate_order_type ────────────────────────────────────
class TestValidateOrderType:
    @pytest.mark.parametrize("ot", VALID_ORDER_TYPES)
    def test_all_valid_types(self, ot):
        assert validate_order_type(ot) == ot

    def test_lowercase_normalised(self):
        assert validate_order_type("market") == "MARKET"

    def test_invalid_raises(self):
        with pytest.raises(ValueError, match="order_type must be one of"):
            validate_order_type("STOP_LOSS")


# ── validate_quantity ──────────────────────────────────────
class TestValidateQuantity:
    def test_valid_quantity(self):
        assert validate_quantity(0.001) == 0.001

    def test_large_quantity(self):
        assert validate_quantity(1000) == 1000

    def test_zero_raises(self):
        with pytest.raises(ValueError, match="quantity must be > 0"):
            validate_quantity(0)

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            validate_quantity(-5)


# ── validate_price ─────────────────────────────────────────
class TestValidatePrice:
    def test_limit_with_valid_price(self):
        assert validate_price(50000, "LIMIT") == 50000

    def test_market_price_none_ok(self):
        assert validate_price(None, "MARKET") is None

    def test_limit_price_none_raises(self):
        with pytest.raises(ValueError, match="price is required"):
            validate_price(None, "LIMIT")

    def test_limit_price_zero_raises(self):
        with pytest.raises(ValueError):
            validate_price(0, "LIMIT")

    def test_limit_price_negative_raises(self):
        with pytest.raises(ValueError):
            validate_price(-100, "LIMIT")


# ── validate_stop_price ────────────────────────────────────
class TestValidateStopPrice:
    def test_stop_market_valid(self):
        assert validate_stop_price(45000, "STOP_MARKET") == 45000

    def test_take_profit_valid(self):
        assert validate_stop_price(60000, "TAKE_PROFIT_MARKET") == 60000

    def test_market_no_stop_price_ok(self):
        assert validate_stop_price(None, "MARKET") is None

    def test_stop_market_none_raises(self):
        with pytest.raises(ValueError, match="stop_price is required"):
            validate_stop_price(None, "STOP_MARKET")

    def test_stop_market_zero_raises(self):
        with pytest.raises(ValueError):
            validate_stop_price(0, "STOP_MARKET")
