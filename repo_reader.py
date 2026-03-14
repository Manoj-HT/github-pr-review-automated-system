import os
import git

MAX_FILES = 20
MAX_FILE_SIZE = 4000  # chars

def load_repo_context(repo_url, branch, tmp_dir="repo_tmp"):
    if os.path.exists(tmp_dir):
        print(f"    -> Using existing repository clone in {tmp_dir}...")
        return extract_context(tmp_dir)

    print(f"    -> Cloning repository from {repo_url} (branch: {branch})...")
    git.Repo.clone_from(repo_url, tmp_dir, branch=branch)
    print("    -> Extracting repository context files...")
    return extract_context(tmp_dir)

def extract_context(repo_dir):
    context = []
    for root, _, files in os.walk(repo_dir):
        for f in files:
            if f.endswith((".py", ".js", ".ts", ".java")):
                path = os.path.join(root, f)
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as file:
                        content = file.read(MAX_FILE_SIZE)
                        context.append(f"\n### {path}\n{content}")
                except (IOError, OSError) as e:
                    print(f"    -> [!] Warning: Could not read file {path}: {e}")
        if len(context) >= MAX_FILES:
            break
    return "\n".join(context)