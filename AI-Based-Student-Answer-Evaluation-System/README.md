# AI-Based Student Answer Evaluation System (v2.0)

A full-stack, enterprise-grade academic evaluation platform powered by **Google Gemini AI** and **MySQL Database**. Featuring dedicated **Student** and **Faculty** portals, comprehensive academic profiling, automated conceptual grading, examiner remarks, pedagogical suggestions, and data storage.

---

## 🌟 What's New in Version 2.0

- **Google Gemini AI Integration**:
  - Leverages Google Gemini 3.5 Flash / Flash Lite for automated semantic grading.
  - Automatically compares student answers against model answers, rubric points, and key concepts.
  - Provides examiner remarks, identified strengths, critical technical improvements, and actionable study suggestions.
  - Automated fallback: if network or quota limitations occur, automatically failovers to the built-in local NLP engine.
- **Role-Based Portals**:
  - **Student Portal**:
    - Complete Student Profile (Name, Roll Number, Department, Submissions Count, Average Score, Performance Grade).
    - Assessment Interface: Browse questions, view model answers, draft answers, and request Gemini AI evaluations.
    - My Evaluation History: Persistent score ledger of all submitted assessments.
  - **Faculty Portal**:
    - Complete Faculty Profile (Name, Faculty ID, Department, Analytics).
    - Student Submissions Data Table: Real-time table of all student scores, marks, remarks, and evaluation timestamps.
    - CSV Grade Export: Download complete student grades as a `.csv` report.
    - Question Bank Management: Form to create and publish new assessment questions with model answers, maximum marks, difficulty, and expected keywords.
- **MySQL Database Integration**:
  - Persistent relational schema (`users`, `questions`, `evaluations`).
  - Seamless dual-engine database: Connects to MySQL on `127.0.0.1:3306`; if MySQL is offline, automatically activates a local SQLite fallback (`student_eval.db`) so the app never crashes!
  - Pre-seeded with ready-to-test Demo Student and Demo Faculty accounts.

---

## 🔑 Configured API Credentials & Settings

Configuration is managed in [`.env`](file:///c:/Users/LENOVO/Downloads/ai/AI-Based-Student-Answer-Evaluation-System/.env):

```env
# Gemini AI Configuration
GEMINI_API_KEY=AQ.Ab8RN6IGJ-0X2pLSQQz7dUIMa3FEuyPo--H25jwSYd987gPyqQ
GEMINI_PROJECT_NAME=projects/781869000408
GEMINI_PROJECT_NUMBER=781869000408
GEMINI_PRIMARY_MODEL=gemini-3.5-flash-lite
GEMINI_FALLBACK_MODEL=gemini-3.5-flash

# MySQL Database Configuration
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DATABASE=student_eval_db
```

---

## ⚡ Default Demo Credentials

You can use the 1-click **⚡ Quick Demo Login** buttons on the sign-in page, or log in manually:

| Portal | Email | Password | Identifier | Department |
| :--- | :--- | :--- | :--- | :--- |
| **Student** | `student@demo.com` | `student123` | `CS2026-042` | Computer Science & Engineering |
| **Faculty** | `faculty@demo.com` | `faculty123` | `FAC-8812` | Computer Science & Engineering |

---

## 🗄️ MySQL Database Setup (Optional)

1. Start your MySQL service (e.g., via **XAMPP**, **WampServer**, or Windows Services).
2. The application will **automatically create** the database `student_eval_db` and all tables on startup.
3. If you prefer to manually import the schema into phpMyAdmin or MySQL CLI, use [`schema.sql`](file:///c:/Users/LENOVO/Downloads/ai/AI-Based-Student-Answer-Evaluation-System/schema.sql):
   ```bash
   mysql -u root -p < schema.sql
   ```

---

## 🚀 Running the Project Locally

The server is currently running in the background.

- **Open in Browser**: [http://127.0.0.1:5000](http://127.0.0.1:5000)
- **Restart or Run via Launcher**:
  ```powershell
  cd c:\Users\LENOVO\Downloads\ai\AI-Based-Student-Answer-Evaluation-System
  .\run.bat
  ```
- **Run via Python Virtual Environment**:
  ```powershell
  cd c:\Users\LENOVO\Downloads\ai\AI-Based-Student-Answer-Evaluation-System
  .\.venv\Scripts\python.exe app.py
  ```
