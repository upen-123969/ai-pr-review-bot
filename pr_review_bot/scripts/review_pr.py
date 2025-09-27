# import os
# from github import Github
# from transformers import pipeline

# # GitHub setup
# token = os.environ["GITHUB_TOKEN"]
# repo_name = os.environ["GITHUB_REPOSITORY"]
# pr_number = os.environ["GITHUB_REF"].split("/")[2]

# print(f"GITHUB_REF: {os.environ['GITHUB_REF']}")
# print(f"Captured PR number value: {pr_number}")  # Add this line

# g = Github(token)
# repo = g.get_repo(repo_name)
# pr = repo.get_pull(int(pr_number))

# # Collect PR diff
# diffs = []
# for f in pr.get_files():
#     if f.patch:
#         diffs.append(f"File: {f.filename}\n{f.patch}")
# diff_text = "\n".join(diffs)

# # Load lightweight model (CodeBERT)
# analyzer = pipeline("text-classification", model="microsoft/codebert-base")

# # Simple heuristic: feed code chunks to model and generate comments
# feedback = []
# for chunk in diffs[:3]:  # keep it short
#     analysis = analyzer(chunk[:400])  # model max input length
#     feedback.append(f"- {chunk[:80]}... → {analysis[0]['label']} (score={analysis[0]['score']:.2f})")

# # Post comment back to PR
# comment_body = "🤖 **AI Review Bot Suggestions (lightweight mode):**\n\n" + "\n".join(feedback)
# pr.create_issue_comment(comment_body)
# print("Review posted to PR.")


import os
import requests
from github import Github

# GitHub setup
token = os.environ["GITHUB_TOKEN"]
repo_name = os.environ["GITHUB_REPOSITORY"]
pr_number = os.environ["GITHUB_REF"].split("/")[2]

g = Github(token)
repo = g.get_repo(repo_name)
pr = repo.get_pull(int(pr_number))

# Collect PR diff
diffs = []
for f in pr.get_files():
    if f.patch:
        diffs.append(f"File: {f.filename}\n{f.patch}")
diff_text = "\n".join(diffs)

# Hugging Face Inference API
API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
headers = {"Authorization": f"Bearer {os.environ['HF_TOKEN']}"}

labels = ["style issue", "bug risk", "optimization", "good code"]

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

analysis = query({
    "inputs": diff_text[:400],  # avoid too long input
    "parameters": {"candidate_labels": labels}
})

# Format results
feedback = []
if "labels" in analysis:
    for label, score in zip(analysis["labels"], analysis["scores"]):
        feedback.append(f"- {label}: {score:.2f}")

comment_body = "### 🤖 AI Review Bot Suggestions\n\n" + "\n".join(feedback)

# Post comment on PR
pr.create_issue_comment(comment_body)
print("Review posted to PR via Hugging Face API.")
