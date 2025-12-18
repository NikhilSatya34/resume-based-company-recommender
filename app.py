import streamlit as st
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Career Readiness & Company Recommender",
    layout="wide"
)

# ---------------- CSS ----------------
st.markdown("""
<style>
.card {
    background: linear-gradient(145deg, #111827, #1f2937);
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 22px;
    box-shadow: 0 15px 40px rgba(0,0,0,0.55);
    border: 1px solid rgba(255,255,255,0.08);
    transition: transform 0.3s ease;
    color: #e5e7eb;
}
.card:hover {
    transform: translateY(-6px);
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
    padding: 5px 12px;
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
st.markdown("## 🎓 Career Readiness & Company Recommender")
st.caption("Smart recommendations based on CGPA, role & required skills")

# ---------------- INPUT SECTION ----------------
st.markdown("### 🔍 Find Suitable Companies")

col1, col2, col3, col4 = st.columns(4)

with col1:
    stream = st.selectbox("Stream", sorted(df["stream"].unique()))

with col2:
    dept = st.selectbox(
        "Department",
        sorted(df[df["stream"] == stream]["department"].unique())
    )

with col3:
    role = st.selectbox(
        "Job Role",
        sorted(
            df[
                (df["stream"] == stream) &
                (df["department"] == dept)
            ]["job_role"].unique()
        )
    )

with col4:
    cgpa = st.slider("Your CGPA", 5.0, 10.0, 7.0, 0.1)

uploaded_resume = st.file_uploader(
    "Optional: Upload your resume (PDF/DOCX)",
    type=["pdf", "docx"]
)

submit = st.button("🔎 Find Companies")

# ---------------- CGPA LOGIC ----------------
def allowed_levels(cgpa):
    if cgpa >= 8.0:
        return ["High", "Mid", "Low", "Startup"]
    elif cgpa >= 6.5:
        return ["Mid", "Low", "Startup"]
    else:
        return ["Low", "Startup"]

# ---------------- CARD FUNCTION ----------------
def show_card(row, tag):
    colors = {
        "High": "#22c55e",
        "Mid": "#facc15",
        "Low": "#38bdf8",
        "Startup": "#a855f7"
    }

    skills = str(row.get("required_skills", "")).split(",")

    html = f"""
<div class="card">
  <h4 style="margin:0; font-size:18px;">🏢 {row['company_name']}</h4>

  <div style="margin-top:10px;">
    <span class="badge" style="background:{colors.get(row['company_level'], '#64748b')};">
      {row['company_level']}
    </span>
    <span class="badge" style="background:#334155;">
      {tag}
    </span>
  </div>

  <p style="margin-top:10px; color:#cbd5f5;">📍 {row['location']}</p>

  <p style="margin-top:12px; font-weight:700; color:#f9a8d4;">
    🎯 Required Skills
  </p>

  <div>
    {''.join(f"<span class='skill'>{s.strip()}</span>" for s in skills if s.strip())}
  </div>
</div>
"""

    st.markdown(html, unsafe_allow_html=True)

# ---------------- RESULTS ----------------
if submit:
    base = df[
        (df["stream"] == stream) &
        (df["department"] == dept) &
        (df["company_level"].isin(allowed_levels(cgpa)))
    ].copy()

    order = ["High", "Mid", "Low", "Startup"]
    base["company_level"] = pd.Categorical(
        base["company_level"], order, ordered=True
    )
    base = base.sort_values("company_level")

    best_df = base[base["job_role"] == role]
    alt_df = base[base["job_role"] != role]

    st.markdown("## 🏢 Recommended Companies")

    # -------- Best Matches --------
    if not best_df.empty:
        st.markdown("### 🎯 Best Matches")
        cols = st.columns(2)
        for i, (_, row) in enumerate(best_df.iterrows()):
            with cols[i % 2]:
                show_card(row, "Best Match")

    # -------- Alternate Opportunities --------
    if not alt_df.empty:
        st.markdown("### 🔁 Alternate Opportunities")
        cols = st.columns(2)
        for i, (_, row) in enumerate(alt_df.iterrows()):
            with cols[i % 2]:
                show_card(row, "Alternate Role")
