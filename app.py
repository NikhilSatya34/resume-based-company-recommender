import streamlit as st
import pandas as pd

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
# INTRO PAGE
# -------------------------------------------------
if not st.session_state.started:

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        "<h1 style='text-align:center;'>🎓 Professional Pivot</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<h4 style='text-align:center;color:gray;'>Resume → Skills → Reality</h4>",
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.write(
        "**Professional Pivot** is not a job portal. "
        "It is a **career reality-check platform** that validates "
        "a student’s resume against real job requirements."
    )

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

        # ---------- Resume text extraction (SAFE) ----------
        resume_text = resume.read().decode(errors="ignore").lower()

        # ---------- Build skill universe dynamically ----------
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
        shown = False

        for i, (_, row) in enumerate(base.iterrows()):
            required = {s.strip().lower() for s in row["required_skill"].split(",")}
            match = skill_match(user_skills, required)

            # Show even low match (honesty mode)
            shown = True

            skill_html = ""
            for s in required:
                if s in user_skills:
                    mark, color = "✔", "#22c55e"
                else:
                    mark, color = "❌", "#ef4444"

                skill_html += f"""
                <span style="
                    background:#1e293b;
                    padding:6px 12px;
                    border-radius:999px;
                    margin:4px;
                    display:inline-block;
                    color:white;
                ">
                <span style="color:{color};font-weight:bold;">{mark}</span> {s}
                </span>
                """

            with cols[i % 2]:
                st.markdown(f"""
                <div style="
                    background:#020617;
                    padding:20px;
                    border-radius:18px;
                    margin-bottom:20px;
                    box-shadow:0 15px 40px rgba(0,0,0,0.6);
                    color:#e5e7eb;
                ">
                    <h4>🏢 {row['company_name']}</h4>
                    <p>📍 {row['location']} | <b>{row['company_level']}</b></p>
                    <p style="margin:6px 0;">
                        🎯 <b>Role:</b> {selected_role}
                    </p>
                    <p><b>Skill Match:</b> {match}%</p>
                    <b>Required Skills</b><br>
                    {skill_html}
                </div>
                """, unsafe_allow_html=True)

        if not shown:
            st.warning(
                "⚠️ Your resume does not align with this role. "
                "Please upskill or update your resume."
            )
