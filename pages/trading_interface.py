import streamlit as st
import time

from src.web.auth import AuthService
from src.web.investors import InvestorsService
from src.modules.yfinance.crawler import YfinanceCrawler
from src.modules.dnse.realtime_data_provider import RealtimeDataProvider
from src.utils.logger import LOGGER
from src.web.components import (
    display_chart,
    display_index_tickers,
    display_order_list,
    display_order_entry,
    display_price_info,
    display_balance,
    display_holdings,
)
AuthService.require_login(role="client")

REFRESH_INTERVAL_SECONDS = 10

st.set_page_config(layout="wide", page_title="Trading Interface")


if 'current_symbol' not in st.session_state:
    st.session_state.current_symbol = "BSI"
if 'selected_order_type' not in st.session_state:
     st.session_state.selected_order_type = "LO"
if 'last_fetch_time_trade' not in st.session_state:
     st.session_state.last_fetch_time_trade = 0


def fetch_trading_data():
    # Fetch market data from Redis
    st.session_state.indices = {
        "VNINDEX": RealtimeDataProvider.get_market_index_info("VNINDEX"),
        "VN30": RealtimeDataProvider.get_market_index_info("VN30"),
        "HNX": RealtimeDataProvider.get_market_index_info("HNX"),
        "HNX30": RealtimeDataProvider.get_market_index_info("HNX30"),
        "UPCOM": RealtimeDataProvider.get_market_index_info("UPCOM"),
        "VNXALLSHARE": RealtimeDataProvider.get_market_index_info("VNXALLSHARE"),
    }

    st.session_state.stock_data = RealtimeDataProvider.get_stock_data("BSI")
    st.session_state.chart_data = YfinanceCrawler.download(
        symbol=st.session_state.stock_data["symbol"],
        interval="1d",
        time_range="1y"
    )

    st.session_state.account_balance = InvestorsService.get_balance()
    st.session_state.orders = []
    st.session_state.holdings = InvestorsService.get_all_holdings()
    st.session_state.selected_order_type = "LO"

    st.session_state.last_fetch_time_trade = time.time()
    return True

# Fetch data periodically
now = time.time()
if now - st.session_state.last_fetch_time_trade > REFRESH_INTERVAL_SECONDS:
    fetch_trading_data()
    needs_rerun = True
else:
    needs_rerun = False

st.title("Trading Interface")
st.write(f"User: {st.session_state.username} ({st.session_state.user_id})")
st.divider()

# --- Render UI ---
display_index_tickers()
st.divider()

col_left, col_mid, col_right = st.columns([6, 2, 2])

with col_left:
    display_chart()
    tab_holdings, tab_orders = st.tabs(["Danh mục", "Sổ lệnh"])
    with tab_holdings:
        display_holdings()
    with tab_orders:
        display_order_list()

with col_mid:
    with st.container():
        display_order_entry()

with col_right:
    with st.container(border=True):
        display_price_info()
    with st.container(border=True):
        display_balance()


if needs_rerun:
     time.sleep(0.1)
     try: st.rerun()
     except Exception as e: LOGGER.error(f"Rerun failed: {e}"); time.sleep(REFRESH_INTERVAL_SECONDS); st.rerun()
else:
     time.sleep(REFRESH_INTERVAL_SECONDS)
     try: st.rerun()
     except Exception as e: LOGGER.error(f"Rerun failed: {e}"); time.sleep(REFRESH_INTERVAL_SECONDS); st.rerun()