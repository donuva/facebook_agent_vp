from logicRAG.vectorDB.query import query
from logicRAG.stream_output import get_llama_response_for_fb, intergrate_context
from logicRAG.vectorDB.indexing import load_index
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
 # Đọc dữ liệu chunk đã lưu sẵn
with open('data/.cache/chunks.txt', 'r', encoding='utf-8') as f:
    all_chunks = [chunk for chunk in f.read().split('\n|||') if chunk.strip()]

#load thử 1 index để test
db_index = load_index("data/.cache/faiss_Default_index.bin")

# -------------------- Xử lý truy vấn và tạo phản hồi --------------------
def facebook_response(user_input):
    search_results = query(query_text=user_input, index=db_index, chunks=all_chunks, distance_threshold=5)
   
    #-------Tóm tắt contextual/ hay RAG----------------------
    docs, summary = "", ""
    for i, doc in enumerate(search_results):
        docs += doc + " "
        if len(docs) > 2000:
            summary = intergrate_context([docs, summary])
            docs = ""
    if docs:
        summary = intergrate_context([docs, summary])
    
    retrieved_context = {"role": "system", "content": f"Retrieved Document: {summary}"}

    
    print(f"retrieved_context is {retrieved_context}")
    
    response_gen =get_llama_response_for_fb(
        retrieved_context,
        user_input
    )
    
    return response_gen
