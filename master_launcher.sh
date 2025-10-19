#!/bin/bash

###############################################################################
# 🚀 ULTRA BOUNTY HUNTER - MASTER LAUNCHER
###############################################################################
# نظام تشغيل متكامل للصيد الذكي للبونتي
###############################################################################

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Files
PID_FILE="master.pid"
LOG_FILE="master.log"
BOT_SCRIPT="ultra_intelligent_bounty_hunter.py"
DASHBOARD_SCRIPT="advanced_dashboard.py"

###############################################################################
# Helper Functions
###############################################################################

print_banner() {
    clear
    echo -e "${PURPLE}"
    echo "═══════════════════════════════════════════════════════════════"
    echo "        🚀 ULTRA INTELLIGENT BOUNTY HUNTER v4.0"
    echo "═══════════════════════════════════════════════════════════════"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

###############################################################################
# Environment Check
###############################################################################

check_environment() {
    print_info "Checking environment..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 not found!"
        exit 1
    fi
    print_success "Python 3: $(python3 --version)"
    
    # Check API keys
    if [ -z "$GITHUB_TOKEN" ]; then
        print_error "GITHUB_TOKEN not set!"
        echo "Please set: export GITHUB_TOKEN='your_token'"
        exit 1
    fi
    print_success "GitHub token: Set"
    
    if [ -z "$ANTHROPIC_API_KEY" ]; then
        print_error "ANTHROPIC_API_KEY not set!"
        echo "Please set: export ANTHROPIC_API_KEY='your_key'"
        exit 1
    fi
    print_success "Anthropic key: Set"
    
    # Check files
    if [ ! -f "$BOT_SCRIPT" ]; then
        print_error "Bot script not found: $BOT_SCRIPT"
        exit 1
    fi
    print_success "Bot script: Found"
    
    if [ ! -f "$DASHBOARD_SCRIPT" ]; then
        print_error "Dashboard script not found: $DASHBOARD_SCRIPT"
        exit 1
    fi
    print_success "Dashboard script: Found"
}

###############################################################################
# Install Dependencies
###############################################################################

install_dependencies() {
    print_info "Installing dependencies..."
    
    pip3 install -q --upgrade pip
    pip3 install -q anthropic PyGithub numpy scikit-learn joblib aiohttp flask pyyaml
    
    print_success "Dependencies installed"
}

###############################################################################
# Start Services
###############################################################################

start_dashboard() {
    print_info "Starting dashboard..."
    
    python3 "$DASHBOARD_SCRIPT" > dashboard.log 2>&1 &
    DASHBOARD_PID=$!
    
    echo "$DASHBOARD_PID" > dashboard.pid
    
    sleep 3
    
    if ps -p $DASHBOARD_PID > /dev/null; then
        print_success "Dashboard started (PID: $DASHBOARD_PID)"
        print_info "Dashboard URL: http://localhost:8080"
    else
        print_error "Dashboard failed to start"
        return 1
    fi
}

start_bot() {
    print_info "Starting bot..."
    
    python3 "$BOT_SCRIPT" > bot.log 2>&1 &
    BOT_PID=$!
    
    echo "$BOT_PID" > bot.pid
    
    sleep 2
    
    if ps -p $BOT_PID > /dev/null; then
        print_success "Bot started (PID: $BOT_PID)"
    else
        print_error "Bot failed to start"
        cat bot.log
        return 1
    fi
}

###############################################################################
# Stop Services
###############################################################################

stop_services() {
    print_info "Stopping services..."
    
    # Stop bot
    if [ -f "bot.pid" ]; then
        BOT_PID=$(cat bot.pid)
        if ps -p $BOT_PID > /dev/null; then
            kill $BOT_PID
            print_success "Bot stopped"
        fi
        rm -f bot.pid
    fi
    
    # Stop dashboard
    if [ -f "dashboard.pid" ]; then
        DASHBOARD_PID=$(cat dashboard.pid)
        if ps -p $DASHBOARD_PID > /dev/null; then
            kill $DASHBOARD_PID
            print_success "Dashboard stopped"
        fi
        rm -f dashboard.pid
    fi
}

###############################################################################
# Status Check
###############################################################################

check_status() {
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}                    SYSTEM STATUS${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    
    # Dashboard status
    if [ -f "dashboard.pid" ]; then
        DASHBOARD_PID=$(cat dashboard.pid)
        if ps -p $DASHBOARD_PID > /dev/null; then
            echo -e "${GREEN}Dashboard: ✅ RUNNING${NC} (PID: $DASHBOARD_PID)"
            echo -e "           ${CYAN}http://localhost:8080${NC}"
        else
            echo -e "${RED}Dashboard: ❌ STOPPED${NC}"
        fi
    else
        echo -e "${YELLOW}Dashboard: ⚠️  NOT STARTED${NC}"
    fi
    
    echo ""
    
    # Bot status
    if [ -f "bot.pid" ]; then
        BOT_PID=$(cat bot.pid)
        if ps -p $BOT_PID > /dev/null; then
            echo -e "${GREEN}Bot:       ✅ RUNNING${NC} (PID: $BOT_PID)"
        else
            echo -e "${RED}Bot:       ❌ STOPPED${NC}"
        fi
    else
        echo -e "${YELLOW}Bot:       ⚠️  NOT STARTED${NC}"
    fi
    
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    # Show recent stats
    if [ -f "stats.json" ]; then
        echo -e "${CYAN}📊 Quick Stats:${NC}"
        python3 << EOF
import json
try:
    with open('stats.json', 'r') as f:
        stats = json.load(f)
    print(f"   💰 Bounties found: {stats.get('total_bounties_found', 0)}")
    print(f"   🧠 Analyzed: {stats.get('total_analyzed', 0)}")
    print(f"   💬 Comments: {stats.get('total_comments', 0)}")
    print(f"   💵 Earnings: \${stats.get('total_earnings', 0):.2f}")
except:
    print("   No stats available yet")
EOF
    fi
    
    echo ""
}

###############################################################################
# Logs
###############################################################################

show_logs() {
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}                    RECENT LOGS${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    
    echo -e "\n${YELLOW}Bot Logs:${NC}"
    if [ -f "bot.log" ]; then
        tail -20 bot.log
    else
        echo "No bot logs yet"
    fi
    
    echo -e "\n${YELLOW}Dashboard Logs:${NC}"
    if [ -f "dashboard.log" ]; then
        tail -20 dashboard.log
    else
        echo "No dashboard logs yet"
    fi
}

###############################################################################
# Test Run
###############################################################################

test_run() {
    print_info "Running test..."
    
    python3 << EOF
import os
import sys
import asyncio

sys.path.insert(0, '.')
from ultra_intelligent_bounty_hunter import UltraIntelligentBountyHunter

async def test():
    hunter = UltraIntelligentBountyHunter()
    print("✅ Bot initialized successfully")
    
    # Test GitHub connection
    try:
        user = hunter.github.get_user()
        print(f"✅ GitHub connected as: {user.login}")
    except Exception as e:
        print(f"❌ GitHub error: {e}")
        return False
    
    # Test Claude connection
    try:
        message = hunter.analyzer.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            messages=[{"role": "user", "content": "Say 'Hello' if you can read this."}]
        )
        print(f"✅ Claude connected: {message.content[0].text[:50]}")
    except Exception as e:
        print(f"❌ Claude error: {e}")
        return False
    
    print("\n✅ All systems operational!")
    return True

if asyncio.run(test()):
    sys.exit(0)
else:
    sys.exit(1)
EOF
    
    if [ $? -eq 0 ]; then
        print_success "Test passed!"
        return 0
    else
        print_error "Test failed!"
        return 1
    fi
}

###############################################################################
# Main Menu
###############################################################################

show_menu() {
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}                    CONTROL MENU${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "1) 🚀 Start All Services"
    echo "2) 🛑 Stop All Services"
    echo "3) 🔄 Restart All Services"
    echo "4) 📊 Show Status"
    echo "5) 📝 Show Logs"
    echo "6) 🧪 Run Test"
    echo "7) 🔧 Install Dependencies"
    echo "8) 🚪 Exit"
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -n "Choose option [1-8]: "
}

###############################################################################
# Main Logic
###############################################################################

case "${1:-menu}" in
    start)
        print_banner
        check_environment
        install_dependencies
        start_dashboard
        start_bot
        check_status
        ;;
    
    stop)
        print_banner
        stop_services
        ;;
    
    restart)
        print_banner
        stop_services
        sleep 2
        check_environment
        start_dashboard
        start_bot
        check_status
        ;;
    
    status)
        print_banner
        check_status
        ;;
    
    logs)
        print_banner
        show_logs
        ;;
    
    test)
        print_banner
        check_environment
        test_run
        ;;
    
    install)
        print_banner
        install_dependencies
        ;;
    
    menu)
        while true; do
            print_banner
            check_status
            show_menu
            
            read choice
            
            case $choice in
                1)
                    check_environment
                    install_dependencies
                    start_dashboard
                    start_bot
                    sleep 3
                    ;;
                2)
                    stop_services
                    sleep 2
                    ;;
                3)
                    stop_services
                    sleep 2
                    check_environment
                    start_dashboard
                    start_bot
                    sleep 3
                    ;;
                4)
                    # Status already shown
                    sleep 1
                    ;;
                5)
                    show_logs
                    echo ""
                    read -p "Press Enter to continue..."
                    ;;
                6)
                    check_environment
                    test_run
                    echo ""
                    read -p "Press Enter to continue..."
                    ;;
                7)
                    install_dependencies
                    echo ""
                    read -p "Press Enter to continue..."
                    ;;
                8)
                    echo ""
                    print_info "Goodbye! 👋"
                    exit 0
                    ;;
                *)
                    print_error "Invalid option"
                    sleep 1
                    ;;
            esac
        done
        ;;
    
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|test|install|menu}"
        exit 1
        ;;
esac
