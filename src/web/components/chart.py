import streamlit as st
import plotly.graph_objects as go


def display_chart():
    st.subheader(f"Biểu đồ {st.session_state.stock_data['symbol']}")
    # Chuẩn bị dữ liệu cho Plotly
    # df = pd.DataFrame(st.session_state.chart_data)
    df = st.session_state.chart_data
    # Chuyển timestamp sang datetime để Plotly hiển thị trục thời gian đẹp hơn

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