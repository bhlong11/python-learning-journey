# Crypto P&L Tracker API

![CI](https://github.com/shipbyaeron/python-learning-journey/actions/workflows/ci.yml/badge.svg)

An all-in-one tracker for your crypto positions.

**Live demo v1.0:** https://crypto-pnl-api.onrender.com/docs

## Overview

The Crypto P&L Tracker API is built to become an ultimate crypto portfolio tracker for daily use.

The end goal is not just to manage your positions, but also to calculate the overall ROI of your portfolio. All numbers will be updated in real time using live market prices.

## Features

The API is now at **v1.0**. In this version, you can:

* Get the real-time price of any coin
* Log all your transactions, including both buy and sell
* View your transaction history anytime
* Update or delete transactions when needed

## Tech Stack

* **Framework:** FastAPI
* **Database:** PostgreSQL & ORM (SQLAlchemy)
* **Test:** Pytest
* **CI:** GitHub Actions
* **Frontend:** Streamlit
* **Deployment:** Render + Docker

## API Endpoints

### 1. `/`

**Method:** GET

**Description:**
The default welcome message of the API.

### 2. `/about`

**Method:** GET

**Description:**
Returns basic information about the API, including its name, version, features, and author.

### 3. `/transaction`

**Method:** POST

**Requires API key**

**Description:**
Log a new transaction in the database.

The transaction details include:

* Coin name
* Action, either buy or sell
* Amount, which is the total amount of coins in that transaction
* Price, which is the buy or sell price

The API will then calculate the total weight of the transaction:

`amount × price`

and return the result.

### 4. `/price/{coin_id}`

**Method:** GET

**Description:**
Get the real-time price of any coin using its `coin_id`.

The `coin_id` follows the IDs defined by CoinGecko, such as:

* `bitcoin`
* `ethereum`
* `solana`

If the coin doesn't exist or there is a typo, the API will return:

> "This coin doesn't exist. Try another one."

### 5. `/transactions`

**Method:** GET

**Requires API key**

**Description:**
Get the details of all transaction history.

### 6. `/transactions/{id}`

**Method:** GET

**Requires API key**

**Description:**
Each transaction has its own ID. You can query any transaction by entering its ID.

The API will return the details of the corresponding transaction.

### 7. `/transactions/{id}`

**Method:** DELETE

**Requires API key**

**Description:**
Delete any transaction by entering its ID.

### 8. `/transactions/{id}`

**Method:** PUT

**Requires API key**

**Description:**
Update any transaction when you need to fix or change its details.

To do this, you need to provide the transaction ID and the new details you want to update.

The API will return a success message once the transaction has been successfully updated.

## Authentication

Among the 8 endpoints above, only 3 are open to the public:

* GET `/`
* GET `/about`
* GET `/price/{coin_id}`

The other 5 require an API key:

* POST `/transaction`
* GET `/transactions`
* GET `/transactions/{id}`
* DELETE `/transactions/{id}`
* PUT `/transactions/{id}`

The API key is passed through the request header as `X-API-Key`.

Here's an example using the GET `/transactions` endpoint:

```bash
curl -H "X-API-Key: your-api-key-here" \
  https://crypto-pnl-api.onrender.com/transactions
```

## Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/shipbyaeron/python-learning-journey.git
cd python-learning-journey/fastapi-pnl
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file with:

```env
DATABASE_URL=your_postgres_connection_string
COINGECKO_API_KEY=your_coingecko_api_key
APP_API_KEY=your-api-key
```

### 5. Run the server

```bash
uvicorn main:app --reload
```

### 6. Open the API documentation

Go to:

`http://127.0.0.1:8000/docs`

From there, you can explore and test the API.

## Running Tests

While running tests for the API endpoints, I wanted to avoid touching the production database. That's why there is a separate database used only for testing.

Add the following to your `.env`:

```env
TEST_DATABASE_URL=your_test_postgres_connection_string
```

Then run:

```bash
python -m pytest
```

## Rotating the API Key

If there are any problems with the API key, make sure to rotate it as soon as possible.

You can generate a new key with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

After rotating the key, update it in these 4 places:

1. `fastapi-pnl/.env` for the local API
2. `streamlit-pnl/.env` for the local frontend
3. Render → Environment → `APP_API_KEY` for production
4. GitHub → Settings → Secrets → `APP_API_KEY` for CI

## Future Improvements

### 1. Rate Limiting for GET `/price/{coin_id}`

Since there are only 3 public endpoints and this is probably the most valuable one for users, I think it will be used the most once the app becomes public.

At the same time, the CoinGecko API has a limited number of requests per minute.

That's why I plan to add rate limiting for each IP address, so there is a lower chance of users running into issues while using the API.

### 2. Entry Price & Position ROI

At the moment, all transactions are disconnected from each other.

For the next version, if multiple transactions have the same coin ID, the API will automatically calculate the average entry price based on the transaction details.

From there, combined with the real-time price from CoinGecko, users will be able to see the ROI of each position, including whether it is in the red or green and by how much.

### 3. Portfolio ROI

The transaction details will give a clear picture of the principal capital a user has put into their portfolio.

Combined with the position ROI, the API will calculate and return the overall ROI of the entire portfolio.

All of this will be updated in real time thanks to the CoinGecko API.

### 4. TP/SL

The vision goes beyond just managing a portfolio. I also want this API to help users rebalance their positions.

The end goal is to connect the API with a trading bot, where users can set TP (Take Profit) or SL (Stop Loss) for each position.

Once the price reaches the target, the API will execute the order through the trading bot and update the portfolio accordingly.

All information will be communicated to users before and after the order goes through.

## Final Vision

The current version is just the beginning.

The goal is to gradually turn this from a simple transaction tracker into a complete crypto portfolio management system, where users can track their positions, understand their P&L, monitor their portfolio ROI, and eventually automate their trading strategy.