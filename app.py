import streamlit as st
import pandas as pd
import pdfplumber
from docx import Document

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Career Readiness & Company Recommender",
    layout="centered"
)

st.title("🎓 Career Readiness & Company Recommender")
st.caption("Find companies based on stream, role, CGPA & resume skills")

# ---------------- LOAD CSV DATA ----------------
def load_data():
    try:
        df = pd.read_csv(
            "data/Companies_CGPA.csv",
            encoding="utf-8",
        )
        return df
    except Exception as e:
        st.error(f"CSV Load Error: {e}")
        st.stop()

df = load_data()

st.success("Company data loaded successfully!")

# ---------------- SKILLS LIST ----------------
SKILLS = [
    "python", "java", "machine learning", "data science", "sql",
    "excel", "statistics", "deep learning", "power bi",
    "tableau", "html", "css", "javascript"
]

# ---------------- RESUME TEXT EXTRACTION ----------------
def extract_resume_text(uploaded_file):
    text = ""
    if uploaded_file.type == "application/pdf":
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    else:
        doc = Document(uploaded_file)
        for para in doc.paragraphs:
            text += para.text + " "
    return text.lower()

def extract_skills(resume_text):
    return [skill for skill in SKILLS if skill in resume_text]

# ---------------- UI FILTERS ----------------
st.subheader("🔍 Find Suitable Companies")

col1, col2 = st.columns(2)

with col1:
    selected_stream = st.selectbox(
        "Select Stream",
        sorted(df["stream"].dropna().unique())
    )

with col2:
    user_cgpa = st.slider("Enter Your CGPA", 5.0, 10.0, 7.0, 0.1)

filtered_stream = df[df["stream"] == selected_stream]

selected_department = st.selectbox(
    "Select Department",
    sorted(filtered_stream["department"].dropna().unique())
)

filtered_dept = filtered_stream[
    filtered_stream["department"] == selected_department
]

selected_role = st.selectbox(
    "Select Job Role",
    sorted(filtered_dept["job_role"].dropna().unique())
)

# ---------------- CGPA LOGIC ----------------
def company_level_from_cgpa(cgpa):
    if cgpa >= 8.0:
        return "High"
    elif cgpa >= 6.5:
        return "Mid"
    else:
        return "Low"

eligible_level = company_level_from_cgpa(user_cgpa)

# ---------------- RESUME UPLOAD ----------------
st.subheader("📄 Optional: Upload Your Resume")

uploaded_resume = st.file_uploader(
    "Upload PDF or DOCX resume",
    type=["pdf", "docx"]
)

resume_skills = []
if uploaded_resume:
    resume_text = extract_resume_text(uploaded_resume)
    resume_skills = extract_skills(resume_text)

    st.success("Resume uploaded successfully!")
    st.write("**Skills found in resume:**", resume_skills if resume_skills else "No skills detected")

# ---------------- FINAL FILTER ----------------
result_df = filtered_dept[
    (filtered_dept["job_role"] == selected_role) &
    (filtered_dept["company_level"].str.lower() == eligible_level.lower())
]

# ---------------- RESULTS ----------------
st.markdown("### 🏢 Recommended Companies")

if result_df.empty:
    st.info("No matching companies found. Try changing CGPA, role or department.")
else:
    st.dataframe(
        result_df[["company_name", "company_level", "location"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )

# ---------------- FOOTER ----------------
st.markdown("---")
st.caption("🚀 Built with Streamlit | Beginner-friendly career recommender")
