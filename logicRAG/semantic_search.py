from typing import List
import numpy as np
from logicRAG.vectorDB.indexing import create_embeddings

class DenseSemanticSearch:
    def __init__(self, documents: List[str]):
        self.documents = documents
        self.embeddings = self._embed_documents(documents)

    def _embed_documents(self, docs: List[str]):
        # Tạo embedding cho toàn bộ documents, loại bỏ None
        embs = create_embeddings(docs)
        return [emb[0] for emb in embs if emb is not None]

    def search(self, query: str, top_k: int = 5) -> List[str]:
        query_emb = create_embeddings([query])[0]
        if query_emb is None:
            return []
        query_emb = query_emb[0]
        scores = self._cosine_sim(query_emb, self.embeddings)
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [self.documents[i] for i in top_indices if scores[i] > 0]

    def _cosine_sim(self, query_emb, doc_embs):
        # Chuẩn hóa vector
        query_norm = query_emb / (np.linalg.norm(query_emb) + 1e-8)
        doc_norms = np.stack([emb / (np.linalg.norm(emb) + 1e-8) for emb in doc_embs])
        return np.dot(doc_norms, query_norm) 