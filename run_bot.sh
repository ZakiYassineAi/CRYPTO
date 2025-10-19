#!/bin/bash
# Smart Bot Runner with Auto-Restart and Monitoring

BOT_SCRIPT="intelligent_money_bot.py"
LOG_FILE="bot_intelligent.log"
PID_FILE=".bot.pid"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if bot is already running
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}Bot is already running (PID: $OLD_PID)${NC}"
        echo "Use './run_bot.sh stop' to stop it first"
        exit 1
    fi
fi

# Function to start bot
start_bot() {
    echo -e "${GREEN}🚀 Starting Intelligent Money Bot...${NC}"
    
    # Check Python dependencies
    echo "📦 Checking dependencies..."
    pip install -q -r requirements.txt
    
    # Start bot in background
    nohup python3 "$BOT_SCRIPT" >> "$LOG_FILE" 2>&1 &
    BOT_PID=$!
    
    echo $BOT_PID > "$PID_FILE"
    
    echo -e "${GREEN}✅ Bot started (PID: $BOT_PID)${NC}"
    echo "📋 Log file: $LOG_FILE"
    echo ""
    echo "Commands:"
    echo "  ./run_bot.sh stop    - Stop the bot"
    echo "  ./run_bot.sh status  - Check bot status"
    echo "  ./run_bot.sh logs    - View logs"
    echo "  tail -f $LOG_FILE    - Follow logs in real-time"
}

# Function to stop bot
stop_bot() {
    if [ ! -f "$PID_FILE" ]; then
        echo -e "${YELLOW}Bot is not running${NC}"
        exit 0
    fi
    
    BOT_PID=$(cat "$PID_FILE")
    
    if ps -p "$BOT_PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}🛑 Stopping bot (PID: $BOT_PID)...${NC}"
        kill "$BOT_PID"
        sleep 2
        
        if ps -p "$BOT_PID" > /dev/null 2>&1; then
            echo "Force killing..."
            kill -9 "$BOT_PID"
        fi
        
        rm "$PID_FILE"
        echo -e "${GREEN}✅ Bot stopped${NC}"
    else
        echo -e "${YELLOW}Bot process not found${NC}"
        rm "$PID_FILE"
    fi
}

# Function to check status
check_status() {
    if [ ! -f "$PID_FILE" ]; then
        echo -e "${RED}❌ Bot is not running${NC}"
        exit 1
    fi
    
    BOT_PID=$(cat "$PID_FILE")
    
    if ps -p "$BOT_PID" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Bot is running (PID: $BOT_PID)${NC}"
        
        # Show last few log lines
        if [ -f "$LOG_FILE" ]; then
            echo ""
            echo "📋 Recent activity:"
            tail -n 10 "$LOG_FILE"
        fi
    else
        echo -e "${RED}❌ Bot process not found${NC}"
        rm "$PID_FILE"
        exit 1
    fi
}

# Function to show logs
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        less +G "$LOG_FILE"
    else
        echo -e "${YELLOW}No log file found${NC}"
    fi
}

# Main command handler
case "${1:-start}" in
    start)
        start_bot
        ;;
    stop)
        stop_bot
        ;;
    restart)
        stop_bot
        sleep 2
        start_bot
        ;;
    status)
        check_status
        ;;
    logs)
        show_logs
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        exit 1
        ;;
esac
