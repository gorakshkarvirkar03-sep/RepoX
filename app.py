import streamlit as st
from modules.github_client import get_repos

st.title("RepoX")
username = st.text_input("GitHub username")

if st.button("Fetch repos") and username:
    try:
        repos = get_repos(username)
        if not repos:
            st.warning("No public repositories found.")
        for r in repos:
            st.write(f"**{r['name']}** | {r['language']} | ⭐ {r['stargazers_count']}")
    except Exception as e:
        st.error(f"Error: {e}")