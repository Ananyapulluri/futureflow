from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from bot.logging_config import setup_logging
from bot.validators import (
    validate_side, validate_order_type,
    validate_quantity, validate_price, validate_stop_price,
)
from bot.orders import OrderService

setup_logging()
logger = logging.getLogger(__name__)
app = Flask(__name__)
CORS(app)  # Allow frontend (Vercel) to talk to backend (Render)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "FutureFlow"})


@app.route("/balance", methods=["GET"])
def balance():
    try:
        service = OrderService()
        bal = service.get_balance()
        return jsonify({"success": True, "data": bal})
    except Exception as e:
        logger.error(str(e))
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/order", methods=["POST"])
def place_order():
    body = request.get_json(force=True)
    if not body:
        return jsonify({"success": False, "error": "Request body must be JSON"}), 400
    try:
        symbol     = body.get("symbol", "").upper()
        side       = validate_side(body.get("side", ""))
        order_type = validate_order_type(body.get("type", ""))
        quantity   = validate_quantity(float(body.get("quantity", 0)))
        price      = validate_price(body.get("price"), order_type)
        stop_price = validate_stop_price(body.get("stop_price"), order_type)
        dry_run    = bool(body.get("dry_run", False))

        summary = {
            "symbol": symbol, "side": side, "type": order_type,
            "quantity": quantity, "price": price,
            "stop_price": stop_price, "dry_run": dry_run,
        }

        if dry_run:
            return jsonify({"success": True, "dry_run": True, "order_preview": summary})

        service = OrderService()
        if order_type == "MARKET":
            response = service.place_market_order(symbol, side, quantity)
        elif order_type == "LIMIT":
            response = service.place_limit_order(symbol, side, quantity, price)
        elif order_type == "STOP_MARKET":
            response = service.place_stop_market_order(symbol, side, quantity, stop_price)
        elif order_type == "TAKE_PROFIT_MARKET":
            response = service.place_take_profit_market_order(symbol, side, quantity, stop_price)

        return jsonify({"success": True, "data": response})

    except (ValueError, TypeError) as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        logger.error(str(e))
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
