"""
Gemini AI Evaluation Module.
Uses Google Gemini API to evaluate student answers against model answers and rubrics,
providing scores, technical remarks, strengths, areas of improvement, and actionable suggestions.
Includes automatic model failover and local NLP fallback.
"""

import os
import json
import re
import requests
from typing import Dict, List, Any, Optional
from evaluator import evaluate_student_answer as local_evaluate

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
PRIMARY_MODEL = os.getenv("GEMINI_PRIMARY_MODEL", "gemini-3.5-flash-lite")
FALLBACK_MODELS = [
    PRIMARY_MODEL,
    "gemini-3.5-flash-lite",
    "gemini-3.5-flash",
    "gemini-2.5-pro",
    "gemini-3.8-flash",
    "gemini-flash-latest"
]
# Remove duplicates while preserving order
FALLBACK_MODELS = list(dict.fromkeys(FALLBACK_MODELS))


def clean_json_text(raw_text: str) -> str:
    """Extract clean JSON object from raw LLM output."""
    raw_text = raw_text.strip()
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    
    start = raw_text.find("{")
    end = raw_text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return raw_text[start:end+1].strip()
    
    return raw_text


def evaluate_with_gemini(
    student_answer: str,
    reference_answer: str,
    question_text: str,
    keywords_list: List[str],
    max_marks: float = 10.0,
    question_title: str = "Assessment"
) -> Dict[str, Any]:
    """
    Evaluates a student's answer using Gemini API.
    Returns structured evaluation with marks, ratings, remarks, strengths, improvements, and suggestions.
    """
    keywords_str = ", ".join(keywords_list) if keywords_list else "None specified"

    prompt = f"""
QUESTION TITLE: {question_title}
QUESTION PROMPT: {question_text}
MAXIMUM MARKS: {max_marks}
EXPECTED KEYWORDS / CONCEPTS: {keywords_str}

OFFICIAL REFERENCE / MODEL ANSWER:
{reference_answer}

STUDENT'S SUBMITTED ANSWER:
{student_answer}

Evaluate the student answer thoroughly and respond ONLY with a JSON object in this exact schema:
{{
    "marks_obtained": <number between 0 and {max_marks}>,
    "max_marks": {max_marks},
    "score_percentage": <number between 0 and 100>,
    "rating": "<one of: Outstanding, Good, Satisfactory / Partial, Needs Improvement>",
    "summary": "<1-2 concise sentences summarizing the evaluation>",
    "remarks": "<Personalized, encouraging, and critical examiner remarks addressed to the student>",
    "strengths": [
        "<Key point 1 correctly explained>",
        "<Key point 2 correctly explained>"
    ],
    "improvements": [
        "<Critical concept omitted or inaccurate>",
        "<Specific technical gap>"
    ],
    "suggestions": [
        "<Actionable study advice or how to structure the answer for full marks>",
        "<Specific resource or principle to review>"
    ],
    "matched_keywords": ["<keyword found in student answer>"],
    "missing_keywords": ["<keyword missing from student answer>"]
}}
"""

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "topP": 0.95
        }
    }

    # Attempt calling models in order
    last_error = None
    for model_name in FALLBACK_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=12)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts and "text" in parts[0]:
                        raw_reply = parts[0]["text"]
                        cleaned = clean_json_text(raw_reply)
                        result = json.loads(cleaned)

                        marks = float(result.get("marks_obtained", 0.0))
                        marks = max(0.0, min(float(max_marks), marks))
                        result["marks_obtained"] = round(marks, 2)
                        result["max_marks"] = float(max_marks)
                        result["score_percentage"] = round((marks / float(max_marks)) * 100.0, 1) if max_marks > 0 else 0.0
                        result["evaluation_engine"] = f"Gemini AI ({model_name})"
                        result["success"] = True
                        return result
            else:
                last_error = f"{model_name} HTTP {resp.status_code}: {resp.text[:120]}"
                print(f"[GEMINI] Notice: {last_error}")
        except Exception as e:
            last_error = str(e)
            print(f"[GEMINI] Notice on {model_name}: {e}")

    # Fallback to local NLP evaluator if Gemini call could not be completed
    print(f"[GEMINI] Falling back to local NLP engine due to: {last_error}")
    kw_formatted = [{"term": k, "synonyms": [], "example": f"Review concept: {k}"} for k in keywords_list]
    local_res = local_evaluate(
        student_answer=student_answer,
        reference_answer=reference_answer,
        keywords_list=kw_formatted,
        max_marks=max_marks
    )

    matched_kw = []
    for k in local_res.get("matched_keywords", []):
        if isinstance(k, dict):
            matched_kw.append(k.get("term", str(k)))
        else:
            matched_kw.append(str(k))

    missing_kw = []
    for k in local_res.get("missing_keywords", []):
        if isinstance(k, dict):
            missing_kw.append(k.get("term", str(k)))
        else:
            missing_kw.append(str(k))

    return {
        "marks_obtained": local_res["marks_obtained"],
        "max_marks": local_res["max_marks"],
        "score_percentage": local_res["score_percentage"],
        "rating": local_res["feedback"]["rating"],
        "summary": local_res["feedback"]["summary"],
        "remarks": f"Evaluated using local NLP heuristic engine. Score is {local_res['score_percentage']}% based on semantic similarity and keyword coverage.",
        "strengths": local_res["feedback"]["strengths"],
        "improvements": local_res["feedback"]["improvements"],
        "suggestions": [
            f"Review model answer: '{reference_answer[:120]}...'",
            "Include technical terminology and definitions for higher marks."
        ],
        "matched_keywords": matched_kw,
        "missing_keywords": missing_kw,
        "evaluation_engine": "Local NLP Engine (Offline Fallback)",
        "success": True
    }
