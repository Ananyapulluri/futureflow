VALID_SIDES = ("BUY", "SELL")
VALID_ORDER_TYPES = ("MARKET", "LIMIT", "STOP_MARKET", "TAKE_PROFIT_MARKET")
TRIGGER_REQUIRED_TYPES = ("STOP_MARKET", "TAKE_PROFIT_MARKET")

def validate_side(side: str) -> str:
    side = side.upper()
    if side not in VALID_SIDES:
        raise ValueError(f"side must be one of: {', '.join(VALID_SIDES)}")
    return side

def validate_order_type(order_type: str) -> str:
    order_type = order_type.upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(f"order_type must be one of: {', '.join(VALID_ORDER_TYPES)}")
    return order_type

def validate_quantity(qty: float) -> float:
    if qty <= 0:
        raise ValueError("quantity must be > 0")
    return qty

def validate_price(price, order_type: str):
    if order_type == "LIMIT":
        if price is None or price <= 0:
            raise ValueError("price is required and must be > 0 for LIMIT orders")
    return price

def validate_stop_price(stop_price, order_type: str):
    if order_type in TRIGGER_REQUIRED_TYPES:
        if stop_price is None or stop_price <= 0:
            raise ValueError(f"stop_price is required and must be > 0 for {order_type} orders")
    return stop_price
