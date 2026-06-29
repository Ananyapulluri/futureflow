import argparse
import logging
from bot.logging_config import setup_logging
from bot.validators import (
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
    validate_stop_price,
)
from bot.orders import OrderService

def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description="PrimeTradeAI — Binance Futures Testnet Bot")
    parser.add_argument("--symbol",     required=True,  help="Trading symbol e.g. BTCUSDT")
    parser.add_argument("--side",       required=True,  help="BUY or SELL")
    parser.add_argument("--type",       required=True,  help="MARKET | LIMIT | STOP_MARKET | TAKE_PROFIT_MARKET")
    parser.add_argument("--quantity",   type=float, required=True, help="Order quantity")
    parser.add_argument("--price",      type=float, help="Limit price (required for LIMIT orders)")
    parser.add_argument("--stop-price", type=float, dest="stop_price",
                        help="Trigger price (required for STOP_MARKET / TAKE_PROFIT_MARKET)")
    parser.add_argument("--dry-run",    action="store_true",
                        help="Preview order without sending it to the exchange")
    parser.add_argument("--balance",    action="store_true",
                        help="Show USDT account balance before placing order")

    args = parser.parse_args()

    try:
        side       = validate_side(args.side)
        order_type = validate_order_type(args.type)
        quantity   = validate_quantity(args.quantity)
        price      = validate_price(args.price, order_type)
        stop_price = validate_stop_price(args.stop_price, order_type)

        print("\n📋 Order Request Summary")
        print("─" * 30)
        print(f"  Symbol    : {args.symbol.upper()}")
        print(f"  Side      : {side}")
        print(f"  Type      : {order_type}")
        print(f"  Quantity  : {quantity}")
        if price:
            print(f"  Price     : {price}")
        if stop_price:
            print(f"  Stop Price: {stop_price}")
        if args.dry_run:
            print("\n🔍 DRY RUN — order NOT sent to exchange")
            return

        service = OrderService()

        if args.balance:
            bal = service.get_balance()
            print(f"\n💰 Account Balance (USDT)")
            print("─" * 30)
            print(f"  Total     : {bal['balance']:.2f} USDT")
            print(f"  Available : {bal['availableBalance']:.2f} USDT")

        if order_type == "MARKET":
            response = service.place_market_order(args.symbol.upper(), side, quantity)
        elif order_type == "LIMIT":
            response = service.place_limit_order(args.symbol.upper(), side, quantity, price)
        elif order_type == "STOP_MARKET":
            response = service.place_stop_market_order(args.symbol.upper(), side, quantity, stop_price)
        elif order_type == "TAKE_PROFIT_MARKET":
            response = service.place_take_profit_market_order(args.symbol.upper(), side, quantity, stop_price)

        print("\n✅ Order Response")
        print("─" * 30)
        print(f"  Order ID    : {response.get('orderId')}")
        print(f"  Status      : {response.get('status')}")
        print(f"  Executed Qty: {response.get('executedQty')}")
        print(f"  Avg Price   : {response.get('avgPrice')}")
        print("\n✅ Order placed successfully!\n")

    except Exception as e:
        logger.error(str(e))
        print(f"\n❌ Order failed: {e}\n")

if __name__ == "__main__":
    main()
