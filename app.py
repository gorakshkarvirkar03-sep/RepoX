from modules.dashboard import show_dashboard
import streamlit as st
from modules.github_client import get_repos
from modules.auth import init_auth_state, login_page, logout
from modules.ai_analyzer import render_ai_analysis_page

# Page configuration
st.set_page_config(
    page_title="RepoX | AI Developer Intelligence",
    page_icon="🚀",
    layout="wide"
)

# Initialize authentication session state
init_auth_state()

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

.role-badge {
    background-color: #312e81;
    color: #e0e7ff;
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
    display: inline-block;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 1. IF NOT LOGGED IN -> SHOW LOGIN SCREEN
# ---------------------------------------------------------
if not st.session_state["authenticated"]:
    login_page()
    st.stop()  # Stops execution of the rest of the app until logged in

# ---------------------------------------------------------
# 2. IF LOGGED IN -> SHOW ROLE-BASED SIDEBAR & CONTENT
# ---------------------------------------------------------
role = st.session_state["user_role"]

with st.sidebar:
    st.title("🚀 RepoX")
    st.caption("AI Developer Intelligence")
    
    # User Profile Badge
    st.markdown(f'<div class="role-badge">👤 {role}</div>', unsafe_allow_html=True)
    st.write(f"**{st.session_state['user_name']}**")
    st.caption(st.session_state["user_email"])
    st.divider()

    # Role-based Navigation Menu
    if role == "Student / Fresher":
        nav_options = ["Home", "Repositories", "AI Analysis", "Job Matching", "Progress"]
    elif role == "Recruiter":
        nav_options = ["Recruiter Dashboard", "Candidate Search", "Post a Job", "AI Shortlisting"]
    elif role == "Admin":
        nav_options = ["Admin Overview", "Manage Users", "System Analytics"]

    page = st.radio(
    "Navigation",
    [
        "Home",
        "Developer Dashboard",
        "Repositories",
        "AI Analysis"
    ]
    )

    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        logout()
    st.caption("RepoX Hackathon MVP")


# =========================================================
# STUDENT / FRESHER VIEWS (Your Original Home Page & Tabs)
# =========================================================
if role == "Student / Fresher":
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

        default_user = st.session_state.get("username", "")
        username = st.text_input(
            "GitHub Username",
            value=default_user,
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

    elif page == "Developer Dashboard":
        username = st.session_state.get("username")
        repos = st.session_state.get("repos", [])
        show_dashboard(username, repos)        

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
                    st.write("Language:", repo.get("language") or "Unknown")
                    st.write("⭐ Stars:", repo.get("stargazers_count", 0))

    elif page == "AI Analysis":
        render_ai_analysis_page()

    elif page == "Job Matching":
        st.title("💼 Job Matching")
        st.info("Job discovery module coming next.")

    elif page == "Progress":
        st.title("📈 Developer Progress")
        st.info("Progress tracking module coming next.")


# =========================================================
# RECRUITER VIEWS
# =========================================================
elif role == "Recruiter":
    if page == "Recruiter Dashboard":
        st.title("🏢 Recruiter Dashboard")
        col1, col2, col3 = st.columns(3)
        col1.metric("Verified Developers", "1,240", "+18% this week")
        col2.metric("Active Job Postings", "4", "2 closing soon")
        col3.metric("AI-Matched Candidates", "38", "Top 5% skill match")

    elif page == "Candidate Search":
        st.title("🔎 Search Developer Talent")
        skill_query = st.text_input("Filter by Tech Stack / Language (e.g., Python, React, PyTorch)")
        st.info("Candidate talent pool integration coming next.")

    elif page == "Post a Job":
        st.title("📢 Post a Job Opportunity")
        with st.form("job_post"):
            st.text_input("Job Title", placeholder="Junior AI Engineer")
            st.text_area("Required Skills & GitHub Signals")
            st.form_submit_button("Publish Job", type="primary")

    elif page == "AI Shortlisting":
        st.title("🤖 AI GitHub Shortlisting")
        st.info("Automated repository evaluation for applicants coming next.")


# =========================================================
# ADMIN VIEWS
# =========================================================
elif role == "Admin":
    if page == "Admin Overview":
        st.title("🛡️ System Administration")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Registered Users", "1,420")
        col2.metric("GitHub API Calls Today", "3,892")
        col3.metric("System Status", "Healthy 🟢")

    elif page == "Manage Users":
        st.title("👥 User Management")
        st.info("User verification and role control table coming next.")

    elif page == "System Analytics":
        st.title("📊 Platform Analytics")
        st.info("Usage metrics and AI token tracking coming next.")