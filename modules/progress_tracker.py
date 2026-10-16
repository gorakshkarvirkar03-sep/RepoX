# modules/progress_tracker.py
import streamlit as st
import pandas as pd
import plotly.express as px

def render_progress_page():
    """Render the Developer Progress & Activity Timeline UI."""
    st.title("📈 Developer Progress Journey")
    st.caption("Track your GitHub output momentum, milestone achievements, and growth roadmap.")

    repos = st.session_state.get("repos", [])
    username = st.session_state.get("username", "Developer")

    if not repos:
        st.info("⚠️ Connect your GitHub account on the **Home** tab first to view your progress timeline.")
        return

    # Extract repository creation dates and languages for visualization
    repo_data = []
    for r in repos:
        created = r.get("created_at")
        name = r.get("name", "Unnamed")
        lang = r.get("language", "Unknown") or "Unknown"
        stars = r.get("stargazers_count", 0)

        if created:
            # Parse year-month string (e.g., "2024-05")
            month_str = created[:7]
            repo_data.append({
                "Repository": name,
                "Month": month_str,
                "Language": lang,
                "Stars": stars
            })

    # --- TIMELINE MOMENTUM CHART ---
    if repo_data:
        df_repos = pd.DataFrame(repo_data)
        df_timeline = df_repos.groupby(["Month", "Language"]).size().reset_index(name="Count")
        df_timeline = df_timeline.sort_values("Month")

        st.subheader("🗓️ Repository Creation Momentum")
        fig_timeline = px.bar(
            df_timeline,
            x="Month",
            y="Count",
            color="Language",
            title=f"Activity & Output Timeline for @{username}",
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig_timeline.update_layout(
            margin=dict(t=30, b=20, l=10, r=10),
            height=340,
            xaxis_title="Creation Month",
            yaxis_title="Repositories Created"
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
    else:
        st.info("Repository timestamp data unavailable for visualization.")

    st.divider()

    # --- GAMIFIED MILESTONES & ACTIONABLE ROADMAP ---
    st.subheader("🎯 Developer Growth & Milestone Roadmap")

    metrics = st.session_state.get("ai_metrics", {})
    doc_ratio = metrics.get("doc_ratio", 50)
    total_repos = metrics.get("total_repos", len(repos))
    total_stars = metrics.get("total_stars", 0)

    m_col1, m_col2 = st.columns(2)

    with m_col1:
        st.write("**🏆 Milestone Achievements:**")
        st.checkbox("🚀 Connect GitHub Profile", value=True, disabled=True)
        st.checkbox("📂 Maintain 5+ Public Repositories", value=(total_repos >= 5), disabled=True)
        st.checkbox("📝 Maintain 70%+ Documentation Rate", value=(doc_ratio >= 70), disabled=True)
        st.checkbox("⭐ Earn Community Stars (3+ Stars)", value=(total_stars >= 3), disabled=True)

    with m_col2:
        st.write("**📌 Actionable Next Steps to Level Up:**")
        st.info("1. **Deploy Live Demos:** Add live project URLs to your top repository descriptions.")
        st.info("2. **Enrich READMEs:** Include architecture diagrams, tech stacks, and setup instructions.")
        st.info("3. **Contribute Weekly:** Keep contribution graphs active with small, consistent commits.")