# DataApp
################################
# Bibliotecas
################################
import streamlit as st
from list_stock import list_stock
import yfinance as yf

################################
# Coletando dados
################################
def get_data(ticker: str, start, end):
    data = yf.download(ticker, start=start, end=end)
    return data

################################
# Configuração da página
################################
st.set_page_config(page_title="DataApp", page_icon="📊", layout="wide")

################################
# Título do App
################################
st.title("DataApp Stock Analysis 📊")

################################
# Construção do App - Sidebar
################################
stock = st.sidebar.selectbox("Ticker", list_stock)
start = st.sidebar.date_input("Start Date", value=None)
end = st.sidebar.date_input("End Date", value=None)

st.sidebar.markdown("---")

################################
# Construção do App - Main
################################
data = get_data(stock, start, end)
st.dataframe(data)
