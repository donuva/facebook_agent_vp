import streamlit as st
st.set_page_config(
    page_title="Data manipulation",
    page_icon="graphics/icon1.png"  
)
from logicRAG.fileProcessor import Processor
from logicRAG.vectorDB.indexing import vectordb, save_index

st.logo('graphics/app_logo.png')
st.title("Data manipulator")
st.subheader("Upload your documents here")

uploaded_files = st.file_uploader("Upload .docx or .pdf files", type=["pdf", "docx"], accept_multiple_files=True)
index = vectordb()
all_chunks = []

if uploaded_files:
    with st.spinner('Wait for it...'):
        st.write("Uploaded Files:")
        for file in uploaded_files:
            st.write(f"📄 {file.name}")
        
        # Prepare files for RAG
        for file in uploaded_files:
            processor = Processor(file, index)
            text, chunks = processor.process()
            all_chunks.extend(chunks)
            st.text_area(f"Content of {file.name}", text)

    with open('data/.cache/chunks.txt', 'w', encoding = 'utf-8') as f:
        for chunk in all_chunks:
            f.write(chunk + "\n|||")  
    st.success("Done!")
    save_index(index,filename='data/.cache/faiss_index.bin')

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
