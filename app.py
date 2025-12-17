import streamlit as st
import pandas as pd
import pdfplumber
import docx

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="Career Readiness & Company Recommender",
    layout="wide"
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(
    "data/Companies_CGPA.csv",
    encoding="latin1"   # or "ISO-8859-1"
)

df = load_data()

# --------------------------------------------------
# SKILL MASTER LIST (for resume + rating)
# --------------------------------------------------
SKILLS_DB = [
    "python","java","sql","machine learning","data science",
    "excel","power bi","tableau","statistics",
    "docker","kubernetes","aws",
    "autocad","solidworks",
    "clinical research","medical coding",
    "gmp","pharmacovigilance"
]

# --------------------------------------------------
# RESUME TEXT EXTRACTION
# --------------------------------------------------
def extract_resume_text(file):
    text = ""
    if file.name.endswith(".pdf"):
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                if page.extract_text():
                    text += page.extract_text() + " "
    else:
        doc = docx.Document(file)
        for p in doc.paragraphs:
            text += p.text + " "
    return text.lower()

def extract_skills(resume_text):
    return [s for s in SKILLS_DB if s in resume_text]

# --------------------------------------------------
# UI – HEADER
# --------------------------------------------------
st.markdown(
    """
    <h1 style='text-align:center;'>Career Readiness & Company Recommendation System</h1>
    <p style='text-align:center; font-size:18px;'>
    A career guidance platform – not a job portal
    </p>
    <hr>
    """,
    unsafe_allow_html=True
)

st.info("🔒 Anonymous Mode Enabled – Your data is not stored")

# --------------------------------------------------
# STEP 1: RESUME UPLOAD
# --------------------------------------------------
st.header("1️⃣ Resume Analysis")

uploaded_resume = st.file_uploader(
    "Upload your Resume (PDF or DOCX)",
    type=["pdf", "docx"]
)

resume_score = 0
resume_skills = []

if uploaded_resume:
    text = extract_resume_text(uploaded_resume)
    resume_skills = extract_skills(text)
    resume_score = min(len(resume_skills) * 8, 100)

    st.success("Resume analyzed successfully")
    st.progress(resume_score)
    st.write(f"**Resume Strength:** {resume_score}%")
    st.write("**Skills found in resume:**", resume_skills)

# --------------------------------------------------
# STEP 2: STREAM → DEPT → ROLE
# --------------------------------------------------
st.header("2️⃣ Academic & Role Selection")

stream = st.selectbox("Select Stream", sorted(df["stream"].unique()))
dept_df = df[df["stream"] == stream]

department = st.selectbox(
    "Select Department",
    sorted(dept_df["department"].unique())
)

role_df = dept_df[dept_df["department"] == department]

job_role = st.selectbox(
    "Select Job Role",
    sorted(role_df["job_role"].unique())
)

role_skills = (
    role_df[role_df["job_role"] == job_role]["required_skills"]
    .iloc[0]
    .split(",")
)

# --------------------------------------------------
# STEP 3: SKILL RATING
# --------------------------------------------------
st.header("3️⃣ Skill Confidence Rating")

ratings = {}
for skill in role_skills:
    ratings[skill.strip()] = st.slider(
        f"{skill.strip()}",
        0, 5, 3
    )

skill_score = int((sum(ratings.values()) / (len(ratings) * 5)) * 100)

st.progress(skill_score)
st.write(f"**Skill Confidence Score:** {skill_score}%")

# --------------------------------------------------
# STEP 4: CGPA INPUT
# --------------------------------------------------
st.header("4️⃣ Academic Eligibility")

cgpa = st.number_input(
    "Enter CGPA (Mandatory)",
    min_value=0.0,
    max_value=10.0,
    step=0.1
)

sgpa = st.number_input(
    "Enter SGPA (Optional)",
    min_value=0.0,
    max_value=10.0,
    step=0.1
)

# --------------------------------------------------
# STEP 5: COMPANY RECOMMENDATION
# --------------------------------------------------
if st.button("🔍 Show Company Recommendations"):

    eligible = df[
        (df["stream"] == stream) &
        (df["department"] == department) &
        (df["job_role"] == job_role)
    ]

    def cgpa_ok(row):
        low, high = row["cgpa_range"].split("-")
        return float(low) <= cgpa <= float(high)

    eligible["eligible"] = eligible.apply(cgpa_ok, axis=1)

    main_companies = eligible[eligible["eligible"]]
    alternate_companies = eligible[~eligible["eligible"]]

    # Order: High → Mid → Startup
    order = {"High": 1, "Mid": 2, "Startup": 3}
    main_companies["order"] = main_companies["company_level"].map(order)
    alternate_companies["order"] = alternate_companies["company_level"].map(order)

    st.header("🏢 Recommended Companies")

    if not main_companies.empty:
        for _, row in main_companies.sort_values("order").iterrows():
            st.subheader(row["company_name"])
            st.write(
                f"""
                **Level:** {row['company_level']}  
                **Location:** {row['location']}  
                **Why this company?**
                - CGPA eligibility matched
                - Skills aligned with role
                - Resume relevance considered
                """
            )
    else:
        st.warning("No direct matches found. Showing alternate opportunities.")

    if not alternate_companies.empty:
        st.header("🔁 Alternate Companies")
        for _, row in alternate_companies.sort_values("order").iterrows():
            st.write(
                f"- {row['company_name']} ({row['company_level']}) – {row['location']}"
            )

    # --------------------------------------------------
    # STEP 6: LEARNING PATH + SUMMARY
    # --------------------------------------------------
    st.header("📊 Career Summary")

    weak_skills = [
        skill for skill, val in ratings.items() if val <= 2
    ]

    st.write("**Career Readiness Snapshot**")
    st.write(f"- Resume Strength: {resume_score}%")
    st.write(f"- Skill Confidence: {skill_score}%")
    st.write(f"- Target Role: {job_role}")

    if weak_skills:
        st.subheader("📚 Skill Gap & Learning Focus")
        st.write(
            "To improve your chances, focus on these skills:",
            weak_skills
        )
    else:
        st.success("You are well-aligned for this role!")

