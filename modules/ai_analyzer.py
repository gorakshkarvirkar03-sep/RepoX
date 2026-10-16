# modules/ai_analyzer.py
import os
from collections import Counter
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def analyze_repositories(repos: list) -> dict:
    """Compute developer metrics, language distribution, and employability score from GitHub repos."""
    total_repos = len(repos)
    if total_repos == 0:
        return {}

    languages = [r.get("language") for r in repos if r.get("language")]
    lang_counts = Counter(languages)

    total_stars = sum(r.get("stargazers_count", 0) for r in repos)
    total_forks = sum(r.get("forks_count", 0) for r in repos)
    documented_repos = sum(1 for r in repos if r.get("description"))
    doc_ratio = round((documented_repos / total_repos) * 100)

    # Calculate Employability Score (out of 100)
    volume_score = min(total_repos * 3, 25)               # Max 25 pts
    diversity_score = min(len(lang_counts) * 6, 25)       # Max 25 pts
    doc_score = round((doc_ratio / 100) * 25)             # Max 25 pts
    impact_score = min((total_stars * 3) + (total_forks * 2) + 10, 25)  # Max 25 pts

    employability_score = min(volume_score + diversity_score + doc_score + impact_score, 98)

    # Determine Developer Archetype & Career Fit
    top_langs = [lang for lang, _ in lang_counts.most_common(3)]
    top_set = set(top_langs)

    if {"Python", "Jupyter Notebook"} & top_set and len(top_set) <= 2:
        archetype = "AI / Data Science Specialist"
        roles = ["Junior AI/ML Engineer", "Data Scientist", "Python Backend Developer"]
    elif {"JavaScript", "TypeScript", "HTML", "CSS"} & top_set and {"Python", "Java", "Go", "C#"} & top_set:
        archetype = "Full-Stack Polyglot Builder"
        roles = ["Full-Stack Developer", "Software Development Engineer (SDE-1)", "Product Engineer"]
    elif {"Java", "C++", "C#", "Go", "Rust"} & top_set:
        archetype = "Systems & Enterprise Backend Engineer"
        roles = ["Backend Software Engineer", "Java Full-Stack Developer", "Cloud/Systems Engineer"]
    elif {"JavaScript", "TypeScript", "HTML", "CSS", "Dart"} & top_set:
        archetype = "Frontend & UI Application Developer"
        roles = ["Frontend Engineer", "React/Next.js Developer", "Mobile/Web Developer"]
    else:
        archetype = "Versatile Software Generalist"
        roles = ["Associate Software Engineer", "Junior Full-Stack Developer", "Graduate Engineer Trainee"]

    # Dynamic Strengths & Portfolio Gaps
    strengths = []
    gaps = []

    if total_repos >= 8:
        strengths.append(f"Consistent builder with **{total_repos} public repositories** showing active hands-on coding.")
    else:
        gaps.append("Build more public repositories (aim for 8+ quality projects) to demonstrate consistent output.")

    if len(lang_counts) >= 3:
        strengths.append(f"Strong multi-language versatility across **{', '.join(top_langs)}**.")
    else:
        gaps.append("Expand tech stack diversity by adding complementary languages (e.g., SQL, TypeScript, or Docker).")

    if doc_ratio >= 65:
        strengths.append(f"Clear communicator: **{doc_ratio}% of repositories** include project summaries and descriptions.")
    else:
        gaps.append(f"Only **{doc_ratio}% of repositories** have descriptions—add clear descriptions and READMEs to boost recruiter readability.")

    if total_stars >= 3:
        strengths.append(f"Community-validated work with **{total_stars} total GitHub stars**.")
    else:
        gaps.append("Pin top 3 projects on GitHub and include live demo links to attract stars and recruiter clicks.")

    return {
        "total_repos": total_repos,
        "lang_counts": lang_counts,
        "top_langs": top_langs,
        "total_stars": total_stars,
        "total_forks": total_forks,
        "doc_ratio": doc_ratio,
        "employability_score": employability_score,
        "sub_scores": {
            "Project Volume": volume_score * 4,
            "Tech Diversity": diversity_score * 4,
            "Documentation": doc_score * 4,
            "Community Impact": impact_score * 4,
        },
        "archetype": archetype,
        "roles": roles,
        "strengths": strengths,
        "gaps": gaps,
    }


def render_ai_analysis_page():
    """Render the complete AI Skill Analysis UI."""
    st.title("🧠 AI Skill Analysis")
    st.caption("Deep technical intelligence generated from your public GitHub repositories.")

    repos = st.session_state.get("repos", [])
    username = st.session_state.get("username", "Developer")

    if not repos:
        st.info("⚠️ Connect your GitHub account on the **Home** tab first to unlock AI Skill Analysis.")
        return

    metrics = analyze_repositories(repos)
    # Store metrics in session state so Job Matching and Recruiter tabs can reuse them
    st.session_state["ai_metrics"] = metrics

    # --- TOP BANNER: ARCHETYPE & EMPLOYABILITY SCORE ---
    with st.container(border=True):
        col_a, col_b = st.columns([2.2, 1])
        with col_a:
            st.subheader(f"🏷️ Archetype: {metrics['archetype']}")
            st.write(f"Analyzed **{metrics['total_repos']} repositories** for **`@{username}`**.")
            st.write("**Top Recommended Career Tracks:**")
            role_badges = "  ".join([f"`🎯 {r}`" for r in metrics["roles"]])
            st.markdown(role_badges)
        with col_b:
            st.metric(
                label="🚀 AI Employability Score",
                value=f"{metrics['employability_score']} / 100",
                delta="Top 15% Fresher Readiness" if metrics["employability_score"] >= 70 else "Room to Grow"
            )
            st.progress(metrics["employability_score"] / 100)

    # --- KPI ROW ---
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Primary Language", metrics["top_langs"][0] if metrics["top_langs"] else "N/A")
    k2.metric("Tech Stack Breadth", f"{len(metrics['lang_counts'])} Languages")
    k3.metric("Documentation Rate", f"{metrics['doc_ratio']}%")
    k4.metric("Total Stars & Forks", f"⭐ {metrics['total_stars']} | 🍴 {metrics['total_forks']}")

    st.divider()

    # --- CHARTS ROW: LANGUAGE DONUT & SKILL RADAR ---
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("📊 Programming Language Breakdown")
        if metrics["lang_counts"]:
            df_lang = pd.DataFrame(
                list(metrics["lang_counts"].items()),
                columns=["Language", "Repositories"]
            )
            fig_donut = px.pie(
                df_lang,
                names="Language",
                values="Repositories",
                hole=0.45,
                color_discrete_sequence=px.colors.sequential.Indigo_r
            )
            fig_donut.update_layout(margin=dict(t=20, b=20, l=10, r=10), height=320)
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.warning("No primary languages detected across repositories.")

    with c2:
        st.subheader("🕸️ 4-Pillar Engineering Radar")
        categories = list(metrics["sub_scores"].keys())
        values = list(metrics["sub_scores"].values())

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill="toself",
            name="Skill Matrix",
            line_color="#4f46e5"
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            margin=dict(t=30, b=20, l=30, r=30),
            height=320
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    st.divider()

    # --- AI STRENGTHS & ACTIONABLE PORTFOLIO GAPS ---
    s_col, g_col = st.columns(2)

    with s_col:
        st.subheader("✅ Verified Technical Strengths")
        for s in metrics["strengths"]:
            st.success(s)

    with g_col:
        st.subheader("🔧 Actionable Portfolio Improvements")
        for g in metrics["gaps"]:
            st.warning(g)

    st.divider()

    # --- DEEP AI PORTFOLIO REVIEW GENERATOR ---
    st.subheader("🤖 Generate Executive AI Codebase Summary")
    st.caption("Creates a recruiter-ready technical pitch based on your top repositories.")

    if st.button("✨ Generate AI Portfolio Pitch", type="primary"):
        with st.spinner("Synthesizing repository signals..."):
            top_repos_sorted = sorted(
                repos,
                key=lambda x: (x.get("stargazers_count", 0), bool(x.get("description"))),
                reverse=True
            )[:4]
            highlight_names = [r.get("name", "Project") for r in top_repos_sorted]

            pitch = f"""
### 📋 Executive Candidate Brief: `@{username}`
* **Engineering Profile:** {metrics['archetype']} with hands-on implementation across **{', '.join(metrics['top_langs']) or 'multiple stacks'}**.
* **Standout Repositories:** `{ '`, `'.join(highlight_names) }` demonstrate practical problem-solving and modular architecture.
* **Recruiter Takeaway:** Strong fit for **{', '.join(metrics['roles'][:2])}** roles. Moving documentation coverage from **{metrics['doc_ratio']}% to 90%+** and adding CI/CD workflows will elevate this profile into the top 5% of fresher applicants.
"""
            st.info(pitch)