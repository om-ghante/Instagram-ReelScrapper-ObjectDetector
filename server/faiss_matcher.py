import faiss
import numpy as np
import json

# Initialize FAISS index
dimension = 512  # CLIP ViT-B/32 dimension
index = faiss.IndexFlatIP(dimension)

# Product database with valid mock embeddings
product_db = [
    {
        "id": 1, 
        "name": "Designer Handbag", 
        "image_url": "https://img.freepik.com/free-photo/beautiful-elegance-luxury-fashion-green-handbag_1203-7655.jpg?semt=ais_items_boosted&w=740",
        "embedding": np.random.rand(dimension).tolist()
    },
    {
        "id": 2, 
        "name": "Modern Chair", 
        "image_url": "https://cdn.decornation.in/wp-content/uploads/2020/07/modern-dining-table-chairs.jpg",
        "embedding": np.random.rand(dimension).tolist()
    }
]

# Initialize index with product embeddings
embeddings = np.array([p["embedding"] for p in product_db]).astype("float32")
index.add(embeddings)

def find_matches(query_embedding: np.ndarray, k=5) -> list:
    """Find k most similar products to the query embedding"""
    D, I = index.search(query_embedding, k)
    return [{
        "product_id": product_db[i]["id"],
        "name": product_db[i]["name"],
        "image_url": product_db[i]["image_url"],
        "similarity_score": float(d)
    } for d, i in zip(D[0], I[0])]