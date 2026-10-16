
import streamlit as st
from collections import Counter

# Hackathon MVP role definitions.
# These are illustrative skill requirements,
# not requirements from live job postings.

JOB_ROLES = {
    "Python Developer": [
        "Python", "SQL", "Git", "Django", "Flask"
    ],
    "Full-Stack Developer": [
        "Python", "JavaScript", "HTML", "CSS",
        "React", "SQL"
    ],
    "AI/ML Engineer": [
        "Python", "SQL", "NumPy", "Pandas",
        "Scikit-learn", "TensorFlow"
    ],
    "Data Analyst": [
        "Python", "SQL", "Pandas", "Excel",
        "Power BI"
    ],
    "Backend Developer": [
        "Python", "SQL", "Git", "FastAPI",
        "Docker"
    ],
    "Frontend Developer": [
        "HTML", "CSS", "JavaScript",
        "React", "TypeScript"
    ]
}


def extract_skills(repos):
    """
    Extract evidence of technologies from
    GitHub repository primary languages.

    This is a baseline, not deep code analysis.
    """
    skills = set()

    for repo in repos:
        language = repo.get("language")

        if language:
            skills.add(language.strip().lower())

    return skills


def calculate_job_matches(skills):
    results = []

    for role, required_skills in JOB_ROLES.items():

        matched = [
            skill for skill in required_skills
            if skill.lower() in skills
        ]

        missing = [
            skill for skill in required_skills
            if skill.lower() not in skills
        ]

        score = round(
            len(matched) / len(required_skills) * 100
        )

        results.append({
            "role": role,
            "score": score,
            "matched": matched,
            "missing": missing
        })

    return sorted(
        results,
        key=lambda result: result["score"],
        reverse=True
    )


def render_job_matching_page():

    st.title("💼 AI Job Matching & Skill Gap Analysis")

    st.caption(
        "Explore career tracks based on technologies "
        "detected in your public GitHub repositories."
    )

    repos = st.session_state.get("repos", [])

    if not repos:
        st.warning(
            "No repositories found. "
            "Connect your GitHub profile first."
        )
        return

    # Extract skills
    skills = extract_skills(repos)

    st.subheader("🧠 Detected Technologies")

    if not skills:
        st.info("No primary languages detected.")
        return

    st.write(", ".join(sorted(skills)))

    st.divider()

    # Match job roles
    matches = calculate_job_matches(skills)

    st.subheader("🎯 Recommended Career Tracks")

    for result in matches:

        with st.container(border=True):

            st.subheader(result["role"])

            st.progress(result["score"] / 100)

            st.metric(
                "Skill Coverage",
                f'{result["score"]}%'
            )

            st.success(
                "Matched: " +
                (
                    ", ".join(result["matched"])
                    if result["matched"]
                    else "None detected"
                )
            )

            if result["missing"]:
                st.warning(
                    "Not detected: " +
                    ", ".join(result["missing"])
                )

            with st.expander("📚 Learning Roadmap"):

                if result["missing"]:
                    for index, skill in enumerate(
                        result["missing"], start=1
                    ):
                        st.write(
                            f"{index}. Learn and build "
                            f"a project using {skill}"
                        )
                else:
                    st.write(
                        "All listed skills detected. "
                        "Explore more advanced projects."
                    )

    st.divider()

    st.caption(
        "Scores measure coverage of illustrative "
        "role skill lists, not hiring probability. "
        "Undetected skills are not necessarily absent."
    )
