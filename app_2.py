import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
import random
import redis # <<< Thư viện Redis
import requests # <<< Thư viện gọi API
import json
from datetime import datetime, timedelta
from enum import Enum # Để định nghĩa Enum nếu cần

# --- Cấu hình (Nên đưa vào file config hoặc env vars) ---
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
API_BASE_URL = "http://localhost:8000/api/v1" # <<< URL của Backend API
USER_ID_DEMO = "user_demo_123" # <<< ID người dùng giả lập
AUTH_TOKEN_DEMO = "your_jwt_token_here" # <<< Token xác thực giả lập
REFRESH_INTERVAL_SECONDS = 2 # Tần suất làm mới giao diện

# --- Enum (Ví dụ - Nên import từ module chung) ---
class OrderSide(str, Enum):
    BUY = 'BUY'
    SELL = 'SELL'

class OrderStatus(str, Enum):
    PENDING = 'PENDING'
    COMPLETE = 'COMPLETE'
    FAILED = 'FAILED'
    CANCELLED = 'CANCELLED'

# --- Kết nối Redis ---
try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        decode_responses=True, # Tự động decode
        socket_timeout=1, # Timeout ngắn để tránh treo
        socket_connect_timeout=1
    )
    redis_client.ping() # Kiểm tra kết nối
    st.session_state.redis_connected = True
    print("Connected to Redis successfully.")
except redis.exceptions.ConnectionError as e:
    st.session_state.redis_connected = False
    print(f"Failed to connect to Redis: {e}")
    # Hiển thị lỗi trên UI ở lần chạy đầu
    if 'redis_error_shown' not in st.session_state:
        st.error(f"Không thể kết nối đến Redis tại {REDIS_HOST}:{REDIS_PORT}. Dữ liệu realtime sẽ không hoạt động.", icon="🚨")
        st.session_state.redis_error_shown = True


# --- Hàm tương tác Backend/Cache ---

def get_data_from_redis(key_pattern: str, data_type: str = 'hash'):
    """Hàm tiện ích đọc dữ liệu từ Redis (cần xử lý lỗi tốt hơn)."""
    if not st.session_state.redis_connected:
        return {} if data_type == 'hash' else []

    try:
        if data_type == 'hash':
            # Ví dụ lấy Hash (cho price, index)
            keys = redis_client.keys(key_pattern)
            data = {}
            for key in keys:
                # Giả sử key có dạng prefix:name
                name = key.split(':')[-1]
                data[name] = redis_client.hgetall(key)
            return data
        elif data_type == 'zset': # Ví dụ lấy Sorted Set (cho order book)
             # key_pattern ở đây là key cụ thể, vd 'bid:VN30F2505'
             # withscores=True trả về list of tuples [(value, score), ...]
             # score thường là giá, value là quantity hoặc ngược lại tùy cách lưu
             return redis_client.zrange(key_pattern, 0, 4, withscores=True, desc=(key_pattern.startswith('bid'))) # Lấy top 5
        # Thêm các kiểu dữ liệu khác nếu cần (string, list)
    except redis.exceptions.TimeoutError:
        print(f"Redis timeout fetching {key_pattern}")
        st.warning("Redis timeout.", icon="⚠️")
    except Exception as e:
        print(f"Error fetching from Redis ({key_pattern}): {e}")
    return {} if data_type == 'hash' else []

def fetch_market_data():
    """Lấy dữ liệu thị trường từ Redis."""
    st.session_state.indices_real = get_data_from_redis("index:*")
    st.session_state.prices_real = get_data_from_redis("price:*")
    # Lấy OHLC nếu có key riêng
    st.session_state.ohlc_real = get_data_from_redis(f"ohlc:{st.session_state.get('current_symbol', 'VN30F2505')}")

    # Lấy Order Book cho mã hiện tại
    symbol = st.session_state.get('current_symbol', 'VN30F2505')
    # Giả sử lưu bids/asks vào Sorted Set, score là giá, value là KL (hoặc ngược lại)
    # Cần điều chỉnh key và logic parse tùy theo cách lưu trong Redis
    raw_bids = get_data_from_redis(f"bid:{symbol}", data_type='zset') # Giá cao nhất trước
    raw_asks = get_data_from_redis(f"ask:{symbol}", data_type='zset') # Giá thấp nhất trước (desc=False mặc định)

    # Chuyển đổi sang format mong muốn [[qty, price]] hoặc [[price, qty]]
    st.session_state.order_book_real = {
         # Giả sử value là KL, score là Giá
        "bids": [[float(qty), float(price)] for qty, price in raw_bids] if raw_bids else [],
        "asks": [[float(price), float(qty)] for qty, price in raw_asks] if raw_asks else [],
        # Lấy giá khớp cuối từ key price:* hoặc key riêng
        "last_match_price": float(st.session_state.prices_real.get(symbol, {}).get('last_price', 0)),
        "last_match_vol": float(st.session_state.prices_real.get(symbol, {}).get('last_vol', 0)),
    }
    # Lấy chart data (có thể từ Redis list, hoặc API khác) - Phần này phức tạp, tạm bỏ qua fetch realtime
    # st.session_state.chart_data_real = fetch_chart_data_from_source(symbol)

def call_api(method: str, endpoint: str, payload: Optional[dict] = None) -> Optional[dict]:
    """Hàm gọi API backend."""
    headers = {"Authorization": f"Bearer {AUTH_TOKEN_DEMO}"} # <<< Thêm header xác thực
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, timeout=5)
        elif method.upper() == 'POST':
            response = requests.post(url, json=payload, headers=headers, timeout=10)
        # Thêm các method khác (PUT, DELETE) nếu cần
        else:
            st.error(f"HTTP method không hợp lệ: {method}")
            return None

        response.raise_for_status() # Raise lỗi cho HTTP status codes >= 400
        return response.json() # Trả về dữ liệu JSON nếu thành công

    except requests.exceptions.ConnectionError:
        st.error("Lỗi kết nối đến API server.", icon="🚨")
    except requests.exceptions.Timeout:
        st.error("API request timeout.", icon="⏱️")
    except requests.exceptions.HTTPError as e:
        # Cố gắng parse lỗi từ response body nếu có
        error_detail = str(e)
        try:
            error_json = e.response.json()
            error_detail = error_json.get("detail", error_detail)
        except json.JSONDecodeError:
            pass # Giữ lỗi gốc nếu response không phải JSON
        st.error(f"API Error {e.response.status_code}: {error_detail}", icon="🔥")
    except Exception as e:
        st.error(f"Lỗi không xác định khi gọi API: {e}", icon="❓")
    return None

def fetch_account_info():
    """Lấy thông tin tài khoản và danh mục từ API."""
    balance_data = call_api('GET', f"/account/{USER_ID_DEMO}/balance")
    holdings_data = call_api('GET', f"/account/{USER_ID_DEMO}/holdings")
    orders_data = call_api('GET', f"/orders/{USER_ID_DEMO}/recent") # Lấy lệnh gần đây

    if balance_data:
        st.session_state.account_real = balance_data # Lưu cấu trúc trả về từ API
    if holdings_data:
        # Chuyển list holdings từ API thành dict để dễ truy cập
        st.session_state.holdings_real = {h['symbol']: h for h in holdings_data}
    if orders_data:
         st.session_state.orders_real = orders_data # Lưu list lệnh

# --- Khởi tạo State (Chỉ chạy lần đầu) ---
if 'last_fetch_time' not in st.session_state:
    st.session_state.last_fetch_time = 0
    st.session_state.current_symbol = "VN30F2505"
    st.session_state.selected_order_type = "LO"
    # Khởi tạo các state *_real với giá trị rỗng/mặc định
    st.session_state.indices_real = {}
    st.session_state.prices_real = {}
    st.session_state.ohlc_real = {}
    st.session_state.order_book_real = {"bids": [], "asks": [], "last_match_price": 0, "last_match_vol": 0}
    st.session_state.chart_data_real = [] # Cần fetch lần đầu nếu muốn hiển thị chart
    st.session_state.account_real = {"nav": 0, "cash": 0, "stock_value": 0, "buying_power": 0, "securing_amount": 0}
    st.session_state.holdings_real = {}
    st.session_state.orders_real = []
    # Fetch lần đầu
    if st.session_state.redis_connected:
        fetch_market_data()
    fetch_account_info() # Fetch tài khoản/lệnh lần đầu

# --- Logic Cập nhật Dữ liệu Định kỳ ---
now = time.time()
if now - st.session_state.last_fetch_time > REFRESH_INTERVAL_SECONDS:
    st.session_state.last_fetch_time = now
    if st.session_state.redis_connected:
        fetch_market_data()
    # Có thể fetch lại account/orders ở đây nếu muốn cập nhật thường xuyên hơn,
    # nhưng có thể không cần thiết nếu không có thay đổi thường xuyên.
    # fetch_account_info()
    needs_rerun = True
else:
    needs_rerun = False

# --- Render Giao diện (Sử dụng dữ liệu *_real từ st.session_state) ---

# --- Hàm Render (Sửa đổi để dùng *_real data) ---
def display_index_tickers_real():
    indices = st.session_state.indices_real
    if not indices:
        st.warning("Không có dữ liệu index từ Redis.")
        return
    cols = st.columns(len(indices))
    i = 0
    for index, data in indices.items():
        try:
             # Parse data từ Redis (giả sử là string)
             value = float(data.get('value', 0))
             ref = float(data.get('ref', value)) # Nếu không có ref, coi như không đổi
             change = value - ref
             pct_change = (change / ref) * 100 if ref else 0

             delta_color = "off"
             if change > 0: delta_color = "normal"
             elif change < 0: delta_color = "inverse"
             with cols[i]:
                 st.metric(
                     label=index,
                     value=f"{value:,.2f}",
                     delta=f"{change:,.2f} ({pct_change:.2f}%)",
                     delta_color=delta_color
                 )
        except Exception as e:
             with cols[i]:
                  st.error(f"Lỗi index {index}")
                  print(f"Error parsing index {index} data {data}: {e}")
        i += 1

def display_chart_real():
    st.subheader(f"Biểu đồ {st.session_state.current_symbol}")
    # TODO: Lấy và vẽ chart_data_real nếu có
    if not st.session_state.get('chart_data_real'):
         st.info("Chưa có dữ liệu biểu đồ.")
         # Có thể vẽ biểu đồ tĩnh hoặc gọi API lấy dữ liệu lịch sử ở đây
         return
    # (Logic vẽ Plotly tương tự ví dụ trước, dùng st.session_state.chart_data_real)


def display_price_info_real():
    symbol = st.session_state.current_symbol
    price_data = st.session_state.prices_real.get(symbol, {})
    ohlc_data = st.session_state.ohlc_real # Đã fetch cho symbol hiện tại

    try:
        price = float(price_data.get('last_price', 0))
        ref = float(price_data.get('ref', price))
        change = price - ref
        pct_change = (change / ref) * 100 if ref else 0

        open_p = float(ohlc_data.get('open', 0))
        high_p = float(ohlc_data.get('high', 0))
        low_p = float(ohlc_data.get('low', 0))
        close_p = price # Lấy giá hiện tại làm close
        volume = int(price_data.get('volume', 0))
        ceil_p = float(price_data.get('ceil', 0))
        floor_p = float(price_data.get('floor', 0))

        delta_color = "off"
        if change > 0: delta_color = "normal"
        elif change < 0: delta_color = "inverse"

        col1, col2 = st.columns([2, 3])
        with col1:
            st.subheader(symbol)
        with col2:
            st.metric(label="Giá hiện tại", value=f"{price:,.1f}", delta=f"{change:+.2f} ({pct_change:+.2f}%)", delta_color=delta_color)

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Mở", f"{open_p:,.1f}")
        c2.metric("Cao", f"{high_p:,.1f}")
        c3.metric("Thấp", f"{low_p:,.1f}")
        c4.metric("Đóng", f"{close_p:,.1f}") # Hiển thị giá hiện tại như giá đóng gần nhất
        c5.metric("KL", f"{volume:,}")

        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"**TC:** <span style='color:#f4b400;'>{ref:,.1f}</span>", unsafe_allow_html=True)
        c2.markdown(f"**Trần:** <span style='color:#db4437;'>{ceil_p:,.1f}</span>", unsafe_allow_html=True)
        c3.markdown(f"**Sàn:** <span style='color:#0f9d58;'>{floor_p:,.1f}</span>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Lỗi hiển thị thông tin giá cho {symbol}.")
        print(f"Error parsing price/ohlc data {price_data}, {ohlc_data}: {e}")


def display_order_book_real():
    st.subheader("Bước giá - Khớp lệnh")
    ob = st.session_state.order_book_real
    stock = st.session_state.prices_real.get(st.session_state.current_symbol, {})
    ref_price = float(stock.get('ref', 0))

    col1, col2, col3 = st.columns([2, 1, 2])

    with col1: # Bids (KL Mua - Giá Mua)
        st.markdown("**KL Mua** | **Giá Mua**")
        if not ob['bids']: st.caption("...")
        for qty, price in ob['bids']: # Đã sort sẵn từ Redis ZRANGE DESC
             st.markdown(f"<span style='color:grey;'>{int(qty):,}</span> | <span style='color:#0f9d58; font-weight:bold;'>{price:,.1f}</span>", unsafe_allow_html=True)

    with col2: # Last Match
         price = ob['last_match_price']
         vol = ob['last_match_vol']
         color_cls = "green" if price >= ref_price else "red"
         if price == ref_price: color_cls = "orange"
         st.markdown(f"""
         <div style='text-align: center; border-top: 1px solid #ccc; border-bottom: 1px solid #ccc; padding: 10px 0; margin: 5px 0;'>
              <span style='color:{color_cls}; font-weight: bold; font-size: 1.2em;'>{price:,.1f}</span><br/>
              <span style='color:grey; font-size: 0.9em;'>{vol:,.0f}</span>
         </div>
         """, unsafe_allow_html=True)

    with col3: # Asks (Giá Bán - KL Bán)
        st.markdown("**Giá Bán** | **KL Bán**")
        if not ob['asks']: st.caption("...")
        for price, qty in ob['asks']: # Đã sort sẵn từ Redis ZRANGE ASC
             st.markdown(f"<span style='color:#db4437; font-weight:bold;'>{price:,.1f}</span> | <span style='color:grey;'>{int(qty):,}</span>", unsafe_allow_html=True)

def display_order_entry_real():
    st.subheader("Đặt Lệnh")
    acc = st.session_state.account_real
    # Lấy giá thị trường hiện tại để tính toán
    current_price = st.session_state.order_book_real.get('last_match_price', 0)

    default_symbol = st.session_state.current_symbol
    order_symbol = st.text_input("Mã CK:", value=default_symbol, key="order_symbol_input").upper()
    # Cập nhật symbol đang xem nếu người dùng nhập mã khác
    if order_symbol != st.session_state.current_symbol:
        st.session_state.current_symbol = order_symbol
        # Fetch lại data cho mã mới
        if st.session_state.redis_connected:
             fetch_market_data() # Lấy giá, sổ lệnh mới
        st.rerun() # Chạy lại để cập nhật UI với mã mới

    order_type = st.radio(
        "Loại lệnh:", ("LO", "MP"),
        index=0 if st.session_state.selected_order_type == "LO" else 1,
        horizontal=True, key="order_type_radio_real"
    )
    st.session_state.selected_order_type = order_type

    limit_price = None
    price_input_disabled = (order_type != "LO")
    limit_price_value = current_price if order_type == "LO" else 0.0
    if order_type == "LO":
        limit_price = st.number_input("Giá đặt:", min_value=0.1, value=limit_price_value, step=0.1, format="%.1f", key="limit_price_input")

    quantity = st.number_input("KL đặt:", min_value=1, value=1, step=1, key="quantity_input")

    # Tính toán sức mua/bán
    current_holding = st.session_state.holdings_real.get(order_symbol)
    # available_shares = current_holding['quantity'] - current_holding.get('locked_quantity', 0) if current_holding else 0 # Nếu có locked_qty
    available_shares = current_holding['quantity'] if current_holding else 0
    price_for_calc = limit_price if order_type == "LO" and limit_price else current_price
    max_buy_qty = int(acc['buying_power'] // price_for_calc) if price_for_calc > 0 else 0

    col1, col2 = st.columns(2)
    # Biến cờ để chỉ rerun MỘT LẦN sau khi nhấn nút
    trigger_rerun = False
    with col1:
        if st.button("MUA", type="primary", use_container_width=True, key="buy_button"):
            payload = {
                "symbol": order_symbol,
                "side": OrderSide.BUY.value,
                "quantity": quantity,
                "order_type": order_type,
                "limit_price": int(limit_price * 10) if limit_price else None # Gửi giá nguyên nếu API yêu cầu
            }
            st.write("Đang gửi lệnh MUA...") # Phản hồi tạm thời
            api_response = call_api('POST', '/orders', payload=payload)
            if api_response and api_response.get("status") == "PENDING": # Kiểm tra response thành công từ API
                st.success(f"Lệnh MUA {quantity} {order_symbol} đã được gửi thành công (ID: {api_response.get('order_id','N/A')}).")
                # Fetch lại thông tin tài khoản và lệnh sau khi đặt thành công
                fetch_account_info()
                trigger_rerun = True
            else:
                # call_api đã hiển thị lỗi chi tiết
                st.warning("Gửi lệnh MUA thất bại.")

    with col2:
        if st.button("BÁN", use_container_width=True, key="sell_button"):
            payload = {
                "symbol": order_symbol,
                "side": OrderSide.SELL.value,
                "quantity": quantity,
                "order_type": order_type,
                "limit_price": int(limit_price * 10) if limit_price else None
            }
            st.write("Đang gửi lệnh BÁN...")
            api_response = call_api('POST', '/orders', payload=payload)
            if api_response and api_response.get("status") == "PENDING":
                st.success(f"Lệnh BÁN {quantity} {order_symbol} đã được gửi thành công (ID: {api_response.get('order_id','N/A')}).")
                fetch_account_info()
                trigger_rerun = True
            else:
                st.warning("Gửi lệnh BÁN thất bại.")

    st.caption(f"Mua tối đa: {max_buy_qty:,} | Bán tối đa: {available_shares:,}")

    # Chỉ rerun nếu có nút được nhấn và API gọi thành công (hoặc thất bại nhưng muốn refresh)
    if trigger_rerun:
         time.sleep(0.5) # Đợi chút để user thấy message
         st.rerun()


def display_balance_real():
    st.subheader("Tài sản")
    acc = st.session_state.account_real
    st.metric("TÀI SẢN RÒNG", f"{acc.get('nav', 0):,.0f}")
    st.metric("Tiền", f"{acc.get('cash', 0):,.0f}")
    st.metric("Giá trị cổ phiếu", f"{acc.get('stock_value', 0):,.0f}")
    st.metric("Sức mua", f"{acc.get('buying_power', 0):,.0f}")
    st.metric("Tiền đang khóa", f"{acc.get('securing_amount', 0):,.0f}")

def display_holdings_real():
    st.subheader("Deal nắm giữ")
    holdings = st.session_state.holdings_real
    prices = st.session_state.prices_real # Lấy giá TT từ cache
    if not holdings:
        st.info("Chưa nắm giữ cổ phiếu nào.")
        return

    data_for_df = []
    for symbol, h_data in holdings.items():
        # Lấy giá thị trường mới nhất từ cache
        market_price = float(prices.get(symbol, {}).get('last_price', h_data.get('cost_basis', 0))) # Fallback về giá vốn nếu không có giá TT
        cost_basis = h_data.get('cost_basis', 0)
        quantity = h_data.get('quantity', 0)

        market_value = quantity * market_price
        cost_value = quantity * cost_basis
        pnl = market_value - cost_value
        pnl_pct = (pnl / cost_value) * 100 if cost_value else 0
        data_for_df.append({
            "Mã CK": symbol,
            "KL": quantity,
            "Giá vốn": f"{cost_basis:,.0f}",
            "Giá TT": f"{market_price:,.1f}", # Hiển thị giá TT chính xác hơn
            "+/- (%)": f"{pnl:,.0f} ({pnl_pct:.1f}%)"
        })

    df = pd.DataFrame(data_for_df)
    # TODO: Thêm định dạng màu sắc cho PnL nếu muốn
    st.dataframe(df, use_container_width=True, hide_index=True)

def display_order_list_real():
     st.subheader("Sổ lệnh thường")
     orders = st.session_state.get('orders_real', [])
     if not orders:
          st.info("Chưa có lệnh trong ngày.")
          # Nút để fetch lại lệnh nếu muốn
          if st.button("Tải lại danh sách lệnh"):
              fetch_account_info()
              st.rerun()
          return

     df_orders = pd.DataFrame(orders[::-1]) # Hiển thị lệnh mới nhất lên trên
     if not df_orders.empty:
         # Chọn lọc và đổi tên cột (điều chỉnh tên cột dựa trên API response thực tế)
         columns_to_show = ['order_id', 'side', 'symbol', 'order_type', 'quantity', 'limit_price', 'status', 'created_at', 'error_message']
         display_columns = {
            'order_id': 'ID Lệnh', 'side': 'M/B', 'symbol': 'Mã CK', 'order_type': 'Loại',
            'quantity':'KL Đặt', 'limit_price': 'Giá Đặt', 'status': 'Trạng Thái',
            'created_at': 'Thời gian', 'error_message': 'Lỗi'
         }
         # Lọc các cột tồn tại trong DataFrame
         existing_cols = [col for col in columns_to_show if col in df_orders.columns]
         df_display = df_orders[existing_cols].rename(columns=display_columns)

         # Định dạng cột Giá Đặt và Thời gian
         if 'Giá Đặt' in df_display.columns:
              df_display['Giá Đặt'] = df_display.apply(lambda row: f"{row['Giá Đặt']/10:,.1f}" if row['Loại'] == 'LO' and row['Giá Đặt'] else row['Loại'], axis=1) # Chia 10 nếu API trả giá nguyên
         if 'Thời gian' in df_display.columns:
              df_display['Thời gian'] = pd.to_datetime(df_display['Thời gian']).dt.strftime('%H:%M:%S %d/%m') # Format thời gian

         st.dataframe(df_display, use_container_width=True, hide_index=True)
     else:
          st.info("Chưa có lệnh trong ngày.")

     if st.button("Tải lại danh sách lệnh "): # Thêm khoảng trắng để key khác
          fetch_account_info()
          st.rerun()


# --- Render Giao diện Chính ---
display_index_tickers_real()
st.divider()

col_left, col_right = st.columns([3, 1.2]) # Điều chỉnh tỷ lệ cột

with col_left:
    # display_chart_real() # Tạm ẩn chart phức tạp
    st.info("Biểu đồ sẽ được tích hợp sau.") # Placeholder
    tab_orders, tab_holdings = st.tabs(["Sổ lệnh thường", "Deal nắm giữ"])
    with tab_orders:
         display_order_list_real()
    with tab_holdings:
        display_holdings_real()


with col_right:
    with st.container(border=True):
        display_price_info_real()
    with st.container(border=True):
        display_order_book_real()
    with st.container(border=True):
        display_order_entry_real()
    with st.container(border=True):
         display_balance_real()


# --- Tự động chạy lại script ---
if needs_rerun:
     time.sleep(0.1) # Chờ chút xíu
     try:
          st.rerun()
     except Exception as e:
          # Xử lý lỗi nếu st.rerun gặp vấn đề (ít khi)
          print(f"Error during st.rerun: {e}")
          # Có thể đặt lại cờ hoặc đợi lâu hơn
          time.sleep(REFRESH_INTERVAL_SECONDS)
          st.rerun()

else:
     # Vẫn rerun định kỳ ngay cả khi không có update từ fetch
     time.sleep(REFRESH_INTERVAL_SECONDS)
     try:
          st.rerun()
     except Exception as e:
          print(f"Error during periodic st.rerun: {e}")
          time.sleep(REFRESH_INTERVAL_SECONDS) # Đợi lâu hơn nếu lỗi
          st.rerun()