#!/usr/bin/env python3
"""
Executive Monitoring System for Bounty Submissions
Professional follow-up and opportunity tracking
"""

import os
import json
import time
from datetime import datetime, timedelta
from github import Github

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', open('.github_token').read().strip() if os.path.exists('.github_token') else '')

class ExecutiveMonitor:
    def __init__(self):
        self.github = Github(GITHUB_TOKEN)
        self.portfolio = []
        
    def check_hyperswitch_status(self):
        """Check status of our $2000 submission"""
        try:
            repo = self.github.get_repo("juspay/hyperswitch")
            issue = repo.get_issue(6007)
            
            # Get all comments
            comments = list(issue.get_comments())
            
            # Find our comment
            our_comment = None
            for comment in comments:
                if "0x958BD67f2f6be2Dc46D0e9e0Dd6d33F52EfCA67C" in comment.body:
                    our_comment = comment
                    break
            
            if our_comment:
                # Check for replies after our comment
                replies = []
                for comment in comments:
                    if comment.created_at > our_comment.created_at and comment.user.login != our_comment.user.login:
                        replies.append({
                            "user": comment.user.login,
                            "time": comment.created_at.isoformat(),
                            "preview": comment.body[:200]
                        })
                
                status = {
                    "submission_time": our_comment.created_at.isoformat(),
                    "days_waiting": (datetime.now(our_comment.created_at.tzinfo) - our_comment.created_at).days,
                    "replies": replies,
                    "status": "REPLIED" if replies else "PENDING"
                }
                
                return status
        except Exception as e:
            return {"error": str(e)}
    
    def find_new_opportunities(self):
        """Search for new legitimate bounties"""
        opportunities = []
        
        # Search queries for legitimate bounties
        queries = [
            'is:issue is:open label:"bounty" created:>2025-01-01',
            'is:issue is:open "funded" in:title created:>2025-01-01',
            'is:issue is:open "$" label:"help wanted" created:>2025-01-01',
        ]
        
        for query in queries:
            try:
                issues = self.github.search_issues(query, sort='created', order='desc')
                count = 0
                for issue in issues:
                    if count >= 5:
                        break
                    
                    # Analyze if it's legitimate
                    if self.is_legitimate_opportunity(issue):
                        opportunities.append({
                            "title": issue.title,
                            "url": issue.html_url,
                            "repo": issue.repository.full_name,
                            "created": issue.created_at.isoformat(),
                            "labels": [l.name for l in issue.labels]
                        })
                        count += 1
                    
                time.sleep(2)  # Rate limit respect
                
            except Exception as e:
                print(f"Search error: {e}")
        
        return opportunities
    
    def is_legitimate_opportunity(self, issue):
        """Evaluate if opportunity is worth pursuing"""
        # Check repository metrics
        repo = issue.repository
        
        # Legitimacy indicators
        if repo.stargazers_count < 100:  # Too small
            return False
        if repo.archived:  # Dead project
            return False
        if not repo.has_issues:  # Issues disabled
            return False
        
        # Check for clear requirements
        if issue.body and len(issue.body) > 200:  # Has detailed description
            return True
        
        return False
    
    def generate_executive_report(self):
        """Generate executive status report"""
        print("\n" + "="*60)
        print("EXECUTIVE PORTFOLIO REPORT")
        print("="*60)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Check Hyperswitch
        print("📊 ACTIVE SUBMISSIONS:")
        print("-" * 40)
        
        hyperswitch_status = self.check_hyperswitch_status()
        print(f"Hyperswitch MedusaJS Plugin ($2000)")
        print(f"  Status: {hyperswitch_status.get('status', 'UNKNOWN')}")
        print(f"  Days waiting: {hyperswitch_status.get('days_waiting', 'N/A')}")
        if hyperswitch_status.get('replies'):
            print(f"  ⚠️ NEW REPLIES DETECTED - ACTION REQUIRED")
        
        print()
        print("🔍 NEW OPPORTUNITIES:")
        print("-" * 40)
        
        opportunities = self.find_new_opportunities()
        if opportunities:
            for opp in opportunities[:3]:
                print(f"• {opp['title'][:60]}")
                print(f"  Repo: {opp['repo']}")
                print(f"  URL: {opp['url']}")
        else:
            print("No new qualified opportunities found")
        
        print()
        print("💡 RECOMMENDATIONS:")
        print("-" * 40)
        
        if hyperswitch_status.get('days_waiting', 0) > 7:
            print("• Follow up on Hyperswitch submission")
        
        if len(opportunities) > 0:
            print("• Evaluate new opportunities for ROI")
        
        print("• Continue building GitHub reputation")
        print("• Document lessons from each interaction")
        
        print()
        print("="*60)
        
        # Save report
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "hyperswitch": hyperswitch_status,
            "opportunities": opportunities,
            "recommendations": []
        }
        
        with open("executive_report.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        return report_data

def main():
    monitor = ExecutiveMonitor()
    report = monitor.generate_executive_report()
    
    # Professional follow-up if needed
    if report['hyperswitch'].get('days_waiting', 0) >= 7:
        print("\n⚠️ EXECUTIVE ACTION: Consider professional follow-up")

if __name__ == "__main__":
    main()