from utils.reader import Reader
from logicRAG.chunker import Chunker
from logicRAG.vectorDB.indexing import create_embeddings, store_embeddings_faiss

class Processor:
    def __init__(self, file, index, chunk_size):
        self.file = file
        self.reader = Reader(self.file)
        self.index = index
        self.chunk_size = chunk_size
        
    def process(self):
        text = self.reader.read()
        chunker = Chunker(text, chunk_size=self.chunk_size)
        chunks = chunker.chunk_text()
        embeddings = create_embeddings(chunks)
        store_embeddings_faiss(embeddings=embeddings, index=self.index)
        return text, chunks