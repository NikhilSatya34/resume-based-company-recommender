import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

# -------------------------------------------------
# PAGE CONFIG (ONLY ONCE)
# -------------------------------------------------
st.set_page_config(
    page_title="Resume Based Company Recommender",
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
        <h1 style='text-align:center;'>🎓 Resume Based Company Recommender</h1>
        <h4 style='text-align:center; color:gray;'>
        Smart, CGPA-aware, and explainable placement recommendations
        </h4>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 1️⃣ Build Your Profile")
        st.write("Select your Stream, Department, Job Role and enter CGPA.")

    with col2:
        st.markdown("### 2️⃣ Upload Resume (Optional)")
        st.write("Upload resume to improve skill-based accuracy.")

    with col3:
        st.markdown("### 3️⃣ Get Smart Recommendations")
        st.write("Receive realistic company suggestions with explanations.")

    st.markdown("<br>", unsafe_allow_html=True)

    st.info(
        "ℹ️ Recommendations are guidance-based and designed to help students "
        "plan their career path effectively."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    center_col = st.columns([1, 2, 1])[1]
    with center_col:
        if st.button("🚀 Get Started", use_container_width=True):
            st.session_state.started = True
            st.rerun()

# -------------------------------------------------
# MAIN APPLICATION
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
        border: 1px solid rgba(255,255,255,0.08);
        color: #e5e7eb;
    }
    .card:hover {
        transform: translateY(-4px);
        transition: 0.3s;
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
        return pd.read_csv("data/Companies_CGPA.csv")

    df = load_data()

    # ---------------- HEADER ----------------
    st.title("🎓 Resume Based Company Recommender")
    st.caption("CGPA • Role • Skills • Explainable Recommendations")

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
        "📄 Upload Resume (Required)",
        type=["txt", "pdf", "docx"]
    )


    submit = st.button("🔎 Find Companies")

    # ---------------- USER SKILLS ----------------
    user_skills = []

    if resume:
        text = resume.read().decode(errors="ignore").lower()
        known_skills = [
            "python","java","sql","machine learning","data science",
            "excel","power bi","tableau","statistics",
            "git","rest","api","cloud","docker"
        ]
        user_skills = [s for s in known_skills if s in text]

    # ---------------- HELPER FUNCTIONS ----------------
    def allowed_levels(cgpa):
        if cgpa >= 8.0:
            return ["High","Mid","Low","Startup"]
        elif cgpa >= 6.5:
            return ["Mid","Low","Startup"]
        else:
            return ["Low","Startup"]

    def calculate_skill_match(user, required):
        if not user or not required:
            return 0
        return int((len(set(user) & set(required)) / len(set(required))) * 100)

    def missing_skills(user, required):
        return [s for s in required if s not in user]

    def skill_bar(percent):
        filled = int(percent / 10)
        return "█" * filled + "░" * (10 - filled)

    # ---------------- CARD ----------------

    def show_card(row, tag):
        level_colors = {
            "High": "#22c55e",
            "Mid": "#facc15",
            "Low": "#38bdf8",
            "Startup": "#a855f7"
        }
    
        required = [
            s.strip().lower()
            for s in str(row["required_skills"]).split(",")
            if s.strip()
        ]
    
        match = calculate_skill_match(user_skills, required)
        gap = missing_skills(user_skills, required)
        bar = skill_bar(match)
    
        html = f"""
    <style>
    .card {{
        background: linear-gradient(145deg, #020617, #0f172a);
        border-radius: 18px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 18px 40px rgba(0,0,0,0.6);
        border: 1px solid rgba(255,255,255,0.08);
        color: #e5e7eb;
        font-family: Arial, sans-serif;
    }}
    .badge {{
        padding: 5px 12px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
        margin-right: 6px;
        display: inline-block;
    }}
    .skill {{
        background: #1e293b;
        color: #e5e7eb;
        padding: 6px 12px;
        border-radius: 999px;
        font-size: 12px;
        margin: 4px 6px 0 0;
        display: inline-block;
    }}
    </style>
    
    <div class="card">
      <h4>🏢 {row['company_name']}</h4>
    
      <span class="badge" style="background:{level_colors[row['company_level']]}; color:black;">
        {row['company_level']}
      </span>
      <span class="badge" style="background:#334155;">{tag}</span>
    
      <p>📍 {row['location']}</p>
      <p><b>🧠 Skill Match:</b> {match}%</p>
      <pre>{bar}</pre>
    
      <b>🎯 Required Skills</b><br>
      {"".join(f"<span class='skill'>{s}</span>" for s in required)}
    
      <br><br><b>❌ Missing Skills</b><br>
      {"".join(
            f"<span class='skill' style='background:#7f1d1d;'>{s}</span>"
            for s in gap[:5]
        ) or "<span class='skill'>None 🎉</span>"}
    
      <p><b>💡 Why this company?</b></p>
      <ul>
        <li>Eligible based on CGPA</li>
        <li>Relevant to selected job role</li>
        <li>Skill compatibility: {match}%</li>
      </ul>
    </div>
    """
    
        components.html(html, height=540, scrolling=False)

    
    # ---------------- RESULTS ----------------
    if submit:
        base = df[
            (df["stream"] == stream) &
            (df["department"] == department) &
            (df["company_level"].isin(allowed_levels(cgpa)))
        ].copy()

        order = ["High","Mid","Low","Startup"]
        base["company_level"] = pd.Categorical(base["company_level"], order, ordered=True)
        base = base.sort_values("company_level")

        best = base[base["job_role"] == role]

        alt = df[
            (df["stream"] == stream) &
            (df["department"] == department) &
            (df["job_role"] != role) &
            (df["company_level"].isin(allowed_levels(cgpa)))
        ]


        st.subheader("🏆 Recommended Companies")

        if not best.empty:
            st.markdown("### 🎯 Best Matches")
            cols = st.columns(2)
            for i, (_, r) in enumerate(best.iterrows()):
                with cols[i % 2]:
                    show_card(r, "Best Match")

        if not alt.empty:
            st.markdown("### 🔁 Alternate Opportunities")
            cols = st.columns(2)
            for i, (_, r) in enumerate(alt.iterrows()):
                with cols[i % 2]:
                    show_card(r, "Alternate Role")

        if best.empty and alt.empty:
            st.warning("No companies found. Try changing CGPA or role.")
