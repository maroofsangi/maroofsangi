"""
Syncs the "All Repositories" section of README.md with the account's
current public repositories, pulled live from the GitHub REST API.

Run by .github/workflows/update-readme-projects.yml on a schedule and
on manual dispatch. Only rewrites the file (and only the marked block)
when something actually changed.
"""

import json
import re
import urllib.request

USERNAME = "maroofsangi"

# Repos already hand-featured above, or not meant to be listed here.
EXCLUDE = {
    "maroofsangi",                 # this profile repo itself
    "Ansible_Translation_Layer",   # already in Featured Projects
    "plant_disease_detection",     # already in Featured Projects
    "myproject",                   # already in Featured Projects
    "wheels",                      # already in Featured Projects
}

START = "<!-- AUTO-PROJECTS:START -->"
END = "<!-- AUTO-PROJECTS:END -->"


def fetch_repos():
    url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&sort=updated"
    req = urllib.request.Request(
        url,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "readme-updater"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def build_table(repos):
    rows = []
    for r in repos:
        if r.get("fork") or r.get("archived"):
            continue
        if r["name"] in EXCLUDE:
            continue
        desc = (r.get("description") or "No description yet").replace("|", "-").strip()
        lang = r.get("language") or "—"
        rows.append(f"| [{r['name']}]({r['html_url']}) | {desc} | {lang} |")

    if not rows:
        return "_No additional public repositories yet._"

    header = "| Repository | Description | Language |\n|---|---|---|\n"
    return header + "\n".join(rows)


def main():
    repos = fetch_repos()
    table = build_table(repos)

    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    block = f"{START}\n{table}\n{END}"
    new_content = re.sub(f"{re.escape(START)}.*?{re.escape(END)}", block, content, flags=re.DOTALL)

    if new_content != content:
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(new_content)
        print("README.md updated")
    else:
        print("No changes")


if __name__ == "__main__":
    main()
