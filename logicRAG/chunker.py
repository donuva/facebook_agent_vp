from langchain.text_splitter import RecursiveCharacterTextSplitter
from concurrent.futures import ThreadPoolExecutor
from queue import PriorityQueue

class Chunker:
    """
    Lớp Chunker giúp chia văn bản thành các đoạn nhỏ (chunk)
    để xử lý trong các mô hình RAG hoặc tìm kiếm ngữ nghĩa.
    """

    def __init__(self, text, chunk_size: int = 300, chunk_overlap: int = 50):
        """
        Khởi tạo với văn bản gốc, độ dài mỗi chunk và phần chồng lặp giữa các chunk.
        """
        self.text = text
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _chunk_text_worker(self, queue: PriorityQueue, index: int, page_text: str):
        """
        Hàm xử lý chia nhỏ văn bản cho từng trang, sử dụng RecursiveCharacterTextSplitter.
        Kết quả được đưa vào hàng đợi kèm chỉ số index để giữ thứ tự.
        """
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        chunks = splitter.split_text(page_text)
        queue.put((index, chunks))

    def chunk_text(self, num_workers: int = 4):
        """
        Chia toàn bộ văn bản thành các chunk nhỏ, xử lý song song theo từng trang.
        Trả về danh sách các chunk đã được sắp xếp đúng thứ tự.
        """
        chunk_queue = PriorityQueue()
        text_pages = self.text.split('\f')  # Phân trang nếu văn bản chứa ký tự form feed

        # Dùng multi-thread để xử lý các trang song song
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            for index, page in enumerate(text_pages):
                executor.submit(self._chunk_text_worker, chunk_queue, index, page)

        # Gom tất cả các chunk lại theo thứ tự trang
        ordered_chunks = []
        while not chunk_queue.empty():
            _, page_chunks = chunk_queue.get()
            ordered_chunks.extend(page_chunks)

        return ordered_chunks
