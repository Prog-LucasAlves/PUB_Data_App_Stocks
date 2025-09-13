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
def get_data_stock(ticker: str, start, end):
    """
    Function to get stock data from Yahoo Finance
    :param ticker: Stock ticker symbol
    :param start: Start date
    :param end: End date
    :return: DataFrame with stock data
    """
    data = yf.download(f"{ticker}.SA", start=start, end=end, auto_adjust=False, progress=False, multi_level_index=False)
    return data

def get_data_benchmark(ticker: str, start, end):
    """
    Function to get benchmark data from Yahoo Finance
    :param ticker: Benchmark ticker symbol
    :param start: Start date
    :param end: End date
    :return: DataFrame with benchmark data
    """
    data = yf.download(f"{ticker}", start=start, end=end, auto_adjust=False, progress=False, multi_level_index=False)
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
start = st.sidebar.date_input("Start Date", value=pd.to_datetime("2025-01-01").date())
today = pd.to_datetime("today").date()
end = st.sidebar.date_input("End Date", value=today, max_value=today)
benchmark = st.sidebar.selectbox("Benchmark", ["^BVSP", "^GSPC", "^IXIC", "^FTSE", "^N225", "^HSI", "GC=F", "CL=F", "EURUSD=X", "JPY=X", "BRL=X"])

st.sidebar.markdown("---")

moving_average = st.sidebar.checkbox("Show Moving Average", value=False)
if moving_average:
    ma_window = st.sidebar.slider("Moving Average Window", min_value=20, max_value=100, value=20, step=5)

################################
# Construção do App - Main
################################
# Coletando dados
dataStock = get_data_stock(stock, start, end)
dataBenchmark = get_data_benchmark(benchmark, start, end)

# Formatando e exibindo os dados - DataFrame
st.dataframe(
    dataStock.style.format({
        "Open": "{:.2f}",
        "High": "{:.2f}",
        "Low": "{:.2f}",
        "Close": "{:.2f}",
        "Adj Close": "{:.2f}",
        "Volume": "{:.0f}",
    }), use_container_width=True,
)

# Botão de download dos dados
csv = dataStock.to_csv().encode('utf-8')
st.download_button(label="Download Data as CSV", data=csv, file_name=f'{stock}.csv', mime='text/csv')

# Coletando valores máximo e mínimo
data_max = dataStock['Adj Close'].max()
date_max = dataStock[dataStock["Adj Close"] == data_max].index[0]
data_min = dataStock['Adj Close'].min()
date_min = dataStock[dataStock["Adj Close"] == data_min].index[0]

# Media Móvel
if moving_average:
    dataStock['MA'] = dataStock['Close'].rolling(window=ma_window).mean()

# Volatilidade
dataStock['Volatility'] = dataStock['Adj Close'].pct_change().rolling(window=21).std() * (21 ** 0.5)

# Calculos
annual_return = (dataStock['Adj Close'][-1] / dataStock['Adj Close'][0]) ** (252 / len(dataStock)) - 1
cumulative_return = (dataStock['Adj Close'][-1] / dataStock['Adj Close'][0]) - 1
annual_volatility = dataStock['Adj Close'].pct_change().std() * (252 ** 0.5)
mothly_volatility = dataStock['Adj Close'].pct_change().std() * (21 ** 0.5)
sharpe_ratio = annual_return / annual_volatility
calmar_ratio = annual_return / abs(dataStock['Adj Close'].pct_change().min() * (252 ** 0.5))
stability = (dataStock['Adj Close'].mean() / dataStock['Adj Close'].std())
max_drawdown = (dataStock['Adj Close'].cummax() - dataStock['Adj Close']).max() / dataStock['Adj Close'].cummax().max()
omega_ratio = (annual_return / annual_volatility) / max_drawdown
sortino_ratio = annual_return / (dataStock['Adj Close'].pct_change()[dataStock['Adj Close'].pct_change() < 0].std() * (252 ** 0.5))
skewness = dataStock['Adj Close'].pct_change().skew()
kurtosis = dataStock['Adj Close'].pct_change().kurtosis()
beta = (
    dataStock['Adj Close'].pct_change().dropna().cov(
    dataBenchmark['Adj Close'].pct_change().dropna(),
    ) /
        dataBenchmark['Adj Close'].pct_change().dropna().var()
)

# Crianddo colunas
col1, col2 = st.columns(2)

with col1:

    # Gráfico de linhas - Preço Ajustado
    fig_line = go.Figure()
    fig_line.add_trace(
        go.Scatter(
            x=dataStock.index, y=dataStock['Adj Close'], mode='lines', name='Adj Close',
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
        x=dataStock.index, open=dataStock["Open"], high=dataStock["High"], low=dataStock["Low"], close=dataStock["Close"],
        name="Candlestick", increasing_line_color="#54A24B", decreasing_line_color="#B82E2E",
    ),
)
if moving_average:
    fig_candle.add_trace(
        go.Scatter(
            x=dataStock.index, y=dataStock["MA"], mode="lines", name="Moving Average",
            line=dict(color="#1F77B4", width=2, shape="spline"),
        ),
    )
fig_candle.update_layout(
    title=f"{stock} Candlestick Chart",
    title_font=dict(size=24),
    xaxis_rangeslider_visible=False,
    xaxis_title="Date", xaxis_title_font=dict(size=15),
    xaxis=dict(type="date",tickfont=dict(size=15)),
    yaxis_tickprefix="R$ ", yaxis_tickformat=".2f", yaxis_title="Price (BRL)",
    yaxis_title_font=dict(size=15),
    yaxis=dict(tickfont=dict(size=15)),
)
date_all = pd.date_range(start=dataStock.index[0], end=dataStock.index[-1], freq="D")
date_all_py = [d.to_pydatetime() for d in date_all]
date_all_obs = [d.to_pydatetime() for d in dataStock.index]
date_all_braks = [d for d in date_all_py if d not in date_all_obs]
fig_candle.update_xaxes(
    rangebreaks=[dict(values=date_all_braks)],
)
st.plotly_chart(fig_candle)

# Crianddo colunas
col1, col2 = st.columns(2)

with col1:

    # Gráfico de Volatilidade
    fig_volatility = go.Figure()
    fig_volatility.add_trace(
        go.Scatter(
            x=dataStock.index, y=round(dataStock["Volatility"] * 100, 2), mode="lines", name="Volatility",
            line=dict(color="#FF7F0E", width=2, shape="spline"),
        ),
    )
    fig_volatility.update_layout(
    title=f"{stock} Annual Volatility",
    title_font=dict(size=24),
    xaxis_rangeslider_visible=False,
    xaxis_title="Date", xaxis_title_font=dict(size=15),
    xaxis=dict(type="date",tickfont=dict(size=15)),
    yaxis_tickformat=".%", yaxis_title="Volatilidade (%)",
    yaxis_title_font=dict(size=15),
    yaxis=dict(tickfont=dict(size=15)),
)
    st.plotly_chart(fig_volatility)
