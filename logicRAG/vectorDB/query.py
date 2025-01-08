    
from logicRAG.vectorDB.indexing import create_embeddings
from logicRAG.vectorDB.embeddingSearch import search_faiss

def query(query, index, chunks, top_k: int = 5):
    
    query_embedding = create_embeddings([query])[0]  # Get embedding for query
    #print("query embed shape o query.py la ", query_embedding.shape)
    distances, indices = search_faiss(index, query_embedding, k=top_k)
    final_indices = [indices[0][i] for i in range(len(indices[0]))  if distances[0][i] >= 15] # Threshold = 15, chỉ có chunks nào có điểm L2 lớn hơn 15 được cho vào, tránh trường hợp sại lệch do thiếu data mà vẫn phải chọn top_k

    print("DISTANCE LIST IS : ", distances)
    closest_chunks = []
    closest_chunks = [chunks[i] for i in final_indices]
    #print("CLOSET CHUNKS IS : ", len(closest_chunks))
    return closest_chunks