    
from logicRAG.vectorDB.indexing import create_embeddings
from logicRAG.vectorDB.embeddingSearch import search_faiss

def query(query, index, chunks, top_k: int = 5):
    
    query_embedding = create_embeddings([query])[0]  # Get embedding for query
    #print("query embed shape o query.py la ", query_embedding.shape)
    _, indices = search_faiss(index, query_embedding, k=top_k)
    closest_chunks = [chunks[i] for i in indices[0]]
    #print("CLOSET CHUNKS IS : ", len(closest_chunks))
    return closest_chunks