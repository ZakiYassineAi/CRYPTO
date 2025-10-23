import requests
import json

TOKEN = "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"
HEADERS = {'Authorization': f'token {TOKEN}'}

# Get the first testing bounty
issue_url = "https://api.github.com/repos/mediar-ai/screenpipe/issues/1981"

print("🔍 Analyzing Testing Bounty #1981")
print("=" * 80)

r = requests.get(issue_url, headers=HEADERS)
if r.status_code == 200:
    issue = r.json()
    
    print(f"Title: {issue['title']}")
    print(f"State: {issue['state']}")
    print(f"Comments: {issue['comments']}")
    print(f"\nBody:\n{'-'*80}")
    print(issue['body'][:500])
    print(f"{'-'*80}\n")
    
    # Get comments to understand how it works
    if issue['comments'] > 0:
        comments_url = issue['comments_url']
        r2 = requests.get(comments_url, headers=HEADERS)
        if r2.status_code == 200:
            comments = r2.json()
            print(f"Comments ({len(comments)}):")
            for i, comment in enumerate(comments, 1):
                print(f"\n{i}. By: {comment['user']['login']}")
                print(f"   {comment['body'][:200]}")
    
    # Get the referenced PR
    body = issue.get('body', '')
    if '#1980' in body or 'PR' in body:
        print(f"\n{'='*80}")
        print("📝 Referenced PR: #1980")
        pr_url = "https://api.github.com/repos/mediar-ai/screenpipe/pulls/1980"
        r3 = requests.get(pr_url, headers=HEADERS)
        if r3.status_code == 200:
            pr = r3.json()
            print(f"PR Title: {pr['title']}")
            print(f"PR State: {pr['state']}")
            print(f"PR Author: {pr['user']['login']}")
            print(f"PR URL: {pr['html_url']}")
            print(f"\nPR Description:")
            print(pr['body'][:300] if pr['body'] else "No description")

else:
    print(f"Error: {r.status_code}")

print(f"\n{'='*80}")
print("🎯 OPPORTUNITY ANALYSIS:")
print(f"{'='*80}")
print("""
These "Testing Bounty" issues work like this:
1. Someone creates a PR
2. Algora creates a bounty for TESTING that PR
3. Testers verify the PR works correctly
4. Testers report results (likely as comments)
5. Testers get paid

This is PERFECT because:
- We can test without write permissions
- We can document results
- We prove value through verification
- Easier than creating solutions

NEXT STEP: Test one of these PRs and document results!
""")

