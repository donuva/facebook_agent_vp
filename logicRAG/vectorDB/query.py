from logicRAG.vectorDB.indexing import create_embeddings
from logicRAG.vectorDB.embeddingSearch import search_faiss

def query(query_text, index, chunks, top_k: int = 5, distance_threshold: float = 20.0):
    """
    Truy vấn vector database FAISS để tìm các đoạn văn gần nhất với câu hỏi đầu vào.

    Tham số:
    - query_text: câu hỏi đầu vào của người dùng (str)
    - index: FAISS index đã được load
    - chunks: danh sách đoạn văn gốc tương ứng với vector trong index
    - top_k: số lượng kết quả gần nhất cần tìm (int)
    - distance_threshold: ngưỡng lọc khoảng cách L2 (float), càng nhỏ thì yêu cầu càng gần hơn

    Trả về:
    - closest_chunks: danh sách các đoạn văn phù hợp nhất
    """
    # Bước 1: Tạo embedding cho câu hỏi
    query_embedding = create_embeddings([query_text])[0]
    print("Embedding của truy vấn:", query_embedding.shape)

    # Bước 2: Truy vấn FAISS để lấy chỉ số và khoảng cách các vector gần nhất
    distances, indices = search_faiss(index, query_embedding, k=top_k)
    print("Khoảng cách FAISS trả về:", distances)

    # Bước 3: Lọc ra những kết quả đủ gần (dựa theo ngưỡng)
    valid_indices = [
        indices[0][i]
        for i in range(len(indices[0]))
        if distances[0][i] >= distance_threshold
    ]

    # Bước 4: Trả về các đoạn văn tương ứng
    closest_chunks = [chunks[i] for i in valid_indices]

    return closest_chunks
