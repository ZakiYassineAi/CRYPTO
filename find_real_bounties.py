import requests
import json

TOKEN = "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"
HEADERS = {'Authorization': f'token {TOKEN}'}

print("🎯 Finding REAL Algora Bounty Issues")
print("=" * 80)

# Algora bounties are typically in specific repos they partner with
# Let's search for issues with  "algora prize" or "algora bounty" labels/text

search_patterns = [
    'label:algora is:issue is:open',
    'label:"bounty" is:issue is:open state:open',
    '"on algora.io" is:issue is:open',
    'comments:">0" "algora" "prize" is:issue is:open',
]

all_bounties = []

for pattern in search_patterns:
    print(f"\nSearching: {pattern}")
    url = f'https://api.github.com/search/issues?q={pattern}&per_page=20'
    
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            items = r.json().get('items', [])
            print(f"  Found: {len(items)} issues")
            
            for item in items:
                if item['html_url'] not in [b['html_url'] for b in all_bounties]:
                    all_bounties.append(item)
        else:
            print(f"  Status: {r.status_code}")
    except Exception as e:
        print(f"  Error: {e}")

print(f"\n{'='*80}")
print(f"📊 TOTAL UNIQUE BOUNTY ISSUES: {len(all_bounties)}")
print(f"{'='*80}")

# Analyze each one
for i, issue in enumerate(all_bounties[:10], 1):
    repo_url = issue['repository_url']
    owner_repo = '/'.join(repo_url.split('/')[-2:])
    
    print(f"\n{i}. {issue['title'][:70]}")
    print(f"   🔗 {issue['html_url']}")
    print(f"   📁 {owner_repo}")
    print(f"   💬 {issue['comments']} comments")
    print(f"   🏷️  Labels: {', '.join([l['name'] for l in issue.get('labels', [])])}")

# Save
with open('/home/user/webapp/real_bounties.json', 'w') as f:
    json.dump(all_bounties, f, indent=2, default=str)

print(f"\n✅ Saved {len(all_bounties)} bounties to real_bounties.json")

