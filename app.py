import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
import random
from decimal import Decimal
from datetime import datetime, timedelta

# --- Cấu hình Trang Streamlit ---
st.set_page_config(layout="wide", page_title="Trading Interface (Python)")

# --- Khởi tạo Trạng thái Session (nếu chưa có) ---
if 'last_update_time' not in st.session_state:
    st.session_state.last_update_time = time.time()
    st.session_state.indices = {
        "VNINDEX": {"value": 1197.13, "change": -9.94, "pct_change": -0.82, "ref": 1197.13 + 9.94},
        "VN30": {"value": 1290.38, "change": -3.91, "pct_change": -0.30, "ref": 1290.38 + 3.91},
        "HNX": {"value": 207.71, "change": -3.76, "pct_change": -1.78, "ref": 207.71 + 3.76},
    }
    st.session_state.stock_data = {
        "symbol": "VN30F2505", # Mã đang xem chính
        "price": 1292.0,
        "change": 1.00,
        "pct_change": 0.08,
        "open": 1285.4,
        "high": 1296.0,
        "low": 1214.1,
        "close": 1292.0, # Close của phiên trước hoặc giá hiện tại
        "volume": 421002,
        "ref": 1291.0,
        "ceil": 1381.3,
        "floor": 1200.7,
    }
    st.session_state.chart_data = [
        # Format: { time: timestamp_seconds, open, high, low, close }
        # Chuyển đổi YYYY-MM-DD sang timestamp
        {"time": int(datetime.strptime('2024-04-25', '%Y-%m-%d').timestamp()), "open": 1250.0, "high": 1265.0, "low": 1245.0, "close": 1260.0},
        {"time": int(datetime.strptime('2024-04-26', '%Y-%m-%d').timestamp()), "open": 1260.0, "high": 1280.0, "low": 1255.0, "close": 1275.0},
        {"time": int(datetime.strptime('2024-04-29', '%Y-%m-%d').timestamp()), "open": 1278.0, "high": 1296.0, "low": 1270.0, "close": 1290.0},
        {"time": int(datetime.strptime('2024-04-30', '%Y-%m-%d').timestamp()), "open": 1290.0, "high": 1295.0, "low": 1285.0, "close": 1291.0},
        {"time": int(datetime.strptime('2024-05-02', '%Y-%m-%d').timestamp()), "open": 1285.4, "high": 1296.0, "low": 1214.1, "close": 1292.0},
    ]
    st.session_state.order_book = {
        "asks": [[1293.0, 47], [1293.2, 2], [1294.0, 32], [1294.1, 50], [1294.2, 1]], # [price, quantity]
        "bids": [[1, 1291.6], [2, 1291.7], [20, 1291.8], [1, 1291.9], [27, 1292.0]], # [quantity, price] - Đảo ngược để hiển thị
        "last_match_price": 1292.0,
        "last_match_vol": 1.00
    }
    st.session_state.account = {
        "nav": 5001832,
        "cash": 5001832,
        "stock_value": 0,
        "buying_power": 5001832,
        "securing_amount": 0, # Tiền đang khóa cho lệnh mua
    }
    st.session_state.holdings = {
        # "FPT": {"quantity": 100, "cost_basis": 90000, "market_price": 95000, "locked_quantity": 0},
    }
    st.session_state.orders = [] # Danh sách các lệnh đã đặt trong phiên
    st.session_state.selected_order_type = "LO" # Default order type

# --- Hàm Giả Lập Dữ Liệu Thay Đổi ---
def simulate_data_update():
    now = time.time()
    # Chỉ cập nhật nếu đã qua khoảng thời gian (ví dụ 2 giây)
    if now - st.session_state.last_update_time < 2:
        return False # Chưa cần cập nhật

    st.session_state.last_update_time = now

    # 1. Simulate Index Changes
    for index in st.session_state.indices:
        data = st.session_state.indices[index]
        change_factor = (random.random() - 0.48) * 0.005 # Thay đổi nhỏ
        new_value = data["value"] * (1 + change_factor)
        data["change"] = new_value - data["ref"]
        data["pct_change"] = (data["change"] / data["ref"]) * 100 if data["ref"] else 0
        data["value"] = new_value

    # 2. Simulate Stock Price Change
    stock = st.session_state.stock_data
    price_change = (random.random() - 0.45) * 2.5
    new_price = round(stock["price"] + price_change, 1)
    if new_price <= 0: new_price = 0.1
    stock["price"] = new_price
    stock["change"] = new_price - stock["ref"]
    stock["pct_change"] = (stock["change"] / stock["ref"]) * 100 if stock["ref"] else 0
    stock["close"] = new_price # Update close to current price
    stock["high"] = max(stock["high"], new_price)
    stock["low"] = min(stock["low"], new_price)
    stock["volume"] += random.randint(50, 500)

    # 3. Simulate Chart Update (update last candle or add new)
    last_candle_time = st.session_state.chart_data[-1]["time"]
    current_candle_time = int(datetime.now().replace(second=0, microsecond=0).timestamp()) # Giả lập nến phút

    # Check if it's time for a new candle (simple check, real charting needs proper timeframe logic)
    if current_candle_time > last_candle_time:
         st.session_state.chart_data.append({
             "time": current_candle_time,
             "open": stock["price"],
             "high": stock["price"],
             "low": stock["price"],
             "close": stock["price"]
         })
         # Limit chart data length (optional)
         if len(st.session_state.chart_data) > 200:
              st.session_state.chart_data.pop(0)
    else:
         # Update the last candle
         last_candle = st.session_state.chart_data[-1]
         last_candle["high"] = max(last_candle["high"], stock["price"])
         last_candle["low"] = min(last_candle["low"], stock["price"])
         last_candle["close"] = stock["price"]


    # 4. Simulate Order Book Change
    ob = st.session_state.order_book
    ob["last_match_price"] = stock["price"]
    ob["last_match_vol"] = round(random.random() * 5 + 1, 2)
    # Simple shift in prices
    step = 0.1
    ob["asks"] = [[round(stock["price"] + i * step, 1), random.randint(1, 50)] for i in range(1, 6)]
    ob["bids"] = [[random.randint(1, 50), round(stock["price"] - i * step, 1)] for i in range(1, 6)]

    # 5. Simulate Holdings Market Price Update & Recalculate Account Value
    total_stock_value = 0
    for symbol, holding_data in st.session_state.holdings.items():
        # Giả lập giá thị trường cho mã đang giữ (cần cơ chế lấy giá thật)
        price_factor = 1 + (random.random() - 0.5) * 0.01
        holding_data["market_price"] = round(holding_data.get("market_price", holding_data["cost_basis"]) * price_factor)
        total_stock_value += holding_data["quantity"] * holding_data["market_price"]

    st.session_state.account["stock_value"] = total_stock_value
    st.session_state.account["nav"] = st.session_state.account["cash"] + st.session_state.account["stock_value"]
    # Cập nhật buying power (ví dụ đơn giản là tiền mặt khả dụng)
    st.session_state.account["buying_power"] = st.session_state.account["cash"] # Cần trừ securing amount nếu có

    return True # Dữ liệu đã được cập nhật


# --- Hàm Render Giao diện ---

def display_index_tickers():
    cols = st.columns(len(st.session_state.indices))
    i = 0
    for index, data in st.session_state.indices.items():
        with cols[i]:
            delta_color = "off" # Neutral if no change
            if data["change"] > 0: delta_color = "normal" # Green for positive
            elif data["change"] < 0: delta_color = "inverse" # Red for negative
            st.metric(
                label=index,
                value=f"{data['value']:,.2f}",
                delta=f"{data['change']:,.2f} ({data['pct_change']:,.2f}%)",
                delta_color=delta_color
            )
        i += 1

def display_chart():
    st.subheader(f"Biểu đồ {st.session_state.stock_data['symbol']}")
    # Chuẩn bị dữ liệu cho Plotly
    df = pd.DataFrame(st.session_state.chart_data)
    # Chuyển timestamp sang datetime để Plotly hiển thị trục thời gian đẹp hơn
    df['time'] = pd.to_datetime(df['time'], unit='s')

    fig = go.Figure(data=[go.Candlestick(x=df['time'],
                                           open=df['open'],
                                           high=df['high'],
                                           low=df['low'],
                                           close=df['close'])])
    fig.update_layout(
        xaxis_rangeslider_visible=False, # Ẩn range slider phía dưới
        height=350,
        margin=dict(l=10, r=10, t=10, b=10), # Giảm margin
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#e0e0e0')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e0e0e0')
    st.plotly_chart(fig, use_container_width=True)


def display_price_info():
    stock = st.session_state.stock_data
    delta_color = "off"
    if stock["change"] > 0: delta_color = "normal"
    elif stock["change"] < 0: delta_color = "inverse"

    col1, col2 = st.columns([2, 3]) # Tỷ lệ cột
    with col1:
        st.subheader(stock["symbol"])
    with col2:
        st.metric(label="Giá hiện tại", value=f"{stock['price']:,.1f}", delta=f"{stock['change']:+.2f} ({stock['pct_change']:+.2f}%)", delta_color=delta_color)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Mở", f"{stock['open']:,.1f}")
    c2.metric("Cao", f"{stock['high']:,.1f}")
    c3.metric("Thấp", f"{stock['low']:,.1f}")
    c4.metric("Đóng", f"{stock['close']:,.1f}")
    c5.metric("KL", f"{stock['volume']:,}")

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"**TC:** <span style='color:#f4b400;'>{stock['ref']:,.1f}</span>", unsafe_allow_html=True)
    c2.markdown(f"**Trần:** <span style='color:#db4437;'>{stock['ceil']:,.1f}</span>", unsafe_allow_html=True)
    c3.markdown(f"**Sàn:** <span style='color:#0f9d58;'>{stock['floor']:,.1f}</span>", unsafe_allow_html=True)


def display_order_book():
    st.subheader("Bước giá - Khớp lệnh")
    ob = st.session_state.order_book

    col1, col2, col3 = st.columns([2, 1, 2]) # KL Mua | Giá Khớp | Giá Bán

    with col1: # Bids (KL Mua - Giá Mua)
        st.markdown("**KL Mua** | **Giá Mua**")
        for qty, price in sorted(ob["bids"], key=lambda x: x[1], reverse=True): # Sắp xếp giá cao nhất lên trên
             st.markdown(f"<span style='color:grey;'>{qty:,}</span> | <span style='color:#0f9d58; font-weight:bold;'>{price:,.1f}</span>", unsafe_allow_html=True)


    with col2: # Last Match
         color_cls = "green" if ob['last_match_price'] >= st.session_state.stock_data['ref'] else "red"
         if ob['last_match_price'] == st.session_state.stock_data['ref']: color_cls = "orange"
         st.markdown(f"""
         <div style='text-align: center; border-top: 1px solid #ccc; border-bottom: 1px solid #ccc; padding: 10px 0; margin: 5px 0;'>
              <span style='color:{color_cls}; font-weight: bold; font-size: 1.2em;'>{ob['last_match_price']:,.1f}</span><br/>
              <span style='color:grey; font-size: 0.9em;'>{ob['last_match_vol']:,.2f}</span>
         </div>
         """, unsafe_allow_html=True)

    with col3: # Asks (Giá Bán - KL Bán)
        st.markdown("**Giá Bán** | **KL Bán**")
        for price, qty in sorted(ob["asks"], key=lambda x: x[0]): # Sắp xếp giá thấp nhất lên trên
             st.markdown(f"<span style='color:#db4437; font-weight:bold;'>{price:,.1f}</span> | <span style='color:grey;'>{qty:,}</span>", unsafe_allow_html=True)


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


def display_balance():
    st.subheader("Tài sản")
    acc = st.session_state.account
    st.metric("TÀI SẢN RÒNG", f"{acc['nav']:,.0f}")
    st.metric("Tiền", f"{acc['cash']:,.0f}")
    st.metric("Giá trị cổ phiếu", f"{acc['stock_value']:,.0f}")
    st.metric("Sức mua", f"{acc['buying_power']:,.0f}")
    # st.metric("Tiền đang khóa", f"{acc['securing_amount']:,.0f}") # Thêm nếu cần


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
          'id': 'ID Lệnh', 'side': 'M/B', 'symbol': 'Mã CK', 'type': 'Loại', 'quantity':'KL Đặt', 'price': 'Giá Đặt', 'status': 'Trạng Thái'
     })
     # Định dạng giá nếu là LO
     df_display['Giá Đặt'] = df_display.apply(lambda row: f"{row['Giá Đặt']:,.1f}" if row['Loại'] == 'LO' and row['Giá Đặt'] else 'MP', axis=1)

     st.dataframe(df_display, use_container_width=True, hide_index=True)


# --- Chạy Giả Lập và Render ---
needs_rerun = simulate_data_update() # Cập nhật dữ liệu nền

# --- Bố cục Giao diện ---
display_index_tickers()
st.divider() # Đường kẻ ngang

col_left, col_right = st.columns([3, 1]) # Chia cột chính, trái rộng hơn

with col_left:
    display_chart()
    tab_orders, tab_holdings = st.tabs(["Sổ lệnh thường", "Deal nắm giữ"])
    with tab_orders:
         display_order_list()
    with tab_holdings:
        display_holdings()


with col_right:
    with st.container(border=True):
        display_price_info()
    with st.container(border=True):
        display_order_book()
    with st.container(border=True):
        display_order_entry()
    with st.container(border=True):
         display_balance()


# --- Tự động chạy lại script để cập nhật UI ---
if needs_rerun:
    time.sleep(0.1) # Chờ một chút xíu trước khi rerun
    st.rerun()
else:
     # Nếu không có update nào, vẫn rerun sau khoảng thời gian cố định
     # để đảm bảo UI không bị "đơ" nếu không có data mới
     time.sleep(3) # Giữ thời gian chờ gốc
     st.rerun()