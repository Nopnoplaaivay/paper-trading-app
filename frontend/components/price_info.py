import streamlit as st

def display_price_info():
    stock = st.session_state.stock_data

    col1, col2 = st.columns([2, 3]) # Tỷ lệ cột
    with col1:
        st.subheader(stock["symbol"])
    with col2:
        st.metric(label="Giá hiện tại", value=f"{stock['price']:,.1f}", delta=f"{stock['change']:+.2f} ({stock['pct_change']:+.2f}%)", delta_color="normal")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.markdown(f"""
        <div style="font-size:18px; font-weight:bold;">Mở</div>
        <div style="font-size:16px;">{stock['open']:,.1f}</div>
    """, unsafe_allow_html=True)
    c2.markdown(f"""
        <div style="font-size:18px; font-weight:bold;">Cao</div>
        <div style="font-size:16px;">{stock['high']:,.1f}</div>
    """, unsafe_allow_html=True)
    c3.markdown(f"""
        <div style="font-size:18px; font-weight:bold;">Thấp</div>
        <div style="font-size:16px;">{stock['low']:,.1f}</div>
    """, unsafe_allow_html=True)
    c4.markdown(f"""
          <div style="font-size:18px; font-weight:bold;">Đóng</div>
          <div style="font-size:16px;">{stock['close']:,.1f}</div>
    """, unsafe_allow_html=True)
    c5.markdown(f"""
            <div style="font-size:18px; font-weight:bold;">KL</div>
            <div style="font-size:16px;">{int(stock['volume'])}</div>
    """, unsafe_allow_html=True)

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"**TC:** <span style='color:#f4b400;'>{stock['ref']:,.1f}</span>", unsafe_allow_html=True)
    c2.markdown(f"**Trần:** <span style='color:#db4437;'>{stock['ceil']:,.1f}</span>", unsafe_allow_html=True)
    c3.markdown(f"**Sàn:** <span style='color:#0f9d58;'>{stock['floor']:,.1f}</span>", unsafe_allow_html=True)