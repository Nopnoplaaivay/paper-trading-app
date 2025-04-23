
# src/redis_client.py
# ... (imports và _connect_redis, get_redis_client như trước) ...

def get_market_data_for_symbol(symbol: str) -> Dict[str, Any]:
    """Fetches market data for a specific symbol from Redis."""
    r = get_redis_client()
    if not r:
        return {
            "price_info": {},
            "order_book": {"bids": [], "asks": [], "last_match_price": 0, "last_match_vol": 0},
            "ohlc": {} # Thêm nếu có
        }

    data = {
        "price_info": {},
        "order_book": {"bids": [], "asks": [], "last_match_price": 0, "last_match_vol": 0},
        "ohlc": {}
        }
    symbol = symbol.upper() # Đảm bảo symbol viết hoa

    try:
        # Price Info (Giả sử key là price:SYMBOL)
        data["price_info"] = r.hgetall(f"price:{symbol}")

        # Order Book (Giả sử key là bid:SYMBOL và ask:SYMBOL)
        raw_bids = r.zrange(f"bid:{symbol}", 0, 4, withscores=True, desc=True)
        raw_asks = r.zrange(f"ask:{symbol}", 0, 4, withscores=True)
        data["order_book"]["bids"] = [[float(v), float(s)] for v, s in raw_bids]
        data["order_book"]["asks"] = [[float(s), float(v)] for v, s in raw_asks]
        data["order_book"]["last_match_price"] = float(data["price_info"].get('last_price', 0))
        data["order_book"]["last_match_vol"] = float(data["price_info"].get('last_vol', 0))

        # OHLC (Giả sử key là ohlc:SYMBOL)
        data["ohlc"] = r.hgetall(f"ohlc:{symbol}")

    except Exception as e:
        logger.error(f"Error fetching market data for {symbol} from Redis: {e}")
        st.warning(f"Could not fetch market data for {symbol} from Redis.", icon="⚠️")
    return data

def get_all_indices_redis() -> Dict[str, Any]:
     """Fetches all index data."""
     r = get_redis_client()
     if not r: return {}
     indices = {}
     try:
         index_keys = r.keys("index:*")
         for key in index_keys:
             name = key.split(':')[-1]
             indices[name] = r.hgetall(key)
     except Exception as e:
          logger.error(f"Error fetching indices from Redis: {e}")
     return indices

# Bỏ hàm get_market_data_redis cũ nếu không dùng nữa

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
from src.auth import require_login, get_user_id
from src.api_client import (
    api_get_balance, api_get_holdings, api_get_recent_orders, api_place_order
)
# Import hàm lấy data mới từ redis_client
from src.redis_client import get_market_data_for_symbol, get_all_indices_redis
from src.config import REFRESH_INTERVAL_SECONDS
from src.utils import logger
# Import lại các hàm display nếu đã tách ra
# from src.display_components import ...
# Hoặc định nghĩa lại chúng ở đây (ví dụ ngắn gọn)

# --- Page Protection ---
require_login(role="client")

# --- Initialize State ---
def init_trading_state():
    # Chỉ khởi tạo nếu chưa có hoặc cần reset
    if 'current_symbol' not in st.session_state:
        st.session_state.current_symbol = "VN30F2505" # Mã mặc định ban đầu
    if 'selected_order_type' not in st.session_state:
        st.session_state.selected_order_type = "LO"
    if 'last_fetch_time_trade' not in st.session_state:
        st.session_state.last_fetch_time_trade = 0
    # Các state data khác sẽ được fetch và cập nhật
    if 'market_data' not in st.session_state:
         st.session_state.market_data = {
             "price_info": {}, "order_book": {"bids": [], "asks": [], "last_match_price": 0, "last_match_vol": 0}, "ohlc": {}
         }
    if 'indices_real' not in st.session_state:
         st.session_state.indices_real = {}
    if 'account_real' not in st.session_state:
        st.session_state.account_real = {"nav": 0, "cash": 0, "stock_value": 0, "buying_power": 0, "securing_amount": 0}
    if 'holdings_real' not in st.session_state:
        st.session_state.holdings_real = {}
    if 'orders_real' not in st.session_state:
        st.session_state.orders_real = []
    # Thêm state cho input trong form để truy cập trong callback
    if 'order_symbol_input' not in st.session_state:
         st.session_state.order_symbol_input = st.session_state.current_symbol


init_trading_state()
user_id = get_user_id() # Lấy user_id một lần

# --- Callback Function for Symbol Change ---
def handle_symbol_change():
    # Hàm này được gọi BẤT CỨ KHI NÀO giá trị của text_input thay đổi
    new_symbol = st.session_state.order_symbol_input.strip().upper()
    if new_symbol and new_symbol != st.session_state.current_symbol:
        logger.info(f"Symbol changed via input: {st.session_state.current_symbol} -> {new_symbol}")
        st.session_state.current_symbol = new_symbol
        # Reset thời gian fetch để fetch data mới ngay lập tức ở lần rerun tới
        st.session_state.last_fetch_time_trade = 0
        # KHÔNG gọi st.rerun() ở đây để tránh vòng lặp vô hạn

# --- Fetch Data ---
def fetch_trading_data(force_fetch_account=False):
    global needs_rerun # Sử dụng biến global để báo hiệu cần rerun
    now = time.time()

    # Chỉ fetch market data nếu đủ thời gian hoặc symbol thay đổi (last_fetch_time=0)
    if now - st.session_state.last_fetch_time_trade > REFRESH_INTERVAL_SECONDS or st.session_state.last_fetch_time_trade == 0:
        if st.session_state.get('redis_connected', False):
            logger.info(f"Fetching market data for: {st.session_state.current_symbol}")
            st.session_state.market_data = get_market_data_for_symbol(st.session_state.current_symbol)
            # Fetch indices riêng
            st.session_state.indices_real = get_all_indices_redis()
            st.session_state.last_fetch_time_trade = now
            needs_rerun = True # Đánh dấu cần rerun vì có data mới
        else:
            logger.warning("Cannot fetch market data, Redis not connected.")

    # Fetch account data lần đầu hoặc khi có yêu cầu (sau khi đặt lệnh)
    if 'account_real' not in st.session_state or st.session_state.last_fetch_time_trade == 0 or force_fetch_account:
        if user_id:
             logger.info(f"Fetching account info for user: {user_id}")
             balance_data = api_get_balance(user_id)
             holdings_data = api_get_holdings(user_id)
             orders_data = api_get_recent_orders(user_id)

             if balance_data: st.session_state.account_real = balance_data
             if holdings_data: st.session_state.holdings_real = {h['symbol']: h for h in holdings_data}
             if orders_data: st.session_state.orders_real = orders_data
             needs_rerun = True # Cần rerun để hiển thị account data mới

# --- Render Functions (Sử dụng dữ liệu market_data, account_real, etc. từ session_state) ---
# (Giữ nguyên các hàm display_* như trước, nhưng chúng sẽ đọc từ
# st.session_state.market_data, st.session_state.account_real, ...)
# Ví dụ sửa đổi display_price_info_real:
def display_price_info_real():
    symbol = st.session_state.current_symbol
    # Lấy dữ liệu đã fetch cho symbol hiện tại
    price_data = st.session_state.market_data.get("price_info", {})
    ohlc_data = st.session_state.market_data.get("ohlc", {})
    # ... (phần còn lại của hàm render dùng price_data, ohlc_data) ...
    try:
        price = float(price_data.get('last_price', 0))
        ref = float(price_data.get('ref', price)) # Dùng giá hiện tại nếu thiếu ref
        change = price - ref
        pct_change = (change / ref) * 100 if ref else 0

        # ... (Lấy OHLC, Volume, Ceil, Floor tương tự từ price_data hoặc ohlc_data) ...
        open_p = float(ohlc_data.get('open', price_data.get('open',0))) # Ưu tiên ohlc
        high_p = float(ohlc_data.get('high', price_data.get('high',0)))
        low_p = float(ohlc_data.get('low', price_data.get('low',0)))
        close_p = price # Giá hiện tại
        volume = int(price_data.get('volume', 0))
        ceil_p = float(price_data.get('ceil', 0))
        floor_p = float(price_data.get('floor', 0))


        delta_color = "off"
        if change > 0: delta_color = "normal"
        elif change < 0: delta_color = "inverse"

        col1, col2 = st.columns([2, 3])
        with col1:
            # Hiển thị symbol đang chọn
            st.subheader(symbol)
        with col2:
            st.metric(label="Giá hiện tại", value=f"{price:,.1f}", delta=f"{change:+.2f} ({pct_change:+.2f}%)", delta_color=delta_color)

        # ... (Hiển thị OHLC, Ceil, Floor như trước) ...
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Mở", f"{open_p:,.1f}")
        c2.metric("Cao", f"{high_p:,.1f}")
        c3.metric("Thấp", f"{low_p:,.1f}")
        c4.metric("Đóng", f"{close_p:,.1f}")
        c5.metric("KL", f"{volume:,}")

        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"**TC:** <span style='color:#f4b400;'>{ref:,.1f}</span>", unsafe_allow_html=True)
        c2.markdown(f"**Trần:** <span style='color:#db4437;'>{ceil_p:,.1f}</span>", unsafe_allow_html=True)
        c3.markdown(f"**Sàn:** <span style='color:#0f9d58;'>{floor_p:,.1f}</span>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Lỗi hiển thị thông tin giá cho {symbol}.")
        logger.error(f"Error rendering price info for {symbol}: {e}")


# Tương tự sửa các hàm display_order_book_real, display_chart_real (nếu có)
# để đọc từ st.session_state.market_data['order_book'], etc.

def display_order_entry_real():
    st.subheader("Đặt Lệnh")
    acc = st.session_state.account_real
    price_info = st.session_state.market_data.get("price_info", {})
    current_price = float(price_info.get('last_price', 0))

    # --- SỬ DỤNG ST.FORM ---
    with st.form("order_entry_form", clear_on_submit=True): # Clear form sau khi submit
        # Input mã CK với callback on_change
        st.text_input(
            "Mã CK:",
            value=st.session_state.current_symbol, # Giá trị hiện tại
            key="order_symbol_input",      # Key để truy cập state
            on_change=handle_symbol_change # Callback khi giá trị thay đổi
        )

        order_type = st.radio(
            "Loại lệnh:", ("LO", "MP"),
            index=0 if st.session_state.selected_order_type == "LO" else 1,
            horizontal=True, key="order_type_radio_form" # Key mới trong form
        )
        # Lưu lại lựa chọn để form giữ đúng trạng thái sau rerun (nếu clear_on_submit=False)
        # st.session_state.selected_order_type = order_type

        limit_price_form = None
        if order_type == "LO":
            limit_price_form = st.number_input("Giá đặt:", min_value=0.1, value=current_price, step=0.1, format="%.1f", key="limit_price_form")

        quantity_form = st.number_input("KL đặt:", min_value=1, value=1, step=1, key="quantity_form")

        # --- Hai nút Submit riêng biệt ---
        submitted_buy = st.form_submit_button("MUA", type="primary", use_container_width=True)
        submitted_sell = st.form_submit_button("BÁN", use_container_width=True)

        # --- Xử lý sau khi form được submit ---
        if submitted_buy or submitted_sell:
            order_symbol_form = st.session_state.order_symbol_input # Lấy từ state key
            side = OrderSide.BUY if submitted_buy else OrderSide.SELL

            # Validate lại lần nữa trước khi gửi
            if not order_symbol_form:
                 st.error("Vui lòng nhập Mã CK.")
            elif quantity_form <= 0:
                 st.error("Vui lòng nhập Khối lượng > 0.")
            elif order_type == "LO" and (limit_price_form is None or limit_price_form <= 0):
                 st.error("Vui lòng nhập Giá đặt > 0 cho lệnh LO.")
            else:
                 # Tạo payload và gọi API
                 payload = {
                     "symbol": order_symbol_form,
                     "side": side.value,
                     "quantity": quantity_form,
                     "order_type": order_type,
                     "limit_price": int(limit_price_form * 10) if order_type == "LO" and limit_price_form else None
                 }
                 st.info(f"Đang gửi lệnh {side.value} {order_symbol_form}...") # Phản hồi ngay
                 api_response = api_place_order(payload)

                 if api_response and api_response.get("status") in ["PENDING", "COMPLETE"]: # Kiểm tra trạng thái trả về
                     st.success(f"Lệnh {side.value} {quantity_form} {order_symbol_form} đã gửi thành công (ID: {api_response.get('order_id','N/A')}).")
                     # Fetch lại account info NGAY LẬP TỨC sau khi lệnh thành công
                     fetch_trading_data(force_fetch_account=True)
                     # Không cần rerun ở đây, form submit đã trigger rerun rồi
                 else:
                     # call_api đã hiển thị lỗi
                     st.warning(f"Gửi lệnh {side.value} thất bại.")
                 # Không cần trigger_rerun nữa vì form submit tự rerun

    # Hiển thị thông tin sức mua/bán bên ngoài form
    current_holding = st.session_state.holdings_real.get(st.session_state.current_symbol)
    available_shares = current_holding['quantity'] if current_holding else 0
    price_for_calc = limit_price_value = st.session_state.market_data.get("price_info", {}).get('last_price', 1) # Lấy giá hiện tại
    max_buy_qty = int(acc.get('buying_power', 0) // price_for_calc) if price_for_calc > 0 else 0
    st.caption(f"Mua tối đa: {max_buy_qty:,} | Bán tối đa: {available_shares:,}")

# (Các hàm display_balance_real, display_holdings_real, display_order_list_real giữ nguyên)


# --- MAIN SCRIPT LOGIC ---
st.title("Trading Interface")
if user_id:
    st.write(f"User: {st.session_state.get('username', 'N/A')} ({user_id})")
else:
     st.error("User not identified. Please login again.")
     st.stop()
st.divider()

# Biến cờ để kiểm tra xem có cần rerun không
needs_rerun = False
# Fetch data (chỉ fetch market data nếu đủ thời gian hoặc symbol thay đổi)
fetch_trading_data()

# --- Render UI ---
display_index_tickers_real() # Nên fetch index riêng nếu nó không đổi theo symbol
st.divider()

col_left, col_right = st.columns([3, 1.2])

with col_left:
    # display_chart_real() # Tạm ẩn
    st.info("Biểu đồ Tạm ẩn")
    tab_orders, tab_holdings = st.tabs(["Sổ lệnh thường", "Deal nắm giữ"])
    with tab_orders:
         display_order_list_real()
    with tab_holdings:
        display_holdings_real()


with col_right:
    # Các container này sẽ tự cập nhật khi st.rerun được gọi
    # và chúng đọc dữ liệu mới nhất từ session_state
    with st.container(border=True):
        display_price_info_real()
    with st.container(border=True):
        display_order_book_real()
    with st.container(border=True):
        display_order_entry_real() # Form xử lý bên trong
    with st.container(border=True):
         display_balance_real()

# --- Rerun Logic (Chỉ chạy lại theo định kỳ) ---
# Form submission và symbol change sẽ tự động trigger rerun khi cần thiết
if needs_rerun:
    # Nếu fetch_data đã đánh dấu cần rerun, thực hiện ngay
     time.sleep(0.1) # Đợi ngắn
     try: st.rerun()
     except Exception as e: logger.error(f"Immediate rerun failed: {e}"); time.sleep(REFRESH_INTERVAL_SECONDS); st.rerun()
else:
    # Nếu không có data mới, vẫn rerun định kỳ
    time.sleep(REFRESH_INTERVAL_SECONDS)
    try: st.rerun()
    except Exception as e: logger.error(f"Periodic rerun failed: {e}"); time.sleep(REFRESH_INTERVAL_SECONDS); st.rerun()