try:
    import os
    import openai
    import faiss
    import numpy as np

except Exception as e:
    raise Exception("Error : {}".format(e))

openai.api_key = os.getenv("OPENAI_API_KEY")

#Create embeddings using OpenAI
def create_embeddings(text_chunks, model="text-embedding-3-small"):
    embeddings = []
    for chunk in text_chunks:
        response = openai.Embedding.create(input=chunk, model=model)
        embeddings.append(response['data'][0]['embedding'])
    return embeddings

def store_embeddings_faiss(embeddings):
    embedding_dim = len(embeddings[0])  # Dimension of embeddings (1536 for OpenAI's ada-002)
    
    # Initialize FAISS index for L2 distance
    index = faiss.IndexFlatL2(embedding_dim)
    
    # Convert embeddings to numpy array and add to FAISS
    embeddings_np = np.array(embeddings).astype('float32')
    index.add(embeddings_np)
    
    return index

