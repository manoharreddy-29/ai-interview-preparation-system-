"""
AI-Based Student Answer Evaluation System
Flask Backend Application with Gemini AI and MySQL Integration.
Provides Student & Faculty Portals, Profiles, Assessments, and Analytics.
"""

import os
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv

load_dotenv()

import database
from gemini_evaluator import evaluate_with_gemini

app = Flask(__name__, static_folder="static", static_url_path="")


@app.after_request
def add_cors_headers(response):
    """Enable CORS for all incoming requests."""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


@app.route("/")
def index():
    """Serve the single-page application frontend."""
    return send_from_directory(app.static_folder, "index.html")


# ======================================================================
# System & Health Check Endpoints
# ======================================================================

@app.route("/api/system/status", methods=["GET"])
def system_status():
    """Return backend status, Gemini AI status, and Database connection info."""
    db_status = database.get_db_status()
    return jsonify({
        "status": "online",
        "service": "AI-Based Student Answer Evaluation System",
        "version": "2.0.0",
        "gemini": {
            "configured": bool(os.getenv("GEMINI_API_KEY")),
            "primary_model": os.getenv("GEMINI_PRIMARY_MODEL", "gemini-3.5-flash"),
            "project_number": os.getenv("GEMINI_PROJECT_NUMBER", "781869000408")
        },
        "database": db_status
    })


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "database": database.DB_MODE})


# ======================================================================
# Authentication Endpoints (Student & Faculty)
# ======================================================================

@app.route("/api/auth/register", methods=["POST"])
def register():
    """Register a new student or faculty member."""
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()
    role = data.get("role", "student").strip().lower()
    identifier = data.get("identifier", "").strip()
    department = data.get("department", "Computer Science").strip()

    if not name or not email or not password or not identifier:
        return jsonify({"success": False, "error": "Please provide name, email, password, and Roll No / Faculty ID."}), 400

    if role not in ("student", "faculty"):
        return jsonify({"success": False, "error": "Role must be 'student' or 'faculty'."}), 400

    existing = database.find_user_by_email(email)
    if existing:
        return jsonify({"success": False, "error": f"An account with email '{email}' already exists."}), 409

    user = database.create_user(name, email, password, role, identifier, department)
    # Exclude password_hash
    user_data = {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "identifier": user["identifier"],
        "department": user["department"],
        "created_at": str(user.get("created_at", ""))
    }
    return jsonify({"success": True, "message": f"{role.capitalize()} registered successfully!", "user": user_data})


@app.route("/api/auth/login", methods=["POST"])
def login():
    """Authenticate student or faculty credentials."""
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()
    expected_role = data.get("role", "").strip().lower()

    if not email or not password:
        return jsonify({"success": False, "error": "Email and password are required."}), 400

    user = database.find_user_by_email(email)
    if not user:
        return jsonify({"success": False, "error": "Invalid email or password."}), 401

    if database.hash_password(password) != user["password_hash"]:
        return jsonify({"success": False, "error": "Invalid email or password."}), 401

    if expected_role and user["role"] != expected_role:
        return jsonify({
            "success": False,
            "error": f"This account is registered as a {user['role']}, not a {expected_role}."
        }), 403

    user_data = {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "identifier": user["identifier"],
        "department": user["department"],
        "created_at": str(user.get("created_at", ""))
    }
    return jsonify({"success": True, "message": f"Welcome back, {user['name']}!", "user": user_data})


@app.route("/api/auth/profile", methods=["GET"])
def profile():
    """Retrieve user profile and performance statistics."""
    user_id = request.args.get("user_id", type=int)
    if not user_id:
        return jsonify({"success": False, "error": "User ID is required."}), 400

    user = database.get_user_by_id(user_id)
    if not user:
        return jsonify({"success": False, "error": "User not found."}), 404

    user_data = {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "identifier": user["identifier"],
        "department": user["department"],
        "created_at": str(user.get("created_at", ""))
    }

    if user["role"] == "student":
        stats = database.get_student_stats(user["id"])
        return jsonify({"success": True, "user": user_data, "stats": stats})
    else:
        stats = database.get_faculty_analytics()
        return jsonify({"success": True, "user": user_data, "analytics": stats})


# ======================================================================
# Student Evaluation Endpoints
# ======================================================================

@app.route("/api/student/questions", methods=["GET"])
@app.route("/api/questions", methods=["GET"])
def list_student_questions():
    """List all available questions."""
    questions = database.get_all_questions()
    return jsonify({"success": True, "count": len(questions), "questions": questions})


@app.route("/api/student/questions/<int:qid>", methods=["GET"])
def get_student_question(qid):
    """Retrieve single question by ID."""
    q = database.get_question_by_id(qid)
    if not q:
        return jsonify({"success": False, "error": f"Question {qid} not found."}), 404
    return jsonify({"success": True, "question": q})


@app.route("/api/student/evaluate", methods=["POST", "OPTIONS"])
@app.route("/api/evaluate", methods=["POST", "OPTIONS"])
def evaluate():
    """
    Evaluate student's answer using Gemini AI and store record in MySQL/database.
    """
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    data = request.get_json(silent=True) or {}
    student_id = data.get("student_id", 2)
    student_answer = data.get("student_answer", "").strip()
    question_id = data.get("question_id")

    if not student_answer:
        return jsonify({"success": False, "error": "Student answer cannot be empty. Please enter an answer."}), 400

    student = database.get_user_by_id(student_id)
    student_name = student["name"] if student else data.get("student_name", "Student")
    student_identifier = student["identifier"] if student else data.get("student_identifier", "STD-001")
    student_department = student["department"] if student else data.get("student_department", "Computer Science")

    # 1. Predefined or Faculty-created question from database
    if question_id and str(question_id) != "custom":
        try:
            qid_int = int(question_id)
            q = database.get_question_by_id(qid_int)
        except Exception:
            q = None

        if not q:
            return jsonify({"success": False, "error": f"Question ID '{question_id}' not found."}), 404

        title = q["title"]
        question_text = q["question_text"]
        reference_answer = q["reference_answer"]
        raw_kw = q.get("keywords", "")
        keywords_list = [k.strip() for k in raw_kw.split(",") if k.strip()] if isinstance(raw_kw, str) else []
        max_marks = float(q.get("max_marks", 10.0))
        target_qid = q["id"]
    else:
        # Custom evaluation
        title = data.get("custom_question", "Custom Assessment")
        question_text = data.get("custom_question", "Custom Question Prompt")
        reference_answer = data.get("custom_reference", "").strip()
        if not reference_answer:
            return jsonify({"success": False, "error": "For custom evaluations, a reference answer is required."}), 400

        raw_kw = data.get("custom_keywords", [])
        if isinstance(raw_kw, str):
            keywords_list = [k.strip() for k in raw_kw.split(",") if k.strip()]
        else:
            keywords_list = [str(k).strip() for k in raw_kw if str(k).strip()]
        max_marks = float(data.get("max_marks", 10.0))
        target_qid = None

    # Run evaluation with Gemini AI (with automated fallback)
    eval_result = evaluate_with_gemini(
        student_answer=student_answer,
        reference_answer=reference_answer,
        question_text=question_text,
        keywords_list=keywords_list,
        max_marks=max_marks,
        question_title=title
    )

    # Save to Database
    eval_id = database.save_evaluation(
        student_id=student_id,
        student_name=student_name,
        student_identifier=student_identifier,
        student_department=student_department,
        question_id=target_qid,
        question_title=title,
        student_answer=student_answer,
        marks_obtained=eval_result["marks_obtained"],
        max_marks=eval_result["max_marks"],
        score_percentage=eval_result["score_percentage"],
        rating=eval_result["rating"],
        summary=eval_result["summary"],
        remarks=eval_result.get("remarks", "Evaluation completed successfully."),
        strengths=eval_result.get("strengths", []),
        improvements=eval_result.get("improvements", []),
        suggestions=eval_result.get("suggestions", []),
        matched_keywords=eval_result.get("matched_keywords", []),
        missing_keywords=eval_result.get("missing_keywords", []),
        evaluation_engine=eval_result.get("evaluation_engine", "Gemini AI")
    )

    eval_result["id"] = eval_id
    eval_result["question_title"] = title
    eval_result["question_text"] = question_text
    eval_result["reference_answer"] = reference_answer

    return jsonify({"success": True, "evaluation": eval_result})


@app.route("/api/student/evaluations", methods=["GET"])
def student_evaluations():
    """Retrieve submission history for a specific student."""
    student_id = request.args.get("student_id", type=int)
    if not student_id:
        return jsonify({"success": False, "error": "student_id is required"}), 400

    records = database.get_evaluations_by_student(student_id)
    return jsonify({"success": True, "count": len(records), "evaluations": records})


@app.route("/api/student/evaluations/<int:eid>", methods=["GET"])
def get_evaluation(eid):
    """Retrieve full evaluation report by ID."""
    record = database.get_evaluation_by_id(eid)
    if not record:
        return jsonify({"success": False, "error": "Evaluation record not found."}), 404
    return jsonify({"success": True, "evaluation": record})


# ======================================================================
# Faculty Management Endpoints
# ======================================================================

@app.route("/api/faculty/questions", methods=["GET", "POST"])
def faculty_questions():
    """List or create faculty questions."""
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        faculty_id = data.get("faculty_id", 1)
        faculty_name = data.get("faculty_name", "Faculty")
        title = data.get("title", "").strip()
        subject = data.get("subject", "").strip()
        question_text = data.get("question_text", "").strip()
        reference_answer = data.get("reference_answer", "").strip()
        keywords = data.get("keywords", "").strip()
        max_marks = float(data.get("max_marks", 10.0))
        difficulty = data.get("difficulty", "Medium").strip()

        if not title or not subject or not question_text or not reference_answer:
            return jsonify({"success": False, "error": "Title, Subject, Question, and Reference Answer are required."}), 400

        q = database.create_question(
            faculty_id=faculty_id,
            faculty_name=faculty_name,
            title=title,
            subject=subject,
            question_text=question_text,
            reference_answer=reference_answer,
            keywords=keywords,
            max_marks=max_marks,
            difficulty=difficulty
        )
        return jsonify({"success": True, "message": "Question created successfully!", "question": q})

    questions = database.get_all_questions()
    return jsonify({"success": True, "count": len(questions), "questions": questions})


@app.route("/api/faculty/questions/<int:qid>", methods=["DELETE"])
def delete_faculty_question(qid):
    """Delete a question."""
    success = database.delete_question(qid)
    return jsonify({"success": success, "message": f"Question {qid} deleted."})


@app.route("/api/faculty/submissions", methods=["GET"])
def faculty_submissions():
    """Retrieve all student submissions with scores and remarks."""
    submissions = database.get_all_evaluations()
    return jsonify({"success": True, "count": len(submissions), "submissions": submissions})


@app.route("/api/faculty/analytics", methods=["GET"])
def faculty_analytics():
    """Get aggregate statistics for the Faculty dashboard."""
    analytics = database.get_faculty_analytics()
    return jsonify({"success": True, "analytics": analytics})


# ======================================================================
# App Entry Point
# ======================================================================

if __name__ == "__main__":
    # Initialize Database on startup
    database.init_db()

    port = int(os.environ.get("PORT", 5000))
    print("=" * 70)
    print("  AI-Based Student Answer Evaluation System - Enhanced Platform")
    print(f"  Gemini Model: {os.getenv('GEMINI_PRIMARY_MODEL', 'gemini-3.5-flash')}")
    print(f"  Database Mode: {database.DB_MODE}")
    print(f"  Web Application URL: http://127.0.0.1:{port}")
    print("=" * 70)
    app.run(host="0.0.0.0", port=port, debug=True)
