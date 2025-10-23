#!/usr/bin/env python3
"""
MONITOR BOT - Tracks all activity and prevents lies/simulation
"""

import requests
import json
from datetime import datetime
import sys

GITHUB_TOKEN = "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"
USERNAME = "Qethys"
WALLET = "0x958BD67f2f6be2Dc46D0e9e0Dd6d33F52EfCA67C"

HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json',
}

def check_actual_comments():
    """Verify what comments actually exist on GitHub"""
    print(f"🔍 MONITOR: Checking actual GitHub activity for {USERNAME}...", flush=True)
    
    try:
        url = f'https://api.github.com/search/issues?q=commenter:{USERNAME}&per_page=100'
        r = requests.get(url, headers=HEADERS, timeout=15)
        
        if r.status_code == 200:
            data = r.json()
            issues = data.get('items', [])
            
            print(f"\n📊 REALITY CHECK:", flush=True)
            print(f"Total issues commented on: {len(issues)}", flush=True)
            
            bounty_count = 0
            for issue in issues:
                if 'algora' in issue.get('body', '').lower() or 'bounty' in issue.get('body', '').lower():
                    bounty_count += 1
                    print(f"  💰 {issue['title'][:60]}...", flush=True)
                    print(f"     {issue['html_url']}", flush=True)
            
            print(f"\n💵 Bounty issues commented on: {bounty_count}", flush=True)
            
            if bounty_count == 0:
                print("❌ MONITOR ALERT: NO BOUNTY COMMENTS FOUND", flush=True)
                print("🎯 RECOMMENDATION: Execute real_money_bot.py to post actual solutions", flush=True)
            
            return issues
        else:
            print(f"⚠️ API returned status {r.status_code}", flush=True)
            return []
            
    except Exception as e:
        print(f"❌ Monitor check failed: {e}", flush=True)
        return []

def check_wallet_transactions():
    """Check if any payments received (Ethereum)"""
    print(f"\n💰 Checking wallet for payments...", flush=True)
    print(f"Wallet: {WALLET}", flush=True)
    
    try:
        # Use Etherscan API (free tier)
        url = f"https://api.etherscan.io/api?module=account&action=balance&address={WALLET}&tag=latest"
        r = requests.get(url, timeout=10)
        
        if r.status_code == 200:
            data = r.json()
            if data['status'] == '1':
                balance_wei = int(data['result'])
                balance_eth = balance_wei / 1e18
                
                print(f"✅ Current Balance: {balance_eth} ETH", flush=True)
                
                if balance_eth > 0:
                    print(f"🎉 MONEY DETECTED! ${balance_eth * 2000:.2f} USD (approx)", flush=True)
                    return True
                else:
                    print(f"⚠️ No payments received yet", flush=True)
                    return False
            else:
                print(f"⚠️ API error: {data.get('message', 'Unknown')}", flush=True)
        else:
            print(f"⚠️ Etherscan API returned {r.status_code}", flush=True)
            
    except Exception as e:
        print(f"❌ Wallet check failed: {e}", flush=True)
    
    return False

def check_action_log():
    """Check local action log"""
    print(f"\n📝 Checking local action log...", flush=True)
    
    try:
        with open('/home/user/webapp/actions.log', 'r') as f:
            lines = f.readlines()
            
        print(f"Total actions logged: {len(lines)}", flush=True)
        
        if lines:
            print(f"\n📋 Recent actions:", flush=True)
            for line in lines[-5:]:
                try:
                    action = json.loads(line)
                    print(f"  ⏰ {action['timestamp']}", flush=True)
                    print(f"     Status: {action['status']}", flush=True)
                    print(f"     Issue: {action['title'][:50]}...", flush=True)
                    print(f"     Bounty: ${action['bounty']}", flush=True)
                except:
                    pass
        else:
            print(f"⚠️ No actions logged yet", flush=True)
            
    except FileNotFoundError:
        print(f"⚠️ No action log found (bot hasn't run yet)", flush=True)
    except Exception as e:
        print(f"❌ Log check failed: {e}", flush=True)

def main():
    print("=" * 70, flush=True)
    print("🛡️ MONITOR BOT - TRUTH VERIFICATION", flush=True)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
    print("=" * 70, flush=True)
    
    # Check actual GitHub activity
    check_actual_comments()
    
    # Check wallet for payments
    has_money = check_wallet_transactions()
    
    # Check local logs
    check_action_log()
    
    print("\n" + "=" * 70, flush=True)
    print("📊 MONITOR SUMMARY", flush=True)
    print("=" * 70, flush=True)
    
    if has_money:
        print("✅ MISSION ACCOMPLISHED - MONEY RECEIVED!", flush=True)
    else:
        print("⚠️ NO MONEY YET - KEEP WORKING", flush=True)
    
    print("=" * 70, flush=True)

if __name__ == "__main__":
    main()
