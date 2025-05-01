import streamlit as st
import pandas as pd

def display_holdings():
    st.subheader("Deal nắm giữ")
    holdings = st.session_state.holdings
    if not holdings:
        st.info("Chưa nắm giữ cổ phiếu nào.")
        return

    data_for_df = []
    for symbol, h_data in holdings.items():
        market_price = h_data.get("market_price", h_data["cost_basis"]) # Dùng giá TT nếu có
        market_value = h_data["quantity"] * market_price
        cost_value = h_data["quantity"] * h_data["cost_basis"]
        pnl = market_value - cost_value
        pnl_pct = (pnl / cost_value) * 100 if cost_value else 0
        data_for_df.append({
            "Mã CK": symbol,
            "KL": h_data["quantity"],
            "Giá vốn": f"{h_data['cost_basis']:,.0f}",
            "Giá TT": f"{market_price:,.0f}",
            "+/- (%)": f"{pnl:,.0f} ({pnl_pct:.1f}%)"
        })

    df = pd.DataFrame(data_for_df)
    st.dataframe(df, use_container_width=True, hide_index=True)