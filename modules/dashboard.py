
import streamlit as st
import requests
import plotly.express as px
from collections import Counter


def show_dashboard(username, repos):
    st.title("🚀 RepoX Developer Dashboard")
    st.caption("Your GitHub Developer Intelligence")

    if not username:
        st.warning("Please connect your GitHub account first.")
        return

    # Fetch GitHub profile
    try:
        response = requests.get(
            f"https://api.github.com/users/{username}",
            headers={
                "Accept": "application/vnd.github+json"
            },
            timeout=15
        )
        response.raise_for_status()
        profile = response.json()

    except requests.RequestException as error:
        st.error(f"GitHub API error: {error}")
        return

    # Profile section
    col1, col2 = st.columns([1, 4])

    with col1:
        st.image(profile["avatar_url"], width=120)

    with col2:
        st.subheader(profile.get("name") or username)
        st.write(profile.get("bio") or "GitHub Developer")
        st.link_button(
            "View GitHub Profile",
            profile["html_url"]
        )

    st.divider()

    # Repository statistics
    stars = sum(
        repo.get("stargazers_count", 0)
        for repo in repos
    )

    languages = Counter(
        repo["language"]
        for repo in repos
        if repo.get("language")
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Public Repositories",
        profile.get("public_repos", 0)
    )
    c2.metric("Stars (Fetched Repos)", stars)
    c3.metric("Languages", len(languages))
    c4.metric("Followers", profile.get("followers", 0))

    st.divider()

    # Language distribution
    st.subheader("💻 Programming Languages")

    if languages:
        fig = px.pie(
            names=list(languages.keys()),
            values=list(languages.values()),
            hole=0.45,
            title="Repositories by Primary Language"
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No programming language data available.")

    # Recent repositories
    st.subheader("📂 Recent Repositories")

    recent_repos = sorted(
        repos,
        key=lambda repo: repo.get("updated_at") or "",
        reverse=True
    )

    if not recent_repos:
        st.info("No repositories found.")

    for repo in recent_repos[:10]:
        with st.container(border=True):
            st.markdown(
                f"**{repo.get('name', 'Unnamed Repository')}**"
            )

            st.write(
                repo.get("description")
                or "No description available."
            )

            st.caption(
                f"Language: {repo.get('language') or 'Unknown'}"
                f" | ⭐ {repo.get('stargazers_count', 0)}"
            )

            if repo.get("html_url"):
                st.link_button(
                    "View Repository",
                    repo["html_url"]
                )

    st.divider()
    st.info("🧠 AI Skill Analysis available separately.")
