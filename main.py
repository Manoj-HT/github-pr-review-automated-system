import json
from github_client import parse_pr_url, fetch_pr
from repo_reader import load_repo_context
from llm import call_llm
from utils import load_policy, extract_json_from_text

SECURITY_POLICY = load_policy("policies/security.md")
COMPANY_POLICY = load_policy("policies/company_standards.md")

def evaluate_pr(pr_url, user_text):
    print(f"[*] Parsing PR URL: {pr_url}...")
    owner, repo, pr_number = parse_pr_url(pr_url)
    
    print(f"[*] Fetching PR #{pr_number} from {owner}/{repo}...")
    pr = fetch_pr(owner, repo, pr_number)

    print("[*] Loading repository context (this may take a moment)...")
    repo_context = load_repo_context(
        pr["base_repo"],
        pr["base_branch"]
    )

    checks = {
        "security": {
            "instruction": f"Check for security issues using this policy:\n{SECURITY_POLICY}",
            "min_rating": 7
        },
        "duplication": {
            "instruction": "Check if PR duplicates existing logic in the repo.",
            "min_rating": 6
        },
        "optimization": {
            "instruction": "Check if code is optimized and idiomatic.",
            "min_rating": 5
        },
        "performance": {
            "instruction": "Check if performance-oriented APIs are used.",
            "min_rating": 5
        },
        "standards": {
            "instruction": f"Check against company standards:\n{COMPANY_POLICY}",
            "min_rating": 6
        }
    }

    results = {}

    for check, config in checks.items():
        instruction = config["instruction"]
        min_rating = config["min_rating"]
        
        prompt = f"""
PR TITLE:
{pr['title']}

PR DESCRIPTION:
{pr['body']}

DIFF:
{pr['diff']}

REPO CONTEXT:
{repo_context}

USER MESSAGE:
{user_text}

TASK:
{instruction}

Rate the PR for '{check}' on a scale from 1 to 10 (1 is bad, 10 is excellent).
The minimum required rating for '{check}' to pass is {min_rating}.
If the rating is >= {min_rating}, set "passed" to true. Otherwise, set it to false.

Respond ONLY in the following JSON format. NO MARKDOWN, NO EXPLANATIONS, NO CODE EXAMPLES:
{{
  "rating": <integer between 1 and 10>,
  "passed": <true or false based on rating >= {min_rating}>,
  "issues": [{{"file": "...", "reason": "...", "fix": "..."}}]
}}
"""
        print(f"[*] Running LLM evaluation for: {check}...")
        response = call_llm("You are a senior code reviewer.", prompt)
        
        # Parse the JSON response
        clean_json_str = extract_json_from_text(response)
        try:
            parsed = json.loads(clean_json_str)
            results[check] = parsed
        except Exception:
            results[check] = {"error": "Failed to parse JSON", "raw": response}

    print("[*] All checks completed successfully.")
    return results


if __name__ == "__main__":
    pr_link = input("PR URL: ")
    user_msg = input("User message: ")

    output = evaluate_pr(pr_link, user_msg)
    print("\n=== FINAL REVIEW ===\n")
    for k, v in output.items():
        print(f"\n--- {k.upper()} ---\n{json.dumps(v, indent=2)}")