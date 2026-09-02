from fastapi import FastAPI, HTTPException, Depends, Header, Request
from pydantic import BaseModel
import httpx
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from models import Transaction
from datetime import datetime

load_dotenv()
dataURL = os.getenv("DATABASE_URL")

engine = create_engine(dataURL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    http_client = httpx.AsyncClient()
    app.state.http_client = http_client
    yield
    await http_client.aclose()

app = FastAPI(lifespan=lifespan)

def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

API_KEY = os.getenv("APP_API_KEY")
if not API_KEY:
    raise ValueError("Security error! Pls add the APP_API_KEY to .env to run this")

class TransactionIn(BaseModel):
    coin: str
    action: str
    amount: float
    price: float

class TransactionOut(BaseModel):
    id: int
    coin: str
    action: str
    amount: float
    price: float
    total: float
    created_at: datetime | None

class TransactionOutMessage(BaseModel):
    message: str
    data: TransactionOut

def get_db():
    with SessionLocal() as session:
        yield session

def check_auth(x_api_key: str | None = Header(None)):
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key!")

@app.get("/")
def read_root():
    return {"message":"Hello, this is my Crypto P&L API"}

@app.get("/about")
def about():
    return {"name":"Crypto P&L Tracker", "version":"v1.0", "feature":"Tracking crypto position & Calculating ROI", "author":"Aeron"}

@app.post("/transaction", dependencies=[Depends(check_auth)], response_model=TransactionOutMessage)
def create_transaction(tx: TransactionIn, session = Depends(get_db)):
    if tx.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount value")
    elif tx.price <= 0:
        raise HTTPException(status_code=400, detail="Invalid price")
    else:
        total = tx.amount * tx.price
        tx_add = Transaction(coin=tx.coin, action=tx.action, amount=tx.amount, price=tx.price, total=total)
        session.add(tx_add)
        session.commit()
        session.refresh(tx_add)
        return {"message": "Transactions are saved", "data": tx_add}

@app.get("/price/{coin_id}")
async def get_price(coin_id: str, http_client: httpx.AsyncClient = Depends(get_http_client)):
    priceUrl = "https://api.coingecko.com/api/v3/simple/price"
    headers = {"x-cg-demo-api-key": os.getenv("COINGECKO_API_KEY")}
    params = {
        "ids": coin_id,
        "vs_currencies": "usd"
    }
    response = await http_client.get(priceUrl, headers=headers, params=params)
    priceData = response.json()

    if coin_id not in priceData:
        raise HTTPException(status_code=404, detail="This coin doesn't exist. Try another one.")
    else:
        return {"coin": coin_id, "price": priceData[coin_id]["usd"]}

@app.get("/transactions", dependencies=[Depends(check_auth)], response_model=list[TransactionOut])
def get_transaction(session = Depends(get_db)):
    txs = session.scalars(select(Transaction)).all()
    return txs

@app.get("/transactions/{id}", dependencies=[Depends(check_auth)], response_model=TransactionOut)
def get_tx_by_id(id:int, session = Depends(get_db)):
    stmt = select(Transaction).where(Transaction.id == id)
    tx_id = session.scalars(stmt).one_or_none()
    if tx_id: 
        return tx_id
    else:
        raise HTTPException(status_code=404, detail="Invalid id number")

@app.delete("/transactions/{id}", dependencies=[Depends(check_auth)])
def del_tx(id:int, session = Depends(get_db)):
    stmt = select(Transaction).where(Transaction.id == id)
    tx_del = session.scalars(stmt).one_or_none()
    if tx_del:
        session.delete(tx_del)
        session.commit()
        return {"message": f"Delete transaction {id} successfully"}
    else:
        raise HTTPException(status_code=404, detail="Invalid id number")

@app.put("/transactions/{id}", dependencies=[Depends(check_auth)])
def alter_tx(id:int, tx: TransactionIn, session = Depends(get_db)):
    stmt = select(Transaction).where(Transaction.id == id)
    tx_alt = session.scalars(stmt).one_or_none()
    if tx_alt:
        tx_alt.coin = tx.coin
        tx_alt.action = tx.action
        tx_alt.amount = tx.amount
        tx_alt.price = tx.price
        tx_alt.total = tx.amount * tx.price
        session.commit()
        return {"message": f"Transaction {id} is updated successfully"}
    else:
        raise HTTPException(status_code=404, detail="Invalid id number")