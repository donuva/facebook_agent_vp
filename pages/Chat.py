import os
import sqlite3
import streamlit as st
import uuid

from langchain.memory import ConversationBufferMemory
from logicRAG.stream_output import get_llama_response, intergrate_context
from logicRAG.vectorDB.query import query
from logicRAG.vectorDB.indexing import load_index
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
# -------------------- Cấu hình hệ thống --------------------
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
st.set_page_config(page_title="Chatbot", page_icon="graphics/icon1.png")
st.logo('graphics/app_logo.png')

# -------------------- Kiểm tra trạng thái đăng nhập --------------------
if not st.session_state.get("is_login", False):
    st.warning("CHƯA ĐĂNG NHẬP")
    st.switch_page("Home.py")

# -------------------- Kết nối cơ sở dữ liệu --------------------
conn = sqlite3.connect("vpbank.sqlite")
cur = conn.cursor()

# -------------------- Tải danh sách từ ngữ cấm --------------------
def load_profanity_words(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        words = f.read().splitlines()
        cleaned_words = []
        for word in words:
            word = word.strip().strip('"')
            if word:
                cleaned_words.append(word)
        return cleaned_words

profanity_list = load_profanity_words("./data/vn_offensive_words.txt")

# -------------------- Lựa chọn nguồn dữ liệu để tìm kiếm --------------------
db_options = st.multiselect(
    "Tìm kiếm trong cơ sở dữ liệu:",
    ["Mail Database", "Default Database", "Drive Database"]
)

# -------------------- Tải các chỉ mục đã chọn --------------------
db_indexes = {}
if "Mail Database" in db_options:
    db_indexes["Mail"] = load_index("data/.cache/faiss_Mail_index.bin")
if "Default Database" in db_options:
    db_indexes["Default"] = load_index("data/.cache/faiss_Default_index.bin")
if "Drive Database" in db_options:
    db_indexes["Drive"] = load_index("data/.cache/faiss_Drive_index.bin")

# -------------------- Khởi tạo bộ nhớ hội thoại --------------------
if "memory" not in st.session_state or st.session_state.memory is None:
    st.session_state.memory = ConversationBufferMemory(
        return_messages=True,
        memory_key="chat_history"
    )

# -------------------- Hiển thị lịch sử hội thoại đã lưu --------------------
def load_chat_history(user_id):
    cur.execute('SELECT role, message FROM history WHERE user_id=?', (user_id,))
    conn.commit()
    return cur.fetchall()

chat_history = load_chat_history(st.session_state.id)
for role, message in chat_history:
    if role in ["user", "assistant"]:
        with st.chat_message(role):
            st.markdown(message)

# -------------------- Nhận đầu vào từ người dùng --------------------
user_input = st.chat_input("Nhập tin nhắn để trò chuyện với chatbot")

# -------------------- Lọc từ ngữ không phù hợp --------------------
def filter_profanity(text, profanity_list):
    for word in profanity_list:
        if word in text:
            text = text.replace(word, "***")
    return text

# -------------------- Xử lý truy vấn và tạo phản hồi --------------------
from logicRAG.semantic_search import SparseBM25Search
def process_database_response(user_input, index, all_chunks):
    search_results = query(query_text=user_input, index=index, chunks=all_chunks, distance_threshold=5)
    bm25_search = SparseBM25Search(all_chunks)
    bm25_results = bm25_search.search(user_input, top_k=5)
    
    # Vector context
    docs, summary = "", ""
    for i, doc in enumerate(search_results):
        docs += doc + " "
        if len(docs) > 2000:
            summary = intergrate_context([docs, summary])
            docs = ""
    if docs:
        summary = intergrate_context([docs, summary])
    retrieved_context = {"role": "system", "content": f"Retrieved Document (Vector): {summary}"}

    # BM25 context
    bm25_docs = " ".join(bm25_results)
    bm25_summary = intergrate_context([bm25_docs]) if bm25_docs else ""
    bm25_context = {"role": "system", "content": f"Retrieved Document (BM25): {bm25_summary}"}

    print(f"retrieved_context is {retrieved_context}")
    print(f"bm25_context is {bm25_context}")

    # Gộp context lại
    merged_context = {"role": "system", "content": f"{retrieved_context['content']}\n{bm25_context['content']}"}

    response_gen = get_llama_response(
        st.session_state.memory.load_memory_variables({}),
        merged_context,
        user_input
    )
    response = "".join([chunk for chunk in response_gen])
    return response

# -------------------- Luồng xử lý chính khi có câu hỏi --------------------
if user_input:
    user_input = filter_profanity(user_input, profanity_list)
    
    with st.chat_message("user"):
        st.markdown(user_input)
        
    # Ghi tin nhắn người dùng vào cơ sở dữ liệu
    cur.execute("INSERT INTO history (user_id, role, message) VALUES (?, ?, ?)",
                (st.session_state.id[0], "user", user_input))
    conn.commit()
    
    # Ghi vào bộ nhớ hội thoại
    st.session_state.memory.chat_memory.add_message({"role": "user", "content": user_input})
    
    # Đọc dữ liệu chunk đã lưu sẵn
    with open('data/.cache/chunks.txt', 'r', encoding='utf-8') as f:
        all_chunks = [chunk for chunk in f.read().split('\n|||') if chunk.strip()]
    
    # Truy vấn từng database đã chọn và tạo phản hồi ban đầu
    partial_answers = []
    for label, index in db_indexes.items():
        partial = process_database_response(user_input, index, all_chunks)
        partial_answers.append(partial)
    
    # Tổng hợp phản hồi từ các database
    final_answer = intergrate_context(partial_answers)
    final_answer = filter_profanity(final_answer, profanity_list)

    with st.chat_message("ai"):
        st.markdown(final_answer)

    # Ghi phản hồi của bot vào bộ nhớ và lịch sử
    st.session_state.memory.chat_memory.add_message({"role": "assistant", "content": final_answer})
    cur.execute("INSERT INTO history (user_id, role, message) VALUES (?, ?, ?)",
                (st.session_state.id[0], "assistant", final_answer))
    conn.commit()

# -------------------- Chân trang --------------------
with st.chat_message(avatar="graphics/app_logo.png", name="system"):
    st.markdown("© 2024 EDA - VPBank. All rights reserved.")
