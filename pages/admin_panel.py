import streamlit as st

st.set_page_config(layout="wide", page_title="Admin Panel")

import pandas as pd
import plotly.express as px

from frontend.services import AuthService, AdminService
from frontend.cookies import WebCookieController
from frontend.components import display_app_header
# Import API client functions (these need to be implemented in your api_client.py)
# from backend.api_client import (
#     api_get_admin_system_stats,
#     api_get_admin_users,
#     api_update_user_role, # Example: to change a user's role
#     api_disable_user,    # Example: to disable/enable a user account
#     api_get_admin_all_orders,
#     api_cancel_order_admin, # Admin can cancel any pending order
#     api_get_system_logs,   # Fetch system logs
#     api_get_redis_info,    # Get info/stats from Redis
#     api_trigger_eod_job,   # Manually trigger an End-of-Day process
#     api_broadcast_message  # Send a message to all users
# )

AuthService.require_login(role="admin")

display_app_header(page_name="admin")

st.title("⚙️ Admin Control Panel")
st.caption(f"Welcome, Admin {WebCookieController.get('account')}!")
st.divider()


# Load initial data
# system_stats = load_system_stats()
# users_data = load_users_data()
# Initial load of orders without filter or with a default
# if 'admin_order_filter' not in st.session_state:
#     st.session_state.admin_order_filter = "ALL"
# orders_data = load_all_orders_data(st.session_state.admin_order_filter)

st.session_state.users_data = AdminService.get_all_users()


# --- Main Admin Panel Tabs ---
tab_users, tab_orders_mgt, tab_system = st.tabs([
    "👥 User Management", "⚙️ Order Management", "🛠️ System Health",
])


# ==========================
#   USER MANAGEMENT TAB
# ==========================
with tab_users:
    st.header("User Management")
    if st.button("Refresh User List", key="refresh_users"):
        st.session_state.users_data = AdminService.get_all_users()
        st.rerun()

    users_data = st.session_state.users_data
    if users_data:
        df_users = pd.DataFrame(users_data)
        df_users.rename(columns={
            "__created_at__": "created at",
            "__updated_at__": "updated at"
        }, inplace=True)



        st.subheader("All Users")
        display_cols_users = ['id', 'account', 'role', 'created at', 'updated at']
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


# ==========================
# ORDER MANAGEMENT TAB
# ==========================
with tab_orders_mgt:
    st.header("Order Management")

    # Order Filters
    order_status_options = ["ALL", "PENDING", "COMPLETE", "FAILED", "CANCELLED"] # Add more from your OrderStatus Enum
    st.session_state.admin_order_filter = st.session_state.get("admin_order_filter", "ALL")
    selected_status_filter = st.selectbox(
        "Filter by Status:",
        options=order_status_options,
        index=order_status_options.index(st.session_state.admin_order_filter),
        key="admin_order_filter_select"
    )
    if selected_status_filter != st.session_state.admin_order_filter:
        st.session_state.admin_order_filter = selected_status_filter
        # load_all_orders_data.clear() # Clear cache to fetch with new filter
        st.rerun() # Rerun to apply filter

    if st.button("Refresh Order List", key="refresh_orders_admin"):
        # load_all_orders_data.clear()
        st.rerun()

    # if orders_data:
    #     df_orders = pd.DataFrame(orders_data)
    #     st.subheader(f"All Orders (Status: {st.session_state.admin_order_filter})")
    #     if not df_orders.empty:
    #         cols_orders = ['order_id', 'account_id', 'username', 'side', 'symbol', 'order_type', 'quantity', 'limit_price', 'status', 'created_at', 'error_message']
    #         display_cols_orders = {k: k.replace('_', ' ').title() for k in cols_orders}
    #         existing_order_cols = [col for col in cols_orders if col in df_orders.columns]
    #         df_display_orders = df_orders[existing_order_cols].rename(columns=display_cols_orders)
    #         # Formatting (similar to client's order list)
    #         st.dataframe(df_display_orders, use_container_width=True, hide_index=True, height=400)
    #
    #         st.subheader("Order Actions")
    #         order_id_to_cancel = st.text_input("Enter PENDING Order ID to Cancel:")
    #         if st.button("Cancel Selected Order", key="admin_cancel_order_btn"):
    #             if order_id_to_cancel:
    #                 response = api_cancel_order_admin(order_id_to_cancel) # API call
    #                 if response and response.get("success"):
    #                     st.success(f"Order {order_id_to_cancel} cancelled successfully.")
    #                     load_all_orders_data.clear() # Refresh order list
    #                     st.rerun()
    #                 else:
    #                     st.error(f"Failed to cancel order {order_id_to_cancel}: {response.get('detail', 'Unknown error')}")
    #             else:
    #                 st.warning("Please enter an Order ID.")
    #     else:
    #         st.info(f"No orders found with status '{st.session_state.admin_order_filter}'.")
    # else:
    #     st.warning("Could not load order data.")


# ==========================
#   SYSTEM HEALTH TAB
# ==========================
with tab_system:
    st.header("System Health & Monitoring")

    col_sys1, col_sys2 = st.columns(2)

    with col_sys1:
        st.subheader("Redis Information")
        if st.button("Refresh Redis Info", key="refresh_redis_info_btn"):
            # load_redis_info_data.clear()
            st.rerun()
        # redis_info = load_redis_info_data()
        # if redis_info:
        #     # Display key Redis stats (example, adapt to what your API returns)
        #     st.json(redis_info, expanded=False) # Show full JSON if needed, or parse
        #     st.metric("Redis Uptime (seconds)", redis_info.get("uptime_in_seconds", "N/A"))
        #     st.metric("Connected Clients", redis_info.get("connected_clients", "N/A"))
        #     st.metric("Memory Used", redis_info.get("used_memory_human", "N/A"))
        # else:
        #     st.warning("Could not retrieve Redis information.")

    with col_sys2:
        st.subheader("Recent System Logs")
        log_lines_to_show = st.number_input("Number of log lines:", min_value=10, max_value=500, value=100, step=10)
        if st.button("Refresh System Logs", key="refresh_logs_btn"):
            # load_system_logs_data.clear() # Clear cache for logs
            st.rerun() # Rerun to fetch with new line count if changed

        # system_logs = load_system_logs_data(lines=log_lines_to_show)
        # if system_logs and "logs" in system_logs:
        #     # Display logs in a text area or styled block
        #     log_text = "\n".join(system_logs["logs"])
        #     st.text_area("Logs:", value=log_text, height=300, disabled=True)
        # else:
        #     st.warning("Could not retrieve system logs.")

    # Placeholder for other system metrics: DB connections, API latency, etc.



# --- Periodic Rerun for Admin Panel (Optional, less critical than trading UI) ---
# If you want parts of the admin panel to auto-refresh, use a similar time-based rerun.
# For admin panels, manual refresh buttons are often sufficient.
# time.sleep(ADMIN_REFRESH_INTERVAL) # Define ADMIN_REFRESH_INTERVAL if needed
# st.rerun()