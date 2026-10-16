
import streamlit as st
from modules.github_client import get_repos

# Page configuration
st.set_page_config(
    page_title="RepoX | AI Developer Intelligence",
    page_icon="🚀",
    layout="wide"
)

# Custom styling
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    max-width: 1200px;
}

.hero {
    text-align: center;
    padding: 45px 15px;
    border-radius: 18px;
    background: linear-gradient(135deg, #172554, #312e81);
    color: white;
    margin-bottom: 25px;
}

.hero h1 {
    font-size: 48px;
    color: white;
}

.hero p {
    color: #cbd5e1;
    font-size: 17px;
}

</style>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.title("🚀 RepoX")
    st.caption("AI Developer Intelligence")

    page = st.radio(
        "Navigation",
        ["Home", "Repositories", "AI Analysis",
         "Job Matching", "Progress"]
    )

    st.divider()
    st.caption("RepoX Hackathon MVP")

# Home screen
if page == "Home":

    st.markdown("""
    <div class="hero">
        <h1>Welcome to RepoX 🚀</h1>
        <p>
        Transform your GitHub projects into
        career opportunities with AI.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Connect Your GitHub")

    username = st.text_input(
        "GitHub Username",
        placeholder="Enter your GitHub username"
    )

    if st.button("🔍 Analyze My GitHub", type="primary"):

        if not username.strip():
            st.warning("Please enter a GitHub username.")
        else:
            with st.spinner("Fetching repositories..."):
                try:
                    repos = get_repos(username.strip())
                    st.session_state["repos"] = repos
                    st.session_state["username"] = username.strip()

                    st.success("GitHub profile connected!")

                except Exception as e:
                    st.error(f"Error: {e}")

    st.divider()
    st.subheader("Explore RepoX Features")

    col1, col2 = st.columns(2)

    with col1:
        st.info("📂 Repository Analysis")
        st.write("Explore your GitHub projects.")

        st.info("💼 Job Matching")
        st.write("Discover relevant career opportunities.")

    with col2:
        st.info("🧠 AI Skill Analysis")
        st.write("Understand your technical strengths.")

        st.info("📈 Developer Progress")
        st.write("Track your development journey.")

# Repository page
elif page == "Repositories":

    st.title("📂 Your GitHub Repositories")

    repos = st.session_state.get("repos", [])

    if not repos:
        st.info("Connect your GitHub account on Home first.")
    else:
        st.metric("Total Repositories", len(repos))

        for repo in repos:
            with st.container(border=True):
                st.subheader(repo.get("name", "Unnamed"))
                st.write(
                    "Language:",
                    repo.get("language") or "Unknown"
                )
                st.write(
                    "⭐ Stars:",
                    repo.get("stargazers_count", 0)
                )

# Placeholder pages for next development stages
elif page == "AI Analysis":
    st.title("🧠 AI Skill Analysis")
    st.info("AI analysis module coming next.")

elif page == "Job Matching":
    st.title("💼 Job Matching")
    st.info("Job discovery module coming next.")

elif page == "Progress":
    st.title("📈 Developer Progress")
    st.info("Progress tracking module coming next.")
