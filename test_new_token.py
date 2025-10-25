import requests

TOKEN = "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"
HEADERS = {'Authorization': f'token {TOKEN}', 'Accept': 'application/vnd.github.v3+json'}

print("🔥 TESTING NEW TOKEN...")

# Test write access
print("\n1. Creating test gist...")
r = requests.post('https://api.github.com/gists', headers=HEADERS, json={
    "description": "Token test",
    "public": False,
    "files": {"test.txt": {"content": "Testing write access"}}
})

if r.status_code == 201:
    print("✅ WRITE ACCESS CONFIRMED!")
    gist = r.json()
    print(f"   Created: {gist['html_url']}")
    # Delete it
    requests.delete(gist['url'], headers=HEADERS)
    print("   Cleaned up")
else:
    print(f"❌ Failed: {r.status_code}")
    print(f"   {r.json().get('message', 'Unknown error')}")

# Test repo access
print("\n2. Checking repo access...")
r = requests.get('https://api.github.com/user/repos', headers=HEADERS)
if r.status_code == 200:
    repos = r.json()
    print(f"✅ Can access {len(repos)} repos")
else:
    print(f"❌ Failed: {r.status_code}")

# Test comment ability
print("\n3. Testing issue comment...")
r = requests.get('https://api.github.com/repos/Qethys/Agent/issues', headers=HEADERS)
if r.status_code == 200:
    print(f"✅ Can read issues")
else:
    print(f"Status: {r.status_code}")

