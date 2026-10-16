
import requests

def get_repos(username):
    url = f"https://api.github.com/users/{username}/repos"

    response = requests.get(
        url,
        params={"per_page": 100, "sort": "updated"},
        headers={"Accept": "application/vnd.github+json"},
        timeout=15
    )

    if response.status_code == 404:
        raise Exception("GitHub username not found.")

    if response.status_code != 200:
        raise Exception(
            f"GitHub API error: {response.status_code}"
        )

    return response.json()
