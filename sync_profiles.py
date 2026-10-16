import os
import requests
from dotenv import load_dotenv
from modules.db import get_client, refresh_if_changed

load_dotenv()


def fetch_repos(username):
    headers = {"Accept": "application/vnd.github+json"}
    token = os.getenv("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    repos, page = [], 1
    while page <= 5:
        r = requests.get(
            f"https://api.github.com/users/{username}/repos",
            params={"per_page": 100, "page": page},
            headers=headers, timeout=20,
        )
        r.raise_for_status()
        data = r.json()
        if not data:
            break
        repos += data
        page += 1
    return repos


def main():
    users = (get_client().table("users")
             .select("id, github_username")
             .eq("role", "Student / Fresher").execute().data)
    for u in users:
        if not u.get("github_username"):
            continue
        try:
            repos = fetch_repos(u["github_username"])
            changed = refresh_if_changed(u["id"], repos)
            print(u["github_username"], "updated" if changed else "no change")
        except Exception as e:
            print(u["github_username"], "failed:", e)


if __name__ == "__main__":
    main()