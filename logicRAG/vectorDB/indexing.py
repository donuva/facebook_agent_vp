import os
import faiss
import torch
import openai
import numpy as np
from transformers import AutoTokenizer, AutoModel
from concurrent.futures import ThreadPoolExecutor, as_completed

# ------------------- CẤU HÌNH MÔ HÌNH EMBEDDING -------------------
model_version = "sentence-transformers/all-MiniLM-L6-v2"
tokenizer = AutoTokenizer.from_pretrained(model_version)
model = AutoModel.from_pretrained(model_version)

# ------------------- HÀM: Lấy embedding từ CLS token -------------------
def cls_pooling(model_output):
    """
    Lấy vector của token CLS đại diện cho cả câu.
    """
    return model_output.last_hidden_state[:, 0]  # [batch_size, hidden_size]

# ------------------- HÀM: Tạo embedding từ 1 đoạn văn bản -------------------
def create_embedding(chunk):
    """
    Sinh embedding vector từ 1 đoạn văn bản.
    """
    with torch.no_grad():
        encoded = tokenizer(chunk, padding=True, truncation=True, return_tensors="pt")
        output = model(**encoded)
        return cls_pooling(output)  # [1, 384]

# ------------------- HÀM: Tạo embedding cho nhiều đoạn văn song song -------------------
def create_embeddings(text_chunks, model=None, max_workers=5):
    """
    Tạo embedding cho nhiều đoạn văn bản bằng multi-threading.
    """
    embeddings = [None] * len(text_chunks)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(create_embedding, chunk): idx
            for idx, chunk in enumerate(text_chunks)
        }

        for future in as_completed(futures):
            idx = futures[future]
            try:
                embeddings[idx] = future.result()
            except Exception as e:
                print(f"Lỗi xử lý chunk ở index {idx}: {e}")
    
    return embeddings

# ------------------- HÀM: Khởi tạo FAISS vector database -------------------
def vectordb(embedding_dim: int = 384):
    """
    Khởi tạo chỉ mục FAISS với khoảng cách L2.
    """
    return faiss.IndexFlatL2(embedding_dim)

# ------------------- HÀM: Lưu embedding vào FAISS -------------------
def store_embeddings_faiss(embeddings, index):
    """
    Chuyển embedding sang numpy và thêm vào FAISS index.
    """
    embeddings_np = np.array(embeddings).astype("float32").squeeze(1)  # [n_samples, dim]
    index.add(embeddings_np)

# ------------------- HÀM: Lưu và tải FAISS index -------------------
def save_index(index, filename='faiss_index.bin'):
    """
    Ghi FAISS index ra file.
    """
    faiss.write_index(index, filename)

def load_index(filename='faiss_index.bin'):
    """
    Đọc FAISS index từ file.
    """
    return faiss.read_index(filename)
