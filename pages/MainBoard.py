import streamlit as st
import pandas as pd
import datetime
import random

# Cấu hình giao diện trang Streamlit
st.set_page_config(page_title="Facebook Agent Mainboard", layout="wide")
st.title("👩‍💼 Facebook Agent Mainboard")

# ======= DỮ LIỆU GIẢ LẬP =======
# Thiết lập seed để đảm bảo kết quả ngẫu nhiên có thể tái hiện
random.seed(42)

# Danh sách admin giả lập
admin_users = ["Admin A", "Admin B", "Admin C"]

# Danh sách intent giả định
intent_list = ["Giá", "Giao hàng", "Bảo hành", "Màu sắc", "Sử dụng", "Khác"]

# Tạo danh sách dữ liệu mô phỏng
data = []
for i in range(50):  # Tạo 50 dòng dữ liệu giả lập
    # === Các trường dữ liệu được random hóa ===
    date = datetime.date(2024, 7, random.randint(1, 10))  # Giả lập ngày từ 1-10/7/2024
    campaign = random.choice(["Summer2024", "Back2School", "Test"])  # Tên chiến dịch giả
    user = random.choice(["Nguyễn A", "Lê B", "Trần C", "Hoàng D", "Linh E"])  # Tên người dùng giả
    question = f"Câu hỏi số {i+1} của {user} ({random.choice(intent_list)})"  # Nội dung câu hỏi giả
    answer = f"Câu trả lời tự động {i+1}" if random.random() > 0.25 else "Xin chờ admin hỗ trợ."  # Tự động trả lời hoặc cần hỗ trợ
    confidence = round(random.uniform(0.4, 0.99), 2)  # Mức độ tự tin LLM (0.4 - 0.99)
    fb_comment_id = str(1000 + i)  # ID comment giả định
    url = f"https://facebook.com/comment/{fb_comment_id}"  # Link giả cho comment
    admin_reply = "" if random.random() > 0.5 else f"Đã phản hồi: {random.choice(admin_users)}"
    edit_log = "" if random.random() > 0.5 else f"Chỉnh sửa bởi {random.choice(admin_users)} lúc {date}."
    admin_note = "" if random.random() > 0.7 else f"Ghi chú nội bộ {i}"
    feedback = "" if random.random() > 0.7 else f"LLM yếu phần này"
    rating = random.choice([1, 2, 3, 4, 5, None, None])  # Chấm điểm LLM hoặc để trống
    handled = random.choice([True, False])  # Trạng thái đã xử lý hay chưa
    intent = random.choice(intent_list)
    
    # Thêm dòng dữ liệu vào danh sách
    data.append({
        "date": date,
        "campaign": campaign,
        "user": user,
        "question": question,
        "answer": answer,
        "confidence": confidence,
        "fb_comment_id": fb_comment_id,
        "url": url,
        "admin_reply": admin_reply,
        "edit_log": edit_log,
        "admin_note": admin_note,
        "feedback": feedback,
        "rating": rating,
        "handled": handled,
        "intent": intent,
        "last_editor": random.choice(admin_users) if edit_log else "",
        "last_edit_time": date if edit_log else "",
        "search": f"{user} {question} {answer}",  # Trường để hỗ trợ tìm kiếm nhanh
    })

# Tạo DataFrame từ dữ liệu giả
df = pd.DataFrame(data)

# ========== GIAO DIỆN BỘ LỌC ========== 
with st.sidebar:
    st.header("Bộ lọc")
    filter_date = st.date_input("Lọc theo ngày", value=None)
    filter_conf = st.slider("Mức tự tin LLM", 0.4, 1.0, (0.4, 1.0), 0.01)
    filter_campaign = st.multiselect("Chiến dịch", options=list(df["campaign"].unique()), default=[])
    filter_user = st.multiselect("User", options=list(df["user"].unique()), default=[])
    filter_handled = st.radio("Trạng thái xử lý", ["Tất cả", "Đã xử lý", "Chưa xử lý"])
    search_key = st.text_input("Tìm kiếm", "")
    st.markdown("---")
    st.write("**Gắn intent/tag nhanh**")
    quick_intent = st.selectbox("Chọn intent phổ biến", [""] + intent_list)

# ========== ÁP DỤNG BỘ LỌC ========== 
df_view = df.copy()
if filter_date:
    df_view = df_view[df_view["date"] == filter_date]
df_view = df_view[(df_view["confidence"] >= filter_conf[0]) & (df_view["confidence"] <= filter_conf[1])]
if filter_campaign:
    df_view = df_view[df_view["campaign"].isin(filter_campaign)]
if filter_user:
    df_view = df_view[df_view["user"].isin(filter_user)]
if filter_handled != "Tất cả":
    df_view = df_view[df_view["handled"] == (filter_handled == "Đã xử lý")]
if search_key:
    df_view = df_view[df_view["search"].str.lower().str.contains(search_key.lower())]
if quick_intent:
    df_view = df_view[df_view["intent"] == quick_intent]

# ========== CẢNH BÁO CÂU KHÓ ========== 
n_new_hard = len(df[(df["confidence"] < 0.7) & (~df["handled"])])
if n_new_hard > 0:
    st.warning(f"⚡ Có {n_new_hard} câu hỏi khó mới chưa được xử lý!")

# ========== BÁO CÁO TỔNG QUÁT ========== 
col1, col2, col3 = st.columns(3)
n_confident = len(df[df["confidence"] >= 0.8])
n_hard = len(df[df["confidence"] < 0.8])
avg_resp = round(df["confidence"].mean() * 10, 2)
col1.metric("Câu tự tin LLM", n_confident)
col2.metric("Câu cần xử lý", n_hard)
col3.metric("Mức tự tin TB (%)", avg_resp * 10)

# ========== HIỂN THỊ MAINBOARD ========== 
left, right = st.columns(2)

# Cột trái: Câu LLM tự tin
with left:
    st.subheader("✅ Câu trả lời tự tin (LLM confident)")
    conf_df = df_view[df_view['confidence'] >= 0.8]
    for i, row in conf_df.iterrows():
        with st.expander(f"{row['user']}: {row['question']} [{row['confidence']}]"):
            st.write(f"**Trả lời:** {row['answer']}")
            st.write(f"**Chiến dịch:** {row['campaign']}")
            st.write(f"**Intent:** {row['intent']}")
            st.write(f"[➡️ Xem bình luận Facebook]({row['url']})")
            st.write(f"**Nhật ký:** {row['edit_log']}")
            llm_score = st.slider(
                f"Chấm điểm LLM (1-5)",
                1, 5,
                int(row["rating"]) if pd.notna(row["rating"]) else 3,
                step=1,
                key=f"score{row['fb_comment_id']}"
            )
            feedback = st.text_area("Góp ý cho chatbot", value=row["feedback"], key=f"fb{row['fb_comment_id']}")
            note = st.text_area("Ghi chú nội bộ", value=row["admin_note"], key=f"note{row['fb_comment_id']}")
            st.write(f"**Lần chỉnh gần nhất:** {row['last_editor']} - {row['last_edit_time']}")
            new_intent = st.selectbox("Gắn intent", intent_list, index=intent_list.index(row["intent"]), key=f"intent{row['fb_comment_id']}")

# Cột phải: Câu hỏi khó
with right:
    st.subheader("🤔 Câu hỏi khó (LLM không tự tin)")
    hard_df = df_view[df_view['confidence'] < 0.8]
    for i, row in hard_df.iterrows():
        with st.expander(f"{row['user']}: {row['question']} [{row['confidence']}]"):
            st.write(f"**Gợi ý trả lời:** {row['answer']}")
            st.write(f"**Chiến dịch:** {row['campaign']}")
            st.write(f"**Intent:** {row['intent']}")
            st.write(f"[➡️ Xem bình luận Facebook]({row['url']})")
            new_reply = st.text_area("Phản hồi của admin", value=row["admin_reply"], key=f"admrep{row['fb_comment_id']}")
            mark = st.checkbox("Đã xử lý", value=row["handled"], key=f"mark{row['fb_comment_id']}")
            note = st.text_area("Ghi chú nội bộ", value=row["admin_note"], key=f"note2{row['fb_comment_id']}")
            st.write(f"**Nhật ký:** {row['edit_log']}")
            llm_score = st.slider(
                f"Chấm điểm LLM (1-5)",
                1, 5,
                int(row["rating"]) if pd.notna(row["rating"]) else 3,
                step=1,
                key=f"score{row['fb_comment_id']}"
            )
            feedback = st.text_area("Góp ý cho chatbot", value=row["feedback"], key=f"fb2{row['fb_comment_id']}")
            new_intent = st.selectbox("Gắn intent", intent_list, index=intent_list.index(row["intent"]), key=f"intent2{row['fb_comment_id']}")
            st.write(f"**Lần chỉnh gần nhất:** {row['last_editor']} - {row['last_edit_time']}")

# ========== BẢNG NHẬT KÝ ========== 
st.markdown("---")
st.subheader("📋 Nhật ký hoạt động")
log_data = df[["fb_comment_id", "user", "question", "last_editor", "last_edit_time", "edit_log"]]
st.dataframe(log_data, hide_index=True)

# ========== LỊCH SỬ CHỈNH SỬA ========== 
st.subheader("🕑 Lịch sử chỉnh sửa admin")
edit_logs = df[df["edit_log"] != ""][["fb_comment_id", "edit_log"]]
st.dataframe(edit_logs, hide_index=True)
