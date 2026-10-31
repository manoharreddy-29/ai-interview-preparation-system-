"""
Core AI and NLP Evaluation Engine.
Provides robust text comparison, TF-IDF cosine similarity, keyword and concept
extraction, typo-tolerant keyword matching, scoring, and pedagogical feedback.
Zero external library dependencies required (pure standard Python math/re/collections),
with optional enhancements.
"""

import re
import math
from collections import Counter
from typing import Dict, List, Any, Optional

# Standard English Stopwords list for robust NLP tokenization
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
    "but", "by", "can", "can't", "cannot", "could", "couldn't", "did", "didn't", "do", "does",
    "doesn't", "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had",
    "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her",
    "here", "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd",
    "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself",
    "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off",
    "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own",
    "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there",
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those", "through",
    "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're",
    "we've", "were", "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you",
    "you'd", "you'll", "you're", "you've", "your", "yours", "yourself", "yourselves", "also", "thus",
    "therefore", "e.g.", "i.e.", "etc"
}


def simple_stem(word: str) -> str:
    """Lightweight suffix-stripping stemmer for English terms."""
    w = word.lower()
    for suffix in ("ization", "isation", "ational", "tional", "ation", "ment", "ness", "able", "ible", "ities", "ity", "ing", "ies", "es", "ed", "s"):
        if len(w) > len(suffix) + 3 and w.endswith(suffix):
            return w[:-len(suffix)]
    return w


def tokenize(text: str, remove_stop: bool = True) -> List[str]:
    """Tokenize text into lowercase alphanumeric tokens."""
    tokens = re.findall(r"\b[a-zA-Z0-9_\-\./']+\b", text.lower())
    if remove_stop:
        return [t for t in tokens if t not in STOPWORDS and len(t) > 1]
    return tokens


def get_ngrams(tokens: List[str], n: int = 2) -> List[str]:
    """Extract character or word n-grams."""
    return [" ".join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]


def levenshtein_distance(s1: str, s2: str) -> int:
    """Compute string edit distance to detect minor typos."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def compute_tfidf_cosine_similarity(text1: str, text2: str) -> float:
    """
    Computes vector cosine similarity using TF-IDF weighting on unigrams and bigrams.
    """
    tokens1 = tokenize(text1, remove_stop=True)
    tokens2 = tokenize(text2, remove_stop=True)

    if not tokens1 or not tokens2:
        return 0.0

    # Include unigrams and bigrams to capture terminology & relationships
    features1 = tokens1 + get_ngrams(tokens1, 2)
    features2 = tokens2 + get_ngrams(tokens2, 2)

    counts1 = Counter(features1)
    counts2 = Counter(features2)

    all_vocab = set(counts1.keys()).union(set(counts2.keys()))

    # Build TF vectors with sublinear scaling (1 + log(tf))
    vec1 = {}
    vec2 = {}
    for term in all_vocab:
        tf1 = counts1.get(term, 0)
        tf2 = counts2.get(term, 0)
        # Inverse document frequency simulation between the two documents
        doc_count = (1 if tf1 > 0 else 0) + (1 if tf2 > 0 else 0)
        idf = math.log((1 + 2) / (1 + doc_count)) + 1.0

        vec1[term] = (1 + math.log(tf1)) * idf if tf1 > 0 else 0.0
        vec2[term] = (1 + math.log(tf2)) * idf if tf2 > 0 else 0.0

    dot_product = sum(vec1[t] * vec2[t] for t in all_vocab)
    norm1 = math.sqrt(sum(v * v for v in vec1.values()))
    norm2 = math.sqrt(sum(v * v for v in vec2.values()))

    if norm1 == 0 or norm2 == 0:
        return 0.0

    cosine = dot_product / (norm1 * norm2)
    return max(0.0, min(1.0, cosine))


def extract_auto_keywords(text: str, max_keywords: int = 6) -> List[Dict[str, Any]]:
    """
    Automatically extract key terms from reference answer if not provided explicitly.
    """
    tokens = tokenize(text, remove_stop=True)
    bigrams = get_ngrams(tokens, 2)

    # Count occurrences
    term_counts = Counter(tokens)
    for bg in bigrams:
        term_counts[bg] += 1.5

    # Filter out single-character or overly common words
    candidates = [
        t for t, c in term_counts.most_common()
        if len(t) > 3 and not t.isdigit()
    ]

    selected = candidates[:max_keywords]
    keywords = []
    for item in selected:
        keywords.append({
            "term": item,
            "synonyms": [simple_stem(item)],
            "example": f"Be sure to incorporate '{item}' when structuring your technical explanation."
        })
    return keywords


def match_keyword_in_text(kw_dict: Dict[str, Any], student_text: str, student_tokens: List[str]) -> bool:
    """
    Check if a keyword or its synonyms/stems exist in the student's text.
    Handles phrase matching, stem matching, and small typo tolerance.
    """
    term = kw_dict["term"].lower()
    synonyms = [s.lower() for s in kw_dict.get("synonyms", [])]
    all_targets = [term] + synonyms

    student_lower = student_text.lower()

    # 1. Direct substring / phrase search
    for target in all_targets:
        pattern = r"\b" + re.escape(target) + r"\b"
        if re.search(pattern, student_lower):
            return True

    # 2. Stemmed comparison on tokens
    target_stems = {simple_stem(t) for t in term.split()}
    student_stems = {simple_stem(t) for t in student_tokens}
    if target_stems.issubset(student_stems):
        return True

    # Check synonyms stemmed
    for syn in synonyms:
        syn_stems = {simple_stem(t) for t in syn.split()}
        if syn_stems.issubset(student_stems):
            return True

    # 3. Fuzzy match for single-word technical terms (typo tolerance)
    if " " not in term and len(term) >= 5:
        term_stem = simple_stem(term)
        for st in student_tokens:
            if abs(len(st) - len(term)) <= 2:
                if levenshtein_distance(st, term) <= 1 or levenshtein_distance(simple_stem(st), term_stem) <= 1:
                    return True

    return False


def evaluate_student_answer(
    student_answer: str,
    reference_answer: str,
    keywords_list: Optional[List[Dict[str, Any]]] = None,
    max_marks: float = 10.0
) -> Dict[str, Any]:
    """
    Evaluate student's answer against the reference answer.
    Returns calculated score, marks, missing/matched keywords, model answer,
    pedagogical examples, and structured feedback.
    """
    cleaned_student = student_answer.strip()
    cleaned_reference = reference_answer.strip()

    if not cleaned_student:
        return {
            "score_percentage": 0,
            "marks_obtained": 0.0,
            "max_marks": max_marks,
            "semantic_similarity": 0.0,
            "keyword_coverage": 0.0,
            "length_factor": 0.0,
            "matched_keywords": [],
            "missing_keywords": [k["term"] for k in (keywords_list or [])],
            "model_answer": cleaned_reference,
            "learning_examples": [
                {"keyword": k["term"], "example": k.get("example", "")}
                for k in (keywords_list or [])
            ],
            "feedback": {
                "summary": "No answer provided.",
                "rating": "Unsatisfactory",
                "color": "#ef4444",
                "strengths": [],
                "improvements": ["Please submit an answer attempting the question."]
            }
        }

    # Prepare keywords
    if not keywords_list or len(keywords_list) == 0:
        keywords_list = extract_auto_keywords(cleaned_reference, max_keywords=5)

    student_tokens = tokenize(cleaned_student, remove_stop=True)
    ref_tokens = tokenize(cleaned_reference, remove_stop=True)

    # 1. Semantic Similarity via TF-IDF Vector Space
    semantic_sim = compute_tfidf_cosine_similarity(cleaned_student, cleaned_reference)

    # 2. Keyword Matching
    matched = []
    missing = []
    learning_examples = []

    for kw in keywords_list:
        term = kw.get("term", "")
        example = kw.get("example", f"Consider discussing '{term}' in the context of this concept.")
        if match_keyword_in_text(kw, cleaned_student, student_tokens):
            matched.append(term)
        else:
            missing.append(term)
            learning_examples.append({
                "keyword": term,
                "example": example
            })

    total_keywords = max(1, len(keywords_list))
    keyword_coverage = len(matched) / total_keywords

    # 3. Completeness & Length Assessment
    student_word_count = len(student_tokens)
    ref_word_count = max(1, len(ref_tokens))
    length_ratio = student_word_count / ref_word_count

    # Length factor: ideal between 0.6 and 1.5
    if length_ratio < 0.25:
        length_factor = length_ratio / 0.25 * 0.5
    elif length_ratio < 0.6:
        length_factor = 0.5 + (length_ratio - 0.25) / 0.35 * 0.4
    else:
        length_factor = 1.0

    # 4. Multi-Factor Score Weighting
    # 45% Semantic Similarity + 35% Keyword Coverage + 20% Completeness
    raw_score = (semantic_sim * 0.45) + (keyword_coverage * 0.35) + (length_factor * 0.20)

    # Bonus for high keyword coverage when semantic is also decent
    if keyword_coverage >= 0.8 and semantic_sim >= 0.5:
        raw_score += 0.05

    # Penalty for extreme brevity if fewer than 6 informative words
    if student_word_count < 6:
        raw_score *= 0.4

    score_percentage = round(max(0.0, min(100.0, raw_score * 100)), 1)
    marks_obtained = round((score_percentage / 100.0) * max_marks, 2)

    # 5. Diagnostic Feedback & Rating
    if score_percentage >= 85:
        rating = "Excellent"
        rating_color = "#10b981"  # Emerald
        summary = "Outstanding answer! You demonstrated thorough conceptual understanding and hit virtually all key concepts."
    elif score_percentage >= 70:
        rating = "Proficient / Good"
        rating_color = "#3b82f6"  # Blue
        summary = "Good job! You covered the core principles well. Reviewing the missing keywords below will make your response complete."
    elif score_percentage >= 50:
        rating = "Satisfactory / Partial"
        rating_color = "#f59e0b"  # Amber
        summary = "Partially correct. You identified some fundamental ideas, but missed critical technical depth and key terms."
    else:
        rating = "Needs Improvement"
        rating_color = "#ef4444"  # Red
        summary = "The response is incomplete or lacks key technical concepts compared to the reference model answer."

    strengths = []
    if matched:
        strengths.append(f"Successfully incorporated key technical concepts: {', '.join(matched[:4])}.")
    if semantic_sim >= 0.65:
        strengths.append("High contextual alignment with standard technical terminology.")
    if student_word_count >= ref_word_count * 0.5:
        strengths.append("Provided substantive explanation and reasonable elaboration.")

    improvements = []
    if missing:
        improvements.append(f"Incorporate missing core concepts: {', '.join(missing[:4])}.")
    if student_word_count < ref_word_count * 0.5:
        improvements.append("Expand on your explanations; brief one-liners omit important mechanism details.")
    if semantic_sim < 0.5:
        improvements.append("Use more precise domain vocabulary rather than generic conversational phrasing.")

    if not improvements:
        improvements.append("Well done! Continue practicing full-length technical responses.")

    return {
        "score_percentage": score_percentage,
        "marks_obtained": marks_obtained,
        "max_marks": max_marks,
        "semantic_similarity": round(semantic_sim * 100, 1),
        "keyword_coverage": round(keyword_coverage * 100, 1),
        "length_factor": round(length_factor * 100, 1),
        "student_word_count": student_word_count,
        "matched_keywords": matched,
        "missing_keywords": missing,
        "model_answer": cleaned_reference,
        "learning_examples": learning_examples,
        "feedback": {
            "summary": summary,
            "rating": rating,
            "color": rating_color,
            "strengths": strengths,
            "improvements": improvements
        }
    }
