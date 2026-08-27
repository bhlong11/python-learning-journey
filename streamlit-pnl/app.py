import streamlit as st
import requests
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("APP_API_KEY")
API_URL = os.getenv("API_URL")

st.title("Crypto P&L Tracker")

# Add description
st.write("Track your portfolio and P&L in real time.")

# Add text input
coin = st.text_input("Enter a coin ID:", "bitcoin")

# Show output
st.write("You entered:", coin)

# Button
if st.button("Get Price"):
    url = f"{API_URL}/price/{coin}"
    response = requests.get(url)
    data = response.json()
    if response.status_code == 200:
        st.metric(label=f"{coin} price", value=data["price"])
    else:
        error_detail = data.get("detail", "Unknown error")
        st.error(f"Error: {error_detail}")  

# Show transactions
if st.button("Show All Transactions"):
    url = f"{API_URL}/transactions"
    response = requests.get(url, headers={"x-api-key": API_KEY})
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)
        st.dataframe(df)
    else:
        error_detail = response.json().get("detail", "Unknown error")
        st.error(f"Error: {error_detail}")      

# POST new transaction
st.subheader("Log your new transaction here ⬇")

tx_coin = st.text_input("Coin name")
tx_action = st.selectbox("Action", ["buy", "sell"])
tx_amount = st.number_input("Amount")
tx_price = st.number_input("Price")

infor = {
    "coin": tx_coin,
    "action": tx_action,
    "amount": tx_amount,
    "price": tx_price
}

if st.button("Add Transaction"):
    url = f"{API_URL}/transaction"
    response = requests.post(url, headers={"x-api-key": API_KEY}, json=infor)
    if response.status_code == 200:
        data = response.json().get("data", {})
        id = data.get("id", "unknown")
        st.success(f"Transaction {id} is saved successfully!")
    else:
        error_detail = response.json().get("detail", "Unknown error")
        st.error(f"Error: {error_detail}")
