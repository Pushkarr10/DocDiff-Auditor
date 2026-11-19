# core/comparator.py
"""Comparison utilities for docdiff-auditor.

Provides functions to embed text chunks, compute similarity, and classify changes.
"""

import numpy as np
from typing import List, Tuple, Dict
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Load model lazily; Streamlit will cache the resource in the UI.

def load_model(model_name: str = "all-MiniLM-L6-v2") -> SentenceTransformer:
    """Load and return a SentenceTransformer model.
    The model is cached at the UI layer via @st.cache_resource.
    """
    return SentenceTransformer(model_name)


def embed_chunks(chunks: List[str], model: SentenceTransformer) -> np.ndarray:
    """Embed a list of text chunks using the provided model.
    Returns a 2D numpy array of shape (len(chunks), embedding_dim).
    """
    return model.encode(chunks, convert_to_numpy=True, normalize_embeddings=True)


def compute_similarity_matrix(emb_a: np.ndarray, emb_b: np.ndarray) -> np.ndarray:
    """Compute cosine similarity matrix between two sets of embeddings.
    Returns matrix shape (len(a), len(b)).
    """
    return cosine_similarity(emb_a, emb_b)


def classify_changes(
    chunks_a: List[str],
    chunks_b: List[str],
    similarity_matrix: np.ndarray,
    unchanged_thr: float = 0.92,
    modified_thr: float = 0.60,
) -> List[Dict]:
    """Classify each chunk as Unchanged, Modified, Added, or Removed.

    For each chunk in A we find the best match in B. If the best similarity
    is >= unchanged_thr → Unchanged.
    If it is between modified_thr and unchanged_thr → Modified.
    If no match in B reaches modified_thr → Removed.
    After processing A, any chunks in B that were not matched become Added.
    """
    matched_b = set()
    results: List[Dict] = []

    for i, a_text in enumerate(chunks_a):
        row = similarity_matrix[i]
        best_j = int(np.argmax(row))
        best_score = float(row[best_j])
        if best_score >= unchanged_thr:
            status = "Unchanged"
        elif best_score >= modified_thr:
            status = "Modified"
        else:
            status = "Removed"
            best_j = None
        b_text = chunks_b[best_j] if best_j is not None else None
        if best_j is not None:
            matched_b.add(best_j)
        results.append({
            "a_text": a_text,
            "b_text": b_text,
            "similarity": best_score,
            "status": status,
        })

    # Add entries for chunks only in B (Added)
    for j, b_text in enumerate(chunks_b):
        if j not in matched_b:
            results.append({
                "a_text": None,
                "b_text": b_text,
                "similarity": None,
                "status": "Added",
            })
    return results
