from langchain.text_splitter import RecursiveCharacterTextSplitter
from concurrent.futures import ThreadPoolExecutor
from queue import PriorityQueue

class Chunker:
    def __init__(self, text, chunk_size: int = 300, chunk_overlap: int = 50):
        super().__init__()
        self.text = text
        self.chunk_size = chunk_size  
        self.chunk_overlap = chunk_overlap

    def chunk_text_worker(self, queue, index):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
        chunks = text_splitter.split_text(self.text)
        queue.put((index, chunks)) # đảm bảo các chunk cùng 1 index

    def chunk_text(self, num_workers=4):
        chunk_queue = PriorityQueue()
        text_pages = self.text.split('\f')  
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            for index, page in enumerate(text_pages):
                executor.submit(self.chunk_text_worker, chunk_queue, index)
        
        all_chunks = []
        
        while not chunk_queue.empty():
            _, page_chunks = chunk_queue.get()
            all_chunks.extend(page_chunks)

        return all_chunks
