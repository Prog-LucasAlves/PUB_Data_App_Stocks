# DataApp
################################
# Bibliotecas
################################
import streamlit as st
from list_stock import list_stock
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

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
today = pd.to_datetime("today").date()
end = st.sidebar.date_input("End Date", value=today, max_value=today)

st.sidebar.markdown("---")

moving_average = st.sidebar.checkbox("Show Moving Average", value=False)
if moving_average:
    ma_window = st.sidebar.slider("Moving Average Window", min_value=5, max_value=100, value=20, step=5)

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

# Media Móvel
if moving_average:
    data['MA'] = data['Close'].rolling(window=ma_window).mean()

# Calculos
annual_return = (data['Adj Close'][-1] / data['Adj Close'][0]) ** (252 / len(data)) - 1
cumulative_return = (data['Adj Close'][-1] / data['Adj Close'][0]) - 1
annual_volatility = data['Adj Close'].pct_change().std() * (252 ** 0.5)
mothly_volatility = data['Adj Close'].pct_change().std() * (21 ** 0.5)
sharpe_ratio = annual_return / annual_volatility
calmar_ratio = annual_return / abs(data['Adj Close'].pct_change().min() * (252 ** 0.5))
stability = (data['Adj Close'].mean() / data['Adj Close'].std())
max_drawdown = (data['Adj Close'].cummax() - data['Adj Close']).max() / data['Adj Close'].cummax().max()
omega_ratio = (annual_return / annual_volatility) / max_drawdown
sortino_ratio = annual_return / (data['Adj Close'].pct_change()[data['Adj Close'].pct_change() < 0].std() * (252 ** 0.5))
skewness = data['Adj Close'].pct_change().skew()
kurtosis = data['Adj Close'].pct_change().kurtosis()
beta = data['Adj Close'].pct_change().cov(data['Adj Close'].pct_change()) / data['Adj Close'].pct_change().var()

# Crianddo colunas
col1, col2 = st.columns(2)

with col1:

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
        )   ,
    )
    fig_line.update_layout(
        title=f"{stock} Adjusted Close Price",
        title_font=dict(size=24),
        xaxis_title="Date", xaxis_title_font=dict(size=15),
        xaxis=dict(tickfont=dict(size=15)),
        yaxis_tickprefix="R$ ", yaxis_tickformat=".2f", yaxis_title="Price (BRL)",
        yaxis_title_font=dict(size=15),
        yaxis=dict(tickfont=dict(size=15)),
        legend=dict(font=dict(size=15)),
    )
    st.plotly_chart(fig_line)

with col2:
    # Métricas
    st.subheader("Key Metrics")
    col_a, col_b, col_c, col_d = st.columns(4)

    with col_a:
        st.metric(label="Maximum Price (BRL)", value=f"R$ {data_max:.2f}", delta=f"on {date_max.date()}")
        st.metric(label="Minimum Price (BRL)", value=f"R$ {data_min:.2f}", delta=f"on {date_min.date()}")
        st.metric(label="Annual Return", value=f"{annual_return*100:.2f} %")
        st.metric(label="Cumulative Return", value=f"{cumulative_return*100:.2f} %")

    with col_b:
        st.metric(label="Annual Volatility", value=f"{annual_volatility*100:.2f} %")
        st.metric(label="Monthly Volatility", value=f"{mothly_volatility*100:.2f} %")
        st.metric(label="Sharpe Ratio", value=f"{sharpe_ratio:.2f}")
        st.metric(label="Calmar Ratio", value=f"{calmar_ratio:.2f}")

    with col_c:
        st.metric(label="Stability", value=f"{stability:.2f}")
        st.metric(label="Max Drawdown", value=f"{max_drawdown*100:.2f} %")
        st.metric(label="Omega Ratio", value=f"{omega_ratio:.2f}")
        st.metric(label="Sortino Ratio", value=f"{sortino_ratio:.2f}")
    with col_d:
        st.metric(label="Skewness", value=f"{skewness:.2f}")
        st.metric(label="Kurtosis", value=f"{kurtosis:.2f}")
        st.metric(label="Beta", value=f"{beta:.2f}")

st.markdown("---")

# Gráfico de Candles - Preço Ajustado
fig_candle = go.Figure()
fig_candle.add_trace(
    go.Candlestick(
        x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'],
        name='Candlestick', increasing_line_color='#54A24B', decreasing_line_color='#B82E2E',
    ),
)
if moving_average:
    fig_candle.add_trace(
        go.Scatter(
            x=data.index, y=data['MA'], mode='lines', name='Moving Average',
            line=dict(color='#1F77B4', width=2, shape='spline'),
        ),
    )
fig_candle.update_layout(
    title=f'{stock} Gráfico de Candlestick', title_font=dict(size=24),
    xaxis_rangeslider_visible=False,
    xaxis_title="Date", xaxis_title_font=dict(size=15),
    xaxis=dict(
        type='date',
    ),
)
date_all = pd.date_range(start=data.index[0], end=data.index[-1], freq='D')
date_all_py = [d.to_pydatetime() for d in date_all]
date_all_obs = [d.to_pydatetime() for d in data.index]
date_all_braks = [d for d in date_all_py if d not in date_all_obs]
fig_candle.update_xaxes(
    rangebreaks=[dict(values=date_all_braks)],
)
st.plotly_chart(fig_candle)
