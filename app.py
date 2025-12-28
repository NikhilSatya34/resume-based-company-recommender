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
# INTRO PAGE
# -------------------------------------------------
# ---------------- INTRO PAGE ----------------
if not st.session_state.started:

    col1, col2 = st.columns([1, 7])

    with col1:
        st.image("fevicon_project.png", width=80)

    with col2:
        st.markdown(
            """
            <h1 style="margin-bottom:0;">Professional Pivot</h1>
            <p style="color:gray;font-size:18px;margin-top:0;">
            Resume → Skills → Reality
            </p>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    st.write("""
    **Professional Pivot** is a smart career recommendation system that helps students
    make informed and realistic career decisions. The system analyzes a student's
    academic profile, skills, and interests to suggest suitable companies and career paths.
    """)

    st.info(
        "⚠️ Resume is the single source of truth. "
        "If skills don’t match, the system will not force recommendations."
    )

    if st.button("🚀 Get Started", use_container_width=True):
        st.session_state.started = True
        st.rerun()

    st.markdown("---")
    st.markdown(
        "<p style='text-align:center;color:#94a3b8;'>"
        "Project developed by <b>B. Nikhil Satya</b> – CSD | <b>25ALCSD002</b>"
        "</p>",
        unsafe_allow_html=True
    )

# -------------------------------------------------
# MAIN APP
# -------------------------------------------------
else:

    # Back button + Header
    c1, c2 = st.columns([1, 9])
    with c1:
        if st.button("⬅ Back"):
            st.session_state.started = False
            st.rerun()

    with c2:
        st.markdown(
            "<h1 style='margin-bottom:0;'>🎓 Professional Pivot</h1>"
            "<p style='color:#94a3b8;'>Resume → Skills → Reality</p>",
            unsafe_allow_html=True
        )

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
    # RESULTS
    # -------------------------------------------------
    if submit:

        if not resume:
            st.warning("⚠️ Kindly Upload the Resume")
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

        base = df[
            (df["stream"] == stream) &
            (df["course"] == course) &
            (df["department"] == department) &
            (df["job_role"] == role)
        ]

        st.subheader("📊 Career Reality Check")

        if base.empty:
            st.warning("No matching roles found for selected inputs.")
            st.stop()

        cols = st.columns(2)

        for i, (_, row) in enumerate(base.iterrows()):
            required = {s.strip().lower() for s in row["required_skill"].split(",")}
            match = skill_match(user_skills, required)

            skill_html = ""
            for s in required:
                if s in user_skills:
                    mark, color = "✔", "#22c55e"
                else:
                    mark, color = "❌", "#ef4444"

                skill_html += f"""
                <span style="
                    background:#1e293b;
                    padding:6px 14px;
                    border-radius:999px;
                    margin:6px;
                    display:inline-flex;
                    align-items:center;
                    gap:6px;
                    color:white;
                    font-size:13px;
                ">
                    <span style="color:{color};font-weight:bold;">{mark}</span>{s}
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
                    color:#e5e7eb;
                ">
                    <h4>🏢 {row['company_name']}</h4>
                    <p>📍 {row['location']} | <b>{row['company_level']}</b></p>
                    <p>🎯 <b>Selected Role:</b> {role} </p>
                    <p><b>Skill Match:</b> {match}%</p>
                    <b>Required Skills</b>
                    <div style="
                        display:flex;
                        flex-wrap:wrap;
                        gap:10px;
                       margin-top:10px;
                    ">
                       {skill_html}
                </div>
                """, unsafe_allow_html=True)
