import pandas as pd
import streamlit as st


def display_order_list():
    st.subheader("Sổ lệnh thường")
    orders = st.session_state.orders
    if not orders:
        st.info("Chưa có lệnh trong ngày.")
        return

    # Hiển thị các lệnh gần nhất lên trên
    df_orders = pd.DataFrame(orders[::-1])
    # Chọn và sắp xếp lại cột cho đẹp
    df_display = df_orders[['id', 'side', 'symbol', 'type', 'quantity', 'price', 'status']].rename(columns={
        'id': 'ID Lệnh', 'side': 'M/B', 'symbol': 'Mã CK', 'type': 'Loại', 'quantity': 'KL Đặt', 'price': 'Giá Đặt',
        'status': 'Trạng Thái'
    })
    # Định dạng giá nếu là LO
    df_display['Giá Đặt'] = df_display.apply(
        lambda row: f"{row['Giá Đặt']:,.1f}" if row['Loại'] == 'LO' and row['Giá Đặt'] else 'MP', axis=1)

    st.dataframe(df_display, use_container_width=True, hide_index=True)