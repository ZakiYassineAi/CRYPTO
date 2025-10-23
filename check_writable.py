import requests

TOKEN = "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"
HEADERS = {'Authorization': f'token {TOKEN}'}

print("Fetching Qethys repositories...")
r = requests.get('https://api.github.com/users/Qethys/repos', headers=HEADERS)

if r.status_code == 200:
    repos = r.json()
    print(f"Found {len(repos)} repositories\n")
    
    for repo in repos:
        name = repo['name']
        permissions = repo.get('permissions', {})
        can_push = permissions.get('push', False)
        
        print(f"📁 {name}")
        print(f"   Push: {can_push}")
        print(f"   URL: {repo['html_url']}")
        print()
        
else:
    print(f"Error: {r.status_code}")

