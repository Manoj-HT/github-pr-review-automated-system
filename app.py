import os
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
from main import evaluate_pr
from github_client import create_pr_comment, create_pull_request_with_fixes, parse_pr_url

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return json.load(f)
    return {}

class PRReviewHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            with open(os.path.join(os.path.dirname(__file__), "templates", "index.html"), 'rb') as f:
                self.wfile.write(f.read())
        elif self.path.startswith('/static/'):
            filepath = os.path.join(os.path.dirname(__file__), self.path[1:])
            if os.path.exists(filepath):
                self.send_response(200)
                if filepath.endswith('.css'):
                    self.send_header('Content-Type', 'text/css')
                elif filepath.endswith('.js'):
                    self.send_header('Content-Type', 'application/javascript')
                self.end_headers()
                with open(filepath, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/api/review':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            pr_url = data.get("pr_url")
            user_msg = data.get("user_message", "")
            
            if not pr_url:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "PR URL is required."}).encode('utf-8'))
                return

            try:
                results = evaluate_pr(pr_url, user_msg)
                
                config = load_config()
                features = config.get("features", {})
                
                enable_comment = features.get("enable_comment_on_pr", False)
                enable_create_pr = features.get("enable_create_pr", False)
                auto_raise = features.get("auto_raise_pr", False)
                
                owner, repo, pr_number = parse_pr_url(pr_url)
                
                all_issues = []
                for k, v in results.items():
                    if type(v) == dict and "issues" in v:
                        all_issues.extend(v["issues"])
                
                if enable_comment and all_issues:
                    comment_body = "## Automated PR Review System Findings\n\n"
                    for issue in all_issues:
                        comment_body += f"- **File**: `{issue.get('file', 'N/A')}`\n  **Reason**: {issue.get('reason', '')}\n  **Fix**: {issue.get('fix', '')}\n\n"
                    create_pr_comment(owner, repo, pr_number, comment_body)
                    
                if enable_create_pr or auto_raise:
                    if all_issues:
                        create_pull_request_with_fixes(
                            owner, repo, "branch", 
                            f"Automated PR Fixes for #{pr_number}",
                            "These are suggested fixes from Automated PR Review System.",
                            all_issues
                        )

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                
                if not features.get("enable_show_in_ui", True):
                    self.wfile.write(json.dumps({"results": {"message": "PR evaluated successfully, but 'enable_show_in_ui' is false."}}).encode('utf-8'))
                else:
                    self.wfile.write(json.dumps({"results": results}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    server_address = ('0.0.0.0', 5000)
    httpd = HTTPServer(server_address, PRReviewHandler)
    print("Serving on port 5000...")
    httpd.serve_forever()
