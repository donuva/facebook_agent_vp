import unittest
from logicRAG.semantic_search import DenseSemanticSearch

class TestDenseSemanticSearch(unittest.TestCase):
    def setUp(self):
        self.docs = [
            "Hôm nay trời đẹp và nắng.",
            "Tôi thích học máy và trí tuệ nhân tạo.",
            "Ngân hàng VPBank cung cấp nhiều dịch vụ tài chính.",
            "Chatbot có thể hỗ trợ khách hàng 24/7.",
            "Dịch vụ ngân hàng số ngày càng phát triển."
        ]
        self.searcher = DenseSemanticSearch(self.docs)

    def test_search_relevant(self):
        query = "ngân hàng và dịch vụ tài chính"
        results = self.searcher.search(query, top_k=2)
        self.assertTrue(any("VPBank" in doc or "dịch vụ tài chính" in doc for doc in results))

    def test_search_irrelevant(self):
        query = "bóng đá thế giới"
        results = self.searcher.search(query, top_k=2)
        # Dense search có thể trả về kết quả gần nhất, nhưng nếu không liên quan sẽ điểm thấp
        self.assertIsInstance(results, list)
        self.assertTrue(len(results) <= 2)

if __name__ == "__main__":
    unittest.main() 