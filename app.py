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
        "<h4 style='text-align:center;color:gray;'>Resume &gt; Skills &gt; Reality</h4>",
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.write("""
    **Professional Pivot** is a career validation platform, not a job portal.

    It strictly analyzes skills from your resume and compares them with
    **real-world job requirements** across **UG & PG**, **all streams**.

    If your profile is weak or mismatched, the system will not please you.
    It will show only **realistic outcomes**.
    """)

    st.info("⚠️ Resume is the only truth source in this system.")

    if st.button("🚀 Get Started"):
        st.session_state.started = True
        st.rerun()

    st.markdown(
        "<p style='text-align:center;color:#94a3b8;'>"
        "Project developed by <b>B. Nikhil Satya</b> – CSD<br>"
        "<b>25ALCSD002</b></p>",
        unsafe_allow_html=True
    )

# -------------------------------------------------
# MAIN APP
# -------------------------------------------------
else:

    # Back button + Header
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

    # Load data
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

            # -------- RESUME SKILL EXTRACTION (GENERIC) --------
        resume_text = resume.read().decode(errors="ignore").lower()
        
        # Collect ALL skills from dataset (all domains)
        all_skills = set()
        
        for skills in df["required_skill"].dropna():
        for s in skills.lower().split(","):
            all_skills.add(s.strip())
        
        # Extract only skills present in resume
        user_skills = [skill for skill in all_skills if skill and skill in resume_text]

        def skill_match(required):
            if not required:
                return 0
            return int((len(set(user_skills) & set(required)) / len(set(required))) * 100)

        base = df[
            (df["stream"] == stream) &
            (df["course"] == course) &
            (df["department"] == department) &
            (df["job_role"] == role)
        ]

        st.subheader("📊 Career Reality Check")

        cols = st.columns(2)
        shown = False

        for i, (_, row) in enumerate(base.iterrows()):
            required = [s.strip().lower() for s in row["required_skill"].split(",")]
            match = skill_match(required)

            if match == 0:
                continue

            shown = True

            # ✔ ❌ Skill display
            skills_html = ""
            for s in required:
                if s in user_skills:
                    skills_html += f"<span style='color:#22c55e;'>✔ {s}</span><br>"
                else:
                    skills_html += f"<span style='color:#ef4444;'>❌ {s}</span><br>"

            with cols[i % 2]:
                st.markdown(f"""
                <div style="
                    background:#020617;
                    padding:18px;
                    border-radius:16px;
                    margin-bottom:20px;
                    box-shadow:0 12px 30px rgba(0,0,0,0.6);
                ">
                    <h4>🏢 {row['company_name']}</h4>
                    <p>📍 {row['location']} | Level: {row['company_level']}</p>
                    <p><b>Skill Match:</b> {match}%</p>
                    <hr>
                    <b>Required Skills Validation</b><br>
                    {skills_html}
                </div>
                """, unsafe_allow_html=True)

        if not shown:
            st.warning(
                "⚠️ Your resume does not align with the selected job role. "
                "Please improve skills or choose a realistic role."
            )
