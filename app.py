import streamlit as st
import pandas as pd
import pdfplumber
from docx import Document

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Career Readiness", layout="wide")

# ---------------- THEME / CSS ----------------
st.markdown("""
<style>
.card {
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(14px);
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 20px;
    box-shadow: 0 12px 30px rgba(0,0,0,0.45);
    transition: 0.3s ease;
}
.card:hover {
    transform: translateY(-6px);
}
.badge {
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    color: white;
    margin-right: 6px;
}
.logo {
    width: 52px;
    height: 52px;
    background: white;
    padding: 6px;
    border-radius: 12px;
}
.flex {
    display: flex;
    gap: 14px;
    align-items: center;
}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.title("🎓 Career Readiness & Company Recommender")
st.caption("Smart recommendations with professional UI")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    return pd.read_csv("data/Companies_CGPA.csv", encoding="utf-8")

df = load_data()
st.success("Company data loaded successfully!")

# ---------------- LOGO HELPER ----------------
def get_logo(company):
    name = company.lower().replace(" ", "")
    known = {
        "tcs": "tcs.com",
        "infosys": "infosys.com",
        "wipro": "wipro.com",
        "accenture": "accenture.com",
        "cognizant": "cognizant.com",
        "capgemini": "capgemini.com",
        "ibm": "ibm.com",
        "amazon": "amazon.com",
        "microsoft": "microsoft.com",
        "google": "google.com",
        "deloitte": "deloitte.com"
    }
    for k, v in known.items():
        if k in name:
            return f"https://logo.clearbit.com/{v}"
    return f"https://logo.clearbit.com/{name}.com"

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
        for p in doc.paragraphs:
            text += p.text + " "
    return text.lower()

def extract_skills(text):
    return [s for s in SKILLS if s in text]

# ---------------- FILTER UI ----------------
st.subheader("🔍 Find Suitable Companies")

c1, c2, c3 = st.columns(3)

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

# ---------------- RESUME UPLOAD (OPTIONAL) ----------------
st.markdown("### 📄 Optional: Upload Your Resume")

uploaded_resume = st.file_uploader(
    "Upload PDF or DOCX resume",
    type=["pdf","docx"]
)

if uploaded_resume:
    text = extract_resume_text(uploaded_resume)
    skills = extract_skills(text)
    st.success("Resume uploaded successfully!")
    st.write("**Skills detected:**", skills if skills else "No matching skills found")

# ---------------- SUBMIT BUTTON ----------------
submit = st.button("🔍 Find Companies")

# ---------------- CARD FUNCTION ----------------
def show_card(row, tag):
    colors = {
        "High": "#22c55e",
        "Mid": "#facc15",
        "Low": "#3b82f6",
        "Startup": "#a855f7"
    }
    color = colors.get(row["company_level"], "#64748b")

    st.markdown(f"""
    <div class="card">
        <div class="flex">
            <img src="{get_logo(row['company_name'])}"
                 class="logo"
                 onerror="this.style.display='none'"/>
            <div>
                <h4 style="margin:0;">{row['company_name']}</h4>
                <div style="margin-top:6px;">
                    <span class="badge" style="background:{color};">
                        {row['company_level']}
                    </span>
                    <span class="badge" style="background:#334155;">
                        {tag}
                    </span>
                </div>
                <p style="margin-top:8px;">📍 {row['location']}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---------------- RESULTS (ONLY AFTER SUBMIT) ----------------
if submit:
    base_df = df[
        (df["stream"] == stream) &
        (df["department"] == department)
    ]

    order = ["High", "Mid", "Low", "Startup"]
    base_df["company_level"] = pd.Categorical(
        base_df["company_level"],
        categories=order,
        ordered=True
    )

    # Best Matches: SAME ROLE, ALL LEVELS
    best_df = base_df[
        base_df["job_role"] == role
    ].sort_values("company_level")

    # Alternate: OTHER ROLES, ALL LEVELS
    alt_df = base_df[
        base_df["job_role"] != role
    ].sort_values("company_level")

    st.markdown("## 🏢 Recommended Companies")

    if not best_df.empty:
        st.subheader("🎯 Best Matches (High → Startup)")
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
        st.info("No companies found for this selection.")

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("🚀 Final Career Recommendation System | Built with Streamlit")
