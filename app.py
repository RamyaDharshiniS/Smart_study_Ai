import math
from datetime import date
from pathlib import Path
import html
import streamlit as st

st.set_page_config(page_title="Smart Study AI", page_icon="📚", layout="wide")

CSS_PATH = Path(__file__).with_name("style.css")
if CSS_PATH.exists():
    st.markdown(f"<style>{CSS_PATH.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

if "subjects" not in st.session_state:
    st.session_state.subjects = []
if "plan" not in st.session_state:
    st.session_state.plan = []

def clean(value):
    return (value or "").strip()

def days_left(exam_date):
    return max(0, (exam_date - date.today()).days)

def allocation_weight(subject):
    days = max(1, days_left(subject["exam_date"]))
    gap_ratio = max(0, subject["target"] - subject["marks"]) / max(1, subject["total"])
    return (0.45 + gap_ratio) * (1 + 1 / math.sqrt(days + 1))

def build_plan(subjects, total_hours):
    if not subjects:
        return []
    weights = [allocation_weight(s) for s in subjects]
    weight_sum = sum(weights) or 1
    rounded = [round((total_hours * w / weight_sum) * 4) / 4 for w in weights]
    if rounded:
        rounded[-1] = max(0, round((total_hours - sum(rounded[:-1])) * 4) / 4)
    result = []
    for subject, hours in sorted(
        zip(subjects, rounded),
        key=lambda pair: (days_left(pair[0]["exam_date"]), -(pair[0]["target"] - pair[0]["marks"]))
    ):
        gap = max(0, subject["target"] - subject["marks"])
        if days_left(subject["exam_date"]) <= 2:
            focus = "Urgent revision and exam-style questions"
        elif gap >= subject["total"] * .25:
            focus = "Prioritise weak topics, then practise questions"
        elif gap > 0:
            focus = "Strengthen weak areas and do timed practice"
        else:
            focus = "Maintain your score with revision and a short quiz"
        result.append({**subject, "hours": hours, "gap": gap, "days": days_left(subject["exam_date"]), "focus": focus})
    return result

st.markdown("""
<div class="hero">
  <div class="eyebrow">YOUR PERSONAL STUDY PLANNER</div>
  <h1>Smart Study <span>AI</span></h1>
  <p>Study with a plan, not with panic. Organise your subjects, see what needs work, and turn your available time into a practical revision schedule.</p>
  <div class="hero-pills"><span>✦ Smart prioritisation</span><span>◷ Exam countdown</span><span>▦ Study timetable</span></div>
</div>
""", unsafe_allow_html=True)

photos = [
    ("https://images.unsplash.com/photo-1434030216411-0b793f4b4173?auto=format&fit=crop&w=1000&q=85", "FOCUS MODE", "Make every study session count"),
    ("https://images.unsplash.com/photo-1453738773917-9c3eff1db985?auto=format&fit=crop&w=1000&q=85", "PLAN YOUR TIME", "A clear plan for every exam"),
    ("https://images.unsplash.com/photo-1517842645767-c639042777db?auto=format&fit=crop&w=1000&q=85", "SMALL STEPS", "Build confidence one topic at a time"),
]
cols = st.columns(3, gap="medium")
for col, (url, label, caption) in zip(cols, photos):
    with col:
        st.markdown(f"""<div class="photo-card"><img src="{url}" alt="Study inspiration"><div class="photo-overlay"><div>{label}</div><p>{caption}</p></div></div>""", unsafe_allow_html=True)

st.markdown('<div class="section-heading"><span>01</span><div><h2>Your exam dashboard</h2><p>Add each subject once. Your marks and exam dates help the planner prioritise.</p></div></div>', unsafe_allow_html=True)

subjects = st.session_state.subjects
upcoming = sorted(subjects, key=lambda s: s["exam_date"])
average = sum(s["marks"] / s["total"] * 100 for s in subjects) / len(subjects) if subjects else None
m1, m2, m3, m4 = st.columns(4)
m1.metric("Subjects added", len(subjects))
m2.metric("Average marks", f"{average:.0f}%" if average is not None else "—")
m3.metric("Next exam", upcoming[0]["name"] if upcoming else "Not added")
m4.metric("Days left", str(days_left(upcoming[0]["exam_date"])) if upcoming else "—")

st.markdown("---")
st.markdown('<div class="section-heading"><span>02</span><div><h2>Add a subject</h2><p>Enter your marks, target marks, exam date, and topics you need to improve.</p></div></div>', unsafe_allow_html=True)

with st.form("subject_form", clear_on_submit=True):
    name = st.text_input("Subject name", placeholder="e.g. Mathematics")
    left, right = st.columns(2)
    with left:
        marks = st.number_input("Marks obtained", min_value=0.0, value=0.0, step=1.0)
        total = st.number_input("Total possible marks", min_value=1.0, value=100.0, step=1.0)
        target = st.number_input("Target marks", min_value=0.0, value=90.0, step=1.0)
    with right:
        exam = st.date_input("Exam date", value=date.today(), min_value=date.today())
        improve = st.text_area("Topics you need to improve", placeholder="e.g. Algebra, essay writing, chemical equations", height=132)
    submitted = st.form_submit_button("＋ Add subject", use_container_width=True)

if submitted:
    name = clean(name)
    if not name:
        st.error("Please enter a subject name.")
    elif marks > total:
        st.error("Marks obtained cannot be greater than total possible marks.")
    elif target > total:
        st.error("Target marks cannot be greater than total possible marks.")
    elif exam < date.today():
        st.error("Please choose today or a future exam date.")
    else:
        record = {
            "name": name, "marks": float(marks), "total": float(total),
            "target": float(target), "exam_date": exam,
            "improve": clean(improve) or "Not specified yet",
        }
        old_index = next((i for i, s in enumerate(st.session_state.subjects) if s["name"].casefold() == name.casefold()), None)
        if old_index is None:
            st.session_state.subjects.append(record)
            st.success(f"Added {name} successfully!")
        else:
            st.session_state.subjects[old_index] = record
            st.success(f"Updated {name} successfully!")
        st.rerun()

st.markdown('<div class="section-heading"><span>03</span><div><h2>Your subject list</h2><p>Update a subject by adding it again with the same name.</p></div></div>', unsafe_allow_html=True)

if not st.session_state.subjects:
    st.markdown('<div class="empty-state"><div class="empty-icon">📚</div><h3>Your study space is ready</h3><p>Add your first subject above. Your subject cards will appear here.</p></div>', unsafe_allow_html=True)
else:
    card_cols = st.columns(2, gap="medium")
    for i, s in enumerate(st.session_state.subjects):
        with card_cols[i % 2]:
            percent = s["marks"] / s["total"] * 100
            safe_name = html.escape(s["name"])
            safe_improve = html.escape(s["improve"])
            st.markdown(f"""
            <div class="subject-card">
              <div class="subject-card-top"><div><div class="subject-kicker">SUBJECT {i+1}</div><h3>{safe_name}</h3></div><div class="countdown">{days_left(s['exam_date'])}<small>days left</small></div></div>
              <div class="mark-row">
                <div><small>Current marks</small><strong>{s['marks']:g} / {s['total']:g}</strong></div>
                <div><small>Target marks</small><strong>{s['target']:g}</strong></div>
                <div><small>Marks to target</small><strong>{max(0, s['target']-s['marks']):g}</strong></div>
              </div>
              <div class="progress-label"><span>Current score</span><b>{percent:.0f}%</b></div>
              <div class="progress-track"><div class="progress-fill" style="width:{min(100,max(0,percent)):.1f}%"></div></div>
              <p class="exam-date">🗓️ Exam date: {s['exam_date'].strftime('%d %b %Y')}</p>
              <p class="weak-topics"><b>Topics to improve:</b> {safe_improve}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Remove {s['name']}", key=f"remove_{i}", use_container_width=True):
                st.session_state.subjects.pop(i)
                st.session_state.plan = []
                st.rerun()

st.markdown('<div class="section-heading"><span>04</span><div><h2>Build your study timetable</h2><p>Enter the total time you have. The planner shares it based on exam urgency and the gap to your target marks.</p></div></div>', unsafe_allow_html=True)

if st.session_state.subjects:
    total_hours = st.number_input("Total study hours available before your exams", min_value=0.5, max_value=1000.0, value=20.0, step=0.5)
    if st.button("✨ Generate my study plan", type="primary", use_container_width=True):
        st.session_state.plan = build_plan(st.session_state.subjects, float(total_hours))
    if st.session_state.plan:
        st.markdown('<div class="plan-banner"><h3>✦ Your personalised study allocation</h3><p>Remember to include breaks, sleep, school, and other commitments.</p></div>', unsafe_allow_html=True)
        for item in st.session_state.plan:
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"### 📘 {item['name']}")
                    st.write(item["focus"])
                    st.caption(f"Exam: {item['exam_date'].strftime('%d %b %Y')} · {item['days']} day(s) left · Marks needed to target: {item['gap']:g}")
                with c2:
                    st.metric("Allocated time", f"{item['hours']:.2f} h")
        st.info(f"Total allocated: {sum(x['hours'] for x in st.session_state.plan):.2f} hours.")
else:
    st.info("Add at least one subject to generate your study timetable.")

st.markdown('<div class="section-heading"><span>05</span><div><h2>Study coach</h2><p>Built-in general study tips for common subjects.</p></div></div>', unsafe_allow_html=True)
options = ["Mathematics", "Science", "Physics", "Chemistry", "Biology", "English", "Tamil", "Social Science", "History", "Geography", "Computer Science", "Economics", "Other"]
tips = {
    "Mathematics": "Study a worked example, solve 5–10 problems without looking at the solution, then correct every mistake.",
    "Science": "Learn definitions, draw diagrams from memory, and explain processes in your own words.",
    "Physics": "List known values, choose the formula, show units at each step, and practise numerical problems.",
    "Chemistry": "Practise equations and balancing, make a small reaction table, and revisit concepts you confuse.",
    "Biology": "Use labelled diagrams, flashcards for terms, and short recall sessions instead of only rereading notes.",
    "English": "Practise a short writing task, revise grammar in context, and plan answers before writing full paragraphs.",
    "Tamil": "Practise reading and writing, revise meanings and grammar, and outline longer answers before composing them.",
    "Social Science": "Create timelines and comparison tables, learn key terms, and practise answers with headings and examples.",
    "History": "Arrange events chronologically, connect causes to consequences, and test yourself on key dates and people.",
    "Geography": "Practise maps and labelled diagrams, learn terms with examples, and explain processes step by step.",
    "Computer Science": "Trace code by hand, practise small programs, and explain each line before running it.",
    "Economics": "Define key terms, draw and label diagrams where relevant, and connect concepts to real examples.",
    "Other": "Break chapters into small topics, use active recall, practise exam-style questions, and review mistakes.",
}
chosen = st.selectbox("Choose a subject for study tips", options)
st.markdown(f'<div class="coach-card"><div class="coach-icon">🧠</div><div><h3>{chosen} study tip</h3><p>{tips[chosen]}</p></div></div>', unsafe_allow_html=True)

st.markdown('<div class="footer-note"><b>Note:</b> The planner uses the information you enter and built-in rule-based guidance. It does not automatically know your exact school syllabus. Subject data remains for the current Streamlit session and is not yet stored permanently.</div>', unsafe_allow_html=True)
