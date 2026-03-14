import requests
from urllib.parse import urlparse
import os

GITHUB_API = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def parse_pr_url(pr_url: str):
    parts = urlparse(pr_url).path.strip("/").split("/")
    owner, repo, _, pr_number = parts
    return owner, repo, pr_number

def fetch_pr(owner, repo, pr_number):
    headers = {
        "Accept": "application/vnd.github.v3+json",
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    pr_api_url = f"{GITHUB_API}/repos/{owner}/{repo}/pulls/{pr_number}"
    diff_url = f"{pr_api_url}.diff"

    try:
        pr_response = requests.get(pr_api_url, headers=headers)
        pr_response.raise_for_status()
        pr_data = pr_response.json()

        diff_response = requests.get(diff_url, headers=headers)
        diff_response.raise_for_status()
        diff_text = diff_response.text

        return {
            "title": pr_data["title"],
            "body": pr_data.get("body", ""),
            "base_repo": pr_data["base"]["repo"]["clone_url"],
            "base_branch": pr_data["base"]["ref"],
            "diff": diff_text
        }
    except requests.exceptions.RequestException as e:
        print(f"[!] Error fetching data from GitHub: {e}")
        # Depending on desired behavior, you might want to exit or raise
        raise