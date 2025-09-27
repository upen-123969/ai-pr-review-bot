import os
from github import Github
from transformers import pipeline

# GitHub setup
token = os.environ["GITHUB_TOKEN"]
repo_name = os.environ["GITHUB_REPOSITORY"]
pr_number = os.environ["GITHUB_REF"].split("/")[-1]

print(f"GITHUB_REF: {os.environ['GITHUB_REF']}")
print(f"Captured PR number value: {pr_number}")  # Add this line

g = Github(token)
repo = g.get_repo(repo_name)
pr = repo.get_pull(int(pr_number))

# Collect PR diff
diffs = []
for f in pr.get_files():
    if f.patch:
        diffs.append(f"File: {f.filename}\n{f.patch}")
diff_text = "\n".join(diffs)

# Load lightweight model (CodeBERT)
analyzer = pipeline("text-classification", model="microsoft/codebert-base")

# Simple heuristic: feed code chunks to model and generate comments
feedback = []
for chunk in diffs[:3]:  # keep it short
    analysis = analyzer(chunk[:400])  # model max input length
    feedback.append(f"- {chunk[:80]}... → {analysis[0]['label']} (score={analysis[0]['score']:.2f})")

# Post comment back to PR
comment_body = "🤖 **AI Review Bot Suggestions (lightweight mode):**\n\n" + "\n".join(feedback)
pr.create_issue_comment(comment_body)
print("Review posted to PR.")
