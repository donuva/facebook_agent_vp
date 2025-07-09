import numpy as np

def search_faiss(index, query_embedding, k=50):
    """
    Tìm kiếm k vector gần nhất trong FAISS index so với query_embedding.

    Tham số:
    - index: FAISS index đã được khởi tạo và thêm vector
    - query_embedding: vector embedding cần truy vấn (1D numpy array hoặc tensor)
    - k: số lượng vector gần nhất cần lấy

    Trả về:
    - distances: khoảng cách L2 đến các vector gần nhất
    - indices: chỉ số tương ứng trong FAISS index
    """
    try:
        # Đảm bảo embedding đầu vào là numpy float32 dạng (1, dim)
        query_np = np.array([query_embedding], dtype=np.float32).reshape(1, -1)

        if query_np.shape[1] != index.d:
            raise ValueError(f"Dimension mismatch: query has {query_np.shape[1]} dims, but index expects {index.d}")

        # Truy vấn top-k gần nhất
        distances, indices = index.search(query_np, k)
        return distances, indices

    except Exception as e:
        raise RuntimeError(f"[FAISS Search Error] {e}")
