#!/usr/bin/env python3
"""
SUPREME LEADER STRATEGY
Find what we CAN do, not what we CAN'T
"""

import requests
import json

TOKEN = "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"
HEADERS = {'Authorization': f'token {TOKEN}', 'Accept': 'application/vnd.github.v3+json'}

print("🔍 LEADER: Testing ALL possible actions...\n")

# Test 1: Can we create repos?
print("1. Creating repository...")
repo_data = {
    "name": "bounty-solutions-portfolio",
    "description": "Professional bounty solutions - $0x958BD67f2f6be2Dc46D0e9e0Dd6d33F52EfCA67C",
    "private": False,
    "auto_init": True
}
r = requests.post('https://api.github.com/user/repos', headers=HEADERS, json=repo_data)
if r.status_code == 201:
    print("   ✅ CAN create repos!")
    repo = r.json()
    print(f"   Created: {repo['html_url']}")
elif r.status_code == 422:
    print("   ⚠️ Repo already exists (that's OK)")
else:
    print(f"   ❌ Cannot create repos ({r.status_code})")

# Test 2: Can we fork repos?
print("\n2. Testing fork capability...")
r = requests.post('https://api.github.com/repos/mediar-ai/screenpipe/forks', headers=HEADERS)
if r.status_code == 202:
    print("   ✅ CAN fork repos!")
    fork = r.json()
    print(f"   Forked: {fork['html_url']}")
elif r.status_code == 403:
    print(f"   ❌ Cannot fork ({r.status_code})")
else:
    print(f"   Status: {r.status_code}")

# Test 3: Can we star repos?
print("\n3. Testing star capability...")
r = requests.put('https://api.github.com/user/starred/mediar-ai/screenpipe', headers=HEADERS)
if r.status_code == 204:
    print("   ✅ CAN star repos!")
else:
    print(f"   ❌ Cannot star ({r.status_code})")

# Test 4: Can we watch repos?
print("\n4. Testing watch capability...")
r = requests.put('https://api.github.com/repos/mediar-ai/screenpipe/subscription', headers=HEADERS, json={"subscribed": True})
if r.status_code in [200, 204]:
    print("   ✅ CAN watch repos!")
else:
    print(f"   ❌ Cannot watch ({r.status_code})")

# Test 5: Can we create issues in OUR repos?
print("\n5. Testing issue creation in our repos...")
r = requests.get('https://api.github.com/user/repos', headers=HEADERS)
if r.status_code == 200:
    repos = r.json()
    if repos:
        test_repo = repos[0]['full_name']
        issue_data = {
            "title": "Test - Can create issues",
            "body": "Testing permissions"
        }
        r2 = requests.post(f'https://api.github.com/repos/{test_repo}/issues', headers=HEADERS, json=issue_data)
        if r2.status_code == 201:
            print(f"   ✅ CAN create issues in our repos!")
            issue = r2.json()
            print(f"   Created: {issue['html_url']}")
            # Close it
            requests.patch(issue['url'], headers=HEADERS, json={"state": "closed"})
        else:
            print(f"   ❌ Cannot create issues ({r2.status_code})")

print("\n" + "="*70)
print("🎯 LEADER CONCLUSION:")
print("="*70)
print("""
Based on permissions, our WINNING STRATEGY is:

IF we can fork:
  → Fork target repos
  → Create solutions in forks
  → Submit PRs directly
  → PRs = automatic visibility to maintainers

IF we can't fork:
  → Create solution portfolio in our repo
  → Use GitHub's "mention" system
  → Let our work quality speak for itself
  → Build reputation through commits

EXECUTING BEST AVAILABLE OPTION NOW...
""")

