#!/usr/bin/env python3
"""
PR Tracker - نظام متابعة احترافي للـ Pull Requests
يتابع PRs المفتوحة ويرسل تذكيرات في الوقت المناسب
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict

class PRTracker:
    def __init__(self):
        self.github_token = self.load_token()
        self.headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.data = self.load_data()
    
    def load_token(self) -> str:
        """تحميل GitHub token"""
        try:
            with open('.github_token', 'r') as f:
                return f.read().strip()
        except:
            print("❌ Error: .github_token file not found")
            exit(1)
    
    def load_data(self) -> Dict:
        """تحميل بيانات التتبع"""
        try:
            with open('pr_tracking.json', 'r') as f:
                return json.load(f)
        except:
            return {
                "tracked_prs": [],
                "completed_prs": [],
                "earnings": []
            }
    
    def save_data(self):
        """حفظ بيانات التتبع"""
        with open('pr_tracking.json', 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_user_info(self) -> Dict:
        """الحصول على معلومات المستخدم"""
        try:
            response = requests.get(
                "https://api.github.com/user",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"⚠️ Error getting user info: {e}")
        return {}
    
    def fetch_open_prs(self, username: str) -> List[Dict]:
        """جلب PRs المفتوحة للمستخدم"""
        try:
            # البحث عن PRs المفتوحة
            url = "https://api.github.com/search/issues"
            params = {
                'q': f'is:pr is:open author:{username}',
                'sort': 'created',
                'order': 'desc',
                'per_page': 100
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('items', [])
        
        except Exception as e:
            print(f"⚠️ Error fetching PRs: {e}")
        
        return []
    
    def check_hyperswitch_pr(self) -> Dict:
        """فحص حالة Hyperswitch PR المحدد"""
        print("\n🔍 Checking Hyperswitch PR status...")
        
        try:
            # البحث عن PR في hyperswitch repo
            url = "https://api.github.com/repos/juspay/hyperswitch/pulls"
            params = {'state': 'all', 'per_page': 100}
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                prs = response.json()
                
                # البحث عن PR للمستخدم
                user_info = self.get_user_info()
                username = user_info.get('login', '')
                
                for pr in prs:
                    if pr['user']['login'] == username:
                        return {
                            'found': True,
                            'number': pr['number'],
                            'title': pr['title'],
                            'state': pr['state'],
                            'url': pr['html_url'],
                            'created_at': pr['created_at'],
                            'updated_at': pr['updated_at'],
                            'merged': pr.get('merged_at') is not None,
                            'comments': pr.get('comments', 0),
                            'review_comments': pr.get('review_comments', 0),
                            'commits': pr.get('commits', 0)
                        }
        
        except Exception as e:
            print(f"⚠️ Error checking Hyperswitch PR: {e}")
        
        return {'found': False}
    
    def analyze_pr_status(self, pr: Dict) -> Dict:
        """تحليل حالة PR وإعطاء توصيات"""
        created = datetime.fromisoformat(pr['created_at'].replace('Z', '+00:00'))
        updated = datetime.fromisoformat(pr['updated_at'].replace('Z', '+00:00'))
        now = datetime.now(created.tzinfo)
        
        days_since_created = (now - created).days
        days_since_updated = (now - updated).days
        
        analysis = {
            'days_open': days_since_created,
            'days_since_activity': days_since_updated,
            'needs_action': False,
            'action': None,
            'priority': 'low'
        }
        
        # تحديد الإجراء المطلوب
        if pr.get('state') == 'closed' and not pr.get('merged'):
            analysis['action'] = 'PR was closed without merging - investigate why'
            analysis['priority'] = 'high'
            analysis['needs_action'] = True
        
        elif pr.get('merged'):
            analysis['action'] = '🎉 PR was merged! Check for bounty payment'
            analysis['priority'] = 'high'
            analysis['needs_action'] = True
        
        elif days_since_updated > 7 and pr.get('state') == 'open':
            analysis['action'] = 'No activity for 7+ days - send polite follow-up'
            analysis['priority'] = 'medium'
            analysis['needs_action'] = True
        
        elif days_since_updated > 3 and pr.get('comments', 0) > 0:
            analysis['action'] = 'There might be comments - check and respond'
            analysis['priority'] = 'high'
            analysis['needs_action'] = True
        
        elif days_since_created < 2:
            analysis['action'] = 'Recently submitted - wait for initial review'
            analysis['priority'] = 'low'
        
        else:
            analysis['action'] = 'Monitor - no action needed yet'
            analysis['priority'] = 'low'
        
        return analysis
    
    def generate_follow_up_message(self, pr: Dict, analysis: Dict) -> str:
        """إنشاء رسالة متابعة مناسبة"""
        days = analysis['days_since_activity']
        
        if days > 7:
            return f"""Hello! 👋

I wanted to follow up on this PR. It's been {days} days since the last activity, and I'm happy to:

- Answer any questions
- Make any requested changes
- Provide additional context or documentation
- Rebase if needed

Please let me know if there's anything I can do to help move this forward!

Best regards"""
        
        elif days > 3:
            return f"""Hi! 👋

Just wanted to check in on this PR. I'm available to address any feedback or make changes as needed.

Thanks for your time reviewing this!"""
        
        return ""
    
    def display_pr_report(self, prs: List[Dict]):
        """عرض تقرير شامل عن PRs"""
        print("\n" + "="*80)
        print("📊 PULL REQUEST TRACKING REPORT")
        print("="*80 + "\n")
        
        if not prs:
            print("ℹ️ No open PRs found\n")
            return
        
        # تصنيف PRs حسب الأولوية
        high_priority = []
        medium_priority = []
        low_priority = []
        
        for pr in prs:
            analysis = self.analyze_pr_status(pr)
            pr['analysis'] = analysis
            
            if analysis['priority'] == 'high':
                high_priority.append(pr)
            elif analysis['priority'] == 'medium':
                medium_priority.append(pr)
            else:
                low_priority.append(pr)
        
        # عرض PRs حسب الأولوية
        for priority, prs_list in [('HIGH', high_priority), ('MEDIUM', medium_priority), ('LOW', low_priority)]:
            if prs_list:
                print(f"\n🔴 {priority} PRIORITY PRs:")
                print("-" * 80)
                
                for pr in prs_list:
                    analysis = pr['analysis']
                    print(f"\n📌 PR #{pr.get('number', 'N/A')}: {pr['title'][:60]}")
                    print(f"   🔗 {pr.get('html_url', pr.get('url', ''))}")
                    print(f"   ⏰ Open for {analysis['days_open']} days")
                    print(f"   💬 Comments: {pr.get('comments', 0)} | Review comments: {pr.get('review_comments', 0)}")
                    print(f"   📝 Action needed: {analysis['action']}")
                    
                    if analysis['needs_action']:
                        print(f"   ⚠️ NEEDS ATTENTION!")
                    
                    print()
        
        print("="*80 + "\n")
    
    def run(self):
        """تشغيل نظام التتبع"""
        print("\n" + "="*80)
        print("🎯 PR TRACKER - Professional Follow-up System")
        print("="*80 + "\n")
        
        # الحصول على معلومات المستخدم
        user_info = self.get_user_info()
        username = user_info.get('login', '')
        
        if not username:
            print("❌ Could not get user info")
            return
        
        print(f"👤 User: {username}")
        print(f"📧 Email: {user_info.get('email', 'N/A')}")
        print()
        
        # فحص Hyperswitch PR أولاً
        hyperswitch_status = self.check_hyperswitch_pr()
        
        if hyperswitch_status.get('found'):
            print("✅ Found Hyperswitch PR!")
            print(f"   PR #{hyperswitch_status['number']}: {hyperswitch_status['title']}")
            print(f"   State: {hyperswitch_status['state']}")
            print(f"   Merged: {hyperswitch_status['merged']}")
            print(f"   URL: {hyperswitch_status['url']}")
            
            if hyperswitch_status['merged']:
                print(f"   🎉🎉🎉 PR WAS MERGED! Expected bounty: $2000")
                print(f"   💰 Check payment to: 0x958BD67f2f6be2Dc46D0e9e0Dd6d33F52EfCA67C")
            elif hyperswitch_status['state'] == 'closed':
                print(f"   ⚠️ PR was closed without merging")
            else:
                analysis = self.analyze_pr_status(hyperswitch_status)
                print(f"   📊 Open for {analysis['days_open']} days")
                print(f"   📝 Action: {analysis['action']}")
        else:
            print("ℹ️ No Hyperswitch PR found for this account")
        
        # جلب جميع PRs المفتوحة
        print(f"\n🔍 Fetching all open PRs for {username}...")
        open_prs = self.fetch_open_prs(username)
        
        # عرض التقرير
        self.display_pr_report(open_prs)
        
        # حفظ البيانات
        self.data['tracked_prs'] = [
            {
                'url': pr.get('html_url', pr.get('url', '')),
                'title': pr['title'],
                'state': pr.get('state', 'open'),
                'created_at': pr['created_at'],
                'last_checked': datetime.now().isoformat()
            }
            for pr in open_prs
        ]
        
        self.save_data()
        
        print(f"\n✅ Tracking data saved to pr_tracking.json")
        print(f"📊 Total open PRs: {len(open_prs)}")
        
        # توصيات نهائية
        print("\n💡 NEXT STEPS:")
        print("-" * 80)
        
        needs_action = [pr for pr in open_prs if pr.get('analysis', {}).get('needs_action', False)]
        
        if needs_action:
            print(f"⚠️ {len(needs_action)} PR(s) need your attention:")
            for pr in needs_action[:3]:
                print(f"   • {pr['title'][:60]}")
                print(f"     Action: {pr['analysis']['action']}")
        else:
            print("✅ All PRs are in good standing")
            print("   Continue monitoring and be ready to respond")
        
        print("-" * 80 + "\n")

if __name__ == "__main__":
    tracker = PRTracker()
    tracker.run()
