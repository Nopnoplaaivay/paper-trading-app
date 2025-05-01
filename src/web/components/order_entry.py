import time
import random
import streamlit as st


def display_order_entry():
    st.subheader("Đặt Lệnh")
    acc = st.session_state.account
    stock = st.session_state.stock_data

    # Lấy mã đang xem làm mặc định
    default_symbol = stock['symbol']
    order_symbol = st.text_input("Mã CK:", value=default_symbol).upper()

    order_type = st.radio(
        "Loại lệnh:",
        ("LO", "MP"), # Thêm ATC, ATO nếu cần
        index=0 if st.session_state.selected_order_type == "LO" else 1, # Giữ lựa chọn trước đó
        horizontal=True,
        key="order_type_radio" # Key để truy cập giá trị
    )
    st.session_state.selected_order_type = order_type # Lưu lại lựa chọn

    limit_price = None
    price_input_disabled = (order_type != "LO")
    limit_price_value = stock['price'] if order_type == "LO" else 0.0 # Default price for LO
    if order_type == "LO":
        limit_price = st.number_input("Giá đặt:", min_value=0.1, value=limit_price_value, step=0.1, format="%.1f")

    quantity = st.number_input("KL đặt:", min_value=1, value=1, step=1)

    # Tính toán sức mua/bán tối đa (Giả lập đơn giản)
    current_holding = st.session_state.holdings.get(order_symbol)
    max_sell_qty = current_holding['quantity'] if current_holding else 0
    price_for_calc = limit_price if order_type == "LO" and limit_price else stock['price']
    max_buy_qty = int(acc['buying_power'] // price_for_calc) if price_for_calc > 0 else 0

    col1, col2 = st.columns(2)
    with col1:
        if st.button("MUA", type="primary", use_container_width=True):
            # --- Logic xử lý lệnh MUA ---
            order_details = { "side": "BUY", "symbol": order_symbol, "type": order_type, "qty": quantity, "price": limit_price }
            print("Processing BUY Order:", order_details) # In ra console Python
            st.success(f"Gửi lệnh MUA {quantity} {order_symbol} {order_type} {('@'+str(limit_price)) if limit_price else ''} (Giả lập)")
            # TODO: Gọi API backend hoặc cập nhật state giả lập
            st.session_state.orders.append({"id": f"B-{random.randint(1000,9999)}", **order_details, "status": "PENDING"}) # Thêm vào list lệnh giả lập
            # Giảm tiền mặt giả lập (ví dụ)
            cost = (limit_price if limit_price else stock['price']) * quantity
            if acc['cash'] >= cost:
                 # Giả lập khóa tiền cho lệnh LO/MP
                 st.session_state.account['cash'] -= cost
                 st.session_state.account['securing_amount'] += cost # Tăng tiền khóa
                 st.session_state.account['buying_power'] -= cost
                 # Simulate fill for MP right away for demo
                 if order_type == "MP":
                     # This should happen in a separate execution logic
                     st.info("Lệnh MP giả lập khớp ngay!")
                     # TODO: Add fill logic simulation (update holdings, unsecure cash etc.)

            else:
                 st.error("Không đủ sức mua!")

            time.sleep(0.5) # Chờ chút để user thấy message
            st.rerun() # Chạy lại để cập nhật UI

    with col2:
        if st.button("BÁN", use_container_width=True):
             # --- Logic xử lý lệnh BÁN ---
            order_details = { "side": "SELL", "symbol": order_symbol, "type": order_type, "qty": quantity, "price": limit_price }
            print("Processing SELL Order:", order_details)
            st.success(f"Gửi lệnh BÁN {quantity} {order_symbol} {order_type} {('@'+str(limit_price)) if limit_price else ''} (Giả lập)")
             # TODO: Gọi API backend hoặc cập nhật state giả lập
            st.session_state.orders.append({"id": f"S-{random.randint(1000,9999)}", **order_details, "status": "PENDING"})
             # Giả lập khóa cổ phiếu nếu có
            if current_holding and current_holding['quantity'] >= quantity:
                 # TODO: Add locking logic if Holdings model supports it
                 # Simulate fill for MP right away for demo
                 if order_type == "MP":
                     st.info("Lệnh MP giả lập khớp ngay!")
                     # TODO: Add fill logic simulation (update holdings, add cash etc.)
                     pass
            else:
                 st.error("Không đủ cổ phiếu để bán!")

            time.sleep(0.5)
            st.rerun()

    st.caption(f"Mua tối đa: {max_buy_qty:,} | Bán tối đa: {max_sell_qty:,}")