from utils.reader import Reader
from logicRAG.chunker import Chunker
from logicRAG.vectorDB.indexing import create_embeddings, store_embeddings_faiss
import time
class Processor:
    def __init__(self, file, index):
        super().__init__()
        self.file = file
        self.reader = Reader(self.file)
        self.index = index
        
    def process(self):
        start = time.time()
        text = self.reader.read()
        self.chunker = Chunker(text)
        chunks = self.chunker.chunk_text()
        embeddings = create_embeddings(chunks)
        store_embeddings_faiss(embeddings=embeddings, index=self.index)
        return text, chunks