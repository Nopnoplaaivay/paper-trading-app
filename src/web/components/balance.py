import streamlit as st

def display_balance():
    st.subheader("Tài sản")
    account_balance = st.session_state.account_balance
    st.metric("TÀI SẢN RÒNG", f"{account_balance['nav']:,.0f}")
    st.metric("Tiền", f"{account_balance['available_cash']:,.0f}")
    st.metric("Giá trị cổ phiếu", f"{account_balance['stock_value']:,.0f}")
    st.metric("Sức mua", f"{account_balance['purchasing_power']:,.0f}")
    # st.metric("Tiền đang khóa", f"{acc['securing_amount']:,.0f}") # Thêm nếu cần