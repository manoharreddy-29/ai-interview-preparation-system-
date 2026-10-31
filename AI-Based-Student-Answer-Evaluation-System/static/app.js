/**
 * AI-Based Student Answer Evaluation System
 * Frontend Application Controller with Gemini AI & MySQL Support
 */

document.addEventListener("DOMContentLoaded", () => {
  // Application State
  const state = {
    user: null,              // Active logged-in user object
    role: "student",         // Current portal role: 'student' | 'faculty'
    authMode: "login",       // 'login' | 'register'
    questions: [],           // All questions loaded from backend
    activeQuestion: null,    // Currently selected question object
    studentHistory: [],      // Submissions for student
    facultySubmissions: [],  // All submissions for faculty
  };

  // Sample answers for predefined questions to test with 1-click
  const SAMPLE_ANSWERS = {
    1: "The four core principles of Object-Oriented Programming are Encapsulation, Abstraction, Inheritance, and Polymorphism. Encapsulation bundles data and methods into a single class to ensure data hiding and security. Abstraction hides internal implementation complexities while presenting a clean interface. Inheritance allows a derived class to reuse code and behaviors from a base class. Polymorphism allows functions to exhibit different behaviors depending on the object invoking them.",
    2: "Database normalization is the systematic technique of organizing relational database schemas to eliminate update anomalies and minimize redundant data storage. A relation is in Third Normal Form (3NF) if it is already in 2NF, and no non-prime attribute possesses a transitive dependency on the primary key. In other words, for every functional dependency X -> Y, either X is a superkey or Y is a prime attribute.",
    3: "Supervised machine learning algorithms learn from labeled training sets where ground truth outputs are provided, allowing them to map inputs to targets for classification or regression tasks (e.g. spam filters). In contrast, unsupervised learning processes unlabeled datasets without explicit target labels to discover latent clusters and data patterns (e.g. K-Means clustering)."
  };

  // ====================================================================
  // DOM Elements
  // ====================================================================
  // Header & Badges
  const aiModelBadge = document.getElementById("aiModelBadge");
  const aiModelText = document.getElementById("aiModelText");
  const dbStatusBadge = document.getElementById("dbStatusBadge");
  const dbDot = document.getElementById("dbDot");
  const dbStatusText = document.getElementById("dbStatusText");
  const userSessionChip = document.getElementById("userSessionChip");
  const userAvatarIcon = document.getElementById("userAvatarIcon");
  const sessionUserName = document.getElementById("sessionUserName");
  const sessionUserRole = document.getElementById("sessionUserRole");
  const logoutBtn = document.getElementById("logoutBtn");
  const toastNotification = document.getElementById("toastNotification");

  // Auth Section
  const authSection = document.getElementById("authSection");
  const tabRoleStudent = document.getElementById("tabRoleStudent");
  const tabRoleFaculty = document.getElementById("tabRoleFaculty");
  const authModeLoginBtn = document.getElementById("authModeLoginBtn");
  const authModeRegisterBtn = document.getElementById("authModeRegisterBtn");
  const authTitle = document.getElementById("authTitle");
  const authSubtitle = document.getElementById("authSubtitle");
  const loginForm = document.getElementById("loginForm");
  const registerForm = document.getElementById("registerForm");
  const lblIdentifier = document.getElementById("lblIdentifier");
  const demoStudentBtn = document.getElementById("demoStudentBtn");
  const demoFacultyBtn = document.getElementById("demoFacultyBtn");

  // Portals
  const studentPortalSection = document.getElementById("studentPortalSection");
  const facultyPortalSection = document.getElementById("facultyPortalSection");

  // Student Portal
  const questionSelect = document.getElementById("questionSelect");
  const qSubjectBadge = document.getElementById("qSubjectBadge");
  const qDifficultyBadge = document.getElementById("qDifficultyBadge");
  const qMaxMarksBadge = document.getElementById("qMaxMarksBadge");
  const qTitleDisplay = document.getElementById("qTitleDisplay");
  const qTextDisplay = document.getElementById("qTextDisplay");
  const toggleRefAnswerBtn = document.getElementById("toggleRefAnswerBtn");
  const refAnswerContainer = document.getElementById("refAnswerContainer");
  const refAnswerText = document.getElementById("refAnswerText");
  const expectedKeywordsTags = document.getElementById("expectedKeywordsTags");
  const studentAnswerInput = document.getElementById("studentAnswerInput");
  const wordCountBadge = document.getElementById("wordCountBadge");
  const charCountBadge = document.getElementById("charCountBadge");
  const loadSampleAnswerBtn = document.getElementById("loadSampleAnswerBtn");
  const clearAnswerBtn = document.getElementById("clearAnswerBtn");
  const evaluateBtn = document.getElementById("evaluateBtn");
  const evalSpinner = document.getElementById("evalSpinner");
  const evalBtnText = document.getElementById("evalBtnText");

  // Evaluation Results
  const resultsEmptyState = document.getElementById("resultsEmptyState");
  const resultsContent = document.getElementById("resultsContent");
  const resMarksObtained = document.getElementById("resMarksObtained");
  const resMaxMarks = document.getElementById("resMaxMarks");
  const resScorePct = document.getElementById("resScorePct");
  const resRatingBadge = document.getElementById("resRatingBadge");
  const resEngineBadge = document.getElementById("resEngineBadge");
  const resRemarksText = document.getElementById("resRemarksText");
  const resStrengthsList = document.getElementById("resStrengthsList");
  const resImprovementsList = document.getElementById("resImprovementsList");
  const resSuggestionsList = document.getElementById("resSuggestionsList");
  const resMatchedKeywords = document.getElementById("resMatchedKeywords");
  const resMissingKeywords = document.getElementById("resMissingKeywords");

  // Student Profile & History
  const profStudentName = document.getElementById("profStudentName");
  const profStudentEmail = document.getElementById("profStudentEmail");
  const profStudentRoll = document.getElementById("profStudentRoll");
  const profStudentDept = document.getElementById("profStudentDept");
  const profStudentJoined = document.getElementById("profStudentJoined");
  const statSubmissionsCount = document.getElementById("statSubmissionsCount");
  const statAverageScore = document.getElementById("statAverageScore");
  const statHighestScore = document.getElementById("statHighestScore");
  const statOverallGrade = document.getElementById("statOverallGrade");
  const studentHistoryTableBody = document.getElementById("studentHistoryTableBody");
  const refreshStudentHistoryBtn = document.getElementById("refreshStudentHistoryBtn");

  // Faculty Portal
  const facultySubmissionsTableBody = document.getElementById("facultySubmissionsTableBody");
  const submissionsSearchInput = document.getElementById("submissionsSearchInput");
  const refreshSubmissionsBtn = document.getElementById("refreshSubmissionsBtn");
  const exportCsvBtn = document.getElementById("exportCsvBtn");
  const createQuestionForm = document.getElementById("createQuestionForm");
  const facultyQuestionsList = document.getElementById("facultyQuestionsList");
  const profFacultyName = document.getElementById("profFacultyName");
  const profFacultyEmail = document.getElementById("profFacultyEmail");
  const profFacultyId = document.getElementById("profFacultyId");
  const profFacultyDept = document.getElementById("profFacultyDept");
  const facStatQuestionsCount = document.getElementById("facStatQuestionsCount");
  const facStatSubmissionsCount = document.getElementById("facStatSubmissionsCount");
  const facStatStudentsCount = document.getElementById("facStatStudentsCount");
  const facStatClassAverage = document.getElementById("facStatClassAverage");

  // Modal
  const reportModal = document.getElementById("reportModal");
  const modalReportTitle = document.getElementById("modalReportTitle");
  const modalReportBody = document.getElementById("modalReportBody");
  const closeReportModalBtn = document.getElementById("closeReportModalBtn");


  // ====================================================================
  // Helper: Toast Notifications
  // ====================================================================
  function showToast(message, type = "success") {
    toastNotification.textContent = message;
    toastNotification.className = `toast-notification ${type}`;
    toastNotification.classList.remove("hidden");
    setTimeout(() => {
      toastNotification.classList.add("hidden");
    }, 4000);
  }


  // ====================================================================
  // 1. Initial System Status Check
  // ====================================================================
  async function checkSystemStatus() {
    try {
      const res = await fetch("/api/system/status");
      const data = await res.json();
      if (data.gemini && data.gemini.configured) {
        aiModelText.textContent = `✨ ${data.gemini.primary_model || "Gemini AI"}`;
      }
      if (data.database) {
        if (data.database.is_mysql) {
          dbStatusText.textContent = `🟢 MySQL: ${data.database.mysql_database}`;
          dbDot.className = "status-dot green";
        } else {
          dbStatusText.textContent = `🟡 Local DB: SQLite`;
          dbDot.className = "status-dot yellow";
        }
      }
    } catch (err) {
      console.warn("Could not check system status:", err);
      dbStatusText.textContent = "Offline Mode";
    }
  }


  // ====================================================================
  // 2. Authentication UI & Logic
  // ====================================================================
  function updateAuthUI() {
    if (state.role === "student") {
      tabRoleStudent.classList.add("active");
      tabRoleFaculty.classList.remove("active");
      authTitle.textContent = state.authMode === "login" ? "Student Portal Login" : "Student Registration";
      authSubtitle.textContent = state.authMode === "login"
        ? "Sign in to access your assessments, submit answers, and receive Gemini AI feedback."
        : "Register your student profile with roll number and department.";
      lblIdentifier.textContent = "Student Roll Number";
      document.getElementById("regIdentifier").placeholder = "e.g. CS2026-042";
    } else {
      tabRoleFaculty.classList.add("active");
      tabRoleStudent.classList.remove("active");
      authTitle.textContent = state.authMode === "login" ? "Faculty Portal Login" : "Faculty Registration";
      authSubtitle.textContent = state.authMode === "login"
        ? "Sign in to review student performance data, scores, and manage question bank."
        : "Register your faculty account with faculty ID and department.";
      lblIdentifier.textContent = "Faculty Employee ID";
      document.getElementById("regIdentifier").placeholder = "e.g. FAC-8812";
    }

    if (state.authMode === "login") {
      authModeLoginBtn.classList.add("active");
      authModeRegisterBtn.classList.remove("active");
      loginForm.classList.remove("hidden");
      registerForm.classList.add("hidden");
    } else {
      authModeRegisterBtn.classList.add("active");
      authModeLoginBtn.classList.remove("active");
      registerForm.classList.remove("hidden");
      loginForm.classList.add("hidden");
    }
  }

  tabRoleStudent.addEventListener("click", () => {
    state.role = "student";
    updateAuthUI();
  });

  tabRoleFaculty.addEventListener("click", () => {
    state.role = "faculty";
    updateAuthUI();
  });

  authModeLoginBtn.addEventListener("click", () => {
    state.authMode = "login";
    updateAuthUI();
  });

  authModeRegisterBtn.addEventListener("click", () => {
    state.authMode = "register";
    updateAuthUI();
  });

  // Fast Demo Login
  demoStudentBtn.addEventListener("click", () => {
    document.getElementById("loginEmail").value = "student@demo.com";
    document.getElementById("loginPassword").value = "student123";
    state.role = "student";
    updateAuthUI();
    loginForm.dispatchEvent(new Event("submit"));
  });

  demoFacultyBtn.addEventListener("click", () => {
    document.getElementById("loginEmail").value = "faculty@demo.com";
    document.getElementById("loginPassword").value = "faculty123";
    state.role = "faculty";
    updateAuthUI();
    loginForm.dispatchEvent(new Event("submit"));
  });

  // Handle Login Form Submit
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("loginEmail").value.trim();
    const password = document.getElementById("loginPassword").value.trim();

    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, role: state.role })
      });
      const data = await res.json();
      if (!data.success) {
        showToast(data.error || "Login failed.", "error");
        return;
      }

      setUserSession(data.user);
      showToast(data.message || "Logged in successfully!", "success");
    } catch (err) {
      showToast("Server connection error during login.", "error");
    }
  });

  // Handle Registration Form Submit
  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = document.getElementById("regName").value.trim();
    const email = document.getElementById("regEmail").value.trim();
    const password = document.getElementById("regPassword").value.trim();
    const identifier = document.getElementById("regIdentifier").value.trim();
    const department = document.getElementById("regDepartment").value.trim();

    try {
      const res = await fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password, role: state.role, identifier, department })
      });
      const data = await res.json();
      if (!data.success) {
        showToast(data.error || "Registration failed.", "error");
        return;
      }

      setUserSession(data.user);
      showToast(data.message || "Account created successfully!", "success");
    } catch (err) {
      showToast("Server connection error during registration.", "error");
    }
  });

  // Set Session and Render Portal
  function setUserSession(user) {
    state.user = user;
    localStorage.setItem("eval_user", JSON.stringify(user));

    // Update session header pill
    sessionUserName.textContent = user.name;
    sessionUserRole.textContent = user.role.toUpperCase();
    userAvatarIcon.textContent = user.role === "faculty" ? "👨‍🏫" : "👨‍🎓";
    userSessionChip.classList.remove("hidden");

    // Hide auth section
    authSection.classList.add("hidden");

    // Show appropriate portal
    if (user.role === "faculty") {
      studentPortalSection.classList.add("hidden");
      facultyPortalSection.classList.remove("hidden");
      initFacultyPortal();
    } else {
      facultyPortalSection.classList.add("hidden");
      studentPortalSection.classList.remove("hidden");
      initStudentPortal();
    }
  }

  // Logout Handler
  logoutBtn.addEventListener("click", () => {
    state.user = null;
    localStorage.removeItem("eval_user");
    userSessionChip.classList.add("hidden");
    studentPortalSection.classList.add("hidden");
    facultyPortalSection.classList.add("hidden");
    authSection.classList.remove("hidden");
    showToast("You have been signed out.", "success");
  });


  // ====================================================================
  // 3. Navigation Tab Switching (Student & Faculty Portals)
  // ====================================================================
  document.querySelectorAll(".portal-nav-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      const parentNav = tab.parentElement;
      parentNav.querySelectorAll(".portal-nav-tab").forEach(t => t.classList.remove("active"));
      tab.classList.add("active");

      const targetTabId = tab.getAttribute("data-tab");
      const portal = parentNav.closest(".portal-section");
      portal.querySelectorAll(".portal-tab-content").forEach(c => c.classList.remove("active"));

      if (targetTabId === "student-assessments") {
        document.getElementById("tabStudentAssessments").classList.add("active");
      } else if (targetTabId === "student-profile") {
        document.getElementById("tabStudentProfile").classList.add("active");
        loadStudentProfile();
      } else if (targetTabId === "student-history") {
        document.getElementById("tabStudentHistory").classList.add("active");
        loadStudentHistory();
      } else if (targetTabId === "faculty-submissions") {
        document.getElementById("tabFacultySubmissions").classList.add("active");
        loadFacultySubmissions();
      } else if (targetTabId === "faculty-questions") {
        document.getElementById("tabFacultyQuestions").classList.add("active");
        loadFacultyQuestions();
      } else if (targetTabId === "faculty-profile") {
        document.getElementById("tabFacultyProfile").classList.add("active");
        loadFacultyProfile();
      }
    });
  });


  // ====================================================================
  // 4. Student Portal Implementation
  // ====================================================================
  async function initStudentPortal() {
    await loadQuestions();
    loadStudentProfile();
  }

  async function loadQuestions() {
    try {
      const res = await fetch("/api/student/questions");
      const data = await res.json();
      if (data.success && data.questions) {
        state.questions = data.questions;
        populateQuestionDropdown(data.questions);
      }
    } catch (err) {
      console.error("Error loading questions:", err);
    }
  }

  function populateQuestionDropdown(questions) {
    questionSelect.innerHTML = "";
    if (questions.length === 0) {
      questionSelect.innerHTML = "<option value='' disabled>No questions available</option>";
      return;
    }

    questions.forEach((q, idx) => {
      const opt = document.createElement("option");
      opt.value = q.id;
      opt.textContent = `${q.title} (${q.subject} - Max: ${q.max_marks}m)`;
      questionSelect.appendChild(opt);
    });

    // Select first question
    selectQuestion(questions[0].id);
  }

  questionSelect.addEventListener("change", (e) => {
    selectQuestion(e.target.value);
  });

  function selectQuestion(qid) {
    const q = state.questions.find(item => String(item.id) === String(qid));
    if (!q) return;

    state.activeQuestion = q;
    qSubjectBadge.textContent = q.subject || "General";
    qDifficultyBadge.textContent = q.difficulty || "Medium";
    qMaxMarksBadge.textContent = `Max Marks: ${q.max_marks}`;
    qTitleDisplay.textContent = q.title;
    qTextDisplay.textContent = q.question_text;
    refAnswerText.textContent = q.reference_answer;

    // Render keyword tags
    expectedKeywordsTags.innerHTML = "";
    const rawKw = q.keywords || "";
    const kwList = rawKw.split(",").map(k => k.trim()).filter(Boolean);
    kwList.forEach(k => {
      const span = document.createElement("span");
      span.className = "tag";
      span.textContent = k;
      expectedKeywordsTags.appendChild(span);
    });
  }

  // Toggle Reference Answer Accordion
  toggleRefAnswerBtn.addEventListener("click", () => {
    refAnswerContainer.classList.toggle("hidden");
    const arrow = toggleRefAnswerBtn.querySelector(".accordion-arrow");
    arrow.textContent = refAnswerContainer.classList.contains("hidden") ? "▼" : "▲";
  });

  // Live Word / Char Counter
  studentAnswerInput.addEventListener("input", () => {
    const text = studentAnswerInput.value.trim();
    const words = text ? text.split(/\s+/).filter(Boolean).length : 0;
    const chars = studentAnswerInput.value.length;
    wordCountBadge.textContent = `${words} words`;
    charCountBadge.textContent = `${chars} chars`;
  });

  // Load Sample Answer
  loadSampleAnswerBtn.addEventListener("click", () => {
    if (!state.activeQuestion) return;
    const sample = SAMPLE_ANSWERS[state.activeQuestion.id] || state.activeQuestion.reference_answer;
    studentAnswerInput.value = sample;
    studentAnswerInput.dispatchEvent(new Event("input"));
    showToast("Sample model response loaded.", "success");
  });

  // Clear Answer
  clearAnswerBtn.addEventListener("click", () => {
    studentAnswerInput.value = "";
    studentAnswerInput.dispatchEvent(new Event("input"));
  });

  // Evaluate Answer with Gemini AI
  evaluateBtn.addEventListener("click", async () => {
    const answer = studentAnswerInput.value.trim();
    if (!answer) {
      showToast("Please enter an answer before requesting evaluation.", "error");
      return;
    }
    if (!state.activeQuestion) {
      showToast("Please select a question to evaluate.", "error");
      return;
    }

    // Set Loading State
    evaluateBtn.disabled = true;
    evalSpinner.classList.remove("hidden");
    evalBtnText.textContent = "Gemini AI Evaluating...";

    try {
      const payload = {
        student_id: state.user.id,
        question_id: state.activeQuestion.id,
        student_answer: answer
      };

      const res = await fetch("/api/student/evaluate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();

      if (!data.success) {
        showToast(data.error || "Evaluation failed.", "error");
        return;
      }

      displayEvaluationResult(data.evaluation);
      showToast("Evaluation complete with marks & examiner remarks!", "success");
    } catch (err) {
      showToast("Evaluation failed due to network error.", "error");
    } finally {
      evaluateBtn.disabled = false;
      evalSpinner.classList.add("hidden");
      evalBtnText.textContent = "🚀 Evaluate Answer with Gemini AI";
    }
  });

  function displayEvaluationResult(ev) {
    resultsEmptyState.classList.add("hidden");
    resultsContent.classList.remove("hidden");

    resMarksObtained.textContent = ev.marks_obtained;
    resMaxMarks.textContent = `/ ${ev.max_marks}`;
    resScorePct.textContent = `${ev.score_percentage}%`;
    resRatingBadge.textContent = ev.rating || "Evaluated";
    resEngineBadge.textContent = `✨ ${ev.evaluation_engine || "Gemini AI"}`;
    resRemarksText.textContent = ev.remarks || ev.summary || "Good effort.";

    // Strengths
    resStrengthsList.innerHTML = "";
    (ev.strengths || []).forEach(s => {
      const li = document.createElement("li");
      li.textContent = s;
      resStrengthsList.appendChild(li);
    });
    if (!ev.strengths || ev.strengths.length === 0) {
      resStrengthsList.innerHTML = "<li>No specific strengths identified.</li>";
    }

    // Improvements
    resImprovementsList.innerHTML = "";
    (ev.improvements || []).forEach(imp => {
      const li = document.createElement("li");
      li.textContent = imp;
      resImprovementsList.appendChild(li);
    });
    if (!ev.improvements || ev.improvements.length === 0) {
      resImprovementsList.innerHTML = "<li>Great job! No major conceptual gaps noted.</li>";
    }

    // Suggestions
    resSuggestionsList.innerHTML = "";
    (ev.suggestions || []).forEach(sug => {
      const li = document.createElement("li");
      li.textContent = sug;
      resSuggestionsList.appendChild(li);
    });
    if (!ev.suggestions || ev.suggestions.length === 0) {
      resSuggestionsList.innerHTML = "<li>Review reference model answer to score 100%.</li>";
    }

    // Keywords
    resMatchedKeywords.innerHTML = "";
    (ev.matched_keywords || []).forEach(k => {
      const tag = document.createElement("span");
      tag.className = "tag tag-matched";
      tag.textContent = `✓ ${k}`;
      resMatchedKeywords.appendChild(tag);
    });
    if (!ev.matched_keywords || ev.matched_keywords.length === 0) {
      resMatchedKeywords.innerHTML = "<span class='text-muted'>None detected</span>";
    }

    resMissingKeywords.innerHTML = "";
    (ev.missing_keywords || []).forEach(k => {
      const tag = document.createElement("span");
      tag.className = "tag tag-missing";
      tag.textContent = `✗ ${k}`;
      resMissingKeywords.appendChild(tag);
    });
    if (!ev.missing_keywords || ev.missing_keywords.length === 0) {
      resMissingKeywords.innerHTML = "<span class='text-muted'>All key concepts covered!</span>";
    }

    // Scroll smoothly to results
    resultsContent.scrollIntoView({ behavior: "smooth" });
  }

  // Load Student Profile & Stats
  async function loadStudentProfile() {
    if (!state.user) return;
    profStudentName.textContent = state.user.name;
    profStudentEmail.textContent = state.user.email;
    profStudentRoll.textContent = state.user.identifier;
    profStudentDept.textContent = state.user.department || "Computer Science";
    profStudentJoined.textContent = state.user.created_at ? state.user.created_at.split(" ")[0] : "Active";

    try {
      const res = await fetch(`/api/auth/profile?user_id=${state.user.id}`);
      const data = await res.json();
      if (data.success && data.stats) {
        statSubmissionsCount.textContent = data.stats.total_submissions;
        statAverageScore.textContent = `${data.stats.average_score}%`;
        statHighestScore.textContent = `${data.stats.highest_score}%`;
        statOverallGrade.textContent = data.stats.grade;
      }
    } catch (err) {
      console.warn("Could not load student stats:", err);
    }
  }

  // Load Student History
  async function loadStudentHistory() {
    if (!state.user) return;
    try {
      const res = await fetch(`/api/student/evaluations?student_id=${state.user.id}`);
      const data = await res.json();
      if (!data.success) return;

      state.studentHistory = data.evaluations;
      studentHistoryTableBody.innerHTML = "";

      if (data.evaluations.length === 0) {
        studentHistoryTableBody.innerHTML = `<tr><td colspan="7" class="text-center text-muted">No assessments completed yet.</td></tr>`;
        return;
      }

      data.evaluations.forEach(ev => {
        const tr = document.createElement("tr");
        const dateStr = ev.created_at ? ev.created_at.split(" ")[0] : "Recent";
        tr.innerHTML = `
          <td>${dateStr}</td>
          <td><strong>${escapeHtml(ev.question_title)}</strong></td>
          <td>${ev.marks_obtained} / ${ev.max_marks}</td>
          <td><span class="badge badge-marks">${ev.score_percentage}%</span></td>
          <td><span class="rating-badge">${escapeHtml(ev.rating)}</span></td>
          <td><span class="engine-badge">${escapeHtml(ev.evaluation_engine || "Gemini AI")}</span></td>
          <td>
            <button class="btn btn-secondary btn-sm" onclick="openEvaluationModal(${ev.id})">
              View Report
            </button>
          </td>
        `;
        studentHistoryTableBody.appendChild(tr);
      });
    } catch (err) {
      console.error("Failed to load student history:", err);
    }
  }

  refreshStudentHistoryBtn.addEventListener("click", loadStudentHistory);


  // ====================================================================
  // 5. Faculty Portal Implementation
  // ====================================================================
  async function initFacultyPortal() {
    loadFacultySubmissions();
    loadFacultyQuestions();
    loadFacultyProfile();
  }

  async function loadFacultySubmissions() {
    try {
      const res = await fetch("/api/faculty/submissions");
      const data = await res.json();
      if (!data.success) return;

      state.facultySubmissions = data.submissions;
      renderFacultySubmissionsTable(data.submissions);
    } catch (err) {
      console.error("Failed to load faculty submissions:", err);
    }
  }

  function renderFacultySubmissionsTable(submissions) {
    facultySubmissionsTableBody.innerHTML = "";
    if (submissions.length === 0) {
      facultySubmissionsTableBody.innerHTML = `<tr><td colspan="9" class="text-center text-muted">No student submissions recorded in database.</td></tr>`;
      return;
    }

    submissions.forEach(sub => {
      const tr = document.createElement("tr");
      const dateStr = sub.created_at ? sub.created_at.split(" ")[0] : "Recent";
      tr.innerHTML = `
        <td><strong>${escapeHtml(sub.student_name)}</strong></td>
        <td><code>${escapeHtml(sub.student_identifier)}</code></td>
        <td>${escapeHtml(sub.student_department || "CS")}</td>
        <td>${escapeHtml(sub.question_title)}</td>
        <td><strong>${sub.marks_obtained}</strong> / ${sub.max_marks}</td>
        <td><span class="badge badge-marks">${sub.score_percentage}%</span></td>
        <td><span class="rating-badge">${escapeHtml(sub.rating)}</span></td>
        <td>${dateStr}</td>
        <td>
          <button class="btn btn-secondary btn-sm" onclick="openEvaluationModal(${sub.id})">
            Inspect
          </button>
        </td>
      `;
      facultySubmissionsTableBody.appendChild(tr);
    });
  }

  // Filter submissions by search input
  submissionsSearchInput.addEventListener("input", (e) => {
    const q = e.target.value.toLowerCase().trim();
    if (!q) {
      renderFacultySubmissionsTable(state.facultySubmissions);
      return;
    }
    const filtered = state.facultySubmissions.filter(s =>
      s.student_name.toLowerCase().includes(q) ||
      s.student_identifier.toLowerCase().includes(q) ||
      s.question_title.toLowerCase().includes(q)
    );
    renderFacultySubmissionsTable(filtered);
  });

  refreshSubmissionsBtn.addEventListener("click", loadFacultySubmissions);

  // Export CSV Report
  exportCsvBtn.addEventListener("click", () => {
    if (!state.facultySubmissions || state.facultySubmissions.length === 0) {
      showToast("No submissions to export.", "error");
      return;
    }

    const headers = ["Student Name", "Roll No", "Department", "Question", "Marks Obtained", "Max Marks", "Percentage", "Rating", "Remarks", "Date"];
    const rows = state.facultySubmissions.map(s => [
      `"${s.student_name}"`,
      `"${s.student_identifier}"`,
      `"${s.student_department}"`,
      `"${s.question_title.replace(/"/g, '""')}"`,
      s.marks_obtained,
      s.max_marks,
      `${s.score_percentage}%`,
      `"${s.rating}"`,
      `"${(s.remarks || '').replace(/"/g, '""')}"`,
      `"${s.created_at}"`
    ]);

    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(r => r.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `Student_Evaluation_Grades_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    showToast("CSV Grade Report generated & downloaded!", "success");
  });

  // Load Faculty Questions List
  async function loadFacultyQuestions() {
    try {
      const res = await fetch("/api/faculty/questions");
      const data = await res.json();
      if (!data.success) return;

      facultyQuestionsList.innerHTML = "";
      if (data.questions.length === 0) {
        facultyQuestionsList.innerHTML = "<div class='text-muted'>No questions published yet.</div>";
        return;
      }

      data.questions.forEach(q => {
        const item = document.createElement("div");
        item.className = "q-bank-item";
        item.innerHTML = `
          <div class="q-bank-item-header">
            <div>
              <span class="badge badge-subject">${escapeHtml(q.subject)}</span>
              <span class="badge badge-diff">${escapeHtml(q.difficulty)}</span>
              <span class="badge badge-marks">${q.max_marks} marks</span>
            </div>
            <button class="btn-delete-q" onclick="deleteFacultyQuestion(${q.id})" title="Delete Question">
              🗑️ Delete
            </button>
          </div>
          <h4 class="q-bank-item-title">${escapeHtml(q.title)}</h4>
          <p class="text-muted" style="font-size:0.85rem">${escapeHtml(q.question_text)}</p>
        `;
        facultyQuestionsList.appendChild(item);
      });
    } catch (err) {
      console.error("Failed to load faculty questions:", err);
    }
  }

  // Create New Question Form Submit
  createQuestionForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const title = document.getElementById("newQTitle").value.trim();
    const subject = document.getElementById("newQSubject").value.trim();
    const max_marks = parseFloat(document.getElementById("newQMaxMarks").value) || 10.0;
    const difficulty = document.getElementById("newQDifficulty").value;
    const question_text = document.getElementById("newQPrompt").value.trim();
    const reference_answer = document.getElementById("newQReference").value.trim();
    const keywords = document.getElementById("newQKeywords").value.trim();

    try {
      const res = await fetch("/api/faculty/questions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          faculty_id: state.user.id,
          faculty_name: state.user.name,
          title,
          subject,
          max_marks,
          difficulty,
          question_text,
          reference_answer,
          keywords
        })
      });
      const data = await res.json();
      if (!data.success) {
        showToast(data.error || "Failed to create question.", "error");
        return;
      }

      createQuestionForm.reset();
      showToast("Question published successfully!", "success");
      loadFacultyQuestions();
      loadQuestions(); // Update student dropdown as well
    } catch (err) {
      showToast("Failed to create question.", "error");
    }
  });

  // Delete Question Global Handler
  window.deleteFacultyQuestion = async function(qid) {
    if (!confirm("Are you sure you want to delete this assessment question?")) return;
    try {
      const res = await fetch(`/api/faculty/questions/${qid}`, { method: "DELETE" });
      const data = await res.json();
      if (data.success) {
        showToast("Question deleted.", "success");
        loadFacultyQuestions();
        loadQuestions();
      }
    } catch (err) {
      showToast("Failed to delete question.", "error");
    }
  };

  // Load Faculty Profile & Class Analytics
  async function loadFacultyProfile() {
    if (!state.user) return;
    profFacultyName.textContent = state.user.name;
    profFacultyEmail.textContent = state.user.email;
    profFacultyId.textContent = state.user.identifier;
    profFacultyDept.textContent = state.user.department || "Computer Science";

    try {
      const res = await fetch("/api/faculty/analytics");
      const data = await res.json();
      if (data.success && data.analytics) {
        facStatQuestionsCount.textContent = data.analytics.total_questions;
        facStatSubmissionsCount.textContent = data.analytics.total_submissions;
        facStatStudentsCount.textContent = data.analytics.total_students;
        facStatClassAverage.textContent = `${data.analytics.class_average}%`;
      }
    } catch (err) {
      console.warn("Could not load faculty analytics:", err);
    }
  }


  // ====================================================================
  // 6. Detailed Evaluation Report Modal
  // ====================================================================
  window.openEvaluationModal = async function(eid) {
    try {
      const res = await fetch(`/api/student/evaluations/${eid}`);
      const data = await res.json();
      if (!data.success || !data.evaluation) {
        showToast("Failed to retrieve evaluation report.", "error");
        return;
      }

      const ev = data.evaluation;
      modalReportTitle.textContent = `Report: ${ev.question_title} (${ev.student_name} - ${ev.student_identifier})`;

      modalReportBody.innerHTML = `
        <div class="score-banner" style="margin-bottom: 20px;">
          <div class="score-main">
            <div class="score-number-box">
              <span class="score-obtained">${ev.marks_obtained}</span>
              <span class="score-max">/ ${ev.max_marks}</span>
            </div>
            <div class="score-percentage-pill">${ev.score_percentage}%</div>
          </div>
          <div class="score-badge-col">
            <span class="rating-badge">${escapeHtml(ev.rating)}</span>
            <span class="engine-badge">${escapeHtml(ev.evaluation_engine || "Gemini AI")}</span>
          </div>
        </div>

        <div class="feedback-card remarks-card" style="margin-bottom: 14px;">
          <h4 style="color:#ffffff; margin-bottom:6px;">👨‍🏫 Examiner Remarks</h4>
          <p class="remarks-text">${escapeHtml(ev.remarks || ev.summary)}</p>
        </div>

        <div class="form-group">
          <label class="form-label">Student's Submitted Answer</label>
          <div style="background:rgba(15,23,42,0.7); padding:12px; border-radius:8px; border:1px solid rgba(255,255,255,0.08); font-size:0.9rem; color:#f8fafc; line-height:1.5;">
            ${escapeHtml(ev.student_answer)}
          </div>
        </div>

        <div class="feedback-columns-grid" style="margin-top:14px;">
          <div class="feedback-card strengths-card">
            <h4 style="color:#ffffff; margin-bottom:8px;">✓ Strengths Identified</h4>
            <ul class="feedback-list">
              ${(ev.strengths || []).map(s => `<li>${escapeHtml(s)}</li>`).join("") || "<li>None recorded</li>"}
            </ul>
          </div>
          <div class="feedback-card improvements-card">
            <h4 style="color:#ffffff; margin-bottom:8px;">⚠️ Areas for Improvement</h4>
            <ul class="feedback-list">
              ${(ev.improvements || []).map(imp => `<li>${escapeHtml(imp)}</li>`).join("") || "<li>None recorded</li>"}
            </ul>
          </div>
        </div>

        <div class="feedback-card suggestions-card" style="margin-top:14px;">
          <h4 style="color:#ffffff; margin-bottom:8px;">💡 Pedagogical Suggestions & Study Guidance</h4>
          <ul class="feedback-list">
            ${(ev.suggestions || []).map(sug => `<li>${escapeHtml(sug)}</li>`).join("") || "<li>Review model answers for complete marks.</li>"}
          </ul>
        </div>
      `;

      reportModal.classList.remove("hidden");
    } catch (err) {
      showToast("Error opening evaluation report.", "error");
    }
  };

  closeReportModalBtn.addEventListener("click", () => {
    reportModal.classList.add("hidden");
  });

  reportModal.addEventListener("click", (e) => {
    if (e.target === reportModal) {
      reportModal.classList.add("hidden");
    }
  });


  // ====================================================================
  // Helper: Escape HTML to prevent injection
  // ====================================================================
  function escapeHtml(str) {
    if (!str) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }


  // ====================================================================
  // Bootstrap Application
  // ====================================================================
  checkSystemStatus();

  // Check saved session
  const savedUser = localStorage.getItem("eval_user");
  if (savedUser) {
    try {
      const userObj = JSON.parse(savedUser);
      setUserSession(userObj);
    } catch (e) {
      localStorage.removeItem("eval_user");
      updateAuthUI();
    }
  } else {
    updateAuthUI();
  }
});
