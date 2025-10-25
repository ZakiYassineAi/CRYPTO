#!/usr/bin/env python3
"""
Deep Opportunity Finder - بحث متعمق عن فرص حقيقية
يركز على مصادر موثوقة وfرص واقعية
"""

import requests
import json
from datetime import datetime
from typing import List, Dict

class DeepOpportunityFinder:
    def __init__(self):
        self.github_token = self.load_token()
        self.headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
    def load_token(self) -> str:
        try:
            with open('.github_token', 'r') as f:
                return f.read().strip()
        except:
            return ""
    
    def search_good_first_issues_with_bounties(self) -> List[Dict]:
        """
        البحث عن good first issues في مشاريع كبيرة معروفة
        التي قد تحتوي على bounties أو تقبل مساهمات
        """
        print("\n🔍 Searching for quality issues in active projects...")
        
        # مشاريع معروفة ونشطة
        quality_repos = [
            # Web frameworks
            "vercel/next.js",
            "remix-run/remix",
            "vitejs/vite",
            "sveltejs/kit",
            
            # Developer tools
            "vercel/turbo",
            "evanw/esbuild",
            "rome/tools",
            
            # Open source platforms
            "supabase/supabase",
            "directus/directus",
            "strapi/strapi",
            
            # Blockchain/Web3
            "ethereum/go-ethereum",
            "ConsenSys/quorum",
            
            # Documentation tools
            "facebook/docusaurus",
            "withastro/astro",
        ]
        
        opportunities = []
        
        for repo in quality_repos[:5]:  # First 5 to avoid rate limits
            try:
                # البحث عن issues
                url = f"https://api.github.com/repos/{repo}/issues"
                params = {
                    'state': 'open',
                    'labels': 'good first issue,help wanted',
                    'per_page': 5
                }
                
                response = requests.get(url, headers=self.headers, params=params, timeout=10)
                
                if response.status_code == 200:
                    issues = response.json()
                    
                    for issue in issues:
                        # تحقق من عدم وجود PR مرتبط
                        if 'pull_request' not in issue:
                            opp = {
                                'repo': repo,
                                'title': issue['title'],
                                'url': issue['html_url'],
                                'number': issue['number'],
                                'labels': [l['name'] for l in issue['labels']],
                                'created_at': issue['created_at'],
                                'comments': issue['comments'],
                                'body': issue['body'][:500] if issue['body'] else '',
                                'source': 'quality_repos'
                            }
                            opportunities.append(opp)
                    
                    print(f"✓ Checked {repo}: found {len(issues)} issues")
            
            except Exception as e:
                print(f"⚠ Error checking {repo}: {e}")
        
        return opportunities
    
    def search_hackerone_public_programs(self) -> List[Dict]:
        """
        البحث عن برامج bug bounty عامة على HackerOne
        (معلومات عامة فقط - لا نحتاج API key)
        """
        print("\n🔍 Searching for security bounty programs...")
        
        # قائمة برامج معروفة ومفتوحة
        known_programs = [
            {
                'platform': 'HackerOne',
                'name': 'Node.js',
                'url': 'https://hackerone.com/nodejs',
                'type': 'Open Source Security',
                'min_bounty': 0,
                'max_bounty': 50000
            },
            {
                'platform': 'HackerOne',
                'name': 'Internet Bug Bounty',
                'url': 'https://hackerone.com/ibb',
                'type': 'Critical Infrastructure',
                'min_bounty': 0,
                'max_bounty': 100000
            },
            {
                'platform': 'Gitcoin',
                'name': 'Open Source Bounties',
                'url': 'https://gitcoin.co/explorer',
                'type': 'Development',
                'min_bounty': 50,
                'max_bounty': 5000
            }
        ]
        
        return known_programs
    
    def check_recent_issues_needing_help(self) -> List[Dict]:
        """
        البحث عن issues حديثة تحتاج مساعدة في مشاريع نشطة
        """
        print("\n🔍 Checking recent issues needing help...")
        
        opportunities = []
        
        try:
            # البحث في GitHub عن issues حديثة مع "help wanted"
            url = "https://api.github.com/search/issues"
            params = {
                'q': 'label:"help wanted" is:issue is:open created:>2025-10-01 stars:>1000',
                'sort': 'created',
                'order': 'desc',
                'per_page': 20
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                for item in data.get('items', []):
                    opp = {
                        'title': item['title'],
                        'url': item['html_url'],
                        'repo': '/'.join(item['repository_url'].split('/')[-2:]),
                        'created_at': item['created_at'],
                        'labels': [l['name'] for l in item['labels']],
                        'comments': item['comments'],
                        'source': 'recent_help_wanted'
                    }
                    opportunities.append(opp)
                
                print(f"✓ Found {len(opportunities)} recent issues needing help")
        
        except Exception as e:
            print(f"⚠ Error: {e}")
        
        return opportunities
    
    def analyze_issue_quality(self, issue: Dict) -> Dict:
        """
        تحليل جودة ال issue وإمكانية العمل عليه
        """
        score = 50  # Base score
        
        # Positive factors
        if issue.get('comments', 0) > 0 and issue.get('comments', 0) < 10:
            score += 10  # Some discussion but not overwhelming
        
        if any(label in str(issue.get('labels', [])).lower() 
               for label in ['good first issue', 'help wanted', 'beginner']):
            score += 15
        
        if issue.get('source') == 'quality_repos':
            score += 20  # Comes from known quality project
        
        # Check if recently created (more likely to still be available)
        try:
            created = datetime.fromisoformat(issue['created_at'].replace('Z', '+00:00'))
            days_old = (datetime.now(created.tzinfo) - created).days
            if days_old < 7:
                score += 15
            elif days_old < 30:
                score += 5
        except:
            pass
        
        # Negative factors
        if issue.get('comments', 0) > 20:
            score -= 15  # Too much discussion, might be complex
        
        return {
            'quality_score': score,
            'recommended': score >= 60,
            'reason': self.get_recommendation_reason(score)
        }
    
    def get_recommendation_reason(self, score: int) -> str:
        """
        سبب التوصية بناءً على النتيجة
        """
        if score >= 80:
            return "Excellent opportunity - recent, clear, and from quality project"
        elif score >= 60:
            return "Good opportunity - worth investigating"
        elif score >= 40:
            return "Moderate - needs careful evaluation"
        else:
            return "Low priority - may be too complex or old"
    
    def generate_report(self):
        """
        إنشاء تقرير شامل بأفضل الفرص
        """
        print("\n" + "="*80)
        print("🎯 DEEP OPPORTUNITY ANALYSIS")
        print("="*80)
        
        all_opportunities = []
        
        # جمع الفرص من مصادر متعددة
        all_opportunities.extend(self.search_good_first_issues_with_bounties())
        all_opportunities.extend(self.check_recent_issues_needing_help())
        
        # تحليل كل فرصة
        for opp in all_opportunities:
            analysis = self.analyze_issue_quality(opp)
            opp['analysis'] = analysis
        
        # ترتيب حسب الجودة
        all_opportunities.sort(key=lambda x: x['analysis']['quality_score'], reverse=True)
        
        # عرض أفضل الفرص
        print("\n" + "="*80)
        print("🏆 TOP OPPORTUNITIES")
        print("="*80 + "\n")
        
        top_opportunities = all_opportunities[:10]
        
        for i, opp in enumerate(top_opportunities, 1):
            analysis = opp['analysis']
            print(f"#{i} - Quality Score: {analysis['quality_score']}/100")
            print(f"   📋 {opp['title'][:70]}")
            print(f"   🔗 {opp['url']}")
            print(f"   📁 Repo: {opp.get('repo', 'N/A')}")
            print(f"   🏷️ Labels: {', '.join(opp.get('labels', [])[:3])}")
            print(f"   💭 Comments: {opp.get('comments', 0)}")
            print(f"   ✨ Status: {analysis['reason']}")
            
            if analysis['recommended']:
                print(f"   ⭐ RECOMMENDED - Start here!")
            print()
        
        # حفظ التقرير
        report_data = {
            'generated_at': datetime.now().isoformat(),
            'total_found': len(all_opportunities),
            'top_opportunities': top_opportunities,
            'security_programs': self.search_hackerone_public_programs()
        }
        
        with open('deep_opportunities.json', 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print("="*80)
        print(f"✅ Found {len(all_opportunities)} total opportunities")
        print(f"📁 Full report saved to: deep_opportunities.json")
        print("="*80 + "\n")
        
        # Security programs
        security_programs = self.search_hackerone_public_programs()
        if security_programs:
            print("\n💼 SECURITY BOUNTY PROGRAMS (Research Recommended)")
            print("="*80)
            for prog in security_programs:
                print(f"\n🔐 {prog['name']}")
                print(f"   Platform: {prog['platform']}")
                print(f"   Type: {prog['type']}")
                print(f"   Rewards: ${prog['min_bounty']} - ${prog['max_bounty']}")
                print(f"   URL: {prog['url']}")
            print()
        
        return top_opportunities

if __name__ == "__main__":
    finder = DeepOpportunityFinder()
    opportunities = finder.generate_report()
    
    if opportunities:
        print("\n💡 RECOMMENDED NEXT STEPS:")
        print("-" * 80)
        print("1. Review top 3 opportunities above")
        print("2. Read each issue thoroughly")
        print("3. Check if you can solve it (tech stack, complexity)")
        print("4. Look for existing PR attempts")
        print("5. If clear: Start coding a professional solution")
        print("6. If unclear: Ask clarifying questions in the issue")
        print("7. Submit quality PR with tests and documentation")
        print("-" * 80 + "\n")
    else:
        print("\n⚠️ No suitable opportunities found right now.")
        print("Try again in a few hours.\n")
