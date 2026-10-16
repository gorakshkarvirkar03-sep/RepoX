import re
import requests
import streamlit as st
from modules.skill_roadmap import detect_skills, DETECT

# Words in a job post that show it needs a skill
JOB_KEYWORDS = {
    "Python": ["python", "django", "flask", "fastapi"],
    "Data Analysis": ["pandas", "numpy", "data analysis", "data analyst", "analytics", "jupyter"],
    "Machine Learning": ["machine learning", "scikit", "sklearn", "ml engineer", "predictive"],
    "Deep Learning": ["deep learning", "tensorflow", "pytorch", "keras", "neural network", "computer vision"],
    "NLP & LLMs": ["nlp", "llm", "langchain", "openai", "generative ai", "large language", "rag"],
    "SQL & Databases": ["sql", "mysql", "postgres", "postgresql", "mongodb", "database", "redis"],
    "Deployment & Docker": ["docker", "kubernetes", "aws", "azure", "gcp", "ci/cd", "devops", "terraform"],
    "HTML & CSS": ["html", "css", "sass", "tailwind"],
    "JavaScript": ["javascript", "typescript", "node.js", "nodejs"],
    "Frontend Framework": ["react", "vue", "angular", "next.js", "svelte"],
    "Backend & APIs": ["rest api", "restful", "graphql", "backend", "back-end", "api"],
    "Data Visualization": ["tableau", "power bi", "powerbi", "looker", "data visualization", "plotly"],
    "Statistics": ["statistics", "statistical", "a/b test", "hypothesis"],
    "Auth & Security": ["oauth", "jwt", "security", "authentication"],
    "Testing": ["pytest", "unit test", "jest", "selenium", "qa automation", "testing"],
}

SENIOR_WORDS = ["senior", "sr.", "sr ", "lead", "principal", "staff", "manager",
                "head of", "director", "architect"]


def _clean(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html or ""))


def _has(text, keyword):
    pattern = r"(?<![a-z0-9])" + re.escape(keyword) + r"(?![a-z0-9])"
    return re.search(pattern, text) is not None


def _job_skills(job):
    text = " ".join([
        job.get("title") or "",
        " ".join(job.get("tags") or []),
        _clean(job.get("description"))[:4000],
    ]).lower()
    return [skill for skill, words in JOB_KEYWORDS.items()
            if any(_has(text, w) for w in words)]


def _open_to_india(location):
    loc = (location or "").lower()
    return (not loc) or any(w in loc for w in ["worldwide", "anywhere", "india", "asia", "apac", "global"])


@st.cache_data(ttl=6 * 60 * 60, show_spinner="Loading live jobs...")
def load_jobs():
    """Fetch the Remotive feed (cached 6 hours to respect their usage limit)."""
    r = requests.get(
        "https://remotive.com/api/remote-jobs",
        timeout=25,
        headers={"User-Agent": "RepoX-hackathon-app"},
    )
    r.raise_for_status()
    jobs = []
    for j in r.json().get("jobs", []):
        skills = _job_skills(j)
        if not skills:
            continue
        jobs.append({
            "id": j.get("id"),
            "title": j.get("title") or "Untitled",
            "company": j.get("company_name") or "",
            "location": j.get("candidate_required_location") or "",
            "type": (j.get("job_type") or "").replace("_", " "),
            "date": (j.get("publication_date") or "")[:10],
            "salary": j.get("salary") or "",
            "url": j.get("url") or "",
            "skills": skills,
        })
    return jobs


def _go_roadmap():
    st.session_state["navigation_radio"] = "Skill Roadmap"


def _card(j, can_apply):
    with st.container(border=True):
        st.markdown(f"**{j['title']}**  ·  {j['company']}")
        meta = f"📍 {j['location'] or 'Remote'}"
        if j["type"]:
            meta += f"  ·  {j['type']}"
        if j["date"]:
            meta += f"  ·  Posted {j['date']}"
        if j["salary"]:
            meta += f"  ·  💰 {j['salary']}"
        st.caption(meta)

        st.progress(j["score"] / 100)
        st.caption(f"Skill match: {j['score']}%")
        if j["have"]:
            st.markdown("✅ You have: " + " ".join(f"`{s}`" for s in j["have"]))
        if j["lack"]:
            st.markdown("🔧 You need: " + " ".join(f"`{s}`" for s in j["lack"]))

        if can_apply:
            st.markdown(f"[Apply on Remotive →]({j['url']})")
        else:
            st.button("🗺️ Build these skills", key=f"learn_{j['id']}", on_click=_go_roadmap)
            st.markdown(f"[View job on Remotive]({j['url']})")


def render_live_jobs_page():
    st.title("💼 Live Jobs For You")
    st.caption("Current remote openings matched with the skills found in your GitHub projects.")

    repos = st.session_state.get("repos", [])
    if not repos:
        st.info("⚠️ Connect your GitHub account on the **Home** tab first.")
        return

    strong, _ = detect_skills(repos, list(DETECT))
    my_skills = set(strong)
    st.markdown("**Your skills:** " + (" ".join(f"`{s}`" for s in strong) or "none detected yet"))

    f1, f2 = st.columns(2)
    hide_senior = f1.checkbox("Hide senior / lead roles", value=True)
    only_open = f2.checkbox("Only jobs open to India / worldwide", value=True)

    try:
        jobs = load_jobs()
    except Exception as e:
        st.error(f"Could not load jobs right now. Please try again later. ({e})")
        return

    can, cannot = [], []
    for j in jobs:
        if hide_senior and any(w in j["title"].lower() for w in SENIOR_WORDS):
            continue
        if only_open and not _open_to_india(j["location"]):
            continue
        have = [s for s in j["skills"] if s in my_skills]
        lack = [s for s in j["skills"] if s not in my_skills]
        score = round(len(have) / len(j["skills"]) * 100)
        item = {**j, "have": have, "lack": lack, "score": score}
        (can if score >= 60 else cannot).append(item)

    can.sort(key=lambda x: (-x["score"], x["date"]), reverse=False)
    cannot.sort(key=lambda x: (-x["score"], len(x["lack"])))

    tab_can, tab_cannot = st.tabs([
        f"✅ You can apply ({len(can)})",
        f"🔒 Skills needed ({len(cannot)})",
    ])

    with tab_can:
        if not can:
            st.info("No strong matches yet. Check the next tab and build those skills.")
        for j in can[:15]:
            _card(j, True)

    with tab_cannot:
        st.caption("You are missing some skills for these jobs. Learn them and they move to the first tab.")
        if not cannot:
            st.success("Nothing here. You match every job in the list!")
        for j in cannot[:15]:
            _card(j, False)

    st.caption("Jobs provided by [Remotive](https://remotive.com). The list refreshes every 6 hours.")