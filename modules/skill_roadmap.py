import re
import streamlit as st
from modules.db import save_roadmap, get_latest_roadmap

# Skills each target role needs, in learning order
ROLE_SKILLS = {
    "AI / ML Engineer": ["Python", "Data Analysis", "Machine Learning", "Deep Learning",
                         "NLP & LLMs", "SQL & Databases", "Deployment & Docker"],
    "Full-Stack Web Developer": ["HTML & CSS", "JavaScript", "Frontend Framework", "Backend & APIs",
                                 "SQL & Databases", "Auth & Security", "Deployment & Docker"],
    "Data Analyst": ["Python", "SQL & Databases", "Data Analysis", "Data Visualization",
                     "Statistics", "Machine Learning"],
    "Backend Developer": ["Python", "Backend & APIs", "SQL & Databases", "Auth & Security",
                          "Testing", "Deployment & Docker"],
}

# How a skill is detected: (GitHub languages, keywords in repo name/description/topics)
DETECT = {
    "Python": (["Python"], []),
    "Data Analysis": (["Jupyter Notebook"], ["pandas", "numpy", "analysis", "analytics", "eda", "dataset", "csv"]),
    "Machine Learning": ([], ["sklearn", "scikit", "ml", "machine learning", "classifier", "prediction", "regression", "model"]),
    "Deep Learning": ([], ["tensorflow", "pytorch", "keras", "cnn", "lstm", "neural", "deep learning", "yolo"]),
    "NLP & LLMs": ([], ["nlp", "llm", "langchain", "openai", "gemini", "chatbot", "rag", "transformer", "gpt", "bert"]),
    "SQL & Databases": (["PLpgSQL", "PLSQL"], ["sql", "mysql", "postgres", "postgresql", "sqlite", "mongodb", "supabase", "firebase", "database", "db"]),
    "Deployment & Docker": (["Dockerfile"], ["docker", "deploy", "deployment", "kubernetes", "vercel", "netlify", "heroku", "aws", "azure", "gcp", "cicd"]),
    "HTML & CSS": (["HTML", "CSS", "SCSS"], []),
    "JavaScript": (["JavaScript", "TypeScript"], []),
    "Frontend Framework": ([], ["react", "nextjs", "next", "vue", "angular", "svelte", "tailwind", "bootstrap"]),
    "Backend & APIs": ([], ["api", "rest", "flask", "django", "fastapi", "express", "node", "nodejs", "spring", "springboot", "backend", "graphql"]),
    "Data Visualization": ([], ["plotly", "matplotlib", "seaborn", "dashboard", "tableau", "powerbi", "visualization", "visualisation", "chart", "charts"]),
    "Statistics": (["R"], ["statistics", "statistical", "probability", "hypothesis", "stats"]),
    "Auth & Security": ([], ["auth", "authentication", "login", "jwt", "oauth", "bcrypt", "security", "encryption", "signup"]),
    "Testing": ([], ["test", "tests", "testing", "pytest", "unittest", "junit", "jest", "selenium"]),
}

# Learning plan for each skill
PLANS = {
    "Python": {"weeks": 2, "steps": ["Learn variables, loops, functions, lists and dictionaries", "Practice file handling and error handling", "Solve 20 beginner problems on LeetCode or HackerRank"], "project": "A command-line expense tracker saved to a file"},
    "Data Analysis": {"weeks": 2, "steps": ["Learn pandas: load CSV, filter, group, merge", "Learn numpy arrays and basic maths", "Clean a messy real dataset from Kaggle"], "project": "Analyse a Kaggle dataset in a Jupyter Notebook and write your findings in the README"},
    "Machine Learning": {"weeks": 3, "steps": ["Learn the ML workflow: train/test split, overfitting, metrics", "Practice scikit-learn: regression, decision trees, random forest", "Tune a model and compare 3 algorithms"], "project": "Predict a real outcome (house price, crop disease or loan approval) and publish it with a README"},
    "Deep Learning": {"weeks": 3, "steps": ["Understand neural networks, layers and backpropagation", "Learn PyTorch or Keras basics", "Train a small CNN on an image dataset"], "project": "An image classifier with a Streamlit demo"},
    "NLP & LLMs": {"weeks": 3, "steps": ["Learn text cleaning, tokenization and embeddings", "Use a Hugging Face model for classification or summarization", "Call an LLM API and build a small RAG chatbot"], "project": "A chatbot that answers questions from your own PDF notes"},
    "SQL & Databases": {"weeks": 2, "steps": ["Learn SELECT, WHERE, JOIN, GROUP BY", "Design tables with primary and foreign keys", "Connect a database to a Python app (Supabase or SQLite)"], "project": "A student or library management app with a real database"},
    "Deployment & Docker": {"weeks": 1, "steps": ["Learn Git branches and GitHub basics", "Write a Dockerfile and run your app in a container", "Deploy a project online (Streamlit Cloud, Render or Vercel)"], "project": "Deploy one of your projects and add the live link to the README"},
    "HTML & CSS": {"weeks": 2, "steps": ["Learn HTML structure and forms", "Learn CSS flexbox, grid and responsive design", "Rebuild a simple website from a screenshot"], "project": "A personal portfolio website"},
    "JavaScript": {"weeks": 3, "steps": ["Learn variables, functions, arrays and objects", "Learn DOM manipulation and events", "Learn fetch, promises and async/await"], "project": "A weather app that uses a public API"},
    "Frontend Framework": {"weeks": 3, "steps": ["Learn React components, props and state", "Learn hooks (useState, useEffect) and routing", "Style with Tailwind CSS"], "project": "A React task manager that talks to an API"},
    "Backend & APIs": {"weeks": 3, "steps": ["Learn how REST APIs work (GET, POST, PUT, DELETE)", "Build an API with FastAPI, Flask or Express", "Add validation, error handling and a database"], "project": "A REST API for a notes or todo app with documentation"},
    "Data Visualization": {"weeks": 1, "steps": ["Learn matplotlib and plotly charts", "Choose the right chart for each question", "Build a dashboard with Streamlit"], "project": "An interactive dashboard on a public dataset"},
    "Statistics": {"weeks": 2, "steps": ["Learn mean, median, variance and distributions", "Learn probability and hypothesis testing", "Apply them to a dataset in Python"], "project": "An A/B test analysis with conclusions"},
    "Auth & Security": {"weeks": 1, "steps": ["Learn password hashing (bcrypt) and sessions", "Learn JWT and OAuth basics", "Learn common attacks: SQL injection and XSS"], "project": "A login system with roles and protected pages"},
    "Testing": {"weeks": 1, "steps": ["Learn unit tests with pytest or Jest", "Test edge cases and error paths", "Run tests automatically with GitHub Actions"], "project": "Add tests to one of your existing projects"},
}


def _repo_text(repo):
    parts = [repo.get("name") or "", repo.get("description") or ""]
    parts += repo.get("topics") or []
    return " ".join(parts).lower()


def detect_skills(repos, required):
    """Returns (strong: {skill: [repo names]}, missing: [skills])."""
    prepared = []
    for r in repos:
        text = _repo_text(r)
        prepared.append((r, text, set(re.split(r"[^a-z0-9]+", text))))

    strong, missing = {}, []
    for skill in required:
        langs, keywords = DETECT[skill]
        evidence = []
        for r, text, tokens in prepared:
            hit = r.get("language") in langs or any(
                (k in tokens) or (" " in k and k in text) for k in keywords
            )
            if hit:
                evidence.append(r.get("name") or "repo")
        if evidence:
            strong[skill] = evidence
        else:
            missing.append(skill)
    return strong, missing


def build_roadmap(missing):
    week, items = 1, []
    for skill in missing:
        plan = PLANS[skill]
        items.append({
            "skill": skill,
            "start_week": week,
            "end_week": week + plan["weeks"] - 1,
            "steps": plan["steps"],
            "project": plan["project"],
        })
        week += plan["weeks"]
    return items


def render_skill_roadmap_page():
    st.title("🗺️ Skill Roadmap")
    st.caption("See what you are good at, what is missing for your dream role, and how to learn it.")

    repos = st.session_state.get("repos", [])
    if not repos:
        st.info("⚠️ Connect your GitHub account on the **Home** tab first.")
        return

    role = st.selectbox("🎯 Your target role", list(ROLE_SKILLS))
    required = ROLE_SKILLS[role]
    strong, missing = detect_skills(repos, required)
    roadmap = build_roadmap(missing)
    readiness = round(len(strong) / len(required) * 100)

    # Save automatically, and celebrate new skills since last time
    user_id = st.session_state.get("user_id")
    if user_id:
        try:
            latest = get_latest_roadmap(user_id, role)
            if latest:
                gained = [s for s in (latest.get("missing_skills") or []) if s in strong]
                if gained:
                    st.success(f"🎉 New skills since your last visit: {', '.join(gained)}")
            if not latest or latest.get("missing_skills") != missing:
                save_roadmap(user_id, role, list(strong), missing, roadmap)
        except Exception as e:
            st.caption(f"Roadmap could not be saved: {e}")

    c1, c2 = st.columns([1, 3])
    c1.metric("Role readiness", f"{readiness}%")
    c2.write("")
    c2.progress(readiness / 100)

    st.divider()
    left, right = st.columns(2)

    with left:
        st.subheader("✅ Skills you already show")
        if strong:
            for skill, repo_names in strong.items():
                st.success(f"**{skill}**  ·  seen in: {', '.join(repo_names[:2])}")
        else:
            st.info("No required skills detected yet. Start with the roadmap on the right.")

    with right:
        st.subheader("🔧 Skills you are missing")
        if missing:
            for skill in missing:
                st.warning(skill)
        else:
            st.success("You already show every skill for this role. Great work!")

    if roadmap:
        st.divider()
        total_weeks = roadmap[-1]["end_week"]
        st.subheader(f"📅 Your {total_weeks}-week roadmap to {role}")
        for item in roadmap:
            label = f"Week {item['start_week']}–{item['end_week']}  ·  {item['skill']}"
            with st.expander(label, expanded=(item is roadmap[0])):
                for i, step in enumerate(item["steps"], 1):
                    st.write(f"{i}. {step}")
                st.info(f"🛠️ **Project to build and push to GitHub:** {item['project']}")
        st.caption("Push the project to GitHub. RepoX re-checks your repositories, and the skill moves to the green list.")