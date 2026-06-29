# PrimeTradeAI — Binance Futures Testnet Trading Bot

A Python CLI + REST API application to place orders on Binance USDT-M Futures Testnet.

---

## Features
- **Order types:** MARKET, LIMIT, STOP_MARKET, TAKE_PROFIT_MARKET
- **BUY and SELL** support
- **`--dry-run` mode** — preview orders without hitting the exchange
- **`--balance` flag** — check USDT balance before placing an order
- **Flask REST API** — same functionality over HTTP
- **44 unit tests** with full mocking (no API key needed to test)
- Rotating file + console logging

---

## Setup

### 1. Install dependencies
```
pip install -r requirements.txt
```

### 2. Create `.env` file
```
BINANCE_API_KEY=your_testnet_api_key
BINANCE_API_SECRET=your_testnet_api_secret
```
Get keys at: https://testnet.binancefuture.com

---

## CLI Usage

```bash
# Market order
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

# Limit order
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 52000

# Stop market (triggers market sell if price drops to 45000)
python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.001 --stop-price 45000

# Take profit market (triggers market sell if price rises to 60000)
python cli.py --symbol BTCUSDT --side SELL --type TAKE_PROFIT_MARKET --quantity 0.001 --stop-price 60000

# Dry run — preview without sending
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001 --dry-run

# Check balance before ordering
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001 --balance
```

---

## Flask API Usage

### Start server
```bash
python app.py
```

### Endpoints

| Method | Endpoint   | Description           |
|--------|------------|-----------------------|
| GET    | /health    | Health check          |
| GET    | /balance   | USDT account balance  |
| POST   | /order     | Place an order        |

### Example requests

```bash
# Health check
curl http://localhost:5000/health

# Balance
curl http://localhost:5000/balance

# Market order
curl -X POST http://localhost:5000/order \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BTCUSDT","side":"BUY","type":"MARKET","quantity":0.001}'

# Dry run
curl -X POST http://localhost:5000/order \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BTCUSDT","side":"BUY","type":"LIMIT","quantity":0.001,"price":50000,"dry_run":true}'

# Stop market
curl -X POST http://localhost:5000/order \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BTCUSDT","side":"SELL","type":"STOP_MARKET","quantity":0.001,"stop_price":45000}'
```

---

## Run Tests

```bash
python -m pytest tests/ -v
```

---

## Project Structure

```
primetradeai/
├── cli.py              # CLI entry point
├── app.py              # Flask REST API
├── requirements.txt
├── .env                # API keys (not committed)
├── bot/
│   ├── client.py       # Binance client wrapper
│   ├── orders.py       # OrderService (MARKET/LIMIT/STOP/TP)
│   ├── validators.py   # Input validation
│   └── logging_config.py
├── tests/
│   ├── test_validators.py
│   ├── test_orders.py
│   └── test_api.py
└── logs/
    └── trading_bot.log
```
