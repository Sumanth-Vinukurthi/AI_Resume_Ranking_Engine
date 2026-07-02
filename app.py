import streamlit as st
import requests
import pandas as pd
from io import BytesIO

st.set_page_config(
    page_title="RedRob AI Recruiter",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
<style>

.main {
    background: linear-gradient(135deg, #0f172a, #1e293b);
}

.hero {
    text-align:center;
    padding:20px;
}

.hero h1{
    color:white;
    font-size:3rem;
    font-weight:700;
}

.hero p{
    color:#cbd5e1;
    font-size:1.1rem;
}

.metric-card{
    background:rgba(255,255,255,0.08);
    backdrop-filter:blur(10px);
    border-radius:20px;
    padding:20px;
    text-align:center;
}

.upload-card{
    background:white;
    border-radius:20px;
    padding:25px;
    box-shadow:0px 8px 24px rgba(0,0,0,0.1);
}

.stButton>button{
    width:100%;
    border-radius:12px;
    height:50px;
    font-size:18px;
    font-weight:bold;
    background:#2563eb;
    color:white;
}

.stButton>button:hover{
    background:#1d4ed8;
}

</style>
""", unsafe_allow_html=True)

# Header

st.markdown("""
<div class="hero">
<h1>🤖 REDROB AI RECRUITER</h1>
<p>Intelligent Candidate Ranking Engine</p>
</div>
""", unsafe_allow_html=True)

# st.markdown("""
# <style>
# div[data-testid="stDataFrame"] {
#     overflow-x: auto !important;
# }

# div[data-testid="stDataFrame"] div {
#     white-space: nowrap !important;
# }
# </style>
# """, unsafe_allow_html=True)
# Metrics

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="metric-card">
    <h2>📄</h2>
    <h3>Job Analysis</h3>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
    <h2>🧠</h2>
    <h3>AI Ranking</h3>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
    <h2>⚡</h2>
    <h3>Fast Screening</h3>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="metric-card">
    <h2>🎯</h2>
    <h3>Best Matches</h3>
    </div>
    """, unsafe_allow_html=True)

st.divider()

left, right = st.columns(2)

with left:

    st.markdown("## 📄 Upload Job Description")

    jd_file = st.file_uploader(
        "Choose Job Description",
        type=["pdf", "docx", "txt"],
        key="jd"
    )

    if jd_file:
        st.success(f"Uploaded: {jd_file.name}")

with right:

    st.markdown("## 👥 Upload Candidate Dataset")

    candidate_file = st.file_uploader(
        "Choose Candidate File",
        type=["json", "jsonl"],
        key="candidate"
    )

    if candidate_file:
        st.success(f"Uploaded: {candidate_file.name}")

st.write("")
st.write("")

col1, col2, col3 = st.columns([1,2,1])

with col2:

    analyze = st.button("🚀 Rank Candidates")

    if analyze:

        if jd_file and candidate_file:

            with st.spinner("Analyzing candidates..."):

                st.success("Ranking completed!")

                st.markdown("### 🏆 Top Candidates")

                files = {
                    "candidates": (
                        candidate_file.name,
                        candidate_file.getvalue(),
                        candidate_file.type or "application/json"
                    ),
                    "job_description": (
                       jd_file.name,
                        jd_file.getvalue(),
                        jd_file.type or "application/octet-stream"
                    )
                }

                response = requests.post(
                    "http://localhost:8000/upload",
                    files=files
                )

                df = pd.DataFrame(response.json())

                st.dataframe(
                    df,
                    use_container_width=True,
                    height= 500
                )

                col1, col2 = st.columns(2)

                with col1:
                    csv = df.to_csv(index=False).encode("utf-8")

                    st.download_button(
                        "📥 Download CSV",
                        csv,
                        "Final_shortlisted_candidates.csv",
                        "text/csv"
                    )

                with col2:

                    xlsx_buffer = BytesIO()

                    with pd.ExcelWriter(
                        xlsx_buffer,
                        engine="openpyxl"
                    ) as writer:
                        df.to_excel(
                            writer,
                            index=False
                        )

                    st.download_button(
                        "📊 Download XLSX",
                        xlsx_buffer.getvalue(),
                        "Final_shortlisted_candidates.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

        else:
            st.error("Please upload both files.")

st.divider()

st.markdown(
    """
    <center>
    Built with ❤️ for AI Recruiting Hackathon
    </center>
    """,
    unsafe_allow_html=True
)