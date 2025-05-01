import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
import random
from datetime import datetime

from src.modules.yfinance.crawler import YfinanceCrawler
from src.modules.dnse.realtime_data_provider import RealtimeDataProvider

st.set_page_config(layout="wide", page_title="Trading Interface (Python)")


if 'last_update_time' not in st.session_state:
    st.session_state.last_update_time = time.time()
    st.session_state.indices = {
        "VNINDEX": RealtimeDataProvider.get_market_index_info("VNINDEX"),
        "VN30": RealtimeDataProvider.get_market_index_info("VN30"),
        "HNX": RealtimeDataProvider.get_market_index_info("HNX"),
        "HNX30": RealtimeDataProvider.get_market_index_info("HNX30"),
        "UPCOM": RealtimeDataProvider.get_market_index_info("UPCOM"),
        "VNXALLSHARE": RealtimeDataProvider.get_market_index_info("VNXALLSHARE"),
    }

    st.session_state.stock_data = RealtimeDataProvider.get_stock_data("BSI")
    st.session_state.chart_data = YfinanceCrawler.download(
        symbol=st.session_state.stock_data["symbol"],
        interval="1d",
        time_range="1y"
    )
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
        "securing_amount": 0,
    }
    st.session_state.holdings = {
        # "FPT": {"quantity": 100, "cost_basis": 90000, "market_price": 95000, "locked_quantity": 0},
    }
    st.session_state.orders = []
    st.session_state.selected_order_type = "LO"

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
        market_info = RealtimeDataProvider.get_market_index_info(market_id=index)
        data["change"] = market_info["change"]
        data["pct_change"] = market_info["pct_change"]
        data["value"] = market_info["value"]

    # 2. Simulate Stock Price Change
    stock = st.session_state.stock_data

    # 3. Simulate Chart Update (update last candle or add new)
    st.session_state.chart_data = YfinanceCrawler.download(
        symbol=stock["symbol"],
        interval="1d",
        time_range="1y"
    )

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
    st.session_state.account["buying_power"] = st.session_state.account["cash"] # Cần trừ securing amount nếu có

    return True


def display_index_tickers():
    cols = st.columns(len(st.session_state.indices))
    i = 0
    for index, data in st.session_state.indices.items():
        with cols[i]:
            st.metric(
                label=index,
                value=f"{data['value']:,.2f}",
                delta=f"{data['change']:,.2f} ({data['pct_change']:,.2f}%)",
                delta_color="normal"
            )
        i += 1


def display_chart():
    st.subheader(f"Biểu đồ {st.session_state.stock_data['symbol']}")
    df = st.session_state.chart_data

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
st.divider()

col_left, col_mid, col_right = st.columns([6, 2, 2])

with col_left:
    display_chart()
    tab_orders, tab_holdings = st.tabs(["Sổ lệnh thường", "Deal nắm giữ"])
    with tab_orders:
        display_order_list()
    with tab_holdings:
        display_holdings()

with col_mid:
    with st.container():
        display_order_entry()

with col_right:
    with st.container(border=True):
        display_price_info()
    with st.container(border=True):
        display_balance()


if needs_rerun:
    time.sleep(0.1)
    st.rerun()
else:
     time.sleep(60*60)
     st.rerun()