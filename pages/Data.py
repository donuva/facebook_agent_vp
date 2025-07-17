import streamlit as st
from logicRAG.fileProcessor import Processor
from logicRAG.vectorDB.indexing import vectordb, save_index, store_embeddings_faiss

# ------------------ Kiểm tra đăng nhập ------------------
if "is_login" not in st.session_state or not st.session_state.is_login:
    st.warning("CHƯA ĐĂNG NHẬP")
    st.switch_page("Home.py")

# ------------------ Cấu hình giao diện Streamlit ------------------
st.set_page_config(
    page_title="Data manipulation",
    page_icon="graphics/icon1.png"
)
st.logo('graphics/app_logo.png')
st.title("Data manipulator")
st.subheader("Tải lên tài liệu của bạn tại đây")

# ------------------ Khởi tạo Vector Database tạm thời ------------------
Mail_index = vectordb(384)
Default_index = vectordb(384)
Drive_index = vectordb(384)

# ------------------ Tải dữ liệu chunks từ bộ nhớ đệm ------------------
with open('data/.cache/chunks.txt', 'r', encoding='utf-8') as f:
    content = f.read()
    all_chunks = [chunk for chunk in content.split('\n|||') if chunk.strip()]

# ------------------ Chọn database để lưu trữ embeddings ------------------
options = st.multiselect(
    "Lưu embeddings vào cơ sở dữ liệu:",
    ["Account Database", "Card Database", "Business Database"],
)

# ------------------ Chọn kích thước đoạn văn (chunk) ------------------
chunk_size = st.slider('Chọn kích thước đoạn văn', min_value=200, max_value=1000, value=300)

# ------------------ Giao diện tải tệp ------------------
uploaded_files = st.file_uploader(
    "Tải lên các tệp .docx hoặc .pdf", 
    type=["pdf", "docx"], 
    accept_multiple_files=True
)

# ------------------ Xử lý tệp sau khi tải lên ------------------
# def process_files():

if uploaded_files:
    with st.spinner('Đang xử lý...'):
        st.write("📂 Danh sách tệp đã tải lên:")
        for file in uploaded_files:
            st.write(f"📄 {file.name}")
        
        for file in uploaded_files:
            processor = Processor(file, options, chunk_size)
            text, chunks, embeddings = processor.process()

            all_chunks.extend(chunks)
            st.text_area(f"Nội dung của {file.name}", text, height=200)

            # Lưu embeddings vào database tương ứng
            if "Account Database" in options:
                store_embeddings_faiss(embeddings=embeddings, index=Mail_index)
            if "Card Database" in options:
                store_embeddings_faiss(embeddings=embeddings, index=Default_index)
            if "Business Database" in options:
                store_embeddings_faiss(embeddings=embeddings, index=Drive_index)

    # ------------------ Ghi lại chunks vào file đệm ------------------
    with open('data/.cache/chunks.txt', 'w', encoding='utf-8') as f:
        for chunk in all_chunks:
            print(chunk)  # In ra log console
            f.write(chunk + "\n|||")

    # ------------------ Lưu chỉ mục FAISS vào file ------------------
    if "Account Database" in options:
        save_index(Mail_index, filename='data/.cache/faiss_Mail_index.bin')
    if "Card Database" in options:
        save_index(Default_index, filename='data/.cache/faiss_Default_index.bin')
    if "Business Database" in options:
        save_index(Drive_index, filename='data/.cache/faiss_Drive_index.bin')

# ------------------ Hiển thị footer ------------------
footer = """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f1f1f1;
        text-align: center;
        padding: 10px;
        font-size: 14px;
        color: #333;
    }
    </style>
    <div class="footer">
        <p>© 2024 EDA - VPBank. All rights reserved.</p>
    </div>
    """
st.markdown(footer, unsafe_allow_html=True)
