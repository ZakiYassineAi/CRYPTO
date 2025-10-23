import requests

TOKEN = "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"
HEADERS = {'Authorization': f'token {TOKEN}'}

# Check user info
r = requests.get('https://api.github.com/user', headers=HEADERS)
print(f"User endpoint: {r.status_code}")
if r.status_code == 200:
    user = r.json()
    print(f"Username: {user.get('login')}")
    print(f"Scopes: {r.headers.get('X-OAuth-Scopes', 'No scopes header')}")
else:
    print(f"Error: {r.text}")

# Try to get token info
r2 = requests.get('https://api.github.com/rate_limit', headers=HEADERS)
if r2.status_code == 200:
    print(f"\nRate limit check: OK")
    scopes = r2.headers.get('X-OAuth-Scopes', '')
    print(f"Scopes from rate_limit: {scopes}")
    
