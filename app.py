# DataApp
################################
# Bibliotecas
################################
import streamlit as st
from list_stock import list_stock
import yfinance as yf
import plotly.graph_objects as go

################################
# Coletando dados
################################
def get_data(ticker: str, start, end):
    data = yf.download(f"{ticker}.SA", start=start, end=end, auto_adjust=False, progress=False, multi_level_index=False)
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
# Coletando dados
data = get_data(stock, start, end)

# Formatando e exibindo os dados - DataFrame
st.dataframe(
    data.style.format({
        "Open": "{:.2f}",
        "High": "{:.2f}",
        "Low": "{:.2f}",
        "Close": "{:.2f}",
        "Adj Close": "{:.2f}",
        "Volume": "{:.0f}",
    }), use_container_width=True,
)

# Botão de download dos dados
csv = data.to_csv().encode('utf-8')
st.download_button(label="Download Data as CSV", data=csv, file_name=f'{stock}.csv', mime='text/csv')
