#!/bin/bash

# Real Money Bot Runner
# Runs the bot and monitor in proper sequence

cd /home/user/webapp

echo "=========================================="
echo "🚀 REAL MONEY BOT - EXECUTION STARTED"
echo "⏰ $(date)"
echo "=========================================="

# First: Run monitor to check current state
echo ""
echo "📊 STEP 1: Running Monitor Bot..."
python3 monitor.py

echo ""
echo "=========================================="
echo "⚡ STEP 2: Running Money Making Bot..."
echo "=========================================="
python3 real_money_bot.py

echo ""
echo "=========================================="
echo "📊 STEP 3: Final Status Check..."
echo "=========================================="
python3 monitor.py

echo ""
echo "=========================================="
echo "✅ EXECUTION COMPLETE"
echo "⏰ $(date)"
echo "=========================================="
