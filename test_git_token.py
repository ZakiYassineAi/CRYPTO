import requests

TOKEN = "ghs_GZUrYEdwlpGY4s6C4TlfTji45t3mDl495e4M"
HEADERS = {'Authorization': f'token {TOKEN}', 'Accept': 'application/vnd.github.v3+json'}

# Check user
print("Testing Git Credential Token...")
r = requests.get('https://api.github.com/user', headers=HEADERS)
print(f"User endpoint: {r.status_code}")
if r.status_code == 200:
    print(f"User: {r.json()['login']}")

# Test gist creation
print("\nTesting write permissions...")
gist_data = {
    "description": "API Permission Test",
    "public": False,
    "files": {
        "test.txt": {
            "content": "Testing write access"
        }
    }
}
r2 = requests.post('https://api.github.com/gists', headers=HEADERS, json=gist_data)
print(f"Create gist: {r2.status_code}")

if r2.status_code == 201:
    print("✅ WRITE ACCESS CONFIRMED!")
    gist = r2.json()
    print(f"Gist URL: {gist['html_url']}")
    
    # Clean up
    gist_id = gist['id']
    r3 = requests.delete(f'https://api.github.com/gists/{gist_id}', headers=HEADERS)
    print(f"Cleanup: {r3.status_code}")
else:
    print(f"❌ No write access: {r2.json().get('message', 'Unknown')}")

# Test issue comment
print("\nTesting issue comment permissions...")
# Use a test issue on our own repo or a known public repo
test_data = {
    "body": "Test comment from API"
}
# We'd need a real issue URL here, so skip for now
print("(Skipped - need target issue)")

