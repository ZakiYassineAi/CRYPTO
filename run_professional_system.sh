#!/bin/bash

# Professional Bounty Hunting System - Master Control Script
# تشغيل النظام الاحترافي الكامل

echo "================================"
echo "🚀 Professional Bounty System"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to run with error checking
run_with_check() {
    echo -e "${BLUE}▶️ Running: $1${NC}"
    if $2; then
        echo -e "${GREEN}✅ Success: $1${NC}"
        echo ""
        return 0
    else
        echo -e "${RED}❌ Failed: $1${NC}"
        echo ""
        return 1
    fi
}

# Check if .github_token exists
if [ ! -f ".github_token" ]; then
    echo -e "${RED}❌ Error: .github_token file not found!${NC}"
    echo "Please create .github_token with your GitHub personal access token"
    exit 1
fi

echo -e "${YELLOW}📊 Phase 1: Tracking Existing PRs${NC}"
echo "==============================="
run_with_check "PR Tracker" "python3 pr_tracker.py"

echo -e "${YELLOW}🎯 Phase 2: Finding New Opportunities${NC}"
echo "================================="
run_with_check "Smart Bounty Hunter" "python3 smart_bounty_hunter.py"

echo -e "${YELLOW}📈 Phase 3: Generating Reports${NC}"
echo "============================="

# Create comprehensive status report
cat > STATUS_REPORT.md << 'EOF'
# 📊 Professional Bounty System - Status Report

## Generated: $(date)

## 🎯 System Overview

This system implements a professional approach to GitHub bounty hunting with:

1. **Smart Opportunity Detection**
   - Filters high-value bounties (>$50)
   - Calculates priority scores
   - Analyzes repo quality and activity

2. **Professional PR Tracking**
   - Monitors all open PRs
   - Provides actionable recommendations
   - Tracks follow-up timing

3. **Quality-First Approach**
   - No spam or automated comments
   - Real solutions with real code
   - Professional communication

## 📁 Key Files

- `smart_bounty_hunter.py` - Main opportunity finder
- `pr_tracker.py` - PR monitoring system
- `professional_dashboard.html` - Visual dashboard
- `smart_metrics.json` - Performance data
- `pr_tracking.json` - PR tracking data

## 🚀 Usage

### Daily Routine:
```bash
# Morning: Check for new opportunities
./run_professional_system.sh

# Afternoon: Work on selected bounty
# (Write actual code, not just comments)

# Evening: Monitor PRs and respond
python3 pr_tracker.py
```

### Weekly Review:
1. Check success rate
2. Analyze what worked
3. Refine strategy
4. Build on wins

## 💰 Payment Address
**PEB20**: 0x958BD67f2f6be2Dc46D0e9e0Dd6d33F52EfCA67C

## 🎯 Strategic Principles

1. **Quality Over Quantity**
   - One great PR > 100 spam comments
   
2. **Choose Wisely**
   - Only pursue bounties we can actually complete
   
3. **Follow Through**
   - Monitor and respond to all PRs
   
4. **Build Reputation**
   - Every interaction matters
   
5. **Learn Continuously**
   - Document what works
   - Iterate on failures

## 📊 Current Metrics

See `smart_metrics.json` for detailed stats.

## 🔄 Next Steps

1. Review opportunities in smart_metrics.json
2. Choose highest priority score
3. Read issue completely
4. Plan solution thoroughly
5. Write professional code
6. Submit quality PR
7. Follow up consistently

---

*System Status: Active*
*Last Updated: $(date)*
EOF

echo -e "${GREEN}✅ Status report generated: STATUS_REPORT.md${NC}"
echo ""

# Display summary
echo "================================"
echo -e "${GREEN}✅ System Run Complete!${NC}"
echo "================================"
echo ""
echo "📊 Generated Files:"
echo "   • smart_metrics.json (opportunity data)"
echo "   • pr_tracking.json (PR tracking)"
echo "   • STATUS_REPORT.md (status report)"
echo ""
echo "🌐 Dashboard:"
echo "   Open professional_dashboard.html in browser"
echo ""
echo "💡 Next Actions:"
echo "   1. Review smart_metrics.json for top opportunities"
echo "   2. Check pr_tracking.json for PRs needing attention"
echo "   3. Open dashboard for visual overview"
echo ""
echo "⏰ Run this script daily for best results"
echo ""

# Check if we have any high-priority items
if [ -f "smart_metrics.json" ]; then
    echo -e "${YELLOW}🎯 Quick Summary:${NC}"
    python3 << 'PYTHON'
import json
try:
    with open('smart_metrics.json', 'r') as f:
        data = json.load(f)
        opps = data.get('opportunities', [])
        if opps:
            top = opps[0]
            print(f"   Top opportunity: ${top.get('amount', 0):.2f}")
            print(f"   Priority score: {top.get('priority_score', 0):.2f}")
            print(f"   URL: {top.get('url', 'N/A')}")
        else:
            print("   No opportunities found. Try again later.")
except:
    print("   Run the hunter script first")
PYTHON
    echo ""
fi

if [ -f "pr_tracking.json" ]; then
    echo -e "${YELLOW}📄 PR Status:${NC}"
    python3 << 'PYTHON'
import json
try:
    with open('pr_tracking.json', 'r') as f:
        data = json.load(f)
        prs = data.get('tracked_prs', [])
        print(f"   Open PRs: {len(prs)}")
        if prs:
            print("   Action: Check for responses and updates")
        else:
            print("   Action: Find and work on new opportunities")
except:
    print("   Run the tracker script first")
PYTHON
    echo ""
fi

echo "================================"
echo "🎯 Professional System Ready!"
echo "================================"
