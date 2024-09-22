try:
    import pdfplumber
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from RAG_logic.indexing import create_embeddings, store_embeddings_faiss
    from RAG_logic.embedding_search import search_faiss
    from concurrent.futures import ThreadPoolExecutor
    from queue import PriorityQueue

except Exception as e:
    raise Exception("Error : {}".format(e)) 

def read_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

#Chunk the text into sections
def chunk_text_worker(text, chunk_size, chunk_overlap, queue, index):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = text_splitter.split_text(text)
    queue.put((index, chunks))

def chunk_text_parallel(text, chunk_size=500, chunk_overlap=50, num_workers=4):
    # Initialize PriorityQueue to store results in order
    chunk_queue = PriorityQueue()
    
    # Split text into pages for parallel processing (or other logical divisions)
    text_pages = text.split('\f')  
    
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        for index, page in enumerate(text_pages):
            executor.submit(chunk_text_worker, page, chunk_size, chunk_overlap, chunk_queue, index)
    
    all_chunks = []
    while not chunk_queue.empty():
        _, page_chunks = chunk_queue.get()
        all_chunks.extend(page_chunks)
    
    return all_chunks


def process_pdf(pdf_path, query, k=5):
    pdf_text = read_pdf(pdf_path)
    chunks = chunk_text_parallel(pdf_text)
    embeddings = create_embeddings(chunks)
    index = store_embeddings_faiss(embeddings)

    #Query
    query_embedding = create_embeddings([query])[0]  # Get embedding for query
    _, indices = search_faiss(index, query_embedding, k=k)

    closest_chunks = [chunks[i] for i in indices[0]]
    return closest_chunks

if __name__ == '__main__':
    pdf_path = r"D:\rag_langchain\demo\data\cong bo thong tin.pdf"
    query = "Số lượng cổ phiếu dự kiến phát hành để trả cổ tức"

    closest_chunks = process_pdf(pdf_path, query)

