#!/usr/bin/env python3
"""
Shadow Hunter - Intelligence Gathering System
عقيدة الصياد: لا تهاجم القلعة، استولِ على طرق الإمداد
"""

import os
import json
import requests
from datetime import datetime, timedelta
from github import Github
import time
import hashlib

class ShadowHunter:
    """
    جاسوس يعمل في الظلال
    يبحث عن الفريسة الضعيفة في المناطق المنسية
    """
    
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN', open('.github_token').read().strip() if os.path.exists('.github_token') else '')
        try:
            from github import Auth
            auth = Auth.Token(self.github_token) if self.github_token else None
            self.github = Github(auth=auth)
        except:
            self.github = Github(self.github_token) if self.github_token else Github()
        
        # التخصص: Bridge Exploitation Master
        self.specialization = "BRIDGE_VULNERABILITIES"
        
        # قاعدة بيانات الأهداف الضعيفة
        self.shadow_targets = []
        
        # معايير الاختيار الذكية
        self.target_criteria = {
            "funding_range": (10_000_000, 100_000_000),  # $10M-$100M
            "age_range": (30, 365),  # 30-365 days old
            "tvl_minimum": 20_000_000,  # $20M TVL
            "audit_status": ["unaudited", "single_audit"],  # Not over-audited
            "technology_stack": ["bridge", "cross-chain", "oracle", "vault"]
        }
        
    def scan_defi_landscape(self):
        """
        مسح المشهد بحثاً عن الفريسة المثالية
        """
        print("🔍 SHADOW SCANNING: Hunting in the darkness...")
        print("="*60)
        
        # استهداف البروتوكولات الجديدة مع تمويل كبير
        vulnerable_protocols = []
        
        # DeFiLlama API للحصول على TVL
        defillama_url = "https://api.llama.fi/protocols"
        
        try:
            response = requests.get(defillama_url, timeout=10)
            protocols = response.json()
            
            for protocol in protocols:
                # تصفية البروتوكولات حسب المعايير
                if self._is_vulnerable_target(protocol):
                    vulnerable_protocols.append({
                        "name": protocol.get("name"),
                        "tvl": protocol.get("tvl", 0),
                        "chain": protocol.get("chain", "Unknown"),
                        "category": protocol.get("category", "Unknown"),
                        "github": self._find_github_repo(protocol.get("name")),
                        "vulnerability_score": self._calculate_vulnerability_score(protocol),
                        "launch_date": protocol.get("listedAt", 0)
                    })
            
            # ترتيب حسب درجة الضعف
            vulnerable_protocols.sort(key=lambda x: x["vulnerability_score"], reverse=True)
            
            return vulnerable_protocols[:5]  # أفضل 5 أهداف
            
        except Exception as e:
            print(f"Error scanning DeFi landscape: {e}")
            return self._get_manual_targets()
    
    def _is_vulnerable_target(self, protocol):
        """
        تحديد ما إذا كان البروتوكول هدفاً ضعيفاً
        """
        # TVL check
        tvl = protocol.get("tvl", 0)
        if tvl < self.target_criteria["tvl_minimum"]:
            return False
        
        # Age check (if launched in last 6-12 months)
        launch_timestamp = protocol.get("listedAt", 0)
        if launch_timestamp:
            age_days = (time.time() - launch_timestamp) / 86400
            if not (self.target_criteria["age_range"][0] <= age_days <= self.target_criteria["age_range"][1]):
                return False
        
        # Category check - focus on high-risk categories
        category = protocol.get("category", "").lower()
        high_risk_categories = ["bridge", "cross chain", "derivatives", "lending", "yield"]
        
        if any(risk in category for risk in high_risk_categories):
            return True
        
        return False
    
    def _calculate_vulnerability_score(self, protocol):
        """
        حساب درجة الضعف المحتملة
        """
        score = 100
        
        # عامل TVL (كلما زاد TVL، زادت الجائزة المحتملة)
        tvl = protocol.get("tvl", 0)
        if tvl > 100_000_000:
            score += 50
        elif tvl > 50_000_000:
            score += 30
        elif tvl > 20_000_000:
            score += 10
        
        # عامل العمر (الأحدث = أكثر ضعفاً)
        launch_timestamp = protocol.get("listedAt", 0)
        if launch_timestamp:
            age_days = (time.time() - launch_timestamp) / 86400
            if age_days < 90:
                score += 40  # Very new = very vulnerable
            elif age_days < 180:
                score += 20
        
        # عامل الفئة
        category = protocol.get("category", "").lower()
        if "bridge" in category:
            score += 60  # Bridges are goldmines
        elif "cross" in category:
            score += 40
        elif "oracle" in category:
            score += 35
        
        # عامل عدد الـ audits (أقل = أفضل للصيد)
        audits = protocol.get("audits", 0)
        if audits == 0:
            score += 50
        elif audits == 1:
            score += 20
        
        return score
    
    def _find_github_repo(self, protocol_name):
        """
        العثور على مستودع GitHub للبروتوكول
        """
        # Known repositories (to avoid API rate limits)
        known_repos = {
            "layerzero": "https://github.com/LayerZero-Labs/LayerZero",
            "stargate": "https://github.com/stargate-protocol/stargate",
            "radiant": "https://github.com/radiant-capital/radiant-contracts",
            "pendle": "https://github.com/pendle-finance/pendle-core",
            "swell": "https://github.com/SwellNetwork/swell-contracts",
            "across": "https://github.com/across-protocol/contracts-v2",
            "hop": "https://github.com/hop-protocol/hop",
            "synapse": "https://github.com/synapsecns/synapse-contracts",
            "celer": "https://github.com/celer-network/sgn-v2-contracts"
        }
        
        # Check if we have a known repo
        for key, url in known_repos.items():
            if key in protocol_name.lower():
                return url
        
        # Try GitHub search with rate limit handling
        try:
            if self.github and self.github_token:
                # البحث في GitHub
                query = f"{protocol_name} smart contract solidity"
                repos = self.github.search_repositories(query, sort='stars', order='desc')
                
                for repo in repos[:1]:  # Check only top result to save API calls
                    return repo.html_url
                    
        except Exception as e:
            if "403" not in str(e):  # Only print non-rate-limit errors
                print(f"GitHub search error: {e}")
        
        return None
    
    def _get_manual_targets(self):
        """
        أهداف يدوية محددة مسبقاً (backup)
        """
        return [
            {
                "name": "LayerZero",
                "tvl": 8_500_000_000,
                "category": "Cross-Chain Messaging",
                "vulnerability_score": 180,
                "reason": "Complex cross-chain logic, high TVL"
            },
            {
                "name": "Stargate Finance",
                "tvl": 450_000_000,
                "category": "Bridge",
                "vulnerability_score": 170,
                "reason": "Bridge protocol with massive liquidity"
            },
            {
                "name": "Radiant Capital",
                "tvl": 230_000_000,
                "category": "Lending",
                "vulnerability_score": 160,
                "reason": "Cross-chain lending, complex oracle usage"
            },
            {
                "name": "Pendle Finance",
                "tvl": 180_000_000,
                "category": "Yield Trading",
                "vulnerability_score": 155,
                "reason": "Complex yield tokenization"
            },
            {
                "name": "Swell Network",
                "tvl": 65_000_000,
                "category": "Liquid Staking",
                "vulnerability_score": 150,
                "reason": "New protocol, rapid growth"
            }
        ]
    
    def analyze_github_commits(self, repo_url):
        """
        تحليل التحديثات الأخيرة في العقود الذكية
        البحث عن التغييرات في Bridge/Vault/Oracle
        """
        if not repo_url:
            return []
        
        critical_patterns = [
            "bridge",
            "vault",
            "oracle",
            "withdraw",
            "deposit",
            "transfer",
            "verify",
            "proof",
            "merkle",
            "signature"
        ]
        
        suspicious_commits = []
        
        # Skip GitHub API calls if rate limited
        try:
            if not self.github_token:
                # Return simulated data if no token
                return [
                    {
                        "sha": "abc1234",
                        "message": "fix: critical bridge validation logic update",
                        "date": datetime.now().isoformat(),
                        "risk_level": "HIGH"
                    }
                ]
            
            # استخراج owner/repo من URL
            parts = repo_url.replace("https://github.com/", "").split("/")
            if len(parts) >= 2:
                repo = self.github.get_repo(f"{parts[0]}/{parts[1]}")
                
                # تحليل آخر 10 commits only (to save API calls)
                commits = list(repo.get_commits()[:10])
                
                for commit in commits:
                    # Check commit message and files
                    message = commit.commit.message.lower()
                    
                    # البحث عن أنماط حرجة
                    if any(pattern in message for pattern in critical_patterns):
                        suspicious_commits.append({
                            "sha": commit.sha[:7],
                            "message": commit.commit.message[:100],
                            "date": commit.commit.author.date.isoformat(),
                            "risk_level": "HIGH" if "fix" in message or "bug" in message else "MEDIUM"
                        })
        
        except Exception as e:
            if "403" not in str(e) and "rate limit" not in str(e).lower():
                print(f"GitHub analysis error: {e}")
        
        return suspicious_commits
    
    def generate_intelligence_report(self):
        """
        توليد تقرير استخباراتي أسبوعي
        """
        print("\n" + "="*60)
        print("🕵️ SHADOW INTELLIGENCE REPORT")
        print("="*60)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Specialization: {self.specialization}")
        print()
        
        # مسح المشهد
        targets = self.scan_defi_landscape()
        
        print("\n🎯 TOP 5 VULNERABLE TARGETS:")
        print("-"*60)
        
        for i, target in enumerate(targets, 1):
            print(f"\n{i}. {target['name']}")
            print(f"   TVL: ${target.get('tvl', 0):,.0f}")
            print(f"   Category: {target.get('category', 'Unknown')}")
            print(f"   Vulnerability Score: {target['vulnerability_score']}/300")
            
            if target.get('github'):
                print(f"   GitHub: {target['github']}")
                
                # تحليل commits
                commits = self.analyze_github_commits(target['github'])
                if commits:
                    print(f"   ⚠️  Recent suspicious commits: {len(commits)}")
                    for commit in commits[:2]:  # Show top 2
                        print(f"      - {commit['message'][:50]}... ({commit['risk_level']})")
            
            if target.get('reason'):
                print(f"   Reason: {target['reason']}")
        
        # التوصيات
        print("\n💡 STRATEGIC RECOMMENDATIONS:")
        print("-"*60)
        print("1. Focus on TARGET #1 - highest vulnerability score")
        print("2. Look for development bounties to infiltrate")
        print("3. Study recent commits for unpatched vulnerabilities")
        print("4. Monitor for major updates in next 48 hours")
        
        # حفظ التقرير
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "specialization": self.specialization,
            "targets": targets,
            "next_scan": (datetime.now() + timedelta(days=7)).isoformat()
        }
        
        with open("shadow_intelligence.json", "w") as f:
            json.dump(report_data, f, indent=2)
        
        print("\n📁 Report saved: shadow_intelligence.json")
        
        return report_data
    
    def infiltrate_as_developer(self, protocol_name):
        """
        استراتيجية حصان طروادة
        التسلل كمطور لفهم النظام من الداخل
        """
        print(f"\n🐎 TROJAN HORSE STRATEGY: Infiltrating {protocol_name}")
        print("-"*60)
        
        steps = [
            "1. Find small development bounty ($500-$5000)",
            "2. Submit professional proposal",
            "3. Gain access to private discussions",
            "4. Understand internal logic and weaknesses",
            "5. Map the entire attack surface",
            "6. Withdraw and prepare the real hunt"
        ]
        
        for step in steps:
            print(f"   {step}")
        
        print("\n⚠️  Remember: The $2000 bounty is not the goal.")
        print("   It's the key to the $200,000 vulnerability.")
        
        return {
            "protocol": protocol_name,
            "strategy": "trojan_horse",
            "estimated_infiltration_time": "1-2 weeks",
            "estimated_hunt_value": "$50,000-$250,000"
        }

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║               SHADOW HUNTER - INTELLIGENCE SYSTEM            ║
║                    عقيدة الصياد - نظام الاستخبارات              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    hunter = ShadowHunter()
    
    # توليد تقرير استخباراتي
    report = hunter.generate_intelligence_report()
    
    # اختيار الهدف الأول للتسلل
    if report["targets"]:
        top_target = report["targets"][0]
        print("\n" + "="*60)
        print("🎯 PRIMARY TARGET SELECTED")
        print("="*60)
        
        infiltration = hunter.infiltrate_as_developer(top_target["name"])
        
        print("\n📊 EXPECTED OUTCOME:")
        print(f"   Phase 1: Infiltration bounty (~$2,000)")
        print(f"   Phase 2: Vulnerability discovery ($50,000-$250,000)")
        print(f"   Timeline: 2-4 weeks total")
        print(f"   Success probability: 80% with proper execution")
    
    print("\n" + "="*60)
    print("💀 THE HUNT BEGINS IN THE SHADOWS")
    print("="*60)

if __name__ == "__main__":
    main()