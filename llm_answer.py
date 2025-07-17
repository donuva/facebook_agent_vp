# logic_rag_with_intent.py

from logicRAG.vectorDB.query import query
from logicRAG.stream_output import get_llama_response_for_fb
from logicRAG.vectorDB.indexing import load_index
from intent_clasify import classify_intent_llm, intents  # <-- import intent list & classify hàm
import os

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# 1. LOAD CHUNKS, INDEX chỉ 1 lần khi import
with open('data/.cache/chunks.txt', 'r', encoding='utf-8') as f:
    all_chunks = [chunk for chunk in f.read().split('\n|||') if chunk.strip()]

db_index = load_index("data/.cache/faiss_Default_index.bin")

# 2. Hàm trả lời Facebook + intent
def facebook_response(user_input):
    """
    Nhận đầu vào user_input (string)
    Trả về (answer, confidence, intent)
    """
    # ---- (a) Truy vấn vector DB lấy context
    search_results = query(query_text=user_input, index=db_index, chunks=all_chunks, top_k=20, distance_threshold=10)
    docs = " ".join(search_results)
    retrieved_context = {"role": "system", "content": f"Retrieved Document: {docs}"}
    
    # ---- (b) LLM sinh câu trả lời
    answer = get_llama_response_for_fb(
        retrieved_context,
        user_input
    )
    
    # ---- (c) LLM classify intent (multi-label, multi-score)
    intent_scores = classify_intent_llm(user_input, intents)
    if intent_scores:
        intent = max(intent_scores, key=intent_scores.get)
        confidence = float(intent_scores[intent])
    else:
        intent = "Khác"
        confidence = 0.6

    return answer, confidence, intent

# --- Test thử ---
if __name__ == "__main__":
    test_question = input("Nhập câu hỏi: ")
    ans, conf, intent = facebook_response(test_question)
    print("\n---- Trả lời ----")
    print("Answer:", ans)
    print("Confidence:", conf)
    print("Intent:", intent)
