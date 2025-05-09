import os
import streamlit as st
import pandas as pd

from frontend.services import DataService
from backend.modules.orders.entities import OrderSide
from backend.common.consts import CommonConsts
from backend.utils.logger import LOGGER

def display_order_entry():
    st.subheader("Đặt Lệnh")
    account_balance = st.session_state.account_balance
    stock = st.session_state.stock_data
    current_price = stock['price']
    current_symbol = stock['symbol']

    def handle_symbol_change():
        new_symbol = st.session_state.order_symbol_selectbox.strip().upper()
        if new_symbol and new_symbol != st.session_state.current_symbol:
            LOGGER.info(f"Symbol changed via input: {st.session_state.current_symbol} -> {new_symbol}")
            st.session_state.current_symbol = new_symbol
            st.session_state.stock_data = DataService.fetch_stock_data()
            st.session_state.last_fetch_time_trade = 0

    stock_folder = os.path.join(CommonConsts.ROOT_FOLDER, "frontend", "stocks")
    stock_list = pd.read_csv(f"{stock_folder}\\stocks.csv")["ticker"].tolist()

    # --- Input Widgets ---
    selected_symbol = st.selectbox(
        "Mã CK:",
        options=stock_list,
        index=stock_list.index(current_symbol) if current_symbol in stock_list else 0,
        key="order_symbol_selectbox",
        on_change=handle_symbol_change
    )
    with st.form("order_entry_form_component", clear_on_submit=False):
        order_type_form = st.radio(
            "Loại lệnh:", ("LO", "MP"),
            index=0 if st.session_state.selected_order_type_form == "LO" else 1,
            horizontal=True,
            key="order_type_radio_component"
        )
        st.session_state.selected_order_type_form = order_type_form

        if order_type_form == "LO":
            input_price = st.number_input(
                "Giá đặt:", min_value=0.1,
                value=float(current_price) if current_price else 0.1, # Đảm bảo là float
                step=0.1, format="%.1f",
                key="input_price_component"
            )
        quantity_form_val = st.number_input("KL đặt:", min_value=1, value=1, step=1, key="quantity_component")
        submitted_buy = st.form_submit_button("MUA", type="primary", use_container_width=True)
        submitted_sell = st.form_submit_button("BÁN", use_container_width=True)

        form_data = None
        if submitted_buy or submitted_sell:
            form_data = {
                "submitted": OrderSide.BUY.value if submitted_buy else OrderSide.SELL.value,
                "symbol": selected_symbol,
                "order_type": order_type_form,
                "quantity": quantity_form_val,
                "price": input_price if order_type_form == "LO" else "MP",
            }
            LOGGER.debug(f"Order form submitted with data: {form_data}")

        holdings = st.session_state.holdings
        if holdings:
            holding_info = holdings.get(current_symbol, None)
            available_shares = holding_info.get("quantity", 0) if holding_info else 0
        else:
            available_shares = 0

        price_for_calc = input_price if order_type_form == "LO" and input_price else current_price
        buying_power = st.session_state.account_balance.get("purchasing_power", 0)
        max_buy_qty = int(buying_power // (price_for_calc * 1000)) if price_for_calc and price_for_calc > 0 else 0

        st.caption(f"Mua tối đa: {max_buy_qty:,} | Bán tối đa: {available_shares:,}")

        return form_data