import streamlit as st

if "is_login" not in st.session_state or not st.session_state.is_login:
    st.warning("CHƯA ĐĂNG NHẬP")
    st.switch_page("Home.py")
    
st.set_page_config(
    page_title="Data manipulation",
    page_icon="graphics/icon1.png"  
)
from logicRAG.fileProcessor import Processor
from logicRAG.vectorDB.indexing import vectordb, save_index, store_embeddings_faiss

st.logo('graphics/app_logo.png')
st.title("Data manipulator")
st.subheader("Upload your documents here")

options = st.multiselect(
    "Save files in vector database:",
    ["Mail Database", "Default Database", "Drive Database"],
)

#init step
Mail_index = vectordb(384)
Default_index = vectordb(384)
Drive_index = vectordb(384)

all_chunks = []
chunk_size = st.slider('Select chunk size', min_value=200, max_value=1000, value=300)
uploaded_files = st.file_uploader("Upload .docx or .pdf files", type=["pdf", "docx"], accept_multiple_files=True)

if uploaded_files:
    with st.spinner('Wait for it...'):
        st.write("Uploaded Files:")
        for file in uploaded_files:
            st.write(f"📄 {file.name}")
        
        # Prepare files for RAG
        for file in uploaded_files:
            processor = Processor(file, options, chunk_size)
            text, chunks, embeddings = processor.process()
            all_chunks.extend(chunks)
            st.text_area(f"Content of {file.name}", text)
            if "Mail Database" in options: store_embeddings_faiss(embeddings=embeddings, index=Mail_index)
            if "Default Database" in options: store_embeddings_faiss(embeddings=embeddings, index=Default_index)
            if "Drive Database" in options: store_embeddings_faiss(embeddings=embeddings, index=Drive_index)

    with open('data/.cache/chunks.txt', 'w', encoding = 'utf-8') as f:
        for chunk in all_chunks:
            f.write(chunk + "\n|||")  

    if "Mail Database" in options: save_index(Mail_index, filename='data/.cache/faiss_Mail_index.bin')
    if "Default Database" in options: save_index(Default_index, filename='data/.cache/faiss_Default_index.bin')
    if "Drive Database" in options: save_index(Drive_index, filename='data/.cache/faiss_Drive_index.bin')

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
