import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()
HEADERS = {"Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"}
BASE = "https://api.github.com"


def get_repos(username):
    r = requests.get(f"{BASE}/users/{username}/repos?per_page=100", headers=HEADERS)
    r.raise_for_status()
    return [repo for repo in r.json() if not repo["fork"]]


def get_file_tree(username, repo, branch="main"):
    r = requests.get(
        f"{BASE}/repos/{username}/{repo}/git/trees/{branch}?recursive=1",
        headers=HEADERS,
    )
    r.raise_for_status()
    return [f["path"] for f in r.json()["tree"] if f["type"] == "blob"]


def get_file_content(username, repo, path):
    r = requests.get(f"{BASE}/repos/{username}/{repo}/contents/{path}", headers=HEADERS)
    r.raise_for_status()
    return base64.b64decode(r.json()["content"]).decode("utf-8", errors="ignore")


def get_commits(username, repo):
    r = requests.get(f"{BASE}/repos/{username}/{repo}/commits?per_page=10", headers=HEADERS)
    r.raise_for_status()
    return r.json()