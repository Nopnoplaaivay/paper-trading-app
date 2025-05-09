import streamlit as st
import time

st.set_page_config(layout="wide", page_title="Trading Interface")

from frontend.services import AuthService
from frontend.processors import OrderPayloadProcessor
from frontend.components import (
    display_chart,
    display_index_tickers,
    display_order_list,
    display_order_entry,
    display_price_info,
    display_balance,
    display_holdings,
    display_app_header,
)
from frontend.services import DataService

from backend.utils.logger import LOGGER


AuthService.require_login(role="client")
REFRESH_INTERVAL_SECONDS = 3


data_updated = DataService.fetch_and_update_trading_data(force_fetch_account=True)

display_app_header(page_name="trading")

display_index_tickers()
st.divider()

col_left, col_mid, col_right = st.columns([6, 2, 2])

with col_left:
    with st.container(border=True):
        display_chart()
    tab_holdings, tab_orders = st.tabs(["Danh mục", "Sổ lệnh"])
    with tab_holdings:
        display_holdings()
    with tab_orders:
        display_order_list()

with col_mid:
    with st.container():
        submitted_form_data = display_order_entry()
        order_processed_successfully = False
        if submitted_form_data:
            order_processed_successfully = OrderPayloadProcessor.create_payload(form_data=submitted_form_data)
            if order_processed_successfully:
                DataService.fetch_and_update_trading_data(force_fetch_account=True)
                data_updated = True

with col_right:
    with st.container(border=True):
        display_price_info()
    with st.container(border=True):
        display_balance()


if data_updated:
    LOGGER.info("Data was updated, signaling potential rerun.")
else:
    time.sleep(REFRESH_INTERVAL_SECONDS)
    try:
        st.rerun()
    except Exception as e:
        LOGGER.error(f"Periodic rerun failed: {e}")
        time.sleep(REFRESH_INTERVAL_SECONDS) # Đợi lâu hơn nếu lỗi
        st.rerun()