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
