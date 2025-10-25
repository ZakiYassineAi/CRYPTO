#!/usr/bin/env python3
"""
Cleanup Script - Delete unnecessary repositories
Keep only money-maker-bot
"""

import os
import sys
from github import Github, GithubException

# Configuration
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')
if not GITHUB_TOKEN and os.path.exists('.github_token'):
    GITHUB_TOKEN = open('.github_token').read().strip()

# Repos to keep
KEEP_REPOS = {
    'money-maker-bot',  # Main bot
}

# Repos to potentially delete (based on your screenshot)
REPOS_TO_DELETE = [
    'AirdropGenie',  # Private, no clear purpose
    'Agent',  # Generic name
    'ai-launch-kit',  # Fork
    'raindrop-io-api-client',  # Fork
    'condynsate',  # Fork
]

def list_all_repos():
    """List all repositories"""
    try:
        g = Github(GITHUB_TOKEN)
        user = g.get_user()
        
        print(f"📊 Repositories for: {user.login}\n")
        print(f"{'Name':<30} {'Private':<10} {'Updated':<20}")
        print("-" * 60)
        
        repos = []
        for repo in user.get_repos():
            repos.append(repo)
            privacy = "🔒 Private" if repo.private else "🌍 Public"
            updated = repo.updated_at.strftime('%Y-%m-%d %H:%M')
            print(f"{repo.name:<30} {privacy:<10} {updated:<20}")
        
        print(f"\n📈 Total repositories: {len(repos)}")
        return repos
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def delete_repo(repo_name: str, dry_run: bool = True):
    """Delete a repository"""
    try:
        g = Github(GITHUB_TOKEN)
        user = g.get_user()
        repo = user.get_repo(repo_name)
        
        if dry_run:
            print(f"🔍 Would delete: {repo.full_name}")
            print(f"   Description: {repo.description or 'No description'}")
            print(f"   Stars: {repo.stargazers_count}")
            print(f"   Last update: {repo.updated_at}")
            return True
        else:
            print(f"🗑️  Deleting: {repo.full_name}...")
            repo.delete()
            print(f"✅ Deleted successfully!")
            return True
            
    except GithubException as e:
        print(f"❌ GitHub error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def cleanup_repos(dry_run: bool = True):
    """Clean up unnecessary repositories"""
    print(f"\n{'🔍 DRY RUN MODE' if dry_run else '⚠️  DELETION MODE'}")
    print("=" * 60)
    
    g = Github(GITHUB_TOKEN)
    user = g.get_user()
    
    print(f"\n🎯 Keeping these repos:")
    for repo_name in KEEP_REPOS:
        print(f"   ✅ {repo_name}")
    
    print(f"\n🗑️  Repos to delete:")
    deleted = 0
    errors = 0
    
    for repo_name in REPOS_TO_DELETE:
        try:
            if delete_repo(repo_name, dry_run):
                deleted += 1
            else:
                errors += 1
            print()
        except Exception as e:
            print(f"❌ Error with {repo_name}: {e}\n")
            errors += 1
    
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"   {'Would delete' if dry_run else 'Deleted'}: {deleted}")
    print(f"   Errors: {errors}")
    
    if dry_run:
        print(f"\n💡 To actually delete, run: python3 {sys.argv[0]} --delete")

def main():
    """Main function"""
    print("🧹 Repository Cleanup Tool\n")
    
    if '--list' in sys.argv:
        list_all_repos()
        return
    
    if '--delete' in sys.argv:
        print("⚠️  WARNING: This will PERMANENTLY delete repositories!")
        print("⚠️  This action CANNOT be undone!")
        response = input("\nType 'DELETE' to confirm: ")
        
        if response == 'DELETE':
            cleanup_repos(dry_run=False)
        else:
            print("❌ Cancelled")
    else:
        # Dry run by default
        cleanup_repos(dry_run=True)

if __name__ == "__main__":
    if not GITHUB_TOKEN:
        print("❌ Error: GitHub token not found!")
        print("Create .github_token file or set GITHUB_TOKEN environment variable")
        sys.exit(1)
    
    main()
