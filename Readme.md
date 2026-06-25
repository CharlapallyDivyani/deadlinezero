# DeadlineZero ⚡
### AI-Powered Productivity Companion | Vibe2Ship Hackathon 2026

> Stop missing deadlines. DeadlineZero is an agentic AI companion that plans, prioritizes, and breaks down your tasks — before the clock runs out.

---

## 🚀 Live Demo
[🔗 Deployed App Link](#) <!-- replace with your Streamlit Cloud / AI Studio link -->

---

## 💡 Problem Statement
**PS1 — The Last-Minute Life Saver**

Students, professionals, and entrepreneurs frequently miss deadlines due to poor prioritization and passive reminder tools. DeadlineZero goes beyond reminders — it acts as a proactive AI agent that reasons about your workload and generates an actionable day plan.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 AI Prioritization | Gemini analyzes all tasks and ranks by urgency + effort |
| 🗓 Smart Daily Schedule | Auto-generates a time-blocked day plan with tips |
| 🔍 Task Breakdown | Breaks any task into 4-6 actionable sub-steps |
| ⚡ AI Nudges | Context-aware motivational pushes based on workload |
| 📊 Workload Dashboard | Live stats — overdue, urgent, on-track counts |
| 🏷 Priority Badges | Critical / High / Medium / Low with visual urgency cues |

---

## 🛠 Tech Stack

- **Frontend:** Streamlit
- **AI:** Google Gemini 1.5 Flash (via `google-generativeai`)
- **Deployment:** Google Cloud (via AI Studio / Streamlit Cloud)
- **Language:** Python 3.10+

## Google Technologies Used
- Google Gemini API (Gemini 1.5 Flash)
- Google AI Studio (deployment)
- Google Cloud (hosting)

---

## 📦 Run Locally

```bash
git clone https://github.com/CharlapallyDivyani/deadlinezero
cd deadlinezero
pip install -r requirements.txt

# Add your Gemini API key
mkdir -p .streamlit
echo 'GEMINI_API_KEY = "your_key_here"' > .streamlit/secrets.toml

streamlit run app.py
```

Get a free Gemini API key at [aistudio.google.com](https://aistudio.google.com)

---

## 🏆 Hackathon
Built for **Vibe2Ship** by Coding Ninjas × Google for Developers | June 2026

---

*Built with ⚡ by Divyani Charlapally*