import streamlit as st
import time

from frontend.services import InvestorsService
from frontend.cookies import WebCookieController
from backend.utils.logger import LOGGER


@st.dialog("Nạp Tiền vào Tài khoản")
def show_deposit_dialog(): # Tên hàm có thể tùy ý
    st.write(f"Tài khoản: {WebCookieController.get('account')}")
    st.markdown("---")

    user_id = WebCookieController.get("userId")
    if not user_id:
        st.error("Không thể xác định người dùng.")
        if st.button("Đóng"):
            st.rerun()
        return

    # Sử dụng form bên trong dialog
    with st.form("deposit_dialog_form_in_func"):
        amount_to_deposit = st.number_input(
            "Số tiền muốn nạp (VND):",
            min_value=10000, value=100000, step=10000, format="%d",
            key="dialog_amount_input"
        )
        payment_method = st.selectbox(
            "Phương thức thanh toán (Giả lập):",
            ("Chuyển khoản ngân hàng", "Ví điện tử Momo", "Thẻ tín dụng/ghi nợ"),
            key="dialog_payment_method_input"
        )
        notes = st.text_area("Ghi chú (nếu có):", key="dialog_notes_input")

        submitted_deposit = st.form_submit_button("Xác nhận Nạp tiền", type="primary")

        if submitted_deposit:
            if amount_to_deposit <= 0:
                st.error("Số tiền nạp phải lớn hơn 0.", icon="⚠️")
            else:
                st.info(f"Đang xử lý nạp {amount_to_deposit:,.0f} VND...")
                LOGGER.info(f"User {user_id} submitted deposit from dialog: Amount={amount_to_deposit}, Method={payment_method}")

                time.sleep(1)
                response = InvestorsService.deposit(amount=amount_to_deposit)

                if response.get("statusCode") == 200:
                    st.success("Nạp tiền thành công!", icon="✅")
                    st.rerun()
                else:
                    st.info(f"Nạp tiền thất bại: {response.get('error')}", icon="❌")

    if st.button("Hủy nạp tiền", key="dialog_cancel_manual"):
         st.rerun()