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
# HEADER
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
            st.button("🚀 Start Career Analysis",
                      on_click=lambda: st.session_state.update(started=True))
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
    **Professional Pivot** evaluates resume–skill alignment
    before recommending companies.
    """)

# -------------------------------------------------
# MAIN PAGE
# -------------------------------------------------
else:

    header(show_back=True)
    st.subheader("🔍 Student Profile")

    col1, col2, col3, col4 = st.columns(4)

    # ---------- Stream ----------
    with col1:
        stream = st.selectbox(
            "Stream",
            sorted(df["stream"].unique()),
            on_change=lambda: st.session_state.update(
                stream_ok=False,
                course_ok=False,
                dept_ok=False,
                role_ok=False
            )
        )

        if st.button("Confirm Stream"):
            st.session_state.stream_ok = True
            st.session_state.course_ok = False   # ### FIX
            st.session_state.dept_ok = False     # ### FIX
            st.session_state.role_ok = False     # ### FIX

    # ---------- Course ----------
    with col2:
        if st.session_state.stream_ok:
            course = st.selectbox(
                "Course",
                sorted(df[df["stream"] == stream]["course"].unique()),
                on_change=lambda: st.session_state.update(
                    course_ok=False,
                    dept_ok=False,
                    role_ok=False
                )
            )

            if st.button("Confirm Course"):
                st.session_state.course_ok = True
                st.session_state.dept_ok = False   # ### FIX
                st.session_state.role_ok = False   # ### FIX

    # ---------- Department ----------
    with col3:
        if st.session_state.course_ok:
            department = st.selectbox(
                "Department",
                sorted(
                    df[
                        (df["stream"] == stream) &
                        (df["course"] == course)
                    ]["department"].unique()
                ),
                on_change=lambda: st.session_state.update(
                    dept_ok=False,
                    role_ok=False
                )
            )


    # ---------- Job Role ----------
    with col4:
        if st.session_state.dept_ok:
            roles_df = df[
                (df["stream"] == stream) &
                (df["course"] == course) &
                (df["department"] == department)
            ]

            role = st.selectbox(
                "Job Role",
                sorted(roles_df["job_role"].unique()),
                key=f"role_{stream}_{course}_{department}"
            )


            if st.button("Confirm Role"):
                st.session_state.role_ok = True

    # ---------- Resume ----------
    resume = st.file_uploader(
        "📄 Upload Resume (Mandatory)",
        type=["txt", "pdf", "docx"]
    )

    if st.session_state.role_ok:
        submit = st.button("🔍 Validate Profile")
    else:
        submit = False
        st.info("Please confirm all selections above to proceed.")

    # -------------------------------------------------
    # RESULT LOGIC
    # -------------------------------------------------
    if submit:

        if not resume:
            st.warning("⚠️ Please upload your resume.")
            st.stop()

        resume_text = resume.read().decode(errors="ignore").lower()

        # ---------- Skill extraction ----------
        all_skills = set(
            ",".join(df["required_skill"].dropna()).lower().split(",")
        )
        all_skills = {s.strip() for s in all_skills if s.strip()}
        user_skills = {s for s in all_skills if s in resume_text}

        base_df = df[
            (df["stream"] == stream) &
            (df["course"] == course) &
            (df["department"] == department) &
            (df["job_role"] == role)
        ]

        if base_df.empty:                       # ### FIX
            st.warning("⚠️ No data found for selected role.")
            st.stop()

        role_skills = {
            s.strip().lower()
            for s in ",".join(base_df["required_skill"]).split(",")
        }

        matched_skills = role_skills & user_skills

        if not matched_skills:
            st.warning(
                "⚠️ Resume does NOT match selected role.\n"
                "Update resume or choose a relevant role."
            )
            st.stop()

        def skill_match(user, required):
            return int(len(user & required) / len(required) * 100)

        skill_percent = skill_match(user_skills, role_skills)

        # ---------- FIX company level case ----------
        if skill_percent >= 70:
            allowed_levels = ["HIGH", "MID"]
        elif skill_percent >= 40:
            allowed_levels = ["MID", "LOW"]
        else:
            allowed_levels = ["LOW", "STARTUP"]

        st.info(f"Skill Match: {skill_percent}%")

        final_df = df[
            (df["stream"] == stream) &
            (df["course"] == course) &
            (df["department"] == department) &
            (df["company_level"].isin(allowed_levels))
        ]

        if final_df.empty:
            st.warning("No companies found for current skill level.")
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
                    <div style="background:#020617;padding:20px;
                    border-radius:18px;color:white;">
                        <h4>🏢 {row['company_name']}</h4>
                        <p>📍 {row['location']}</p>
                        <p>Skill Match: {match}%</p>
                    </div>
                    """,
                    height=220
                )
