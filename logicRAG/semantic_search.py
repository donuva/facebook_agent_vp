from typing import List
import re
from rank_bm25 import BM25Okapi

class SparseBM25Search:
    def __init__(self, documents: List[str]):
        self.documents = documents
        self.tokenized_corpus = [self._tokenize(doc) for doc in documents]
        self.bm25 = BM25Okapi(self.tokenized_corpus)

    def _tokenize(self, text: str) -> List[str]:
        # Tokenize đơn giản: tách từ, loại bỏ ký tự đặc biệt
        return re.findall(r"\w+", text.lower())

    def search(self, query: str, top_k: int = 5) -> List[str]:
        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        return [self.documents[i] for i in top_indices if scores[i] > 0] 