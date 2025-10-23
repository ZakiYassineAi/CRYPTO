import requests

TOKEN = "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"
HEADERS = {'Authorization': f'token {TOKEN}', 'Accept': 'application/vnd.github.v3+json'}

# Try to get user repos (write test)
print("Testing repository access...")
r = requests.get('https://api.github.com/user/repos', headers=HEADERS)
print(f"Get repos: {r.status_code}")

# Try to create a gist (simple write test)
print("\nTesting gist creation (simple write)...")
gist_data = {
    "description": "Test gist for API permissions",
    "public": False,
    "files": {
        "test.txt": {
            "content": "Testing API write permissions"
        }
    }
}
r2 = requests.post('https://api.github.com/gists', headers=HEADERS, json=gist_data)
print(f"Create gist: {r2.status_code}")
if r2.status_code != 201:
    print(f"Error: {r2.json().get('message', 'Unknown error')}")
else:
    gist = r2.json()
    print(f"Success! Gist URL: {gist['html_url']}")
    
    # Delete test gist
    gist_id = gist['id']
    r3 = requests.delete(f'https://api.github.com/gists/{gist_id}', headers=HEADERS)
    print(f"Deleted test gist: {r3.status_code}")

