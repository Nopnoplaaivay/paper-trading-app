import streamlit as st
import plotly.graph_objects as go


def display_chart():
    st.subheader(f"Biểu đồ {st.session_state.stock_data['symbol']}")
    df = st.session_state.chart_data
    last_close = df['close'].iloc[-1]

    fig = go.Figure(data=[go.Candlestick(
        x=df['time'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        increasing=dict(line=dict(color='#449782')),  # Xanh cho nến tăng
        decreasing=dict(line=dict(color='#df484b'))  # Đỏ cho nến giảm
    )])
    fig.add_shape(
        type="line",
        x0=df['time'].min(),
        y0=last_close,
        x1=df['time'].max(),
        y1=last_close,
        line=dict(
            color="red",
            width=1,
            dash="dash"
        )
    )
    fig.update_layout(
        paper_bgcolor='#141721',
        plot_bgcolor='#141721',
        height=350,
        xaxis_rangeslider_visible=False,
        margin=dict(l=10, r=10, t=10, b=10),
        yaxis_tickformat=','
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#141721')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#141721')
    st.plotly_chart(fig, use_container_width=True)