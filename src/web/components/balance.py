import streamlit as st

def display_balance():
    st.subheader("Tài sản")
    acc = st.session_state.account
    st.metric("TÀI SẢN RÒNG", f"{acc['nav']:,.0f}")
    st.metric("Tiền", f"{acc['cash']:,.0f}")
    st.metric("Giá trị cổ phiếu", f"{acc['stock_value']:,.0f}")
    st.metric("Sức mua", f"{acc['buying_power']:,.0f}")
    # st.metric("Tiền đang khóa", f"{acc['securing_amount']:,.0f}") # Thêm nếu cần