import streamlit as st


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