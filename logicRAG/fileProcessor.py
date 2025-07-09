from utils.reader import Reader
from logicRAG.chunker import Chunker
from logicRAG.vectorDB.indexing import create_embeddings

class Processor:
    """
    Lớp xử lý pipeline: Đọc file → chia văn bản thành đoạn nhỏ → tạo vector embeddings.
    """

    def __init__(self, file, options, chunk_size):
        """
        Khởi tạo Processor với:
        - file: đối tượng tệp tải lên (.pdf hoặc .docx)
        - options: các lựa chọn cơ sở dữ liệu lưu embeddings (không sử dụng trực tiếp tại đây)
        - chunk_size: độ dài mỗi đoạn văn
        """
        self.file = file
        self.options = options
        self.chunk_size = chunk_size
        self.reader = Reader(file)  # Dùng lớp Reader để trích xuất văn bản

    def process(self):
        """
        Thực hiện pipeline xử lý:
        1. Đọc nội dung từ file
        2. Chia nhỏ văn bản thành các đoạn
        3. Tạo embeddings cho từng đoạn
        Trả về: text gốc, danh sách các đoạn, và embeddings tương ứng
        """
        text = self.reader.read()

        # Chia đoạn văn bản
        chunker = Chunker(text, chunk_size=self.chunk_size)
        chunks = chunker.chunk_text()

        # Tạo embedding cho từng chunk
        embeddings = create_embeddings(chunks)

        return text, chunks, embeddings
