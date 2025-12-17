import streamlit as st
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Career Readiness & Company Recommender",
    layout="centered"
)

st.title("Career Readiness & Company Recommender")

# ---------------- LOAD CSV DATA ----------------
def load_data():
    try:
        df = pd.read_csv(
            "data/Companies_CGPA.csv",
            encoding="latin1",
            engine="python",
            sep=",",
            on_bad_lines="skip",
            nrows=5000   # prevents hanging
        )
        return df
    except Exception as e:
        st.error(f"CSV Load Error: {e}")
        st.stop()

# ---------------- CALL FUNCTION ----------------
with st.spinner("Loading company data..."):
    df = load_data()

st.success("Company data loaded successfully!")

# ---------------- USER INPUT FILTERS ----------------
st.subheader("Find Suitable Companies")

# Stream selection
streams = sorted(df["stream"].dropna().unique())
selected_stream = st.selectbox("Select Stream", streams)

# Department based on stream
filtered_by_stream = df[df["stream"] == selected_stream]
departments = sorted(filtered_by_stream["department"].dropna().unique())
selected_department = st.selectbox("Select Department", departments)

# Job role based on department
filtered_by_dept = filtered_by_stream[
    filtered_by_stream["department"] == selected_department
]
roles = sorted(filtered_by_dept["job_role"].dropna().unique())
selected_role = st.selectbox("Select Job Role", roles)

# ---------------- SHOW RESULTS ----------------
result_df = filtered_by_dept[
    filtered_by_dept["job_role"] == selected_role
]

st.markdown("### Recommended Companies")

if result_df.empty:
    st.warning("No companies found for the selected criteria.")
else:
    st.dataframe(
        result_df[
            ["company_name", "company_level", "location"]
        ].reset_index(drop=True)
    )
