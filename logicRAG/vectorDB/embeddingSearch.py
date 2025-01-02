import numpy as np

def search_faiss(index, query_embedding, k=5):
    try:
        query_np = np.array([query_embedding]).astype('float32')
        print("CHIỀU Ở FAISS LƯU LÀ : ",query_np.reshape((1,-1)).shape)
        print("CHIỀU Ở INDEX LƯU LÀ : ",index.d)
        query_np = query_np.reshape((1,-1))
        distances, indices = index.search(query_np, k)  # k is the number of nearest neighbors
        return distances, indices
    except Exception as e:
        raise Exception("Error : {}".format(e))