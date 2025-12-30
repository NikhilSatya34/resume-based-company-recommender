import streamlit.components.v1 as components
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
if "stream_ok" not in st.session_state:
    st.session_state.stream_ok = False
if "course_ok" not in st.session_state:
    st.session_state.course_ok = False
if "dept_ok" not in st.session_state:
    st.session_state.dept_ok = False
if "role_ok" not in st.session_state:
    st.session_state.role_ok = False

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_csv("newlyadded_deduplicated.csv")

df = load_data()
# -------------------------------
# DATA NORMALIZATION (CRITICAL)
# -------------------------------
df["stream"] = df["stream"].astype(str).str.strip().str.upper()
df["course"] = df["course"].astype(str).str.strip()
df["department"] = df["department"].astype(str).str.strip().str.upper()
df["job_role"] = df["job_role"].astype(str).str.strip()
df["company_level"] = df["company_level"].astype(str).str.strip().str.upper()

# -------------------------------------------------
# COMMON HEADER (INTRO + MAIN)
# -------------------------------------------------
def header(show_start=False, show_back=False):
    c1, c2, c3 = st.columns([1, 7, 2])

    with c1:
        st.image("fevicon_project.png", width=60)

    with c2:
        st.markdown("""
        <h1 style="margin-bottom:0;">Professional Pivot</h1>
        <p style="color:#94a3b8;margin-top:0;">
        Resume → Skills → Reality
        </p>
        """, unsafe_allow_html=True)

    with c3:
        if show_start:
            st.button(
                "🚀 Start Career Analysis",
                on_click=lambda: st.session_state.update(started=True)
            )
        if show_back:
            if st.button("⬅ Back"):
                st.session_state.started = False
                st.rerun()

    st.markdown("<hr style='border:1px solid #1f2933;'>",
                unsafe_allow_html=True)

# -------------------------------------------------
# INTRO PAGE
# -------------------------------------------------
if not st.session_state.started:

    header(show_start=True)

    st.markdown("""
    ## 🎯 About the Project

    **Professional Pivot** is not a traditional job portal.  
    It is a **career readiness evaluation system** that analyzes a student’s resume
    and compares it with **real industry skill requirements** before recommending companies.

    Unlike job portals that show the same jobs to everyone, Professional Pivot ensures
    that recommendations are **realistic, skill-based, and achievable**.

    ### 🔍 How Professional Pivot Works
    - Resume skill extraction (keyword-based)
    - Skill match percentage calculation
    - Identification of skill gaps
    - Company recommendations based on skill readiness

    > ⚠️ Resume is the single source of truth.  
    > If skills don’t match, the system will not force recommendations.

    ### 🆚 Professional Pivot vs Job Portals
    """)

    st.table({
        "Job Portals": [
            "Focus on job listings",
            "Same jobs for all users",
            "Apply-first approach",
            "No readiness feedback",
            "May show unrealistic roles"
        ],
        "Professional Pivot": [
            "Focus on career readiness",
            "Personalized recommendations",
            "Improve-first approach",
            "Clear skill gap feedback",
            "Shows only realistic companies"
        ]
    })

    st.info(
        "ℹ️ Recommendations are generated from a curated dataset of real-world "
        "job requirements. Skill extraction is keyword-based and depends on resume content."
    )

    st.markdown("""
    ---
    **Developed by:** B. Nikhil Satya  
    **Department:** CSD  
    **College:** Annamacharya University
    """)

# -------------------------------------------------
# MAIN PAGE
# -------------------------------------------------
else:

    header(show_back=True)

    st.subheader("🔍 Student Profile")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        stream = st.selectbox("Stream", sorted(df["stream"].unique()))
        if st.button("Confirm Stream"):
            st.session_state.stream_ok = True

    with col2:
        if st.session_state.stream_ok:
            course = st.selectbox(
                "Course",
                sorted(df[df["stream"] == stream]["course"].unique())
            )
    
            if st.button("Confirm Course"):
                st.session_state.course_ok = True


    with col3:
        if st.session_state.course_ok:
            department = st.selectbox(
                "Department",
                sorted(
                    df[
                        (df["stream"] == stream) &
                        (df["course"] == course)
                    ]["department"].unique()
                )
            )
            if st.button("Confirm Department"):
                st.session_state.dept_ok = True


    with col4:
        if st.session_state.dept_ok:
            roles_df = df[
                (df["stream"] == stream) &
                (df["course"] == course) &
                (df["department"] == department)
            ]
    
            role = st.selectbox(
                "Job Role",
                sorted(roles_df["job_role"].unique())
            )
    
            if st.button("Confirm Role"):
                st.session_state.role_ok = True



    resume = st.file_uploader(
        "📄 Upload Resume (Mandatory)",
        type=["txt", "pdf", "docx"]
    )

    if st.session_state.role_ok:
        submit = st.button("🔍 Validate Profile")
    else:
        st.info("Please confirm all selections above to proceed.")


    # -------------------------------------------------
    # RESULT LOGIC
    # -------------------------------------------------
    if submit:

        if not resume:
            st.warning("⚠️ Please upload your resume to proceed.")
            st.stop()

        resume_text = resume.read().decode(errors="ignore").lower()

                # Base filter (already present in your code)
        base_df = df[
            (df["stream"] == stream) &
            (df["course"] == course) &
            (df["department"] == department) &
            (df["job_role"] == role)
        ]
        
        # 🔴 STRICT RESUME vs ROLE VALIDATION
        role_skills = {
            s.strip().lower()
            for s in ",".join(base_df["required_skill"]).split(",")
        }
        
        matched_skills = role_skills & user_skills
        
        if not matched_skills:
            st.warning(
                "⚠️ Your resume does NOT match the selected job role.\n\n"
                "👉 Please select a role relevant to your resume "
                "or update your resume with required skills."
            )
            st.stop()


        # Collect all skills from dataset
        all_skills = set(
            ",".join(df["required_skill"].dropna())
            .lower()
            .split(",")
        )
        all_skills = {s.strip() for s in all_skills if s.strip()}

        # Skills present in resume
        user_skills = {s for s in all_skills if s in resume_text}

        def skill_match(user, required):
            if not user or not required:
                return 0
            return int(len(user & required) / len(required) * 100)

        if base_df.empty:
            st.warning("⚠️ No data available for the selected inputs.")
            st.stop()

        required_skills = {
            s.strip().lower()
            for s in ",".join(base_df["required_skill"]).split(",")
        }

        skill_percent = skill_match(user_skills, required_skills)

        # Skill % → company level mapping
        if skill_percent >= 70:
            allowed_levels = ["High", "Mid"]
        elif skill_percent >= 40:
            allowed_levels = ["Mid", "Low"]
        else:
            allowed_levels = ["Low", "STARTUP"]

        st.subheader("📊 Career Reality Check")

        st.info(
            f"Based on your **{skill_percent}% skill match**, "
            f"showing **{', '.join(allowed_levels)} level companies**."
        )

        final_df = df[
            (df["stream"] == stream) &
            (df["course"] == course) &
            (df["department"] == department) &
            (df["company_level"].isin(allowed_levels))
        ]

        if final_df.empty:
            st.warning(
                "❌ No matching companies found based on your current skill level.\n\n"
                "👉 Focus on improving ❌ marked skills to unlock recommendations."
            )
            st.stop()

        cols = st.columns(2)

        for i, (_, row) in enumerate(final_df.iterrows()):
            req = {s.strip().lower() for s in row["required_skill"].split(",")}
            match = skill_match(user_skills, req)

            if match == 0:
                continue

            with cols[i % 2]:
                components.html(
                    f"""
                    <div style="
                        background:#020617;
                        padding:20px;
                        border-radius:18px;
                        margin-bottom:20px;
                        box-shadow:0 15px 40px rgba(0,0,0,0.6);
                        color:white;
                    ">
                        <h4>🏢 {row['company_name']}</h4>
                        <p>📍 {row['location']}</p>
                        <p>🎯 <b>Role:</b> {role}</p>
                
                        <b>Skill Match</b>
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
                
                        <p style="margin-top:10px;"><b>Required Skills</b></p>
                        <ul>
                            {''.join(
                                f"<li>{'✔️' if s in user_skills else '❌'} {s}</li>"
                                for s in req
                            )}
                        </ul>
                
                        <p style="color:#fca5a5;">
                            Focus on improving ❌ marked skills to increase eligibility.
                        </p>
                    </div>
                    """,
                    height=420
                )
