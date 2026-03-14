#!/usr/bin/env python3
from github_client import parse_pr_url, fetch_pr
from repo_reader import load_repo_context
from llm import call_llm
from utils import load_policy, extract_json_from_text

SECURITY_POLICY = load_policy("policies/security.md")
COMPANY_POLICY = load_policy("policies/company_standards.md")

def evaluate_pr(pr_url):
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
        "security": f"""
Check for security issues using this policy:
{SECURITY_POLICY}
""",
        "duplication": "Check if PR duplicates existing logic in the repo.",
        "optimization": "Check if code is optimized and idiomatic.",
        "performance": "Check if performance-oriented APIs are used.",
        "standards": f"""
Check against company standards:
{COMPANY_POLICY}
"""
    }

    results = {}

    for check, instruction in checks.items():
        prompt = f"""
PR TITLE:
{pr['title']}

PR DESCRIPTION:
{pr['body']}

DIFF:
{pr['diff']}

REPO CONTEXT:
{repo_context}

TASK:
{instruction}

Respond ONLY in the following JSON format. NO MARKDOWN, NO EXPLANATIONS, NO CODE EXAMPLES:
{{
  "passed": true/false,
  "issues": [{{"file": "...", "reason": "...", "fix": "..."}}]
}}
"""
        print(f"[*] Running LLM evaluation for: {check}...")
        response = call_llm("You are a senior code reviewer.", prompt)
        results[check] = response

    print("[*] All checks completed successfully.")
    return results


if __name__ == "__main__":
    while True:
        pr_link = input("PR URL (or type 'exit' to quit): ")
        if pr_link.lower() == 'exit':
            break

        output = evaluate_pr(pr_link)
        print("\n=== FINAL REVIEW ===\n")
        for k, v in output.items():
            clean_v = extract_json_from_text(v)
            print(f"\n--- {k.upper()} ---\n{clean_v}")