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

    st.markdown(
        "<h1 style='text-align:center;'>🎓 Professional Pivot</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<h4 style='text-align:center; color:gray;'>"
        "Resume-driven career validation platform"
        "</h4>",
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.subheader("📌 Project Description")

    st.write(
        "**Professional Pivot** is not a normal job recommendation website. "
        "It is a **career validation platform** designed to show students "
        "a **realistic view of their job readiness**."
    )

    st.write(
        "The system strictly analyzes skills from the uploaded resume and "
        "matches them with real-world job requirements across "
        "**Engineering, Medical, Pharmacy, Science, and Management** domains "
        "for both **UG and PG** programs."
    )

    st.write(
        "If the resume does not match the selected stream, course, department, "
        "or job role, the system **does not force recommendations**. "
        "Instead, it highlights mismatches and shows only realistic options."
    )

    st.info(
        "⚠️ This platform is intentionally strict. "
        "It reflects industry reality, not false motivation."
    )

    center_col = st.columns([1, 2, 1])[1]
    with center_col:
        if st.button("🚀 Get Started", use_container_width=True):
            st.session_state.started = True
            st.rerun()

    st.markdown("---")

    st.markdown(
        "<p style='text-align:center; color:#94a3b8; font-size:14px;'>"
        "Project developed by <b>B. Nikhil Satya</b> – CSD<br>"
        "<b>25ALCSD002</b>"
        "</p>",
        unsafe_allow_html=True
    )

# -------------------------------------------------
# MAIN APPLICATION
# -------------------------------------------------
else:

    # ---------------- BACK BUTTON ----------------
    col1, col2 = st.columns([1, 9])
    with col1:
        if st.button("⬅ Back"):
            st.session_state.started = False
            st.rerun()

    with col2:
        st.markdown("""
        <h1 style="margin-bottom:0;">🎓 Professional Pivot</h1>
        <p style="color:#94a3b8;">Resume &gt; Skills &gt; Reality</p>
        """, unsafe_allow_html=True)

    # ---------------- LOAD DATA ----------------
    @st.cache_data
    def load_data():
        return pd.read_csv("new1.csv")

    df = load_data()

    # ---------------- INPUT FLOW ----------------
    st.subheader("🔍 Student Profile")

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        stream = st.selectbox("Stream", sorted(df["stream"].unique()))

    with c2:
        course = st.selectbox(
            "Course",
            sorted(df[df["stream"] == stream]["course"].unique())
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

    with c5:
        cgpa = st.slider("CGPA", 5.0, 10.0, 7.0, 0.1)

    resume = st.file_uploader(
        "📄 Upload Resume (Mandatory)",
        type=["txt", "pdf", "docx"]
    )

    submit = st.button("🔍 Validate Profile")

    # ---------------- RESULTS ----------------
    if submit:

        if not resume:
            st.warning("⚠️ Kindly Upload the Resume")
            st.stop()

        # Skill extraction
        text = resume.read().decode(errors="ignore").lower()
        all_skills = set(",".join(df["required_skill"].dropna()).lower().split(","))
        user_skills = [s for s in all_skills if s.strip() and s in text]

        def skill_match(user, required):
            if not user or not required:
                return 0
            return int((len(set(user) & set(required)) / len(set(required))) * 100)

        base = df[
            (df["stream"] == stream) &
            (df["course"] == course) &
            (df["department"] == department)
        ]

        st.subheader("📊 Career Reality Check")

        cols = st.columns(2)
        shown = False

        for i, (_, row) in enumerate(base.iterrows()):
            required = [s.strip() for s in row["required_skill"].split(",")]
            match = skill_match(user_skills, required)

            if match == 0:
                continue

            shown = True

            with cols[i % 2]:
                st.markdown(f"""
                <div style="
                    background:#020617;
                    padding:18px;
                    border-radius:16px;
                    margin-bottom:20px;
                    color:#e5e7eb;
                    box-shadow:0 12px 30px rgba(0,0,0,0.6);
                ">
                    <h4>🏢 {row['company_name']}</h4>
                    <p>📍 {row['location']}</p>
                    <p><b>Level:</b> {row['company_level']}</p>
                    <p><b>Skill Match:</b> {match}%</p>
                    <b>Required Skills</b><br>
                    {"".join(f"<span style='background:#1e293b;padding:6px 10px;border-radius:999px;margin:4px;display:inline-block;'>{s}</span>" for s in required)}
                </div>
                """, unsafe_allow_html=True)

        if not shown:
            st.warning(
                "⚠️ Your resume skills do not align with the selected role. "
                "Please improve your skills or update your resume."
            )
