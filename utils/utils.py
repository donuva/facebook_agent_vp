import numpy as np

def print_all_embeddings(index):
    n_total = index.ntotal  # Total number of stored embeddings
    if n_total > 0:
        all_embeddings = np.zeros((n_total, index.d), dtype='float32')
        index.reconstruct_n(0, n_total, all_embeddings)  # Retrieve all embeddings
        print(all_embeddings.shape)
        print(all_embeddings)
    else:
        return 