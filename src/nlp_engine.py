import re
from collections import Counter
from typing import List, Tuple

import numpy as np
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer


def normalize_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    return text.strip()


def split_sentences(text: str) -> List[str]:
    """Split text into candidate sentences with a robust regex fallback."""
    cleaned = normalize_text(text)
    chunks = re.split(r"(?<=[.!?])\s+", cleaned)
    filtered = [c.strip() for c in chunks if len(c.strip()) > 35]
    return filtered


def extract_key_concepts(text: str, top_n: int = 24) -> List[str]:
    """Extract key uni/bi-gram concepts using TF-IDF importance."""
    try:
        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=1500,
            min_df=1,
        )
        matrix = vectorizer.fit_transform([text])
        scores = matrix.toarray()[0]
        features = np.array(vectorizer.get_feature_names_out())
        ranked = features[np.argsort(scores)[::-1]]

        concepts = []
        for term in ranked:
            tokens = term.split()
            if any(token in ENGLISH_STOP_WORDS for token in tokens):
                continue
            if len(term) < 3:
                continue
            if term not in concepts:
                concepts.append(term)
            if len(concepts) >= top_n:
                break
        return concepts
    except Exception:
        # TF-IDF can fail on very short documents; fallback to frequency heuristic.
        words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())
        words = [w for w in words if w not in ENGLISH_STOP_WORDS]
        freq = Counter(words)
        return [w for w, _ in freq.most_common(top_n)]


def sentence_relevance(sentences: List[str], concepts: List[str]) -> List[Tuple[str, float]]:
    """Score sentences by concept overlap and lexical richness."""
    scored = []
    for sentence in sentences:
        s_lower = sentence.lower()
        overlap = sum(1 for concept in concepts if concept in s_lower)
        length_bonus = min(len(sentence) / 180, 1.0)
        score = overlap * 1.5 + length_bonus
        scored.append((sentence, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored
