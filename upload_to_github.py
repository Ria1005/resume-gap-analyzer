"""
Automated GitHub uploader for Resume-to-Job Gap Analyzer.
Uploads all project files directly to https://github.com/Ria1005/resume-gap-analyzer
using the GitHub REST API.

Usage:
    python upload_to_github.py <YOUR_GITHUB_TOKEN>
"""

import sys
import os
import base64
import json
import urllib.request
import urllib.error
from pathlib import Path

REPO_OWNER = "Ria1005"
REPO_NAME = "resume-gap-analyzer"

# Files and directories to upload
INCLUDE_EXTENSIONS = {
    ".py", ".csv", ".txt", ".md", ".toml", ".png", ".pdf", ".docx", ".gitignore"
}

IGNORED_DIRS = {
    ".git", "__pycache__", "venv", "env", "gap_engine_project",
    "resume_gap_app", "resume_parser_project", "validation_project"
}


def get_project_files():
    root = Path(__file__).parent
    files_to_upload = []

    for path in root.rglob("*"):
        if path.is_file():
            # Check ignored directories
            parts = set(path.parts)
            if parts & IGNORED_DIRS:
                continue
            if path.name.endswith(".zip"):
                continue
            if path.name in ("generate_screenshots.py", "generate_screenshots_selenium.py", "upload_to_github.py"):
                continue

            rel_path = path.relative_to(root).as_posix()
            files_to_upload.append((rel_path, path))

    return sorted(files_to_upload)


def upload_file(rel_path, abs_path, token):
    content_bytes = abs_path.read_bytes()
    b64_content = base64.b64encode(content_bytes).decode("utf-8")

    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{rel_path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "Resume-Gap-Analyzer-Uploader"
    }

    # Check if file already exists to get SHA for update
    sha = None
    try:
        check_req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(check_req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            sha = data.get("sha")
    except urllib.error.HTTPError as e:
        if e.code != 404:
            print(f"  Warning checking {rel_path}: {e}")

    payload = {
        "message": f"Upload {rel_path}",
        "content": b64_content,
        "branch": "main"
    }
    if sha:
        payload["sha"] = sha

    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers, method="PUT")

    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status in (200, 201):
                print(f"Uploaded: {rel_path}")
                return True
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8", errors="replace")
        print(f"Failed to upload {rel_path}: HTTP {e.code} - {err_msg}")
        return False
    except Exception as e:
        print(f"Error uploading {rel_path}: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python upload_to_github.py <YOUR_GITHUB_TOKEN>")
        print("Create a token with 'repo' scope at: https://github.com/settings/tokens")
        sys.exit(1)

    token = sys.argv[1].strip()
    files = get_project_files()
    print(f"Found {len(files)} files to upload to {REPO_OWNER}/{REPO_NAME}...")

    success_count = 0
    for rel_path, abs_path in files:
        if upload_file(rel_path, abs_path, token):
            success_count += 1

    print(f"\nDone! Successfully uploaded {success_count} / {len(files)} files.")
    print(f"Visit: https://github.com/{REPO_OWNER}/{REPO_NAME}")


if __name__ == "__main__":
    main()
