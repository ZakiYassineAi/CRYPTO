import requests
import json
import re

TOKEN = "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"
HEADERS = {'Authorization': f'token {TOKEN}'}

print("🔍 Comprehensive Algora Bounty Analysis")
print("=" * 80)

# Get ALL algora issues
url = 'https://api.github.com/search/issues?q=algora.io+in:body+is:issue+is:open&per_page=30&sort=created&order=desc'
r = requests.get(url, headers=HEADERS, timeout=20)

if r.status_code != 200:
    print(f"Error: {r.status_code}")
    exit(1)

issues = r.json().get('items', [])
print(f"📊 Found {len(issues)} total bounty issues\n")

opportunities = []

for i, issue in enumerate(issues, 1):
    repo_url = issue['repository_url']
    owner_repo = '/'.join(repo_url.split('/')[-2:])
    
    # Extract bounty amount
    body = issue.get('body', '')
    bounty_match = re.search(r'(\$\d+|\d+\s*USD)', body, re.IGNORECASE)
    bounty = bounty_match.group(0) if bounty_match else "Unknown"
    
    # Analyze solvability
    title_lower = issue['title'].lower()
    body_lower = body.lower()
    
    score = 0
    reasons = []
    
    # Simple issues worth pursuing
    if any(word in title_lower for word in ['typo', 'spelling', 'grammar']):
        score += 40
        reasons.append("✅ Typo fix (easy)")
    
    if any(word in title_lower for word in ['doc', 'documentation', 'readme']):
        score += 35
        reasons.append("✅ Documentation (medium)")
    
    if 'bug' in title_lower and 'link' in title_lower:
        score += 30
        reasons.append("✅ Link bug (easy)")
    
    if any(word in title_lower for word in ['ui', 'display', 'show']):
        score += 20
        reasons.append("✅ UI/Display issue")
    
    # Bonus for clear description
    if len(body) > 200:
        score += 10
        reasons.append("✅ Good description")
    
    # Penalty for complexity
    if issue['comments'] > 5:
        score -= 15
        reasons.append("⚠️ Many comments (competitive)")
    
    if any(word in title_lower for word in ['feature', 'implement', 'add']):
        score -= 10
        reasons.append("⚠️ Feature request (complex)")
    
    if score > 20:  # Only show promising ones
        print(f"\n{'='*80}")
        print(f"#{i} Score: {score}/100 | Bounty: {bounty}")
        print(f"📌 {issue['title']}")
        print(f"🔗 {issue['html_url']}")
        print(f"📁 Repo: {owner_repo}")
        print(f"💬 Comments: {issue['comments']}")
        
        for reason in reasons:
            print(f"   {reason}")
        
        opportunities.append({
            'score': score,
            'issue': issue,
            'bounty': bounty,
            'repo': owner_repo,
            'reasons': reasons
        })

# Sort by score
opportunities.sort(key=lambda x: x['score'], reverse=True)

print(f"\n{'='*80}")
print(f"🎯 TOP 3 BEST OPPORTUNITIES:")
print(f"{'='*80}")

for i, opp in enumerate(opportunities[:3], 1):
    print(f"\n{i}. Score: {opp['score']}/100 | Bounty: {opp['bounty']}")
    print(f"   Title: {opp['issue']['title']}")
    print(f"   URL: {opp['issue']['html_url']}")
    print(f"   Repo: {opp['repo']}")

# Save full report
with open('/home/user/webapp/bounty_analysis.json', 'w') as f:
    json.dump(opportunities, f, indent=2, default=str)

print(f"\n✅ Full analysis saved to bounty_analysis.json")
print(f"📊 Total promising opportunities: {len(opportunities)}")

