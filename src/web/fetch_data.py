import streamlit as st
import time


from src.web.investors import InvestorsService
from src.modules.yfinance.crawler import YfinanceCrawler
from src.modules.dnse.realtime_data_provider import RealtimeDataProvider
from src.utils.logger import LOGGER

REFRESH_INTERVAL_SECONDS = 3

class DataFetcher:
    @classmethod
    def fetch_and_update_trading_data(cls, force_fetch_account: bool = False) -> bool:
        data_was_updated = False
        now = time.time()

        if 'current_symbol' not in st.session_state:
            st.session_state.current_symbol = "VCB"
        if 'selected_order_type' not in st.session_state:
            st.session_state.selected_order_type = "LO"
        if 'last_fetch_time_trade' not in st.session_state:
            st.session_state.last_fetch_time_trade = 0
        if 'indices' not in st.session_state:
            st.session_state.indices = cls.fetch_index()
        if 'selected_order_type_form' not in st.session_state:  # Key cho form trong component
            st.session_state.selected_order_type_form = "LO"

        if (now - st.session_state.last_fetch_time_trade > REFRESH_INTERVAL_SECONDS) or \
                (st.session_state.last_fetch_time_trade == 0):

            new_indices_data = cls.fetch_index()
            if new_indices_data != st.session_state.indices:
                st.session_state.indices = new_indices_data
                data_was_updated = True

            st.session_state.last_fetch_time_trade = now
            cls.fetch_stock_data()


        if 'account_balance' not in st.session_state or st.session_state.last_fetch_time_trade == now or force_fetch_account:
            st.session_state.account_balance = InvestorsService.get_balance()
            st.session_state.orders = []
            st.session_state.holdings = InvestorsService.get_all_holdings()
            data_was_updated = True


        st.session_state.selected_order_type = "LO"
        st.session_state.last_fetch_time_trade = time.time()
        if data_was_updated:
            LOGGER.debug("Data was updated, signaling potential rerun.")
        return data_was_updated

    @classmethod
    def fetch_index(cls):
        return {
            "VNINDEX": RealtimeDataProvider.get_market_index_info("VNINDEX"),
            "VN30": RealtimeDataProvider.get_market_index_info("VN30"),
            "HNX": RealtimeDataProvider.get_market_index_info("HNX"),
            "HNX30": RealtimeDataProvider.get_market_index_info("HNX30"),
            "UPCOM": RealtimeDataProvider.get_market_index_info("UPCOM"),
            "VNXALLSHARE": RealtimeDataProvider.get_market_index_info("VNXALLSHARE"),
        }


    @classmethod
    def fetch_stock_data(cls):
        st.session_state.stock_data = RealtimeDataProvider.get_stock_data(st.session_state.current_symbol)
        try:
            st.session_state.chart_data = YfinanceCrawler.download(
                symbol=st.session_state.stock_data["symbol"],
                interval="1d",
                time_range="1y"
            )
        except Exception as e:
            st.session_state.chart_data = None
            st.error(f"Error fetching chart data: {e}")



