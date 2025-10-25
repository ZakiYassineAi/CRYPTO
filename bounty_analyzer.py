#!/usr/bin/env python3
"""
GitHub Bounty Analyzer - Professional Tool
Analyzes GitHub issues for bounty opportunities

Created for demonstrating capabilities
Payment wallet: 0x958BD67f2f6be2Dc46D0e9e0Dd6d33F52EfCA67C
"""

import requests
import json
from datetime import datetime

class BountyAnalyzer:
    """Analyzes GitHub repositories for bounty opportunities"""
    
    def __init__(self, token=None):
        self.token = token
        self.headers = {
            'Accept': 'application/vnd.github.v3+json'
        }
        if token:
            self.headers['Authorization'] = f'token {token}'
    
    def search_bounties(self, keywords=['bounty', 'reward', 'prize']):
        """Search for issues with bounty keywords"""
        results = []
        
        for keyword in keywords:
            query = f'{keyword} is:issue is:open'
            url = f'https://api.github.com/search/issues?q={query}&per_page=10'
            
            try:
                r = requests.get(url, headers=self.headers, timeout=10)
                if r.status_code == 200:
                    items = r.json().get('items', [])
                    results.extend(items)
            except:
                pass
        
        return results
    
    def analyze_issue(self, issue):
        """Analyze an issue for bounty potential"""
        score = 0
        signals = []
        
        # Check title and body
        text = f"{issue.get('title', '')} {issue.get('body', '')}".lower()
        
        # Positive signals
        if any(word in text for word in ['$', 'usd', 'bounty', 'reward']):
            score += 30
            signals.append("💰 Has payment mention")
        
        if any(word in text for word in ['easy', 'simple', 'beginner']):
            score += 20
            signals.append("✅ Marked as easy")
        
        if issue.get('comments', 0) < 5:
            score += 15
            signals.append("✅ Low competition")
        
        # Extract info
        result = {
            'title': issue.get('title', ''),
            'url': issue.get('html_url', ''),
            'repo': issue.get('repository_url', '').split('/')[-2:],
            'score': score,
            'signals': signals,
            'created': issue.get('created_at', ''),
            'comments': issue.get('comments', 0)
        }
        
        return result
    
    def generate_report(self, limit=10):
        """Generate a complete bounty report"""
        print("🔍 Searching for bounty opportunities...")
        issues = self.search_bounties()
        
        print(f"📊 Found {len(issues)} potential bounties")
        
        analyzed = []
        for issue in issues[:limit]:
            result = self.analyze_issue(issue)
            if result['score'] > 20:
                analyzed.append(result)
        
        # Sort by score
        analyzed.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"\n🎯 Top {len(analyzed)} opportunities:")
        for i, item in enumerate(analyzed, 1):
            print(f"\n{i}. {item['title'][:60]}...")
            print(f"   Score: {item['score']}")
            print(f"   URL: {item['url']}")
            for signal in item['signals']:
                print(f"   {signal}")
        
        return analyzed

if __name__ == "__main__":
    analyzer = BountyAnalyzer()
    results = analyzer.generate_report()
    
    # Save results
    with open('bounty_report.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Report saved to bounty_report.json")
    print(f"📧 Contact: Wallet 0x958BD67f2f6be2Dc46D0e9e0Dd6d33F52EfCA67C")
