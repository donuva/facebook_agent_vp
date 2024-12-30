import numpy as np

def search_faiss(index, query_embedding, k=5):
    try:
        query_np = np.array([query_embedding]).astype('float32')
        print(query_np.shape)
        distances, indices = index.search(query_np, k)  # k is the number of nearest neighbors
        return distances, indices
    except Exception as e:
        raise Exception("Error : {}".format(e))