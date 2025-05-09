import streamlit as st

st.set_page_config(layout="wide", page_title="Admin Panel")

import pandas as pd

from frontend.services import AuthService, AdminService
from frontend.cookies import WebCookieController
from frontend.components import display_app_header

AuthService.require_login(role="admin")

display_app_header(page_name="admin")

st.title("⚙️ Admin Control Panel")
st.caption(f"Welcome, Admin {WebCookieController.get('account')}!")
st.divider()



st.session_state.users_data = AdminService.get_all_users()
st.session_state.orders_data = AdminService.get_all_orders()


# --- Main Admin Panel Tabs ---
tab_users, tab_orders_mgt = st.tabs([
    "👥 User Management", "🛠️ Order Management"
])



with tab_users:
    st.header("User Management")
    if st.button("Refresh User List", key="refresh_users"):
        st.session_state.users_data = AdminService.get_all_users()
        st.rerun()

    users_data = st.session_state.users_data
    if users_data:
        df_users = pd.DataFrame(users_data)
        df_users.rename(columns={
            "__created_at__": "created_at",
            "__updated_at__": "updated_at"
        }, inplace=True)



        st.subheader("All Users")
        display_cols_users = ['id', 'account', 'role', 'created_at', 'updated_at']
        existing_user_cols = [col for col in display_cols_users if col in df_users.columns]
        st.dataframe(df_users[existing_user_cols], use_container_width=True, hide_index=True)

        st.subheader("User Actions")
        selected_user_id = st.selectbox(
            "Select User ID to Manage:",
            options=[""] + [user.get("id") for user in users_data if user.get("id")],
            format_func=lambda x: next((user.get("account", x) for user in users_data if user.get("id") == x), x)
        )

        if selected_user_id:
            selected_user = next((user for user in users_data if user.get("id") == selected_user_id), None)
            if selected_user:
                st.write(f"Managing User: **{selected_user.get('username')}** (ID: {selected_user_id})")
                col_action1, col_action2 = st.columns(2)
                with col_action1:
                    new_role = st.selectbox(
                        "Change Role to:",
                        options=["client", "admin"],
                        index=["client", "admin"].index(selected_user.get("role", "client")),
                        key=f"role_change_{selected_user_id}"
                    )
                    if st.button(f"Update Role for {selected_user.get('account')}", key=f"update_role_btn_{selected_user_id}"):
                        if new_role != selected_user.get("role"):
                            response = AdminService.update_user_role(selected_user_id, new_role)
                            if response.get("statusCode") == 200:
                                st.success(f"Role for {selected_user.get('account')} updated to {new_role}.")
                            else:
                                st.error(f"Failed to update role: {response.get('errors', 'Unknown error')}")
                        else:
                            st.info("Role is already set to the selected value.")
            else:
                st.warning("Selected user not found in the current data.")
    else:
        st.info("There is no users.")


with tab_orders_mgt:
    st.header("Order Management")

    # Order Filters
    order_status_options = ["ALL", "PENDING", "COMPLETE", "CANCELED"]
    st.session_state.admin_order_filter = st.session_state.get("admin_order_filter", "ALL")
    selected_status_filter = st.selectbox(
        "Filter by Status:",
        options=order_status_options,
        index=order_status_options.index(st.session_state.admin_order_filter),
        key="admin_order_filter_select"
    )
    if selected_status_filter != st.session_state.admin_order_filter:
        st.session_state.admin_order_filter = selected_status_filter
        st.rerun()

    if st.button("Refresh Order List", key="refresh_orders_admin"):
        st.session_state.orders_data = AdminService.get_all_orders()
        st.rerun()

    orders_data = st.session_state.orders_data
    if orders_data:
        df_orders = pd.DataFrame(orders_data)
        df_orders.rename(columns={
            "__created_at__": "created_at",
            "__updated_at__": "updated_at"
        }, inplace=True)
        df_orders = df_orders.sort_values(by="created_at", ascending=False)
        df_orders = df_orders[df_orders["status"] == st.session_state.admin_order_filter] if st.session_state.admin_order_filter != "ALL" else df_orders

        st.subheader(f"All Orders (Status: {st.session_state.admin_order_filter})")
        if not df_orders.empty:
            cols_orders = ['id', 'account_id', 'side', 'symbol', 'order_type', 'quantity', 'limit_price', 'status', 'created_at']
            display_cols_orders = {k: k.replace('_', ' ').title() for k in cols_orders}
            existing_order_cols = [col for col in cols_orders if col in df_orders.columns]
            df_display_orders = df_orders[existing_order_cols].rename(columns=display_cols_orders)
            st.dataframe(df_display_orders, use_container_width=True, hide_index=True, height=400)

            st.subheader("Order Actions")
            order_id_to_cancel = st.text_input("Enter PENDING Order ID to Cancel:")
            if st.button("Cancel Selected Order", key="admin_cancel_order_btn"):
                if order_id_to_cancel:
                    response = AdminService.cancel_order(order_id_to_cancel)
                    if response.get("statusCode") == 200:
                        st.success(f"Order {order_id_to_cancel} cancelled successfully.")
                        st.rerun()
                    else:
                        st.error(f"Failed to cancel order {order_id_to_cancel}: {response.get('errors', 'Unknown error')}")
                else:
                    st.warning("Please enter an Order ID.")
        else:
            st.info(f"No orders found with status '{st.session_state.admin_order_filter}'.")
    else:
        st.warning("Could not load order data.")
