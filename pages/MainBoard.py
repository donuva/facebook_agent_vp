import streamlit as st
import pandas as pd
from db_actions import load_all, update_admin_fields

st.set_page_config(page_title="Facebook Agent Mainboard", layout="wide")
st.title("👩‍💼 Facebook Agent Mainboard")

# ======= Định nghĩa intent và admin =======
intent_list = ["Account Types",
                "Card Types",
                "Online Services (Business)"]
admin_users = ["Admin A", "Admin B"] 

# ======= LOAD DỮ LIỆU THẬT TỪ DB =======
df = load_all()

# Đảm bảo đủ cột (nếu thiếu thì tạo cột trống)
columns_needed = [
    "date", "campaign", "user", "question", "answer", "confidence", "fb_comment_id",
    "url", "admin_reply", "edit_log", "admin_note", "feedback", "rating", "handled",
    "intent", "last_editor", "last_edit_time", "search"
]
for col in columns_needed:
    if col not in df.columns:
        df[col] = ""

# ========== GIAO DIỆN BỘ LỌC ==========
with st.sidebar:
    st.header("Bộ lọc")
    filter_date = st.date_input("Lọc theo ngày", value=None)
    try:
        filter_conf = st.slider("Mức tự tin LLM", 0.4, 1.0, (0.4, 1.0), 0.01)
    except:
        filter_conf = (0.4, 1.0)
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
    # Chuyển đổi trường "date" thành ngày và so sánh với filter_date
    df_view['date'] = pd.to_datetime(df_view['date']).dt.date  # Chỉ lấy phần ngày
    df_view = df_view[df_view["date"] == filter_date]
df_view = df_view[(df_view["confidence"].astype(str).astype(float) >= filter_conf[0]) & (df_view["confidence"].astype(str).astype(float) <= filter_conf[1])]
if filter_campaign:
    df_view = df_view[df_view["campaign"].isin(filter_campaign)]
if filter_user:
    df_view = df_view[df_view["user"].isin(filter_user)]
if filter_handled != "Tất cả":
    handled_val = (filter_handled == "Đã xử lý")
    df_view = df_view[df_view["handled"].astype(str).apply(lambda x: x in ["1", "True", "true"]) == handled_val]
if search_key:
    df_view = df_view[df_view["search"].str.lower().str.contains(search_key.lower())]
if quick_intent:
    df_view = df_view[df_view["intent"] == quick_intent]


# ========== CẢNH BÁO CÂU KHÓ ==========
try:
    n_new_hard = len(df[(df["confidence"].astype(float) < 0.75) & (~df["handled"].astype(str).isin(["1", "True", "true"]))])
except:
    n_new_hard = 0
if n_new_hard > 0:
    st.warning(f"⚡ Có {n_new_hard} câu hỏi khó mới chưa được xử lý!")

# ========== BÁO CÁO TỔNG QUÁT ==========
col1, col2, col3 = st.columns(3)
try:
    n_confident = len(df[df["confidence"].astype(float) >= 0.75])
    n_hard = len(df[df["confidence"].astype(float) < 0.75])
    avg_resp = round(df["confidence"].astype(float).mean() * 10, 2)
except:
    n_confident = 0
    n_hard = 0
    avg_resp = 0
col1.metric("Câu tự tin LLM", n_confident)
col2.metric("Câu cần xử lý", n_hard)
col3.metric("Mức tự tin TB (%)", avg_resp * 10)

# ========== HIỂN THỊ MAINBOARD ========== 
left, right = st.columns(2)

def save_admin_edit(row, note, feedback, admin_reply, handled, rating, intent, editor):
    from datetime import datetime
    update_admin_fields(
        fb_comment_id=row['fb_comment_id'],
        admin_note=note,
        feedback=feedback,
        admin_reply=admin_reply,
        handled=handled,
        rating=rating,
        last_editor=editor,
    )
    st.success("Đã lưu chỉnh sửa!")

# Cột trái: Câu LLM tự tin
with left:
    st.subheader("✅ Câu trả lời tự tin ")
    conf_df = df_view[df_view['confidence'].astype(float) >= 0.75]
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
                int(row["rating"]) if pd.notna(row["rating"]) and str(row["rating"]).isdigit() else 3,
                step=1,
                key=f"score{row['fb_comment_id']}"
            )
            feedback = st.text_area("Góp ý cho chatbot", value=row["feedback"], key=f"fb{row['fb_comment_id']}")
            note = st.text_area("Ghi chú nội bộ", value=row["admin_note"], key=f"note{row['fb_comment_id']}")
            admin_reply = st.text_area("Phản hồi admin", value=row["admin_reply"], key=f"admrep{row['fb_comment_id']}")
            intent_val = st.selectbox("Gắn intent", intent_list, index=intent_list.index(row["intent"]) if row["intent"] in intent_list else 0, key=f"intent{row['fb_comment_id']}")
            handled = st.checkbox("Đã xử lý", value=(str(row["handled"]).lower() in ["1", "true"]), key=f"handled{row['fb_comment_id']}")
            editor = st.selectbox("Người chỉnh", admin_users, key=f"editor{row['fb_comment_id']}")
            if st.button("Lưu chỉnh sửa", key=f"save{row['fb_comment_id']}"):
                save_admin_edit(row, note, feedback, admin_reply, handled, llm_score, intent_val, editor)
                st.rerun()

# # Cột phải: Câu hỏi khó
# with right:
#     st.subheader("🤔 Câu hỏi khó")
#     hard_df = df_view[df_view['confidence'].astype(float) < 0.75]
#     for i, row in hard_df.iterrows():
#         with st.expander(f"{row['user']}: {row['question']} [{row['confidence']}]"):
#             st.write(f"**Gợi ý trả lời:** {row['answer']}")
#             st.write(f"**Chiến dịch:** {row['campaign']}")
#             st.write(f"**Intent:** {row['intent']}")
#             st.write(f"[➡️ Xem bình luận Facebook]({row['url']})")
#             note = st.text_area("Ghi chú nội bộ", value=row["admin_note"], key=f"note2{row['fb_comment_id']}")
#             feedback = st.text_area("Góp ý cho chatbot", value=row["feedback"], key=f"fb2{row['fb_comment_id']}")
#             admin_reply = st.text_area("Phản hồi admin", value=row["admin_reply"], key=f"admrep2{row['fb_comment_id']}")
#             llm_score = st.slider(
#                 f"Chấm điểm LLM (1-5)",
#                 1, 5,
#                 int(row["rating"]) if pd.notna(row["rating"]) and str(row["rating"]).isdigit() else 3,
#                 step=1,
#                 key=f"score2{row['fb_comment_id']}"
#             )
#             intent_val = st.selectbox("Gắn intent", intent_list, index=intent_list.index(row["intent"]) if row["intent"] in intent_list else 0, key=f"intent2{row['fb_comment_id']}")
#             handled = st.checkbox("Đã xử lý", value=(str(row["handled"]).lower() in ["1", "true"]), key=f"handled2{row['fb_comment_id']}")
#             editor = st.selectbox("Người chỉnh", admin_users, key=f"editor2{row['fb_comment_id']}")
#             if st.button("Lưu chỉnh sửa", key=f"save2{row['fb_comment_id']}"):
#                 save_admin_edit(row, note, feedback, admin_reply, handled, llm_score, intent_val, editor)
#                 st.rerun()

with right:
    st.subheader("🤔 Câu hỏi khó (LLM không tự tin)")
    hard_df = df[(df["confidence"].astype(float) < 0.75)]  # Lọc từ df gốc, không phải df_view, vì có thể bị loại trong filter khác
    # Kiểm tra dữ liệu đã tồn tại chưa
    if hard_df.empty:
        st.info("Không có câu hỏi khó trong dữ liệu được lọc.")
    for i, row in hard_df.iterrows():
        with st.expander(f"{row['user']}: {row['question']} [{row['confidence']}]"):
            st.write(f"**Gợi ý trả lời:** {row['answer']}")
            st.write(f"**Chiến dịch:** {row['campaign']}")
            st.write(f"**Intent:** {row['intent']}")
            st.write(f"[➡️ Xem bình luận Facebook]({row['url']})")
            note = st.text_area("Ghi chú nội bộ", value=row["admin_note"], key=f"note2{row['fb_comment_id']}")
            feedback = st.text_area("Góp ý cho chatbot", value=row["feedback"], key=f"fb2{row['fb_comment_id']}")
            admin_reply = st.text_area("Phản hồi admin", value=row["admin_reply"], key=f"admrep2{row['fb_comment_id']}")
            llm_score = st.slider(
                f"Chấm điểm LLM (1-5)",
                1, 5,
                int(row["rating"]) if pd.notna(row["rating"]) and str(row["rating"]).isdigit() else 3,
                step=1,
                key=f"score2{row['fb_comment_id']}"
            )
            intent_val = st.selectbox("Gắn intent", intent_list, index=intent_list.index(row["intent"]) if row["intent"] in intent_list else 0, key=f"intent2{row['fb_comment_id']}")
            handled = st.checkbox("Đã xử lý", value=(str(row["handled"]).lower() in ["1", "true"]), key=f"handled2{row['fb_comment_id']}")
            editor = st.selectbox("Người chỉnh", admin_users, key=f"editor2{row['fb_comment_id']}")
            if st.button("Lưu chỉnh sửa", key=f"save2{row['fb_comment_id']}"):
                save_admin_edit(row, note, feedback, admin_reply, handled, llm_score, intent_val, editor)
                st.rerun()

# ========== BẢNG NHẬT KÝ ==========
st.markdown("---")
st.subheader("📋 Nhật ký hoạt động")
log_data = df[["fb_comment_id", "user", "question", "last_editor", "last_edit_time", "edit_log"]] if all(col in df.columns for col in ["fb_comment_id", "user", "question", "last_editor", "last_edit_time", "edit_log"]) else pd.DataFrame()
if not log_data.empty:
    st.dataframe(log_data, hide_index=True)

# ========== LỊCH SỬ CHỈNH SỬA ==========
st.subheader("🕑 Lịch sử chỉnh sửa admin")
if "edit_log" in df.columns:
    edit_logs = df[df["edit_log"] != ""][["fb_comment_id", "edit_log"]]
    st.dataframe(edit_logs, hide_index=True)
