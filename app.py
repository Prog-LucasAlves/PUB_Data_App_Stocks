# DataApp
################################
# Bibliotecas
################################
import streamlit as st
from list_stock import list_stock
import pandas as pd

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
