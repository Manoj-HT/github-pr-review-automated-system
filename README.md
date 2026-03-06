# GitHub PR Review Automated System

An automated code review agent that evaluates Pull Requests against security policies, company standards, and common coding best practices using LLMs.

## Features

- **Automated PR Fetching**: Automatically parses PR URLs and fetches metadata and diffs.
- **Context-Aware Analysis**: Clones the repository to provide full context for better code understanding (e.g., checking for logic duplication).
- **Policy-Based Reviews**: Evaluates code against custom policies:
  - Security (defined in `policies/security.md`)
  - Company Standards (defined in `policies/company_standards.md`)
  - Code Optimization & Optimization
  - Performance APIs
- **JSON Output**: Returns structured results for easy integration.

## Installation

1.  Clone the repository.
2.  Create a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Configure your environment variables (e.g., `.env` for LLM API keys and GitHub tokens).

## Usage

Run the main script:
```bash
python main.py
```

Provide the GitHub PR URL and any additional context or instructions when prompted.

## Project Structure

- `main.py`: Entry point for the PR evaluation logic.
- `github_client.py`: Handles GitHub API interaction.
- `llm.py`: Interface for calling the LLM.
- `repo_reader.py`: Clones repositories and extracts content for context.
- `policies/`: Directory containing markdown files for specific review policies.
- `utils.py`: Utility functions for parsing and data handling.
