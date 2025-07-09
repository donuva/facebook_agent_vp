from logicRAG.vectorDB.query import query
from logicRAG.stream_output import get_llama_response_for_fb, intergrate_context
from logicRAG.vectorDB.indexing import load_index
from logicRAG.semantic_search import SparseBM25Search
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
 # Đọc dữ liệu chunk đã lưu sẵn
with open('data/.cache/chunks.txt', 'r', encoding='utf-8') as f:
    all_chunks = [chunk for chunk in f.read().split('\n|||') if chunk.strip()]

#load thử 1 index để test
db_index = load_index("data/.cache/faiss_Default_index.bin")

# Khởi tạo SparseBM25Search cho toàn bộ chunks
bm25_search = SparseBM25Search(all_chunks)

# -------------------- Xử lý truy vấn và tạo phản hồi --------------------
def facebook_response(user_input):
    search_results = query(query_text=user_input, index=db_index, chunks=all_chunks, distance_threshold=5)
    bm25_results = bm25_search.search(user_input, top_k=5)
    
    #-------Tóm tắt contextual/ hay RAG----------------------
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

    # Gộp context lại (có thể cải tiến logic này tuỳ mục đích)
    merged_context = {"role": "system", "content": f"{retrieved_context['content']}\n{bm25_context['content']}"}

    response_gen =get_llama_response_for_fb(
        merged_context,
        user_input
    )
    
    return response_gen
