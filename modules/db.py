import os
import secrets
import string

import bcrypt
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()


def _secret(key):
    """Read from .env locally, or from Streamlit secrets when deployed."""
    val = os.getenv(key)
    if val:
        return val
    try:
        import streamlit as st
        return st.secrets[key]
    except Exception:
        return None


_client = None


def get_client():
    global _client
    if _client is None:
        _client = create_client(_secret("SUPABASE_URL"), _secret("SUPABASE_KEY"))
    return _client


def _new_repox_id():
    chars = string.ascii_uppercase + string.digits
    return "RX-" + "".join(secrets.choice(chars) for _ in range(6))


# ---------- Users ----------

def create_user(full_name, email, password, role="Student / Fresher"):
    """Returns (user_dict, None) on success or (None, error_message)."""
    email = email.strip().lower()
    db = get_client()

    # Only these roles can self-register. Admin is set manually in Supabase.
    if role not in ("Student / Fresher", "Recruiter"):
        role = "Student / Fresher"

    existing = db.table("users").select("id").eq("email", email).execute()
    if existing.data:
        return None, "An account with this email already exists."

    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    last_error = ""
    for _ in range(5):
        try:
            res = db.table("users").insert({
                "full_name": full_name.strip(),
                "email": email,
                "password_hash": pw_hash,
                "role": role,
                "repox_id": _new_repox_id(),
            }).execute()
            return _public(res.data[0]), None
        except Exception as e:
            last_error = str(e)
    return None, f"Could not create account: {last_error}"


def verify_user(email, password):
    """Returns (user_dict, None) if login is correct, else (None, error)."""
    res = (get_client().table("users").select("*")
           .eq("email", email.strip().lower()).execute())
    if not res.data:
        return None, "Invalid email or password."
    user = res.data[0]
    if bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        return _public(user), None
    return None, "Invalid email or password."


def _public(user):
    """Never hand the password hash to the UI."""
    return {k: v for k, v in user.items() if k != "password_hash"}


def link_github(user_id, github_username):
    get_client().table("users").update(
        {"github_username": github_username}
    ).eq("id", user_id).execute()


def set_recruiter_consent(user_id, allowed: bool):
    get_client().table("users").update(
        {"recruiter_consent": allowed}
    ).eq("id", user_id).execute()


def get_user_by_repox_id(repox_id):
    """For the recruiter verification page. Respects consent."""
    res = (get_client().table("users")
           .select("id, full_name, github_username, repox_id, recruiter_consent")
           .eq("repox_id", repox_id.strip().upper()).execute())
    if res.data and res.data[0]["recruiter_consent"]:
        return res.data[0]
    return None


# ---------- Analyses ----------

def save_analysis(user_id, skills, job_match=None):
    get_client().table("analyses").insert({
        "user_id": user_id,
        "skills": skills,
        "job_match": job_match,
    }).execute()


def get_latest_analysis(user_id):
    res = (get_client().table("analyses").select("*")
           .eq("user_id", user_id)
           .order("created_at", desc=True).limit(1).execute())
    return res.data[0] if res.data else None


# ---------- Candidate profile (for recruiters) ----------

def build_snapshot(repos):
    """Turn the GitHub repo list into a small summary to store."""
    from collections import Counter
    langs = Counter(r.get("language") for r in repos if r.get("language"))
    top = sorted(repos, key=lambda r: r.get("stargazers_count", 0), reverse=True)[:6]
    return {
        "total_repos": len(repos),
        "total_stars": sum(r.get("stargazers_count", 0) for r in repos),
        "last_push": max((r.get("pushed_at") or "" for r in repos), default=""),
        "languages": dict(langs.most_common()),
        "top_repos": [
            {
                "name": r.get("name"),
                "language": r.get("language"),
                "stars": r.get("stargazers_count", 0),
                "description": r.get("description"),
                "url": r.get("html_url"),
            }
            for r in top
        ],
    }


def _fingerprint(s):
    return (s.get("total_repos"), s.get("total_stars"),
            s.get("last_push"), s.get("languages"))


def refresh_if_changed(user_id, repos):
    """Save a new snapshot only if GitHub activity changed. Returns True if updated."""
    new = build_snapshot(repos)
    latest = get_latest_analysis(user_id)
    old = (latest or {}).get("skills") or {}
    if latest and _fingerprint(old) == _fingerprint(new):
        return False
    save_analysis(user_id, new)
    return True


def find_candidate(repox_id):
    """Returns (profile, None) or (None, error_message)."""
    res = (get_client().table("users")
           .select("id, full_name, github_username, repox_id, recruiter_consent, role")
           .eq("repox_id", repox_id.strip().upper())
           .eq("role", "Student / Fresher").execute())
    if not res.data:
        return None, "No candidate found with this RepoX ID."
    user = res.data[0]
    if not user["recruiter_consent"]:
        return None, "This candidate has not allowed recruiters to view their profile."
    return {"user": user, "analysis": get_latest_analysis(user["id"])}, None