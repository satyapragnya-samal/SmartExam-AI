# SmartExam AI 🎓🤖
> **AI-Powered Online Examination & Assessment System**

SmartExam AI is a full-stack examination ecosystem built with Django, MySQL, and Google Gemini 2.5 Flash. It features automated question authoring, real-time proctoring safeguards, server-side PDF certification, and instant AI-driven diagnostic feedback.

---

## 🚀 Key Features

- **Role-Based Access Control (RBAC):** Dedicated candidate and instructor portals with organization passcode verification (`FACULTY2026`).
- **GenAI MCQ Authoring:** Automated question generation from curriculum topics via Google Gemini 2.5 Flash with strict JSON validation.
- **Anti-Cheat Proctoring:** Active window blur and tab-switching monitoring using JavaScript Page Visibility APIs with a 3-strike disqualification rule.
- **Single-Attempt Policy:** Server-side assessment lockdown preventing duplicate submissions.
- **Performance Diagnostics & Doubt Chat:** Context-aware doubt chatbot and post-exam error diagnostics with personalized study roadmaps.
- **Verified PDF Certification:** Server-side dynamic PDF generation (`xhtml2pdf`) for passing candidates.

---

## 🛠️ Tech Stack

- **Backend:** Python 3.13, Django 5.x
- **Database:** MySQL / SQLite
- **AI & LLM:** Google GenAI SDK (`gemini-2.5-flash`)
- **Frontend:** Semantic HTML5, CSS3, JavaScript (Fetch API, Page Visibility API)
- **Document Pipeline:** `xhtml2pdf`

---

## ⚙️ Quickstart Guide

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/SmartExam-AI.git](https://github.com/your-username/SmartExam-AI.git)
   cd SmartExam-AI