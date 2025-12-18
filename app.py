import streamlit as st
import pandas as pd
import pdfplumber
from docx import Document
import streamlit.components.v1 as components

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Career Readiness", layout="wide")

# ---------------- CSS ----------------
st.markdown("""
<style>

/* Base card */
.card {
    color: #e5e7eb;
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 20px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.6);
    border: 1px solid rgba(255,255,255,0.08);
    transition: all 0.3s ease;
}

/* Company level colors */
.card.high {
    background: linear-gradient(135deg, #064e3b, #022c22);
}
.card.mid {
    background: linear-gradient(135deg, #78350f, #451a03);
}
.card.low {
    background: linear-gradient(135deg, #1e3a8a, #020617);
}
.card.startup {
    background: linear-gradient(135deg, #581c87, #2e1065);
}

.card:hover {
    transform: translateY(-6px) scale(1.01);
}

.badge {
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    color: white;
    margin-right: 6px;
}

.skill {
    display: inline-block;
    padding: 4px 10px;
    margin: 4px 6px 0 0;
    font-size: 12px;
    border-radius: 14px;
    background: rgba(255,255,255,0.15);
    color: #e5e7eb;
}

</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.title("🎓 Career Readiness & Company Recommender")
st.caption("Smart recommendations based on CGPA, role & required skills")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    return pd.read_csv("data/Companies_CGPA.csv", encoding="utf-8")

df = load_data()

# ---------------- RESUME FUNCTIONS ----------------
SKILLS = [
    "python","java","sql","machine learning","data science",
    "excel","power bi","tableau","deep learning","statistics"
]

def extract_resume_text(file):
    text = ""
    if file.type == "application/pdf":
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    else:
        doc = Document(file)
        for para in doc.paragraphs:
            text += para.text + " "
    return text.lower()

def extract_skills(text):
    return [s for s in SKILLS if s in text]

# ---------------- FILTER UI ----------------
st.subheader("🔍 Find Suitable Companies")

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
        sorted(df[
            (df["stream"] == stream) &
            (df["department"] == department)
        ]["job_role"].unique())
    )

with c4:
    cgpa = st.slider("Your CGPA", 5.0, 10.0, 7.0, 0.1)

# ---------------- RESUME UPLOAD ----------------
st.markdown("### 📄 Optional: Upload Your Resume")
uploaded_resume = st.file_uploader("Upload PDF or DOCX", type=["pdf","docx"])

if uploaded_resume:
    text = extract_resume_text(uploaded_resume)
    resume_skills = extract_skills(text)
    st.write("**Skills detected from resume:**", resume_skills if resume_skills else "No matching skills")

# ---------------- SUBMIT ----------------
submit = st.button("🔍 Find Companies")

# ---------------- CGPA LOGIC ----------------
def allowed_levels(cgpa):
    if cgpa >= 8.0:
        return ["High","Mid","Low","Startup"]
    elif cgpa >= 6.5:
        return ["Mid","Low","Startup"]
    else:
        return ["Low","Startup"]

# ---------------- CARD ----------------
def show_card(row, tag):
    skills = str(row.get("required_skills", "")).split(",")

    html = f"""
    <div class="card {row['company_level'].lower()}">
        <h4 style="margin:0;">🏢 {row['company_name']}</h4>

        <div style="margin-top:6px;">
            <span class="badge" style="background:#16a34a;">
                {row['company_level']}
            </span>
            <span class="badge" style="background:#334155;">
                {tag}
            </span>
        </div>

        <p style="margin-top:8px;">📍 {row['location']}</p>

        <p style="margin-top:10px; font-weight:600;">🧠 Required Skills</p>
        <div>
            {''.join([f"<span class='skill'>{s.strip()}</span>" for s in skills if s.strip()])}
        </div>
    </div>
    """

    components.html(html, height=360)

# ---------------- RESULTS ----------------
if submit:
    base = df[
        (df["stream"] == stream) &
        (df["department"] == department)
    ]

    base = base[base["company_level"].isin(allowed_levels(cgpa))]

    order = ["High","Mid","Low","Startup"]
    base["company_level"] = pd.Categorical(base["company_level"], order, ordered=True)

    best_df = base[base["job_role"] == role].sort_values("company_level")
    alt_df  = base[base["job_role"] != role].sort_values("company_level")

    st.markdown("## 🏢 Recommended Companies")

    if not best_df.empty:
        st.subheader("🎯 Best Matches")
        cols = st.columns(2)
        for i, (_, r) in enumerate(best_df.drop_duplicates().iterrows()):
            with cols[i % 2]:
                show_card(r, "Best Match")

    if not alt_df.empty:
        st.subheader("🔁 Alternate Opportunities")
        cols = st.columns(2)
        for i, (_, r) in enumerate(alt_df.drop_duplicates().iterrows()):
            with cols[i % 2]:
                show_card(r, "Alternate Role")

    if best_df.empty and alt_df.empty:
        st.info("No companies found for this CGPA and role.")

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("🚀 Career Recommendation System | Role & Skill Focused | Built with Streamlit")
