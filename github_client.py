import os
import json
import requests
from urllib.parse import urlparse

GITHUB_API = "https://api.github.com"

def get_auth_headers():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config = json.load(f)
            pat = config.get("github", {}).get("pat")
            if pat and pat != "YOUR_PERSONAL_ACCESS_TOKEN":
                return {"Authorization": f"Bearer {pat}", "Accept": "application/vnd.github.v3+json"}
    return {"Accept": "application/vnd.github.v3+json"}

def parse_pr_url(pr_url: str):
    parts = urlparse(pr_url).path.strip("/").split("/")
    owner, repo, _, pr_number = parts
    return owner, repo, pr_number

def fetch_pr(owner, repo, pr_number):
    pr_api = f"{GITHUB_API}/repos/{owner}/{repo}/pulls/{pr_number}"
    diff_url = pr_api + ".diff"

    headers = get_auth_headers()
    
    pr_data_req = requests.get(pr_api, headers=headers)
    pr_data_req.raise_for_status()
    pr_data = pr_data_req.json()
    
    diff_text_req = requests.get(diff_url, headers=headers)
    diff_text = diff_text_req.text

    return {
        "title": pr_data["title"],
        "body": pr_data.get("body", ""),
        "base_repo": pr_data["base"]["repo"]["clone_url"],
        "base_branch": pr_data["base"]["ref"],
        "diff": diff_text
    }

def create_pr_comment(owner, repo, pr_number, body):
    api_url = f"{GITHUB_API}/repos/{owner}/{repo}/issues/{pr_number}/comments"
    headers = get_auth_headers()
    if "Authorization" not in headers:
        print("[!] Cannot add PR comment: Missing GitHub PAT in config.json")
        return False
        
    res = requests.post(api_url, headers=headers, json={"body": body})
    if res.status_code == 201:
        print(f"[*] Successfully added comment to PR #{pr_number}")
        return True
    else:
        print(f"[!] Failed to add comment: {res.text}")
        return False
        
def create_pull_request_with_fixes(owner, repo, base_branch, title, body, changes):
    # This is a simplified placeholder that would use the GitHub API to 
    # 1. Get latest commit SHAs
    # 2. Create a new branch
    # 3. Create blobs for modified files
    # 4. Create a tree
    # 5. Create a commit
    # 6. Update branch ref
    # 7. Create PR
    # For now, we will print that it's mocked due to complexity requirements.
    # In a full production system, we'd use PyGithub or raw API calls as outlined.
    print(f"[*] [MOCK] Would create PR on {owner}/{repo} with title '{title}' fixing {len(changes)} files.")
    return True