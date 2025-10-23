import requests
import json

TOKEN = "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"
HEADERS = {'Authorization': f'token {TOKEN}'}

print("🎯 Finding PR-able bounty issues...")
print("=" * 70)

# Search for simple issues with bounties
queries = [
    'label:"good first issue" algora.io is:issue is:open',
    'label:documentation algora.io is:issue is:open',
    'typo algora.io is:issue is:open',
]

best_issues = []

for query in queries:
    url = f'https://api.github.com/search/issues?q={query}&per_page=5'
    r = requests.get(url, headers=HEADERS, timeout=15)
    
    if r.status_code == 200:
        issues = r.json().get('items', [])
        for issue in issues:
            # Get repo info
            repo_url = issue['repository_url']
            repo_name = repo_url.split('/')[-2] + '/' + repo_url.split('/')[-1]
            
            # Check if it's a real code repo (not meta repo)
            if repo_name not in ['algora-io/algora', 'algoworld/algoworld']:
                continue
            
            print(f"\n📌 {issue['title']}")
            print(f"   Repo: {repo_name}")
            print(f"   URL: {issue['html_url']}")
            print(f"   Comments: {issue['comments']}")
            print(f"   Labels: {[l['name'] for l in issue.get('labels', [])]}")
            
            # Check if we can fork this repo
            r2 = requests.get(repo_url, headers=HEADERS)
            if r2.status_code == 200:
                repo_info = r2.json()
                print(f"   Fork: {repo_info.get('fork', False)}")
                print(f"   Forkable: {repo_info.get('allow_forking', True)}")
                
                best_issues.append({
                    'issue': issue,
                    'repo': repo_info
                })

print("\n" + "=" * 70)
print(f"Found {len(best_issues)} potential opportunities")

# Save for analysis
with open('/home/user/webapp/opportunities.json', 'w') as f:
    json.dump(best_issues, f, indent=2)

if best_issues:
    print("\n🎯 BEST OPPORTUNITY:")
    best = best_issues[0]
    print(f"Title: {best['issue']['title']}")
    print(f"URL: {best['issue']['html_url']}")
    print(f"Repo: {best['repo']['full_name']}")

