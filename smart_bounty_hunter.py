#!/usr/bin/env python3
"""
Smart Bounty Hunter V2.0
استراتيجية احترافية للبحث عن bounties حقيقية وتنفيذها
"""

import os
import json
import time
import requests
from datetime import datetime
from typing import List, Dict, Optional
import re

class SmartBountyHunter:
    def __init__(self):
        self.github_token = self.load_token()
        self.payment_address = "0x958BD67f2f6be2Dc46D0e9e0Dd6d33F52EfCA67C"
        self.headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.metrics = self.load_metrics()
        
    def load_token(self) -> str:
        """تحميل GitHub token"""
        try:
            with open('.github_token', 'r') as f:
                return f.read().strip()
        except:
            print("❌ Error: .github_token file not found")
            exit(1)
    
    def load_metrics(self) -> Dict:
        """تحميل المقاييس السابقة"""
        try:
            with open('smart_metrics.json', 'r') as f:
                return json.load(f)
        except:
            return {
                "bounties_found": 0,
                "bounties_attempted": 0,
                "prs_submitted": 0,
                "prs_accepted": 0,
                "total_earned": 0,
                "opportunities": [],
                "last_updated": None
            }
    
    def save_metrics(self):
        """حفظ المقاييس"""
        self.metrics["last_updated"] = datetime.now().isoformat()
        with open('smart_metrics.json', 'w') as f:
            json.dump(self.metrics, f, indent=2)
    
    def calculate_priority_score(self, bounty: Dict) -> float:
        """
        حساب درجة الأولوية للbounty
        Score = (Amount × Probability) / Estimated_Hours
        """
        amount = bounty.get('amount', 0)
        
        # تقدير احتمالية النجاح
        probability = 0.5  # default
        
        # زيادة الاحتمال إذا:
        if bounty.get('repo_active', False):
            probability += 0.2
        if bounty.get('clear_requirements', False):
            probability += 0.15
        if bounty.get('maintainer_responsive', False):
            probability += 0.15
        
        # تقدير الوقت المطلوب
        complexity = bounty.get('complexity', 'medium')
        hours = {
            'easy': 2,
            'medium': 6,
            'hard': 16
        }.get(complexity, 6)
        
        score = (amount * probability) / hours
        return round(score, 2)
    
    def search_algora_bounties(self) -> List[Dict]:
        """البحث في Algora عن bounties نشطة"""
        print("\n🎯 Searching Algora bounties...")
        
        try:
            # Algora API endpoint
            response = requests.get(
                "https://console.algora.io/api/bounties",
                headers={"Accept": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                bounties = []
                
                for item in data.get('bounties', []):
                    if item.get('status') == 'open':
                        bounty = {
                            'platform': 'algora',
                            'title': item.get('title', ''),
                            'amount': item.get('reward_amount', 0) / 100,  # cents to dollars
                            'url': item.get('html_url', ''),
                            'repo': item.get('repository', {}).get('full_name', ''),
                            'created_at': item.get('created_at', ''),
                            'complexity': self.estimate_complexity(item.get('title', '')),
                        }
                        
                        # تحليل الجودة
                        bounty['priority_score'] = self.calculate_priority_score(bounty)
                        
                        if bounty['amount'] >= 50:  # فقط bounties > $50
                            bounties.append(bounty)
                
                print(f"✅ Found {len(bounties)} Algora bounties > $50")
                return sorted(bounties, key=lambda x: x['priority_score'], reverse=True)
            
        except Exception as e:
            print(f"⚠️ Error searching Algora: {e}")
        
        return []
    
    def search_github_bounties(self) -> List[Dict]:
        """البحث في GitHub Issues مع bounties"""
        print("\n🔍 Searching GitHub bounties...")
        
        bounties = []
        
        # keywords للبحث
        keywords = [
            "bounty $",
            "reward $",
            "prize $",
            "paid issue",
            "compensation $"
        ]
        
        for keyword in keywords:
            try:
                url = "https://api.github.com/search/issues"
                params = {
                    'q': f'{keyword} is:issue is:open',
                    'sort': 'created',
                    'order': 'desc',
                    'per_page': 10
                }
                
                response = requests.get(url, headers=self.headers, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for item in data.get('items', []):
                        # استخراج المبلغ من العنوان أو الوصف
                        text = f"{item['title']} {item.get('body', '')}"
                        amount = self.extract_amount(text)
                        
                        if amount >= 50:  # فقط > $50
                            bounty = {
                                'platform': 'github',
                                'title': item['title'],
                                'amount': amount,
                                'url': item['html_url'],
                                'repo': item['repository_url'].split('/')[-2:],
                                'created_at': item['created_at'],
                                'labels': [l['name'] for l in item.get('labels', [])],
                                'comments': item.get('comments', 0),
                                'complexity': self.estimate_complexity(item['title'])
                            }
                            
                            bounty['priority_score'] = self.calculate_priority_score(bounty)
                            bounties.append(bounty)
                
                time.sleep(2)  # rate limiting
                
            except Exception as e:
                print(f"⚠️ Error searching '{keyword}': {e}")
        
        # إزالة المكررات
        unique_bounties = {b['url']: b for b in bounties}.values()
        sorted_bounties = sorted(unique_bounties, key=lambda x: x['priority_score'], reverse=True)
        
        print(f"✅ Found {len(sorted_bounties)} GitHub bounties > $50")
        return list(sorted_bounties)
    
    def extract_amount(self, text: str) -> float:
        """استخراج المبلغ المالي من النص"""
        # patterns للبحث عن مبالغ
        patterns = [
            r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)',  # $1000 or $1,000.00
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:USD|dollars?)',  # 1000 USD
            r'bounty[:\s]+\$?\s*(\d+)',  # bounty: $100
            r'reward[:\s]+\$?\s*(\d+)',  # reward: $100
        ]
        
        amounts = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    amount = float(match.replace(',', ''))
                    amounts.append(amount)
                except:
                    continue
        
        return max(amounts) if amounts else 0
    
    def estimate_complexity(self, title: str) -> str:
        """تقدير تعقيد المهمة"""
        title_lower = title.lower()
        
        easy_keywords = ['typo', 'documentation', 'readme', 'comment', 'formatting']
        hard_keywords = ['refactor', 'architecture', 'security', 'performance', 'algorithm']
        
        if any(k in title_lower for k in easy_keywords):
            return 'easy'
        elif any(k in title_lower for k in hard_keywords):
            return 'hard'
        else:
            return 'medium'
    
    def analyze_repo_quality(self, repo_url: str) -> Dict:
        """تحليل جودة ونشاط المشروع"""
        try:
            # استخراج owner/repo من URL
            parts = repo_url.replace('https://github.com/', '').split('/')
            if len(parts) >= 2:
                owner, repo = parts[0], parts[1]
                
                # جلب معلومات المشروع
                api_url = f"https://api.github.com/repos/{owner}/{repo}"
                response = requests.get(api_url, headers=self.headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # تحليل النشاط
                    pushed_at = datetime.fromisoformat(data['pushed_at'].replace('Z', '+00:00'))
                    days_since_push = (datetime.now(pushed_at.tzinfo) - pushed_at).days
                    
                    return {
                        'stars': data.get('stargazers_count', 0),
                        'forks': data.get('forks_count', 0),
                        'open_issues': data.get('open_issues_count', 0),
                        'days_since_push': days_since_push,
                        'active': days_since_push < 30,
                        'popular': data.get('stargazers_count', 0) > 100,
                        'language': data.get('language', 'Unknown')
                    }
        except Exception as e:
            print(f"⚠️ Error analyzing repo: {e}")
        
        return {}
    
    def display_opportunities(self, bounties: List[Dict], limit: int = 5):
        """عرض أفضل الفرص"""
        print(f"\n{'='*80}")
        print(f"🎯 TOP {limit} OPPORTUNITIES (sorted by priority score)")
        print(f"{'='*80}\n")
        
        for i, bounty in enumerate(bounties[:limit], 1):
            print(f"#{i} - Priority Score: {bounty.get('priority_score', 0):.2f}")
            print(f"   💰 Amount: ${bounty.get('amount', 0):.2f}")
            print(f"   📋 Title: {bounty.get('title', '')[:80]}")
            print(f"   🔗 URL: {bounty.get('url', '')}")
            print(f"   🏢 Platform: {bounty.get('platform', '')}")
            print(f"   ⚙️ Complexity: {bounty.get('complexity', 'unknown')}")
            print(f"   📁 Repo: {bounty.get('repo', '')}")
            print()
        
        print(f"{'='*80}\n")
    
    def run(self):
        """تشغيل البوت"""
        print("\n" + "="*80)
        print("🚀 SMART BOUNTY HUNTER V2.0")
        print("="*80)
        print(f"💰 Payment Address: {self.payment_address}")
        print(f"📊 Total Earned (historical): ${self.metrics.get('total_earned', 0)}")
        print("="*80 + "\n")
        
        # جمع الfرص من مصادر متعددة
        all_bounties = []
        
        # Algora
        algora_bounties = self.search_algora_bounties()
        all_bounties.extend(algora_bounties)
        
        # GitHub
        github_bounties = self.search_github_bounties()
        all_bounties.extend(github_bounties)
        
        # ترتيب حسب Priority Score
        all_bounties = sorted(all_bounties, key=lambda x: x.get('priority_score', 0), reverse=True)
        
        # حفظ الفرص
        self.metrics['opportunities'] = all_bounties[:20]  # top 20
        self.metrics['bounties_found'] = len(all_bounties)
        self.save_metrics()
        
        # عرض أفضل الفرص
        self.display_opportunities(all_bounties, limit=10)
        
        # توصيات
        print("💡 RECOMMENDATIONS:")
        print("-" * 80)
        if all_bounties:
            top = all_bounties[0]
            print(f"🎯 Best opportunity: {top['title'][:60]}")
            print(f"   Amount: ${top['amount']:.2f}")
            print(f"   Score: {top['priority_score']:.2f}")
            print(f"   Action: Start working on this immediately!")
            print(f"   URL: {top['url']}")
        else:
            print("⚠️ No high-quality bounties found at this time.")
            print("   Check again in 1 hour.")
        print("-" * 80 + "\n")
        
        return all_bounties

if __name__ == "__main__":
    hunter = SmartBountyHunter()
    opportunities = hunter.run()
    
    print(f"\n✅ Search complete!")
    print(f"📊 Found {len(opportunities)} bounties")
    print(f"📁 Results saved to: smart_metrics.json")
    print(f"\n💡 Next steps:")
    print("   1. Review top opportunities above")
    print("   2. Choose one with highest priority score")
    print("   3. Read the issue carefully")
    print("   4. Plan your solution")
    print("   5. Write professional code")
    print("   6. Submit quality PR")
    print("   7. Follow up consistently\n")
