import streamlit as st
import google.generativeai as genai
import json
from datetime import datetime, date
import os

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DeadlineZero",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500&display=swap');

/* ── Root palette ── */
:root {
    --bg:       #0d0f1a;
    --surface:  #161929;
    --card:     #1e2235;
    --border:   #2a2f4a;
    --accent1:  #7c5cfc;   /* violet */
    --accent2:  #f97316;   /* vivid orange */
    --accent3:  #22d3ee;   /* cyan */
    --accent4:  #4ade80;   /* green */
    --text:     #e8eaf6;
    --muted:    #8891b4;
    --danger:   #f43f5e;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif;
}

/* hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
[data-testid="stSidebar"] { background: var(--surface) !important; }

/* ── Typography ── */
h1, h2, h3, h4 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: var(--text) !important;
}

/* ── Hero banner ── */
.hero {
    background: linear-gradient(135deg, #1a1040 0%, #0d1a3a 50%, #001a2e 100%);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(124,92,252,0.25) 0%, transparent 70%);
    pointer-events: none;
}
.hero::after {
    content: '';
    position: absolute;
    bottom: -40px; left: 30%;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(249,115,22,0.15) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.8rem;
    font-weight: 700;
    background: linear-gradient(90deg, #7c5cfc, #f97316, #22d3ee);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 0.4rem 0;
    line-height: 1.1;
}
.hero-sub {
    color: var(--muted);
    font-size: 1.05rem;
    margin: 0;
}

/* ── Stat pills ── */
.stats-row {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
    flex-wrap: wrap;
}
.stat-pill {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem 1.5rem;
    flex: 1;
    min-width: 120px;
    text-align: center;
}
.stat-number {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    line-height: 1;
    display: block;
}
.stat-label {
    color: var(--muted);
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 0.3rem;
    display: block;
}
.stat-violet .stat-number { color: var(--accent1); }
.stat-orange .stat-number { color: var(--accent2); }
.stat-cyan   .stat-number { color: var(--accent3); }
.stat-green  .stat-number { color: var(--accent4); }

/* ── Cards ── */
.section-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}
.section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--muted);
    margin: 0 0 1.2rem 0;
}

/* ── Priority badges ── */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.07em;
}
.badge-critical { background: rgba(244,63,94,0.15); color: #f43f5e; border: 1px solid rgba(244,63,94,0.3); }
.badge-high     { background: rgba(249,115,22,0.15); color: #f97316; border: 1px solid rgba(249,115,22,0.3); }
.badge-medium   { background: rgba(124,92,252,0.15); color: #a78bfa; border: 1px solid rgba(124,92,252,0.3); }
.badge-low      { background: rgba(74,222,128,0.15); color: #4ade80; border: 1px solid rgba(74,222,128,0.3); }

/* ── Task cards ── */
.task-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
    border-left: 3px solid var(--accent1);
    transition: border-color 0.2s;
}
.task-card.critical { border-left-color: var(--danger); }
.task-card.high     { border-left-color: var(--accent2); }
.task-card.medium   { border-left-color: var(--accent1); }
.task-card.low      { border-left-color: var(--accent4); }

.task-name {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 1rem;
    margin: 0 0 0.3rem 0;
}
.task-meta {
    color: var(--muted);
    font-size: 0.82rem;
}

/* ── Schedule blocks ── */
.schedule-block {
    display: flex;
    gap: 1rem;
    align-items: flex-start;
    margin-bottom: 1rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border);
}
.schedule-time {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    color: var(--accent3);
    font-size: 0.85rem;
    min-width: 80px;
    margin-top: 0.15rem;
}
.schedule-content {
    flex: 1;
}
.schedule-task {
    font-weight: 500;
    font-size: 0.95rem;
    margin: 0 0 0.2rem 0;
}
.schedule-detail {
    color: var(--muted);
    font-size: 0.82rem;
}

/* ── AI insight box ── */
.ai-box {
    background: linear-gradient(135deg, rgba(124,92,252,0.1), rgba(34,211,238,0.06));
    border: 1px solid rgba(124,92,252,0.3);
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1.5rem;
}
.ai-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--accent1);
    font-weight: 600;
    margin-bottom: 0.5rem;
}
.ai-text {
    color: var(--text);
    font-size: 0.95rem;
    line-height: 1.6;
}

/* ── Streamlit overrides ── */
.stTextInput > div > div > input,
.stSelectbox > div > div,
.stDateInput > div > div > input,
.stTextArea > div > div > textarea {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 10px !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent1) !important;
    box-shadow: 0 0 0 2px rgba(124,92,252,0.2) !important;
}
label, .stSelectbox label, .stTextInput label,
.stDateInput label, .stTextArea label,
.stNumberInput label {
    color: var(--muted) !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}
.stButton > button {
    border-radius: 10px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    transition: all 0.2s !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--accent1), #5b3fcf) !important;
    border: none !important;
    color: white !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(124,92,252,0.4) !important;
}
.stButton > button[kind="secondary"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
}
div[data-testid="stExpander"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
}
div[data-testid="stExpander"] summary {
    color: var(--text) !important;
}
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--muted) !important;
    border-radius: 8px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 500 !important;
}
.stTabs [aria-selected="true"] {
    background: var(--card) !important;
    color: var(--text) !important;
}
[data-testid="stNotification"] {
    background: var(--card) !important;
    border-radius: 12px !important;
}
.stSpinner > div { border-top-color: var(--accent1) !important; }
hr { border-color: var(--border) !important; }
</style>
""", unsafe_allow_html=True)

# ── Gemini setup ───────────────────────────────────────────────────────────────
def get_gemini_client():
    api_key = st.secrets.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))
    if not api_key:
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-1.5-flash")

# ── Session state ──────────────────────────────────────────────────────────────
if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "ai_schedule" not in st.session_state:
    st.session_state.ai_schedule = None
if "ai_insight" not in st.session_state:
    st.session_state.ai_insight = None
if "subtasks" not in st.session_state:
    st.session_state.subtasks = {}

# ── Helpers ────────────────────────────────────────────────────────────────────
def days_until(deadline_str):
    try:
        d = datetime.strptime(deadline_str, "%Y-%m-%d").date()
        return (d - date.today()).days
    except:
        return 999

def urgency_color(days):
    if days <= 1:   return "critical"
    if days <= 3:   return "high"
    if days <= 7:   return "medium"
    return "low"

def badge_html(level):
    return f'<span class="badge badge-{level}">{level}</span>'

# ── Gemini calls ───────────────────────────────────────────────────────────────
def ai_prioritize_and_schedule(model, tasks):
    if not tasks:
        return None, None
    today_str = date.today().strftime("%B %d, %Y")
    task_list = "\n".join([
        f"- Task: {t['name']} | Deadline: {t['deadline']} | Effort: {t['effort']}h | Category: {t['category']}"
        for t in tasks
    ])
    prompt = f"""You are DeadlineZero, an AI productivity agent. Today is {today_str}.

Here are the user's tasks:
{task_list}

Respond with ONLY valid JSON (no markdown, no backticks):
{{
  "insight": "2-3 sentence smart analysis of the user's workload — mention the most urgent task, warn about bottlenecks, give a confidence-boosting but honest assessment",
  "prioritized": [
    {{
      "name": "task name",
      "priority": "critical|high|medium|low",
      "reason": "one-line reason",
      "deadline": "original deadline"
    }}
  ],
  "schedule": [
    {{
      "time": "e.g. 9:00 AM",
      "task": "task name",
      "duration": "e.g. 1.5 hours",
      "tip": "one practical tip for this block"
    }}
  ]
}}

Rules:
- Sort prioritized list by urgency (most urgent first)
- Schedule should cover today realistically (8 AM - 10 PM, include breaks)
- Be specific and actionable in tips
"""
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        return {"error": str(e)}

def ai_break_into_steps(model, task_name, effort_hours, deadline):
    prompt = f"""You are DeadlineZero. Break this task into actionable sub-steps.

Task: {task_name}
Total effort: {effort_hours} hours
Deadline: {deadline}

Respond with ONLY valid JSON:
{{
  "steps": [
    {{"step": "step description", "time": "estimated minutes", "tip": "quick tip"}}
  ]
}}

Keep it to 4-6 steps. Be specific and practical."""
    try:
        response = model.generate_content(prompt)
        text = response.text.strip().replace("```json","").replace("```","").strip()
        data = json.loads(text)
        return data.get("steps", [])
    except:
        return []

def ai_nudge(model, tasks):
    if not tasks:
        return "Add your tasks above and I'll help you crush them. ⚡"
    overdue = [t for t in tasks if days_until(t['deadline']) < 0]
    urgent  = [t for t in tasks if 0 <= days_until(t['deadline']) <= 2]
    today_str = date.today().strftime("%B %d, %Y")
    prompt = f"""Today is {today_str}. User has {len(tasks)} tasks. {len(overdue)} overdue, {len(urgent)} due in ≤2 days.
Tasks: {[t['name'] for t in tasks[:5]]}
Write ONE short, punchy motivational nudge (max 25 words). Be direct, energetic, specific. No fluff."""
    try:
        return model.generate_content(prompt).text.strip()
    except:
        return "You've got this. Focus on the most urgent task first. ⚡"

# ══════════════════════════════════════════════════════════════════════════════
# MAIN UI
# ══════════════════════════════════════════════════════════════════════════════

model = get_gemini_client()

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <p class="hero-title">DeadlineZero ⚡</p>
  <p class="hero-sub">Your AI agent that plans, prioritizes, and helps you ship — before the clock runs out.</p>
</div>
""", unsafe_allow_html=True)

# API key input if not set
if not model:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 🔑 Connect Gemini API")
    api_input = st.text_input("Paste your Gemini API key to activate the AI agent:", type="password",
                               placeholder="AIza...")
    if api_input:
        os.environ["GEMINI_API_KEY"] = api_input
        genai.configure(api_key=api_input)
        model = genai.GenerativeModel("gemini-1.5-flash")
        st.success("✅ AI agent connected!")
        st.rerun()
    st.markdown("Get a free key at [aistudio.google.com](https://aistudio.google.com)")
    st.markdown('</div>', unsafe_allow_html=True)

# ── Stats ──────────────────────────────────────────────────────────────────────
tasks = st.session_state.tasks
total   = len(tasks)
overdue = len([t for t in tasks if days_until(t['deadline']) < 0])
urgent  = len([t for t in tasks if 0 <= days_until(t['deadline']) <= 2])
on_track = total - overdue - urgent

st.markdown(f"""
<div class="stats-row">
  <div class="stat-pill stat-violet">
    <span class="stat-number">{total}</span>
    <span class="stat-label">Total Tasks</span>
  </div>
  <div class="stat-pill stat-orange">
    <span class="stat-number">{urgent}</span>
    <span class="stat-label">Due in 48h</span>
  </div>
  <div class="stat-pill" style="background:var(--card);border:1px solid var(--border)">
    <span class="stat-number" style="color:var(--danger)">{overdue}</span>
    <span class="stat-label">Overdue</span>
  </div>
  <div class="stat-pill stat-green">
    <span class="stat-number">{on_track}</span>
    <span class="stat-label">On Track</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── AI nudge ───────────────────────────────────────────────────────────────────
if model and tasks:
    nudge = ai_nudge(model, tasks)
    st.markdown(f"""
    <div class="ai-box">
      <div class="ai-label">⚡ AI Agent Says</div>
      <div class="ai-text">{nudge}</div>
    </div>
    """, unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["➕ Add Task", "📋 My Tasks", "🗓 AI Schedule", "🔍 Break It Down"])

# ══════════ TAB 1: ADD TASK ════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">New Task</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        task_name = st.text_input("Task name", placeholder="e.g. Submit project report")
        category  = st.selectbox("Category", ["📚 Study / Assignment", "💼 Work / Internship",
                                               "🏠 Personal", "💰 Bills / Finance", "🎯 Goal / Habit", "Other"])
    with col2:
        deadline  = st.date_input("Deadline", min_value=date.today())
        effort    = st.slider("Estimated effort (hours)", 0.5, 12.0, 2.0, 0.5)

    notes = st.text_area("Notes (optional)", placeholder="Any extra context...", height=80)

    col_a, col_b = st.columns([1, 3])
    with col_a:
        add_clicked = st.button("Add Task ⚡", type="primary", use_container_width=True)

    if add_clicked and task_name.strip():
        st.session_state.tasks.append({
            "name":     task_name.strip(),
            "category": category,
            "deadline": str(deadline),
            "effort":   effort,
            "notes":    notes,
            "done":     False,
        })
        st.session_state.ai_schedule = None  # reset so it regenerates
        st.success(f"✅ **{task_name}** added!")
        st.rerun()
    elif add_clicked:
        st.warning("Please enter a task name.")

    st.markdown('</div>', unsafe_allow_html=True)

    # Quick-add examples
    st.markdown('<p class="section-title" style="margin-top:1rem">Quick Add Examples</p>', unsafe_allow_html=True)
    examples = [
        ("Submit internship report", "2026-06-28", 3.0, "💼 Work / Internship"),
        ("Pay electricity bill",     "2026-06-27", 0.5, "💰 Bills / Finance"),
        ("Prepare for interview",    "2026-06-30", 5.0, "💼 Work / Internship"),
    ]
    for ex_name, ex_date, ex_eff, ex_cat in examples:
        if st.button(f"+ {ex_name}", key=f"ex_{ex_name}"):
            st.session_state.tasks.append({
                "name": ex_name, "category": ex_cat,
                "deadline": ex_date, "effort": ex_eff,
                "notes": "", "done": False
            })
            st.session_state.ai_schedule = None
            st.rerun()

# ══════════ TAB 2: MY TASKS ════════════════════════════════════════════════════
with tab2:
    if not tasks:
        st.markdown("""
        <div style="text-align:center;padding:3rem;color:var(--muted)">
          <div style="font-size:3rem">📋</div>
          <p style="font-family:'Space Grotesk',sans-serif;font-size:1.1rem;margin-top:1rem">No tasks yet.</p>
          <p>Head to <b>Add Task</b> to get started.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Sort by urgency
        sorted_tasks = sorted(tasks, key=lambda t: days_until(t['deadline']))

        col_run, col_clr = st.columns([2, 1])
        with col_run:
            if model:
                run_ai = st.button("🤖 Run AI Prioritization", type="primary", use_container_width=True)
                if run_ai:
                    with st.spinner("AI agent analyzing your tasks..."):
                        result = ai_prioritize_and_schedule(model, [t for t in tasks if not t['done']])
                        if result and "error" not in result:
                            st.session_state.ai_schedule = result.get("schedule")
                            st.session_state.ai_insight  = result.get("insight")
                            st.session_state.prioritized = result.get("prioritized", [])
                            st.success("✅ AI analysis complete! Check the Schedule tab.")
        with col_clr:
            if st.button("🗑 Clear All", use_container_width=True):
                st.session_state.tasks = []
                st.session_state.ai_schedule = None
                st.rerun()

        # AI insight if available
        if st.session_state.ai_insight:
            st.markdown(f"""
            <div class="ai-box" style="margin-top:1rem">
              <div class="ai-label">🤖 AI Workload Analysis</div>
              <div class="ai-text">{st.session_state.ai_insight}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<p class="section-title" style="margin-top:1rem">Your Tasks</p>', unsafe_allow_html=True)

        for i, task in enumerate(sorted_tasks):
            days = days_until(task['deadline'])
            level = urgency_color(days)
            days_label = "Overdue!" if days < 0 else (f"{days}d left" if days > 0 else "Due today!")

            # find AI priority reason if available
            ai_reason = ""
            if hasattr(st.session_state, 'prioritized'):
                for p in st.session_state.get('prioritized', []):
                    if p.get('name','').lower() in task['name'].lower():
                        ai_reason = f" · <i>{p.get('reason','')}</i>"
                        break

            st.markdown(f"""
            <div class="task-card {level}">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:0.5rem">
                <p class="task-name">{task['name']}</p>
                {badge_html(level)}
              </div>
              <p class="task-meta">
                {task['category']} &nbsp;·&nbsp; 📅 {task['deadline']} &nbsp;·&nbsp; ⏱ {task['effort']}h &nbsp;·&nbsp;
                <b style="color:{'var(--danger)' if days<0 else 'var(--accent3)'}">{days_label}</b>
                {ai_reason}
              </p>
              {f'<p class="task-meta" style="margin-top:0.3rem;color:var(--muted)">{task["notes"]}</p>' if task.get("notes") else ""}
            </div>
            """, unsafe_allow_html=True)

            col_done, col_del = st.columns([3, 1])
            with col_done:
                if st.button(f"✅ Mark done", key=f"done_{i}", use_container_width=True):
                    st.session_state.tasks[st.session_state.tasks.index(task)]['done'] = True
                    st.rerun()
            with col_del:
                if st.button("🗑", key=f"del_{i}", use_container_width=True):
                    st.session_state.tasks.remove(task)
                    st.rerun()

# ══════════ TAB 3: AI SCHEDULE ═════════════════════════════════════════════════
with tab3:
    if not model:
        st.info("Connect your Gemini API key to generate AI schedules.")
    elif not tasks:
        st.info("Add tasks first, then run AI prioritization to get your schedule.")
    elif not st.session_state.ai_schedule:
        st.markdown("""
        <div style="text-align:center;padding:2.5rem;color:var(--muted)">
          <div style="font-size:2.5rem">🗓</div>
          <p style="font-family:'Space Grotesk',sans-serif;font-size:1rem;margin-top:1rem">
            Go to <b>My Tasks</b> and click <b>Run AI Prioritization</b> to generate your schedule.
          </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<p class="section-title">Your AI-Generated Day Plan</p>', unsafe_allow_html=True)
        schedule = st.session_state.ai_schedule

        for block in schedule:
            st.markdown(f"""
            <div class="schedule-block">
              <div class="schedule-time">{block.get('time','')}</div>
              <div class="schedule-content">
                <p class="schedule-task">{block.get('task','')}</p>
                <p class="schedule-detail">⏱ {block.get('duration','')} &nbsp;·&nbsp; 💡 {block.get('tip','')}</p>
              </div>
            </div>
            """, unsafe_allow_html=True)

        if st.button("🔄 Regenerate Schedule", type="secondary"):
            with st.spinner("Regenerating..."):
                result = ai_prioritize_and_schedule(model, [t for t in tasks if not t['done']])
                if result and "error" not in result:
                    st.session_state.ai_schedule = result.get("schedule")
                    st.session_state.ai_insight  = result.get("insight")
                    st.rerun()

# ══════════ TAB 4: BREAK IT DOWN ═══════════════════════════════════════════════
with tab4:
    if not model:
        st.info("Connect your Gemini API key to break tasks into steps.")
    elif not tasks:
        st.info("Add some tasks first!")
    else:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-title">AI Task Breakdown</p>', unsafe_allow_html=True)

        task_names = [t['name'] for t in tasks if not t['done']]
        if task_names:
            selected = st.selectbox("Pick a task to break down:", task_names)
            sel_task = next((t for t in tasks if t['name'] == selected), None)

            if st.button("🤖 Break it into steps", type="primary"):
                with st.spinner(f"Breaking down '{selected}'..."):
                    steps = ai_break_into_steps(model, selected,
                                                sel_task['effort'], sel_task['deadline'])
                    st.session_state.subtasks[selected] = steps

            if selected in st.session_state.subtasks:
                steps = st.session_state.subtasks[selected]
                st.markdown(f"<p style='color:var(--muted);font-size:0.85rem;margin:1rem 0 0.5rem'>Steps for: <b style='color:var(--text)'>{selected}</b></p>", unsafe_allow_html=True)
                for j, step in enumerate(steps, 1):
                    st.markdown(f"""
                    <div style="background:var(--bg);border:1px solid var(--border);border-radius:10px;
                                padding:0.9rem 1.1rem;margin-bottom:0.6rem;
                                border-left:3px solid var(--accent1)">
                      <p style="margin:0 0 0.2rem;font-weight:600;font-size:0.95rem">
                        <span style="color:var(--accent1)">Step {j}.</span> {step.get('step','')}
                      </p>
                      <p style="margin:0;color:var(--muted);font-size:0.82rem">
                        ⏱ {step.get('time','')} min &nbsp;·&nbsp; 💡 {step.get('tip','')}
                      </p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("All tasks are marked done! Add more to break down.")
        st.markdown('</div>', unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:2rem 0 1rem;color:var(--muted);font-size:0.8rem">
  Built with ⚡ Gemini AI · Google Cloud · Streamlit &nbsp;|&nbsp; Vibe2Ship Hackathon 2026
</div>
""", unsafe_allow_html=True)