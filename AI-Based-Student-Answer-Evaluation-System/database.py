"""
Database Management Layer for AI-Based Student Answer Evaluation System.
Supports MySQL as the primary database with an automatic SQLite fallback
if MySQL is not yet started on localhost.
"""

import os
import json
import sqlite3
import hashlib
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "student_eval_db")

SQLITE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "student_eval.db")

DB_MODE = "UNINITIALIZED"
_mysql_available = False


def hash_password(password: str) -> str:
    """Hash password using SHA-256 for secure local storage."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def test_mysql_connection():
    """Attempt connecting to MySQL server."""
    try:
        import pymysql
        conn = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            connect_timeout=2
        )
        conn.close()
        return True
    except Exception as e:
        return False


def get_mysql_conn(select_db: bool = True):
    """Obtain a PyMySQL connection with dictionary cursor."""
    import pymysql
    kwargs = {
        "host": MYSQL_HOST,
        "port": MYSQL_PORT,
        "user": MYSQL_USER,
        "password": MYSQL_PASSWORD,
        "charset": "utf8mb4",
        "cursorclass": pymysql.cursors.DictCursor,
        "autocommit": True
    }
    if select_db:
        kwargs["database"] = MYSQL_DATABASE
    return pymysql.connect(**kwargs)


def get_sqlite_conn():
    """Obtain a SQLite connection with Row factory."""
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize tables and seed default accounts on MySQL or fallback SQLite."""
    global DB_MODE, _mysql_available

    if test_mysql_connection():
        try:
            # 1. Connect without database and create database if needed
            root_conn = get_mysql_conn(select_db=False)
            with root_conn.cursor() as cur:
                cur.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DATABASE}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            root_conn.close()

            # 2. Create tables
            conn = get_mysql_conn(select_db=True)
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(150) NOT NULL,
                        email VARCHAR(150) NOT NULL UNIQUE,
                        password_hash VARCHAR(255) NOT NULL,
                        role VARCHAR(20) NOT NULL,
                        identifier VARCHAR(100) NOT NULL,
                        department VARCHAR(100) DEFAULT 'Computer Science',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)

                cur.execute("""
                    CREATE TABLE IF NOT EXISTS questions (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        faculty_id INT NULL,
                        faculty_name VARCHAR(150) DEFAULT 'Faculty Administrator',
                        title VARCHAR(255) NOT NULL,
                        subject VARCHAR(100) NOT NULL,
                        question_text TEXT NOT NULL,
                        reference_answer TEXT NOT NULL,
                        keywords TEXT NOT NULL,
                        max_marks DECIMAL(5, 2) DEFAULT 10.00,
                        difficulty VARCHAR(20) DEFAULT 'Medium',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)

                cur.execute("""
                    CREATE TABLE IF NOT EXISTS evaluations (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        student_id INT NOT NULL,
                        student_name VARCHAR(150) NOT NULL,
                        student_identifier VARCHAR(100) NOT NULL,
                        student_department VARCHAR(100) DEFAULT 'Computer Science',
                        question_id INT NULL,
                        question_title VARCHAR(255) NOT NULL,
                        student_answer TEXT NOT NULL,
                        marks_obtained DECIMAL(5, 2) NOT NULL,
                        max_marks DECIMAL(5, 2) NOT NULL,
                        score_percentage DECIMAL(5, 2) NOT NULL,
                        rating VARCHAR(50) NOT NULL,
                        summary TEXT NOT NULL,
                        remarks TEXT NOT NULL,
                        strengths TEXT NOT NULL,
                        improvements TEXT NOT NULL,
                        suggestions TEXT NOT NULL,
                        matched_keywords TEXT NOT NULL,
                        missing_keywords TEXT NOT NULL,
                        evaluation_engine VARCHAR(100) DEFAULT 'Gemini AI',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
                """)

            seed_defaults_mysql(conn)
            conn.close()
            DB_MODE = "MySQL"
            _mysql_available = True
            print(f"[DATABASE] Connected to MySQL database '{MYSQL_DATABASE}' on {MYSQL_HOST}:{MYSQL_PORT}")
            return
        except Exception as e:
            print(f"[DATABASE] Failed to initialize MySQL schema: {e}")

    # Fallback to SQLite
    DB_MODE = "SQLite (Local Fallback)"
    _mysql_available = False
    print(f"[DATABASE] MySQL not available at {MYSQL_HOST}:{MYSQL_PORT}. Active engine: SQLite ({SQLITE_PATH})")
    conn = get_sqlite_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            identifier TEXT NOT NULL,
            department TEXT DEFAULT 'Computer Science',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            faculty_id INTEGER NULL,
            faculty_name TEXT DEFAULT 'Faculty Administrator',
            title TEXT NOT NULL,
            subject TEXT NOT NULL,
            question_text TEXT NOT NULL,
            reference_answer TEXT NOT NULL,
            keywords TEXT NOT NULL,
            max_marks REAL DEFAULT 10.0,
            difficulty TEXT DEFAULT 'Medium',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            student_name TEXT NOT NULL,
            student_identifier TEXT NOT NULL,
            student_department TEXT DEFAULT 'Computer Science',
            question_id INTEGER NULL,
            question_title TEXT NOT NULL,
            student_answer TEXT NOT NULL,
            marks_obtained REAL NOT NULL,
            max_marks REAL NOT NULL,
            score_percentage REAL NOT NULL,
            rating TEXT NOT NULL,
            summary TEXT NOT NULL,
            remarks TEXT NOT NULL,
            strengths TEXT NOT NULL,
            improvements TEXT NOT NULL,
            suggestions TEXT NOT NULL,
            matched_keywords TEXT NOT NULL,
            missing_keywords TEXT NOT NULL,
            evaluation_engine TEXT DEFAULT 'Gemini AI',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    seed_defaults_sqlite(conn)
    conn.close()


def seed_defaults_mysql(conn):
    """Seed initial demo users and questions in MySQL if empty."""
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS cnt FROM users")
        if cur.fetchone()["cnt"] == 0:
            faculty_pw = hash_password("faculty123")
            student_pw = hash_password("student123")
            cur.execute("""
                INSERT INTO users (id, name, email, password_hash, role, identifier, department) VALUES
                (1, 'Dr. Evelyn Reed', 'faculty@demo.com', %s, 'faculty', 'FAC-8812', 'Computer Science & Engineering'),
                (2, 'Alex Morgan', 'student@demo.com', %s, 'student', 'CS2026-042', 'Computer Science & Engineering');
            """, (faculty_pw, student_pw))

        cur.execute("SELECT COUNT(*) AS cnt FROM questions")
        if cur.fetchone()["cnt"] == 0:
            q_data = [
                (1, 1, 'Dr. Evelyn Reed', 'Core Principles of OOP', 'Object Oriented Programming',
                 'Explain the four core principles of Object-Oriented Programming (OOP) and briefly describe their significance in software design.',
                 'The four core principles of Object-Oriented Programming are Encapsulation, Abstraction, Inheritance, and Polymorphism. Encapsulation binds together data and functions into a single unit (class) and restricts direct access to internal state, promoting data hiding and security. Abstraction hides complex implementation details and exposes only the essential features to the user, typically via interfaces and abstract classes. Inheritance enables a child class to inherit properties and behaviors from a parent class, facilitating code reusability and hierarchical organization. Polymorphism allows objects to take multiple forms and respond differently to the same method call, achieved through method overloading (compile-time) and method overriding (runtime).',
                 'encapsulation, abstraction, inheritance, polymorphism, code reusability, data hiding', 10.0, 'Medium'),
                (2, 1, 'Dr. Evelyn Reed', 'Database Normalization & 3NF', 'Database Management Systems',
                 'Define database normalization and explain the conditions required for a relation to be in Third Normal Form (3NF).',
                 'Database normalization is the process of structuring a relational database to minimize data redundancy and prevent insertion, update, and deletion anomalies. For a relation to achieve Third Normal Form (3NF), it must first satisfy Second Normal Form (2NF), meaning it is in 1NF and all non-key attributes are fully functionally dependent on the primary key. Second, every non-prime attribute in the relation must not be transitively dependent on any candidate key. In formal terms, for every non-trivial functional dependency X -> Y, either X is a superkey or Y is a prime attribute (part of a candidate key). Normalizing to 3NF ensures data integrity and storage efficiency.',
                 'normalization, 3nf, third normal form, 2nf, functional dependency, transitive dependency, superkey, prime attribute, data redundancy, anomalies', 10.0, 'Hard'),
                (3, 1, 'Dr. Evelyn Reed', 'Supervised vs Unsupervised Learning', 'Artificial Intelligence & ML',
                 'Distinguish between supervised and unsupervised machine learning paradigms, providing representative examples for each.',
                 'Supervised machine learning algorithms learn from labeled training datasets where input features are paired with ground-truth target outputs or class labels. The objective is to learn a mapping function from inputs to outputs to predict targets on unseen data. Core sub-types include classification (e.g., spam detection, image classification) and regression (e.g., house price forecasting). In contrast, unsupervised learning processes unlabeled datasets without explicit target supervisory signals. The algorithm identifies latent patterns, clustering structures, or intrinsic dimensional representations on its own. Common tasks include clustering (e.g., K-Means customer segmentation) and dimensionality reduction (e.g., Principal Component Analysis).',
                 'supervised learning, unsupervised learning, labeled data, unlabeled data, classification, regression, clustering, patterns, k-means, target output', 10.0, 'Easy')
            ]
            cur.executemany("""
                INSERT INTO questions (id, faculty_id, faculty_name, title, subject, question_text, reference_answer, keywords, max_marks, difficulty)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, q_data)


def seed_defaults_sqlite(conn):
    """Seed initial demo users and questions in SQLite if empty."""
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS cnt FROM users")
    if cur.fetchone()[0] == 0:
        faculty_pw = hash_password("faculty123")
        student_pw = hash_password("student123")
        cur.execute("""
            INSERT INTO users (id, name, email, password_hash, role, identifier, department) VALUES
            (1, 'Dr. Evelyn Reed', 'faculty@demo.com', ?, 'faculty', 'FAC-8812', 'Computer Science & Engineering'),
            (2, 'Alex Morgan', 'student@demo.com', ?, 'student', 'CS2026-042', 'Computer Science & Engineering')
        """, (faculty_pw, student_pw))

    cur.execute("SELECT COUNT(*) AS cnt FROM questions")
    if cur.fetchone()[0] == 0:
        q_data = [
            (1, 1, 'Dr. Evelyn Reed', 'Core Principles of OOP', 'Object Oriented Programming',
             'Explain the four core principles of Object-Oriented Programming (OOP) and briefly describe their significance in software design.',
             'The four core principles of Object-Oriented Programming are Encapsulation, Abstraction, Inheritance, and Polymorphism. Encapsulation binds together data and functions into a single unit (class) and restricts direct access to internal state, promoting data hiding and security. Abstraction hides complex implementation details and exposes only the essential features to the user, typically via interfaces and abstract classes. Inheritance enables a child class to inherit properties and behaviors from a parent class, facilitating code reusability and hierarchical organization. Polymorphism allows objects to take multiple forms and respond differently to the same method call, achieved through method overloading (compile-time) and method overriding (runtime).',
             'encapsulation, abstraction, inheritance, polymorphism, code reusability, data hiding', 10.0, 'Medium'),
            (2, 1, 'Dr. Evelyn Reed', 'Database Normalization & 3NF', 'Database Management Systems',
             'Define database normalization and explain the conditions required for a relation to be in Third Normal Form (3NF).',
             'Database normalization is the process of structuring a relational database to minimize data redundancy and prevent insertion, update, and deletion anomalies. For a relation to achieve Third Normal Form (3NF), it must first satisfy Second Normal Form (2NF), meaning it is in 1NF and all non-key attributes are fully functionally dependent on the primary key. Second, every non-prime attribute in the relation must not be transitively dependent on any candidate key. In formal terms, for every non-trivial functional dependency X -> Y, either X is a superkey or Y is a prime attribute (part of a candidate key). Normalizing to 3NF ensures data integrity and storage efficiency.',
             'normalization, 3nf, third normal form, 2nf, functional dependency, transitive dependency, superkey, prime attribute, data redundancy, anomalies', 10.0, 'Hard'),
            (3, 1, 'Dr. Evelyn Reed', 'Supervised vs Unsupervised Learning', 'Artificial Intelligence & ML',
             'Distinguish between supervised and unsupervised machine learning paradigms, providing representative examples for each.',
             'Supervised machine learning algorithms learn from labeled training datasets where input features are paired with ground-truth target outputs or class labels. The objective is to learn a mapping function from inputs to outputs to predict targets on unseen data. Core sub-types include classification (e.g., spam detection, image classification) and regression (e.g., house price forecasting). In contrast, unsupervised learning processes unlabeled datasets without explicit target supervisory signals. The algorithm identifies latent patterns, clustering structures, or intrinsic dimensional representations on its own. Common tasks include clustering (e.g., K-Means customer segmentation) and dimensionality reduction (e.g., Principal Component Analysis).',
             'supervised learning, unsupervised learning, labeled data, unlabeled data, classification, regression, clustering, patterns, k-means, target output', 10.0, 'Easy')
        ]
        cur.executemany("""
            INSERT INTO questions (id, faculty_id, faculty_name, title, subject, question_text, reference_answer, keywords, max_marks, difficulty)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, q_data)
    conn.commit()


def get_db_status() -> Dict[str, Any]:
    """Return current database connection status."""
    return {
        "mode": DB_MODE,
        "is_mysql": (DB_MODE == "MySQL"),
        "mysql_host": MYSQL_HOST,
        "mysql_port": MYSQL_PORT,
        "mysql_database": MYSQL_DATABASE,
        "sqlite_path": SQLITE_PATH if DB_MODE != "MySQL" else None
    }


# ======================================================================
# User Authentication & Profile Queries
# ======================================================================

def find_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Look up user by email."""
    if DB_MODE == "MySQL":
        conn = get_mysql_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE email = %s", (email.strip().lower(),))
            user = cur.fetchone()
        conn.close()
        return user
    else:
        conn = get_sqlite_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = ?", (email.strip().lower(),))
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None


def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Look up user by ID."""
    if DB_MODE == "MySQL":
        conn = get_mysql_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cur.fetchone()
        conn.close()
        return user
    else:
        conn = get_sqlite_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None


def create_user(name: str, email: str, password_raw: str, role: str, identifier: str, department: str = "Computer Science") -> Dict[str, Any]:
    """Register a new student or faculty user."""
    pw_hash = hash_password(password_raw)
    email_clean = email.strip().lower()

    if DB_MODE == "MySQL":
        conn = get_mysql_conn()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (name, email, password_hash, role, identifier, department)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name.strip(), email_clean, pw_hash, role.strip().lower(), identifier.strip(), department.strip()))
            user_id = cur.lastrowid
        conn.close()
    else:
        conn = get_sqlite_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO users (name, email, password_hash, role, identifier, department)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name.strip(), email_clean, pw_hash, role.strip().lower(), identifier.strip(), department.strip()))
        user_id = cur.lastrowid
        conn.commit()
        conn.close()

    return get_user_by_id(user_id)


# ======================================================================
# Questions CRUD
# ======================================================================

def get_all_questions() -> List[Dict[str, Any]]:
    """Retrieve all available questions."""
    if DB_MODE == "MySQL":
        conn = get_mysql_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM questions ORDER BY id DESC")
            rows = cur.fetchall()
        conn.close()
        return rows
    else:
        conn = get_sqlite_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM questions ORDER BY id DESC")
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows


def get_question_by_id(question_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve a single question by ID."""
    if DB_MODE == "MySQL":
        conn = get_mysql_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM questions WHERE id = %s", (question_id,))
            q = cur.fetchone()
        conn.close()
        return q
    else:
        conn = get_sqlite_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM questions WHERE id = ?", (question_id,))
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None


def create_question(faculty_id: int, faculty_name: str, title: str, subject: str, question_text: str, reference_answer: str, keywords: str, max_marks: float = 10.0, difficulty: str = "Medium") -> Dict[str, Any]:
    """Create a new faculty question."""
    if DB_MODE == "MySQL":
        conn = get_mysql_conn()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO questions (faculty_id, faculty_name, title, subject, question_text, reference_answer, keywords, max_marks, difficulty)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (faculty_id, faculty_name, title.strip(), subject.strip(), question_text.strip(), reference_answer.strip(), keywords.strip(), max_marks, difficulty.strip()))
            qid = cur.lastrowid
        conn.close()
    else:
        conn = get_sqlite_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO questions (faculty_id, faculty_name, title, subject, question_text, reference_answer, keywords, max_marks, difficulty)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (faculty_id, faculty_name, title.strip(), subject.strip(), question_text.strip(), reference_answer.strip(), keywords.strip(), max_marks, difficulty.strip()))
        qid = cur.lastrowid
        conn.commit()
        conn.close()

    return get_question_by_id(qid)


def delete_question(question_id: int) -> bool:
    """Delete a question by ID."""
    if DB_MODE == "MySQL":
        conn = get_mysql_conn()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM questions WHERE id = %s", (question_id,))
        conn.close()
        return True
    else:
        conn = get_sqlite_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM questions WHERE id = ?", (question_id,))
        conn.commit()
        conn.close()
        return True


# ======================================================================
# Evaluations / Submissions Queries
# ======================================================================

def save_evaluation(
    student_id: int,
    student_name: str,
    student_identifier: str,
    student_department: str,
    question_id: Optional[int],
    question_title: str,
    student_answer: str,
    marks_obtained: float,
    max_marks: float,
    score_percentage: float,
    rating: str,
    summary: str,
    remarks: str,
    strengths: List[str],
    improvements: List[str],
    suggestions: List[str],
    matched_keywords: List[str],
    missing_keywords: List[str],
    evaluation_engine: str = "Gemini AI"
) -> int:
    """Store complete student evaluation record."""
    strengths_json = json.dumps(strengths)
    improvements_json = json.dumps(improvements)
    suggestions_json = json.dumps(suggestions)
    matched_kw_str = ", ".join(matched_keywords) if isinstance(matched_keywords, list) else str(matched_keywords)
    missing_kw_str = ", ".join(missing_keywords) if isinstance(missing_keywords, list) else str(missing_keywords)

    if DB_MODE == "MySQL":
        conn = get_mysql_conn()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO evaluations (
                    student_id, student_name, student_identifier, student_department,
                    question_id, question_title, student_answer, marks_obtained, max_marks,
                    score_percentage, rating, summary, remarks, strengths, improvements,
                    suggestions, matched_keywords, missing_keywords, evaluation_engine
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                student_id, student_name, student_identifier, student_department,
                question_id, question_title, student_answer, marks_obtained, max_marks,
                score_percentage, rating, summary, remarks, strengths_json, improvements_json,
                suggestions_json, matched_kw_str, missing_kw_str, evaluation_engine
            ))
            eval_id = cur.lastrowid
        conn.close()
    else:
        conn = get_sqlite_conn()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO evaluations (
                student_id, student_name, student_identifier, student_department,
                question_id, question_title, student_answer, marks_obtained, max_marks,
                score_percentage, rating, summary, remarks, strengths, improvements,
                suggestions, matched_keywords, missing_keywords, evaluation_engine
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            student_id, student_name, student_identifier, student_department,
            question_id, question_title, student_answer, marks_obtained, max_marks,
            score_percentage, rating, summary, remarks, strengths_json, improvements_json,
            suggestions_json, matched_kw_str, missing_kw_str, evaluation_engine
        ))
        eval_id = cur.lastrowid
        conn.commit()
        conn.close()

    return eval_id


def get_evaluations_by_student(student_id: int) -> List[Dict[str, Any]]:
    """Retrieve all evaluations submitted by a student."""
    if DB_MODE == "MySQL":
        conn = get_mysql_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM evaluations WHERE student_id = %s ORDER BY id DESC", (student_id,))
            rows = cur.fetchall()
        conn.close()
    else:
        conn = get_sqlite_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM evaluations WHERE student_id = ? ORDER BY id DESC", (student_id,))
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()

    for r in rows:
        try:
            r["strengths"] = json.loads(r.get("strengths") or "[]")
            r["improvements"] = json.loads(r.get("improvements") or "[]")
            r["suggestions"] = json.loads(r.get("suggestions") or "[]")
        except Exception:
            pass
    return rows


def get_all_evaluations() -> List[Dict[str, Any]]:
    """Retrieve all student evaluations for Faculty view."""
    if DB_MODE == "MySQL":
        conn = get_mysql_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM evaluations ORDER BY id DESC")
            rows = cur.fetchall()
        conn.close()
    else:
        conn = get_sqlite_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM evaluations ORDER BY id DESC")
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()

    for r in rows:
        try:
            r["strengths"] = json.loads(r.get("strengths") or "[]")
            r["improvements"] = json.loads(r.get("improvements") or "[]")
            r["suggestions"] = json.loads(r.get("suggestions") or "[]")
        except Exception:
            pass
    return rows


def get_evaluation_by_id(eval_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve single detailed evaluation."""
    if DB_MODE == "MySQL":
        conn = get_mysql_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM evaluations WHERE id = %s", (eval_id,))
            row = cur.fetchone()
        conn.close()
    else:
        conn = get_sqlite_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM evaluations WHERE id = ?", (eval_id,))
        r = cur.fetchone()
        row = dict(r) if r else None
        conn.close()

    if row:
        try:
            row["strengths"] = json.loads(row.get("strengths") or "[]")
            row["improvements"] = json.loads(row.get("improvements") or "[]")
            row["suggestions"] = json.loads(row.get("suggestions") or "[]")
        except Exception:
            pass
    return row


def get_student_stats(student_id: int) -> Dict[str, Any]:
    """Compute performance stats for a student."""
    evals = get_evaluations_by_student(student_id)
    if not evals:
        return {
            "total_submissions": 0,
            "average_score": 0.0,
            "highest_score": 0.0,
            "grade": "N/A"
        }
    percentages = [float(e.get("score_percentage", 0)) for e in evals]
    avg = sum(percentages) / len(percentages)
    highest = max(percentages)
    if avg >= 85:
        grade = "A+ (Excellent)"
    elif avg >= 70:
        grade = "A (Very Good)"
    elif avg >= 55:
        grade = "B (Satisfactory)"
    else:
        grade = "C (Needs Improvement)"

    return {
        "total_submissions": len(evals),
        "average_score": round(avg, 1),
        "highest_score": round(highest, 1),
        "grade": grade
    }


def get_faculty_analytics() -> Dict[str, Any]:
    """Compute aggregate analytics for the faculty dashboard."""
    questions = get_all_questions()
    evals = get_all_evaluations()

    total_submissions = len(evals)
    total_questions = len(questions)

    if total_submissions > 0:
        percentages = [float(e.get("score_percentage", 0)) for e in evals]
        class_avg = round(sum(percentages) / total_submissions, 1)
        highest_score = round(max(percentages), 1)
        lowest_score = round(min(percentages), 1)
    else:
        class_avg = 0.0
        highest_score = 0.0
        lowest_score = 0.0

    # Count distinct students
    student_ids = set(e["student_id"] for e in evals)

    return {
        "total_questions": total_questions,
        "total_submissions": total_submissions,
        "total_students": len(student_ids),
        "class_average": class_avg,
        "highest_score": highest_score,
        "lowest_score": lowest_score
    }
