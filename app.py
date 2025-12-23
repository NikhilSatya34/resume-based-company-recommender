import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Professional Pivot",
    page_icon="🎓",
    layout="wide"
)

# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------
if "started" not in st.session_state:
    st.session_state.started = False

# -------------------------------------------------
# INTRO / ONBOARDING SCREEN
# -------------------------------------------------
if not st.session_state.started:

    st.markdown("<br><br>", unsafe_allow_html=True)

    # Title
    st.markdown(
        "<h1 style='text-align:center;'>🎓 Professional Pivot</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<h4 style='text-align:center; color:gray;'>"
        "A resume-driven career validation platform"
        "</h4>",
        unsafe_allow_html=True
    )

    st.markdown("---")

    # Purpose / Description
    st.subheader("📌 Project Description")

    st.write(
        "**Professional Pivot** is a resume-driven career validation platform "
        "designed to give students a **realistic understanding of their job readiness**. "
        "Unlike traditional job recommendation systems that focus on user satisfaction, "
        "this platform follows an **honesty-first approach**, where the resume and skills "
        "act as the primary truth source."
    )

    st.write(
        "The system analyzes the skills present in a student’s resume and strictly matches "
        "them with real-world job role requirements across multiple domains such as "
        "**Engineering, Medical, Pharmacy, Science, and Management**, for both **UG and PG** programs."
    )

    st.write(
        "Professional Pivot does not guarantee recommendations for every user. "
        "If a student’s selected stream, department, or job role does not align with the "
        "skills found in their resume, the system clearly highlights the mismatch instead "
        "of providing misleading results."
    )

    st.write(
        "The platform is powered by a large-scale dataset containing "
        "**11,000+ real-world company records**, categorized into **High, Mid, Low, and Startup** levels. "
        "This strict and transparent approach prepares students to face real industry standards "
        "and make informed career decisions."
    )

    st.markdown("""
    - 📄 **Your resume is the primary truth source**
    - 🧠 Skills in your resume are matched with real job expectations
    - ⚠️ If your profile is weak or mismatched, the system will **not please you**
    - 🚀 Only realistic opportunities (including startups) are shown
    - 🎓 Helps students understand **where they actually stand**, not where they wish to be
    """)
    
    st.info(
        "⚠️ This platform is intentionally strict. It reflects reality, not false motivation."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Get Started Button
    center_col = st.columns([1, 2, 1])[1]
    with center_col:
        if st.button("🚀 Get Started", use_container_width=True):
            st.session_state.started = True
            st.rerun()

    st.markdown("---")

    # Footer Credit
    st.markdown(
        "<p style='text-align:center; color:#94a3b8; font-size:14px;'>"
        "Project developed by <b>B. Nikhil Satya</b> – CSD<br>"
        "<b>25ALCSD002</b>"
        "</p>",
        unsafe_allow_html=True
    )

# -------------------------------------------------
# MAIN APP
# -------------------------------------------------
else:

    # ---------------- CSS ----------------
    st.markdown("""
    <style>
    .card {
        background: linear-gradient(145deg, #020617, #0f172a);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 24px;
        box-shadow: 0 18px 45px rgba(0,0,0,0.65);
        color: #e5e7eb;
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
        return pd.read_csv("new1.csv")

    df = load_data()

    # ---------------- HEADER ----------------
    st.title("🎓 Professional Pivot")
    st.caption("Resume > Skills > Reality")


    # ---------------- INPUTS ----------------
    st.subheader("🔍 Student Profile")
    
    c1, c2, c3, c4, c5 = st.columns(5)
    
    with c1:
        stream = st.selectbox(
            "Stream",
            sorted(df["stream"].unique())
        )
    
    with c2:
         course = st.selectbox(
            "Course",
             sorted(
                df[df["stream"] == stream]["course"].unique()
            )
         )
    
    with c3:
        department = st.selectbox(
            "Department",
            sorted(
                df[
                    (df["stream"] == stream) &
                    (df["course"] == course)
                    ]["department"].unique()
            )
         )
    
    with c4:
        role = st.selectbox(
            "Job Role",
             sorted(
                df[
                    (df["stream"] == stream) &
                    (df["course"] == course) &
                    (df["department"] == department)
                ]["job_role"].unique()
            )
        )
    
    resume = st.file_uploader(
        "📄 Upload Resume (Mandatory)",
        type=["txt", "pdf", "docx"]
    )

    submit = st.button("🔍 Validate Profile")

    # ---------------- SKILL EXTRACTION ----------------
    user_skills = []

    if resume:
        text = resume.read().decode(errors="ignore").lower()
        known_skills = set(
            ",".join(df["required_skill"].dropna()).lower().split(",")
        )
        user_skills = [s for s in known_skills if s.strip() and s in text]

    # ---------------- HELPER FUNCTIONS ----------------
    def allowed_levels(cgpa):
        if cgpa >= 8.0:
            return ["High","Mid","Low","Startup"]
        elif cgpa >= 6.5:
            return ["Mid","Low","Startup"]
        else:
            return ["Startup"]

    def calculate_skill_match(user, required):
        if not user or not required:
            return 0
        return int((len(set(user) & set(required)) / len(set(required))) * 100)

    def skill_bar(percent):
        return "█" * (percent // 10) + "░" * (10 - percent // 10)

    # ---------------- CARD ----------------
    def show_card(row, tag):

        required = [s.strip() for s in row["required_skill"].split(",")]
        match = calculate_skill_match(user_skills, required)

        html = f"""
        <div class="card">
            <h4>🏢 {row['company_name']}</h4>
            <span class="badge">{row['company_level']}</span>
            <span class="badge">{tag}</span>
            <p>📍 {row['location']}</p>
            <p><b>Skill Match:</b> {match}%</p>
            <pre>{skill_bar(match)}</pre>
            <b>Required Skills</b><br>
            {"".join(f"<span class='skill'>{s}</span>" for s in required)}
        </div>
        """
        components.html(html, height=350)

    # ---------------- RESULTS ----------------
    if submit:

        base = df[
            (df["stream"] == stream) &
            (df["department"] == department) &
            (df["company_level"].isin(allowed_levels(cgpa)))
        ]

        best = base[base["job_role"] == role]

        st.subheader("📌 Career Reality Check")

        if best.empty:
            st.warning(
                "⚠️ Your profile does not meet role expectations. "
                "Only startup-level opportunities are realistic at this stage."
            )

        cols = st.columns(2)
        for i, (_, r) in enumerate(best.iterrows()):
            with cols[i % 2]:
                show_card(r, "Match")
