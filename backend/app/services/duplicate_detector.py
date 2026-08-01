from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SIMILARITY_THRESHOLD = 0.55


def find_duplicates(new_text: str, existing: List[Tuple[str, str]]) -> List[dict]:
    """
    existing: list of (complaint_id, complaint_text) tuples already stored in DB.
    Returns matches above SIMILARITY_THRESHOLD, sorted by similarity desc.

    Keeping this to classic TF-IDF/cosine (rather than a vector DB + embeddings API)
    is a deliberate scope choice - it's fast, needs no extra infra, and is explainable
    in the demo walkthrough.
    """
    if not existing:
        return []

    ids, texts = zip(*existing)
    corpus = list(texts) + [new_text]

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(corpus)

    new_vector = tfidf_matrix[-1]
    existing_vectors = tfidf_matrix[:-1]

    similarities = cosine_similarity(new_vector, existing_vectors)[0]

    matches = []
    for complaint_id, text, score in zip(ids, texts, similarities):
        if score >= SIMILARITY_THRESHOLD:
            matches.append({"id": str(complaint_id), "similarity": round(float(score), 3), "complaint_text": text})

    matches.sort(key=lambda m: m["similarity"], reverse=True)
    return matches
