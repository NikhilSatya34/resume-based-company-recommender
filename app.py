import streamlit as st
import pandas as pd

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Professional Pivot",
    page_icon="fevicon_project.png",
    layout="wide"
)

# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------
if "started" not in st.session_state:
    st.session_state.started = False

# -------------------------------------------------
# HEADER (USED IN BOTH INTRO & MAIN PAGE)
# -------------------------------------------------
def header(show_start_button=False):
    col1, col2, col3 = st.columns([1.4, 7.1, 1.5])

    with col1:
        st.image("fevicon_project.png", width=150)

    with col2:
        st.markdown(
            """
            <div style="display:flex; flex-direction:column; justify-content:center; height:100px;">
                <h1 style="margin:0;">Professional Pivot</h1>
                <p style="color:#94a3b8;font-size:18px;margin:4px 0 0 0;">
                    Resume → Skills → Reality
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        if show_start_button:
            if st.button("🚀 Start Career Analysis"):
                st.session_state.started = True
                st.rerun()

    st.markdown("<hr style='border:1px solid #1f2933;'>", unsafe_allow_html=True)

# -------------------------------------------------
# INTRO PAGE
# -------------------------------------------------
if not st.session_state.started:

    header(show_start_button=True)
    
    st.info(
    "ℹ️ This platform evaluates career readiness, not job availability."
     )
    
    st.markdown("""
    ## 🚀 About the Project

    **Professional Pivot** is a skill-driven career readiness system.
    Unlike traditional job portals, this platform evaluates a student's
    **actual skill preparedness** before suggesting companies.

    Students often rely only on CGPA and resumes, which leads to unrealistic
    job expectations. Professional Pivot bridges this gap by analyzing
    **resume skills**, calculating **skill match percentage**, identifying
    **skill gaps**, and recommending only **achievable company levels**.

    ---

    ## ⚙️ What This Project Does
    - Extracts skills from resume
    - Calculates skill match percentage
    - Displays matched skills & skill gaps
    - Filters companies based on skill readiness
    - Provides realistic career guidance

    ---

    ## 🔄 How It Works
    **Resume → Skill Analysis → Skill % → Skill Gap →  
    Skill-Based Company Filtering → Career Guidance**

    ---

    ## 🔍 Professional Pivot vs Job Portals
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### 🌐 Job Searching Platforms
        - Focus on job listings
        - Same jobs for all users
        - Apply-first approach
        - No readiness feedback
        - May show unrealistic roles
        """)

    with col2:
        st.markdown("""
        ### 🎓 Professional Pivot
        - Focus on career readiness
        - Personalized recommendations
        - Improve-first approach
        - Clear skill gap feedback
        - Shows only realistic companies
        """)

    st.warning(
        "⚠️ Resume is the single source of truth. "
        "If skills don’t match, the system will not force recommendations."
    )

    st.markdown("---")

    st.markdown(
        """
        <p style="text-align:center;color:#9ca3af;font-size:15px;">
            Project developed by <b>B. Nikhil Satya</b><br>
            Department of <b>CSD</b><br>
            Annamacharya University
        </p>
        """,
        unsafe_allow_html=True
    )

# -------------------------------------------------
# MAIN PAGE
# -------------------------------------------------
else:

    # HEADER MUST BE FIRST
    header(show_start_button=False)

    # Back button
    if st.button("⬅ Back"):
        st.session_state.started = False
        st.rerun()

    # -------------------------------------------------
    # LOAD DATA
    # -------------------------------------------------
    @st.cache_data
    def load_data():
        return pd.read_csv("new1.csv")

    df = load_data()

    # -------------------------------------------------
    # INPUT FLOW
    # -------------------------------------------------
    st.subheader("🔍 Student Profile")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        stream = st.selectbox("Stream", sorted(df["stream"].unique()))

    with col2:
        course = st.selectbox(
            "Course",
            sorted(df[df["stream"] == stream]["course"].unique())
        )

    with col3:
        department = st.selectbox(
            "Department",
            sorted(
                df[
                    (df["stream"] == stream) &
                    (df["course"] == course)
                ]["department"].unique()
            )
        )

    with col4:
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

    with col5:
        cgpa = st.slider("CGPA", 5.0, 10.0, 7.0, 0.1)

    resume = st.file_uploader(
        "📄 Upload Resume (Mandatory)",
        type=["txt", "pdf", "docx"]
    )

    submit = st.button("🔍 Validate Profile")

    # -------------------------------------------------
    # HELPER FUNCTIONS
    # -------------------------------------------------
    def skill_match(user, required):
        if not user or not required:
            return 0
        return int(len(user & required) / len(required) * 100)

    def allowed_company_levels(skill_pct):
        if skill_pct >= 80:
            return ["HIGH", "MID"]
        elif skill_pct >= 60:
            return ["MID"]
        elif skill_pct >= 40:
            return ["LOW"]
        else:
            return ["STARTUP", "LOW"]

    # -------------------------------------------------
    # RESULTS
    # -------------------------------------------------
    if submit:

        if not resume:
            st.warning("⚠️ Kindly upload the resume")
            st.stop()

        resume_text = resume.read().decode(errors="ignore").lower()

        all_skills = set(
            ",".join(df["required_skill"].dropna())
            .lower().split(",")
        )
        all_skills = {s.strip() for s in all_skills if s.strip()}

        user_skills = {s for s in all_skills if s in resume_text}

        pre_base = df[
            (df["stream"] == stream) &
            (df["course"] == course) &
            (df["department"] == department) &
            (df["job_role"] == role)
        ].copy()

        if pre_base.empty:
            st.warning("No matching roles found.")
            st.stop()

        pre_base["skill_match"] = pre_base["required_skill"].apply(
            lambda x: skill_match(
                user_skills,
                {s.strip().lower() for s in x.split(",")}
            )
        )

        pre_base["allowed_levels"] = pre_base["skill_match"].apply(
            allowed_company_levels
        )

        base = pre_base[
            pre_base.apply(
                lambda r: r["company_level"] in r["allowed_levels"],
                axis=1
            )
        ]

        avg_skill = int(pre_base["skill_match"].mean())

        st.subheader("📊 Career Reality Check")
        st.info(
            f"Based on your **{avg_skill}% skill match**, "
            f"we are showing **{', '.join(allowed_company_levels(avg_skill))} level companies**."
        )

        cols = st.columns(2)

        for i, (_, row) in enumerate(base.iterrows()):
            required = {s.strip().lower() for s in row["required_skill"].split(",")}
            match = row["skill_match"]

            matched_skills = required & user_skills
            skill_gap = required - user_skills

            with cols[i % 2]:
                st.markdown(f"""
                <div style="
                    background:#020617;
                    padding:22px;
                    border-radius:18px;
                    margin-bottom:24px;
                    box-shadow:0 15px 40px rgba(0,0,0,0.6);
                    color:#e5e7eb;
                ">
                    <h4>🏢 {row['company_name']}</h4>
                    <p>📍 {row['location']} | <b>{row['company_level']}</b></p>
                    <p><b>🎯 Skill Match:</b> {match}%</p>
                </div>
                """, unsafe_allow_html=True)

                st.progress(match / 100)

                st.markdown("#### ✅ Matched Skills")
                st.write(", ".join(matched_skills) if matched_skills else "No matched skills")

                st.markdown("#### ❌ Skill Gap (Skills to Improve)")
                if skill_gap:
                    st.write(", ".join(skill_gap))
                else:
                    st.success("🎉 No skill gap! You are industry ready.")
