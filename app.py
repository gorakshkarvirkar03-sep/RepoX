from modules.progress_tracker import render_progress_page
from modules.job_matching import render_job_matching_page
from modules.dashboard import show_dashboard
import streamlit as st
from modules.github_client import get_repos
from modules.auth import init_auth_state, login_page, logout
from modules.ai_analyzer import render_ai_analysis_page
from modules.db import save_analysis, link_github, build_snapshot, find_candidate, set_recruiter_consent, refresh_if_changed

def navigate_to(page_name):
    st.session_state["navigation_radio"] = page_name

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

# Auto-refresh profile from GitHub once per login session
if (role == "Student / Fresher" and st.session_state.get("user_id")
        and st.session_state.get("username")
        and not st.session_state.get("auto_synced")):
    st.session_state["auto_synced"] = True
    try:
        _repos = get_repos(st.session_state["username"])
        st.session_state["repos"] = _repos
        if refresh_if_changed(st.session_state["user_id"], _repos):
            st.toast("🔄 New GitHub activity found. Your RepoX profile was updated!")
    except Exception:
        pass

with st.sidebar:
    st.title("🚀 RepoX")
    st.caption("AI Developer Intelligence")

    # User Profile Badge
    st.markdown(f'<div class="role-badge">👤 {role}</div>', unsafe_allow_html=True)
    st.write(f"**{st.session_state['user_name']}**")
    st.caption(st.session_state["user_email"])

    # RepoX ID + recruiter consent switch (real accounts only)
    if role == "Student / Fresher" and st.session_state.get("user_id"):
        st.markdown(f"**RepoX ID:** `{st.session_state['repox_id']}`")
        allow = st.toggle(
            "Let recruiters view my profile",
            value=st.session_state.get("recruiter_consent", False),
        )
        if allow != st.session_state.get("recruiter_consent", False):
            set_recruiter_consent(st.session_state["user_id"], allow)
            st.session_state["recruiter_consent"] = allow

    st.divider()

    # Role-based navigation Menu
    if role == "Student / Fresher":
        nav_options = ["Home", "Repositories", "AI Analysis", "Job Matching", "Progress"]
    elif role == "Recruiter":
        nav_options = ["Candidate Search"]
    elif role == "Admin":
        nav_options = ["Admin Overview", "Manage Users", "System Analytics"]

    if (
        "navigation_radio" not in st.session_state
        or st.session_state["navigation_radio"] not in nav_options
    ):
        st.session_state["navigation_radio"] = nav_options[0]

    page = st.radio(
        "Navigation",
        nav_options,
        key="navigation_radio"
    )

    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        logout()
    st.caption("RepoX Hackathon MVP")


# =========================================================
# STUDENT / FRESHER VIEWS
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

                        # Save summary to the database for recruiters
                        if st.session_state.get("user_id"):
                            try:
                                link_github(st.session_state["user_id"], username.strip())
                                save_analysis(st.session_state["user_id"], build_snapshot(repos))
                            except Exception as db_err:
                                st.warning(f"Profile could not be saved: {db_err}")
                    except Exception as e:
                        st.error(f"Error: {e}")

        st.divider()
        st.subheader("Explore RepoX Features")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("📂 Repository Analysis", use_container_width=True):
                st.session_state["selected_page"] = "Repositories"
                st.rerun()

            if st.button("💼 Job Matching", use_container_width=True):
                st.session_state["selected_page"] = "Job Matching"
                st.rerun()

        with col2:
            if st.button("🧠 AI Skill Analysis", use_container_width=True):
                st.session_state["selected_page"] = "AI Analysis"
                st.rerun()

            if st.button("📈 Developer Progress", use_container_width=True):
                st.session_state["selected_page"] = "Progress"
                st.rerun()

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
        render_job_matching_page()

    elif page == "Progress":
        render_progress_page()


# =========================================================
# RECRUITER VIEWS
# =========================================================
elif role == "Recruiter":
    if page == "Candidate Search":
        st.title("🔎 Search & Evaluate Developer Talent")
        st.caption("Discover verified fresher profiles and evaluate their public GitHub repositories.")

        # ---------- Search by RepoX ID ----------
        st.subheader("🆔 Search by RepoX ID")
        rid = st.text_input("RepoX ID", placeholder="e.g. RX-AB12CD")
        if st.button("Find Candidate", type="primary", key="find_by_id"):
            if not rid.strip():
                st.warning("Please enter a RepoX ID.")
            else:
                found, err = find_candidate(rid)
                if err:
                    st.session_state["found_candidate"] = None
                    st.error(err)
                else:
                    st.session_state["found_candidate"] = found

        found = st.session_state.get("found_candidate")
        if found:
            u = found["user"]
            a = found["analysis"]
            with st.container(border=True):
                st.subheader(u["full_name"])
                st.caption(f"RepoX ID: {u['repox_id']}  |  GitHub: @{u['github_username'] or 'not linked'}")
                if not a:
                    st.info("This candidate has not analyzed their GitHub yet.")
                else:
                    s = a.get("skills") or {}
                    st.caption(f"Last analyzed: {a['created_at'][:10]}")
                    m1, m2 = st.columns(2)
                    m1.metric("Repositories built", s.get("total_repos", 0))
                    m2.metric("Total GitHub stars", s.get("total_stars", 0))

                    langs = s.get("languages", {})
                    if langs:
                        st.markdown("**Skills (from GitHub languages)**")
                        st.write(" ".join(f"`{l}`" for l in langs))
                        st.bar_chart(langs)

                    st.markdown("**Top repositories**")
                    for r in s.get("top_repos", []):
                        with st.container(border=True):
                            st.markdown(f"**{r['name']}**  ·  {r.get('language') or 'Unknown'}  ·  ⭐ {r['stars']}")
                            if r.get("description"):
                                st.write(r["description"])
                            if r.get("url"):
                                st.markdown(f"[View on GitHub]({r['url']})")

        st.divider()

        # ---------- Search by GitHub username ----------
        st.subheader("🔎 Search by GitHub Username")
        col1, col2 = st.columns([3, 1])
        with col1:
            candidate_gh = st.text_input("Enter Candidate GitHub Username", placeholder="e.g., torvalds or octocat")
        with col2:
            st.write("")
            st.write("")
            search_btn = st.button("Analyze Candidate", type="primary", use_container_width=True)

        if search_btn:
            if not candidate_gh.strip():
                st.warning("Please enter a valid GitHub username.")
            else:
                with st.spinner(f"Fetching public repositories for @{candidate_gh.strip()}..."):
                    try:
                        c_repos = get_repos(candidate_gh.strip())
                        if c_repos:
                            st.success(f"Successfully loaded {len(c_repos)} repositories for **@{candidate_gh.strip()}**")

                            # Quick stats preview for the recruiter
                            total_stars = sum(r.get("stargazers_count", 0) for r in c_repos)
                            languages = [r.get("language") for r in c_repos if r.get("language")]

                            rc1, rc2 = st.columns(2)
                            rc1.metric("Total Public Repos", len(c_repos))
                            rc2.metric("Total GitHub Stars", total_stars)

                            st.subheader("📁 Repository Highlights")
                            for r in c_repos[:6]:
                                with st.container(border=True):
                                    st.markdown(f"**{r.get('name', 'Unnamed')}**")
                                    st.caption(f"Language: {r.get('language') or 'Unknown'} | ⭐ Stars: {r.get('stargazers_count', 0)}")
                                    if r.get("description"):
                                        st.write(r.get("description"))
                        else:
                            st.info("No public repositories found for this username.")
                    except Exception as e:
                        st.error(f"Error fetching candidate profile: {e}")

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