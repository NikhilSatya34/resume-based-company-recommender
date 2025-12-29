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
# LOAD DATA
# -------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_csv("new1.csv")

df = load_data()

# -------------------------------------------------
# COMMON HEADER (INTRO + MAIN PAGE)
# -------------------------------------------------
def header(show_back=False):
    c1, c2, c3 = st.columns([1, 8, 2])

    with c1:
        st.image("fevicon_project.png", width=65)

    with c2:
        st.markdown(
            """
            <h1 style="margin-bottom:0;">Professional Pivot</h1>
            <p style="color:#94a3b8;margin-top:0;">
            Resume → Skills → Reality
            </p>
            """,
            unsafe_allow_html=True
        )

    with c3:
        if show_back:
            if st.button("⬅ Back"):
                st.session_state.started = False
                st.rerun()

    st.markdown("<hr style='border:1px solid #1f2933;'>", unsafe_allow_html=True)

# -------------------------------------------------
# INTRO PAGE
# -------------------------------------------------
if not st.session_state.started:

    header()

    st.markdown("""
    ## 🚀 About the Project

    **Professional Pivot** is a skill-driven career readiness and recommendation system.
    Unlike job portals that only list openings, this platform evaluates a student’s **actual
    skill preparedness** before suggesting companies.

    Many students rely only on CGPA and resumes, leading to unrealistic job expectations
    and repeated rejections. Professional Pivot bridges this gap by analyzing **resume skills,
    skill match percentage, and skill gaps** to recommend only **achievable company levels**.
    """)

    st.markdown("""
    ## ⚙️ What This Project Does
    - Extracts skills from resume
    - Calculates skill match percentage
    - Displays matched skills & skill gaps
    - Filters companies based on skill readiness
    - Provides realistic career direction
    """)

    st.markdown("""
    ## 🔄 How It Works
    **Resume → Skill Analysis → Skill % → Skill Gap →  
    Skill-Based Company Filtering → Career Guidance**
    """)

    st.markdown("## 🔍 Professional Pivot vs Job Portals")

    st.markdown("""
    | Job Searching Platforms | Professional Pivot |
    |------------------------|--------------------|
    | Focus on job listings | Focus on career readiness |
    | Same jobs for all users | Personalized recommendations |
    | Apply-first approach | Improve-first approach |
    | No readiness feedback | Clear skill gap feedback |
    | May show unrealistic roles | Shows only realistic companies |
    """)

    st.warning(
        "⚠️ Resume is the single source of truth. "
        "If skills don’t match, the system will not force recommendations."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.button(
        "🚀 Start Career Analysis",
        on_click=lambda: st.session_state.update(started=True)
    )

    st.markdown(
        "<br><p style='text-align:center;color:#94a3b8;'>"
        "Project developed by <b>B. Nikhil Satya</b> – CSD | Annamacharya University"
        "</p>",
        unsafe_allow_html=True
    )

# -------------------------------------------------
# MAIN PAGE
# -------------------------------------------------
else:

    header(show_back=True)

    st.subheader("🔎 Student Profile")

    # Only streams present in dataset (PG auto-hidden)
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
    # RESULTS
    # -------------------------------------------------
    if submit:

        if not resume:
            st.warning("⚠️ Kindly upload your resume")
            st.stop()

        resume_text = resume.read().decode(errors="ignore").lower()

        all_skills = set(
            ",".join(df["required_skill"].dropna())
            .lower().split(",")
        )
        all_skills = {s.strip() for s in all_skills if s.strip()}

        user_skills = {s for s in all_skills if s in resume_text}

        def skill_match(user, required):
            if not user or not required:
                return 0
            return int(len(user & required) / len(required) * 100)

        pre_base = df[
            (df["stream"] == stream) &
            (df["course"] == course) &
            (df["department"] == department)
        ]

        st.subheader("📊 Career Reality Check")

        results = []

        for _, row in pre_base.iterrows():
            required = {s.strip().lower() for s in row["required_skill"].split(",")}
            match = skill_match(user_skills, required)
            results.append((row, match))

        if not results:
            st.warning("No matching data found.")
            st.stop()

        avg_skill = sum(m for _, m in results) // len(results)

        if avg_skill >= 80:
            allowed_levels = ["high", "mid"]
        elif avg_skill >= 60:
            allowed_levels = ["mid"]
        else:
            allowed_levels = ["low", "startup"]

        st.info(
            f"Based on your **{avg_skill}% skill match**, "
            f"we are showing **{', '.join(allowed_levels).upper()}** level companies."
        )

        base = pre_base[
            (pre_base["job_role"] == role) &
            (pre_base["company_level"].str.lower().isin(allowed_levels))
        ]

        # Fallback if strict filtering fails
        if base.empty:
            st.warning(
                "⚠️ Exact role matches are limited. "
                "Showing similar companies based on your skill readiness."
            )

            base = pre_base[
                pre_base["company_level"].str.lower().isin(allowed_levels)
            ].head(5)

        cols = st.columns(2)

        for i, (_, row) in enumerate(base.iterrows()):
            required = {s.strip().lower() for s in row["required_skill"].split(",")}
            match = skill_match(user_skills, required)

            missing = required - user_skills

            skill_html = ""
            for s in required:
                mark = "✔" if s in user_skills else "❌"
                color = "#22c55e" if s in user_skills else "#ef4444"
                skill_html += f"""
                <span style="
                    background:#1e293b;
                    padding:6px 14px;
                    border-radius:999px;
                    margin:6px;
                    display:inline-block;
                    color:white;
                    font-size:13px;
                ">
                <span style="color:{color};font-weight:bold;">{mark}</span> {s}
                </span>
                """

            with cols[i % 2]:
                st.markdown(f"""
                <div style="
                    background:#020617;
                    padding:22px;
                    border-radius:18px;
                    margin-bottom:24px;
                    box-shadow:0 15px 40px rgba(0,0,0,0.6);
                ">
                    <h4>🏢 {row['company_name']}</h4>
                    <p>📍 {row['location']} | <b>{row['company_level']}</b></p>
                    <p><b>Skill Match:</b> {match}%</p>

                    <div style="background:#1e293b;border-radius:10px;">
                        <div style="
                            width:{match}%;
                            background:#22c55e;
                            padding:6px;
                            border-radius:10px;
                            text-align:right;
                            color:black;
                        ">
                        {match}%
                        </div>
                    </div>

                    <p><b>Required Skills</b></p>
                    {skill_html}

                    <p style="color:#fca5a5;">
                    <b>Skill Gap:</b> {', '.join(missing) if missing else 'None'}
                    </p>
                </div>
                """, unsafe_allow_html=True)
