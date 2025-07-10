import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Chatbot Facebook Dashboard", layout="wide")

# ====== Giả lập dữ liệu chatbot ======
np.random.seed(42)
n = 500
start_date = datetime(2024, 1, 1)

chat_df = pd.DataFrame({
    'timestamp': [start_date + timedelta(minutes=30*i) for i in range(n)],
    'user_id': np.random.randint(1, 100, n),
    'message': np.random.choice(['Hi', 'Order', 'Thanks', 'Help', 'CTA Clicked', 'Bye'], n),
    'is_bot_reply': np.random.choice([True, False], n, p=[0.9, 0.1]),
    'response_time': np.random.normal(2, 0.5, n).clip(min=0.5),
    'intent': np.random.choice(['greeting', 'order', 'thankyou', 'support', 'cta', 'goodbye'], n),
    'clicked_cta': np.random.choice([True, False], n, p=[0.2, 0.8]),
    'rating': np.random.choice([1, 2, 3, 4, 5, None], n, p=[0.1, 0.1, 0.2, 0.3, 0.2, 0.1])
})
chat_df['date'] = chat_df['timestamp'].dt.date

# ====== Tính toán các chỉ số ======
total_msgs = len(chat_df)
bot_replies = chat_df['is_bot_reply'].sum()
success_rate = bot_replies / total_msgs
avg_response = chat_df['response_time'].dropna().mean()
intent_counts = chat_df['intent'].value_counts()
cta_clicks = chat_df['clicked_cta'].sum()
cta_rate = cta_clicks / total_msgs
avg_rating = chat_df['rating'].dropna().mean()
total_rated = chat_df['rating'].count()
rating_dist = chat_df['rating'].value_counts().sort_index()
msg_by_day = chat_df.groupby('date').size()

# ====== Giao diện Dashboard ======
st.title("🤖 Chatbot Facebook Analytics Dashboard")
st.markdown("### Phân tích hiệu quả chatbot Facebook tự động (dữ liệu demo)")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Tổng tin nhắn", total_msgs)
col2.metric("Tỷ lệ trả lời tự động", f"{success_rate:.2%}")
col3.metric("Thời gian phản hồi TB", f"{avg_response:.2f} giây")
col4.metric("Điểm hài lòng TB", f"{avg_rating:.2f}/5 ⭐")

with st.expander("🔍 Xem bảng dữ liệu gốc"):
    st.dataframe(chat_df)

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["Biểu đồ tổng quan", "Phân tích chi tiết", "Tương tác theo thời gian"])

with tab1:
    c1, c2 = st.columns([1,1])
    with c1:
        # Biểu đồ intent
        intent_df = intent_counts.reset_index()
        intent_df.columns = ['intent', 'count']  # Đảm bảo đúng tên cột
        fig1 = px.bar(intent_df, x='intent', y='count',
                    labels={'intent': 'Intent', 'count': 'Số lượt'},
                    color='count',
                    title="Intent phổ biến nhất")
        st.plotly_chart(fig1, use_container_width=True)
    with c2:
        # Donut CTA
        cta_data = pd.DataFrame({
            'Loại': ['Nhấp CTA', 'Không nhấp'],
            'Số lượng': [cta_clicks, total_msgs - cta_clicks]
        })
        fig2 = px.pie(cta_data, values='Số lượng', names='Loại', hole=0.5,
                      color_discrete_sequence=px.colors.sequential.RdBu,
                      title="Tỷ lệ chuyển đổi CTA")
        st.plotly_chart(fig2, use_container_width=True)
    c3, c4 = st.columns([1,1])
    with c3:
        # Gauge Rating
        fig3 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=avg_rating,
            gauge={'axis': {'range': [0, 5]},
                   'bar': {'color': "#21B573"},
                   'steps': [
                        {'range': [0, 2], 'color': "#FFC4C4"},
                        {'range': [2, 4], 'color': "#FFD59E"},
                        {'range': [4, 5], 'color': "#C8E6C9"}],
                   },
            title={'text': "Điểm hài lòng trung bình"}
        ))
        st.plotly_chart(fig3, use_container_width=True)
    with c4:
        # Biểu đồ phân phối rating
        fig4 = px.bar(x=rating_dist.index, y=rating_dist.values,
                      labels={'x': 'Rating', 'y': 'Số lượng'},
                      color=rating_dist.values,
                      color_continuous_scale="Viridis",
                      title="Phân phối điểm hài lòng")
        st.plotly_chart(fig4, use_container_width=True)

with tab2:
    st.markdown("#### Số lượng tin nhắn theo intent")
    st.dataframe(intent_counts.rename_axis("Intent").reset_index(name="Số lượng"))
    st.markdown("#### Thống kê chuyển đổi CTA & đánh giá")
    st.metric("Số lượt nhấp CTA", cta_clicks)
    st.metric("Tổng lượt đánh giá", total_rated)

with tab3:
    st.markdown("#### Lượt tin nhắn mỗi ngày")
    fig5 = px.line(x=msg_by_day.index, y=msg_by_day.values,
                   labels={'x': 'Ngày', 'y': 'Số tin nhắn'},
                   title="Tương tác người dùng theo ngày")
    st.plotly_chart(fig5, use_container_width=True)

    # Có thể thêm filter ngày tại đây nếu muốn nâng cao

st.markdown("""
---
*TEAM 202*
""")
