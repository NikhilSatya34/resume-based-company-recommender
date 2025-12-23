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

    st.markdown("""
        <h1 style='text-align:center;'>🎓 Professional Pivot</h1>
        <h4 style='text-align:center; color:gray;'>
        A reality-check platform for career decisions
        </h4>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div style="
        max-width:900px;
        margin:auto;
        background:#0f172a;
        padding:25px;
        border-radius:16px;
        box-shadow:0 12px 30px rgba(0,0,0,0.6);
        color:#e5e7eb;
        font-size:16px;
        line-height:1.7;
    ">
        <h3>🎯 Purpose of this Website</h3>
        <p>
        <b>Professional Pivot</b> is not a normal job recommendation website.
        This platform is designed to give students a <b>realistic career mirror</b>.
        </p>

        <ul>
            <li>📄 Your <b>resume is the primary truth source</b></li>
            <li>🧠 Skills in your resume are matched with real job expectations</li>
            <li>⚠️ If your profile is weak or mismatched, the system will <b>not please you</b></li>
            <li>🚀 Only realistic opportunities (including startups) are shown</li>
            <li>🎓 Helps students understand <b>where they actually stand</b>, not where they wish to be</li>
        </ul>

        <p style="color:#94a3b8;">
        This honesty-driven approach prepares students for real industry standards
        instead of false hopes.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    center_col = st.columns([1, 2, 1])[1]
    with center_col:
        if st.button("🚀 Get Started", use_container_width=True):
            st.session_state.started = True
            st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)

    # ----------- FOOTER CREDIT -----------
    st.markdown("""
        <hr style="border:1px solid #1e293b;">
        <p style="text-align:center; color:#94a3b8; font-size:14px;">
        Project developed by <b>B. Nikhil Satya</b> – CSD <br>
        <b>25ALCSD002</b>
        </p>
    """, unsafe_allow_html=True)

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

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        stream = st.selectbox("Stream", sorted(df["stream"].unique()))

    with c2:
        department = st.selectbox(
            "Department",
            sorted(df[df["stream"] == stream]["department"].unique())
        )

    with c3:
        role = st.selectbox(
            "Job Role",
            sorted(
                df[
                    (df["stream"] == stream) &
                    (df["department"] == department)
                ]["job_role"].unique()
            )
        )

    with c4:
        cgpa = st.slider("CGPA", 5.0, 10.0, 7.0, 0.1)

    resume = st.file_uploader(
        "📄 Upload Resume (Mandatory)",
        type=["txt", "pdf", "docx"]
    )

    submit = st.button("🔎 Validate Profile")

    # ---------------- RESUME CHECK ----------------
    if submit and not resume:
        st.error("❌ Resume upload is mandatory to continue.")
        st.stop()

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
