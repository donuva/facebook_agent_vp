import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from db_actions import load_all  # Hàm load_all() để lấy dữ liệu từ DB

# Cấu hình trang hiển thị
st.set_page_config(page_title="Chatbot Facebook Dashboard", layout="wide")


# ====== LOAD DỮ LIỆU THẬT ======
# Load dữ liệu từ DB
df = load_all()  # Giả sử bạn có hàm load_all() trong db_actions.py để lấy dữ liệu từ DB

st.dataframe(df)
# # Tạo cột ngày để nhóm thống kê theo ngày
# df['date'] = pd.to_datetime(df['timestamp']).dt.date  # Thêm cột ngày để nhóm theo ngày

# ====== TÍNH TOÁN CHỈ SỐ TỔNG HỢP ======
total_msgs = len(df)  # Tổng số tin nhắn
bot_replies = df['is_bot_reply'].sum()  # Số tin nhắn do bot phản hồi
success_rate = bot_replies / total_msgs  # Tỷ lệ bot phản hồi
avg_response = df['response_time'].mean()  # Thời gian phản hồi trung bình
intent_counts = df['intent'].value_counts()  # Số lượng intent
cta_clicks = df['clicked_cta'].sum()  # Số lượt nhấp CTA
cta_rate = cta_clicks / total_msgs  # Tỷ lệ chuyển đổi CTA
avg_rating = df['rating'].dropna().mean()  # Điểm hài lòng trung bình
total_rated = df['rating'].count()  # Số lượt đánh giá
rating_dist = df['rating'].value_counts().sort_index()  # Phân phối điểm
msg_by_day = df.groupby('date').size()  # Số lượng tin nhắn theo ngày

# ====== DASHBOARD ======
st.title("🤖 Chatbot Facebook Analytics Dashboard")
st.markdown("### Phân tích hiệu quả chatbot Facebook tự động")

# 4 chỉ số chính
col1, col2, col3, col4 = st.columns(4)
col1.metric("Tổng tin nhắn", total_msgs)
col2.metric("Tỷ lệ trả lời tự động", f"{success_rate:.2%}")
col3.metric("Thời gian phản hồi TB", f"{avg_response:.2f} giây")
col4.metric("Điểm hài lòng TB", f"{avg_rating:.2f}/5 ⭐")

# Hiển thị bảng dữ liệu đầy đủ
with st.expander("🔍 Xem bảng dữ liệu gốc"):
    st.dataframe(df)

st.markdown("---")

# Tabs chia nội dung thành 3 phần chính
tab1, tab2, tab3 = st.tabs(["Biểu đồ tổng quan", "Phân tích chi tiết", "Tương tác theo thời gian"])

# ====== TAB 1: Biểu đồ tổng quan ======
with tab1:
    c1, c2 = st.columns([1, 1])
    with c1:
        # Biểu đồ cột: intent phổ biến
        intent_df = intent_counts.reset_index()
        intent_df.columns = ['intent', 'count']
        fig1 = px.bar(intent_df, x='intent', y='count',
                      labels={'intent': 'Intent', 'count': 'Số lượt'},
                      color='count',
                      title="Intent phổ biến nhất")
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        # Biểu đồ donut: tỷ lệ nhấp CTA
        cta_data = pd.DataFrame({
            'Loại': ['Nhấp CTA', 'Không nhấp'],
            'Số lượng': [cta_clicks, total_msgs - cta_clicks]
        })
        fig2 = px.pie(cta_data, values='Số lượng', names='Loại', hole=0.5,
                      color_discrete_sequence=px.colors.sequential.RdBu,
                      title="Tỷ lệ chuyển đổi CTA")
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns([1, 1])
    with c3:
        # Gauge: đánh giá trung bình
        fig3 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=avg_rating,
            gauge={
                'axis': {'range': [0, 5]},
                'bar': {'color': "#21B573"},
                'steps': [
                    {'range': [0, 2], 'color': "#FFC4C4"},
                    {'range': [2, 4], 'color': "#FFD59E"},
                    {'range': [4, 5], 'color': "#C8E6C9"}
                ],
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

# ====== TAB 2: Phân tích chi tiết ======
with tab2:
    st.markdown("#### Số lượng tin nhắn theo intent")
    st.dataframe(intent_counts.rename_axis("Intent").reset_index(name="Số lượng"))
    
    st.markdown("#### Thống kê chuyển đổi CTA & đánh giá")
    st.metric("Số lượt nhấp CTA", cta_clicks)
    st.metric("Tổng lượt đánh giá", total_rated)

# ====== TAB 3: Tương tác theo thời gian ======
with tab3:
    st.markdown("#### Lượt tin nhắn mỗi ngày")
    fig5 = px.line(x=msg_by_day.index, y=msg_by_day.values,
                   labels={'x': 'Ngày', 'y': 'Số tin nhắn'},
                   title="Tương tác người dùng theo ngày")
    st.plotly_chart(fig5, use_container_width=True)

    # Nếu cần, có thể thêm bộ lọc ngày tại đây

# ====== CHÂN TRANG ======
st.markdown("""
---
*TEAM 202_CHALLENGE 12: FACEBOOK_AGENT*
""")
