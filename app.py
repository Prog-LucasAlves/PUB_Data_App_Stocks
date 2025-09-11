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
    """
    Function to get stock data from Yahoo Finance
    :param ticker: Stock ticker symbol
    :param start: Start date
    :param end: End date
    :return: DataFrame with stock data
    """
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

# Coletando valores máximo e mínimo
data_max = data['Adj Close'].max()
date_max = data[data["Adj Close"] == data_max].index[0]
data_min = data['Adj Close'].min()
date_min = data[data["Adj Close"] == data_min].index[0]

# Gráfico de linhas - Preço Ajustado
fig_line = go.Figure()
fig_line.add_trace(
    go.Scatter(
        x=data.index, y=data['Adj Close'], mode='lines', name='Adj Close',
        line=dict(color='#1F77B4', width=2, shape='spline'),
    ),
)
fig_line.add_trace(
    go.Scatter(
        x=[date_max], y=[data_max], mode='markers+text', name='Biggest High',
        marker=dict(symbol="circle", size=10, color="#54A24B"),
        text=[f"R$ {data_max:.2f}"], textposition="bottom center",
        textfont=dict(color="white", size=15),
    ),
)
fig_line.add_trace(
    go.Scatter(
        x=[date_min], y=[data_min], mode='markers+text', name='Biggest Low',
        marker=dict(symbol="circle", size=10, color="#B82E2E"),
        text=[f"R$ {data_min:.2f}"], textposition="top center",
        textfont=dict(color="white", size=15),
    ),
)
fig_line.update_layout(
    title=f"{stock} Adjusted Close Price",
    title_font=dict(size=24),
    xaxis_title="Date", xaxis_title_font=dict(size=15),
    xaxis=dict(tickfont=dict(size=15)),
    yaxis_tickprefix="R$ ", yaxis_tickformat=".2f", yaxis_title="Price (BRL)",
    yaxis_title_font=dict(size=15),
    yaxis=dict(tickfont=dict(size=15)),
    legend=dict(font=dict(size=18)),
)
st.plotly_chart(fig_line)
