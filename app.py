import streamlit as st
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Resume Based Company Recommender",
    layout="wide"
)

# ---------------- CSS ----------------
st.markdown("""
<style>
.card {
    background: linear-gradient(145deg, #020617, #0f172a);
    border-radius: 20px;
    padding: 20px;
    margin-bottom: 24px;
    box-shadow: 0 18px 45px rgba(0,0,0,0.65);
    border: 1px solid rgba(255,255,255,0.08);
    color: #e5e7eb;
}
.card:hover {
    transform: translateY(-4px);
    transition: 0.3s;
}
.badge {
    padding: 5px 14px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
    margin-right: 6px;
    display: inline-block;
}
.skill {
    background: #1e293b;
    color: #e5e7eb;
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 12px;
    margin: 4px 6px 0 0;
    display: inline-block;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    return pd.read_csv("data/Companies_CGPA.csv")

df = load_data()

# ---------------- HEADER ----------------
st.title("🎓 Resume Based Company Recommender")
st.caption("CGPA • Role • Skills • Explainable Recommendations")

# ---------------- INPUTS ----------------
st.subheader("🔍 Student Profile")

c1, c2, c3, c4 = st.columns(4)

with c1:
    stream = st.selectbox("Stream", sorted(df["stream"].unique()))

with c2:
    department = st.selectbox(
        "Department",
        sorted(df[df["stream"] == stream]["department"].unique())
    )

with c3:
    role = st.selectbox(
        "Job Role",
        sorted(
            df[
                (df["stream"] == stream) &
                (df["department"] == department)
            ]["job_role"].unique()
        )
    )

with c4:
    cgpa = st.slider("CGPA", 5.0, 10.0, 7.0, 0.1)

resume = st.file_uploader("Optional: Upload Resume (TXT/PDF/DOCX)", type=["txt","pdf","docx"])

submit = st.button("🔎 Find Companies")

# ---------------- USER SKILLS (simple extraction) ----------------
user_skills = []

if resume:
    text = resume.read().decode(errors="ignore").lower()
    known_skills = [
        "python","java","sql","machine learning","data science",
        "excel","power bi","tableau","statistics",
        "git","rest","api","cloud","docker"
    ]
    user_skills = [s for s in known_skills if s in text]

# ---------------- HELPER FUNCTIONS ----------------
def allowed_levels(cgpa):
    if cgpa >= 8.0:
        return ["High","Mid","Low","Startup"]
    elif cgpa >= 6.5:
        return ["Mid","Low","Startup"]
    else:
        return ["Low","Startup"]

def calculate_skill_match(user, required):
    if not user or not required:
        return 0
    return int((len(set(user) & set(required)) / len(set(required))) * 100)

def missing_skills(user, required):
    return [s for s in required if s not in user]

def skill_bar(percent):
    filled = int(percent / 10)
    return "█" * filled + "░" * (10 - filled)

# ---------------- CARD ----------------
def show_card(row, tag):
    level_colors = {
        "High": "#22c55e",
        "Mid": "#facc15",
        "Low": "#38bdf8",
        "Startup": "#a855f7"
    }

    required = [s.strip().lower() for s in str(row["required_skills"]).split(",") if s.strip()]
    match = calculate_skill_match(user_skills, required)
    gap = missing_skills(user_skills, required)
    bar = skill_bar(match)

    html = f"""
<div class="card">
  <h4 style="margin:0;">🏢 {row['company_name']}</h4>

  <div style="margin-top:8px;">
    <span class="badge" style="background:{level_colors[row['company_level']]}; color:black;">
      {row['company_level']}
    </span>
    <span class="badge" style="background:#334155;">
      {tag}
    </span>
  </div>

  <p style="margin-top:8px; color:#cbd5f5;">📍 {row['location']}</p>

  <p style="margin-top:10px; font-weight:700; color:#86efac;">
    🧠 Skill Match: {match}%
  </p>

  <div style="font-family:monospace; color:#22c55e; margin-bottom:8px;">
    {bar}
  </div>

  <p style="font-weight:700;">🎯 Required Skills</p>
  <div>
    {"".join(f"<span class='skill'>{s}</span>" for s in required)}
  </div>

  <p style="margin-top:10px; font-weight:700; color:#fca5a5;">
    ❌ Missing Skills
  </p>
  <div>
    {"".join(f"<span class='skill' style='background:#7f1d1d;'>{s}</span>" for s in gap[:5]) or "<span class='skill'>None 🎉</span>"}
  </div>

  <p style="margin-top:12px; font-weight:700; color:#93c5fd;">
    💡 Why this company?
  </p>
  <ul>
    <li>Eligible based on CGPA</li>
    <li>Relevant to selected job role</li>
    <li>Skill compatibility: {match}%</li>
  </ul>
</div>
"""
    st.markdown(html, unsafe_allow_html=True)

# ---------------- RESULTS ----------------
if submit:
    base = df[
        (df["stream"] == stream) &
        (df["department"] == department) &
        (df["company_level"].isin(allowed_levels(cgpa)))
    ].copy()

    order = ["High","Mid","Low","Startup"]
    base["company_level"] = pd.Categorical(base["company_level"], order, ordered=True)
    base = base.sort_values("company_level")

    best = base[base["job_role"] == role]
    alt = base[base["job_role"] != role]

    st.subheader("🏆 Recommended Companies")

    if not best.empty:
        st.markdown("### 🎯 Best Matches")
        cols = st.columns(2)
        for i, (_, r) in enumerate(best.iterrows()):
            with cols[i % 2]:
                show_card(r, "Best Match")

    if not alt.empty:
        st.markdown("### 🔁 Alternate Opportunities")
        cols = st.columns(2)
        for i, (_, r) in enumerate(alt.iterrows()):
            with cols[i % 2]:
                show_card(r, "Alternate Role")

    if best.empty and alt.empty:
        st.warning("No companies found. Try changing CGPA or role.")
