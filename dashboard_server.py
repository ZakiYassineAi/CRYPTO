#!/usr/bin/env python3
"""
Real-time Dashboard for Money Maker Bot
Displays live statistics and bot activity
"""

import json
import os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_dashboard_html().encode())
        elif self.path == '/api/stats':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(self.get_stats()).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def get_stats(self):
        """Get current bot statistics"""
        stats = {
            'status': 'offline',
            'uptime': '0m',
            'issues_analyzed': 0,
            'issues_solved': 0,
            'comments_posted': 0,
            'estimated_earnings': 0,
            'actual_earnings': 0,
            'success_rate': 0,
            'last_update': datetime.now().isoformat()
        }
        
        # Read from memory file
        if os.path.exists('smart_bot_memory.json'):
            try:
                with open('smart_bot_memory.json', 'r') as f:
                    memory = json.load(f)
                    if 'stats' in memory:
                        stats.update(memory['stats'])
                    
                    # Check if bot is running
                    if 'last_run' in memory:
                        last_run = datetime.fromisoformat(memory['last_run'])
                        if (datetime.now() - last_run).seconds < 600:
                            stats['status'] = 'running'
            except:
                pass
        
        # Check if process is running
        if os.path.exists('.bot.pid'):
            with open('.bot.pid', 'r') as f:
                pid = f.read().strip()
                if os.path.exists(f'/proc/{pid}'):
                    stats['status'] = 'running'
        
        return stats
    
    def get_dashboard_html(self):
        """Generate dashboard HTML"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>💰 Intelligent Money Bot Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #fff;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        h1 {
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .subtitle {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .stat-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-label {
            font-size: 0.9em;
            opacity: 0.8;
            margin-bottom: 10px;
        }
        
        .stat-value {
            font-size: 2.5em;
            font-weight: bold;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        
        .status-running {
            background: #00ff00;
        }
        
        .status-offline {
            background: #ff0000;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .info-panel {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 30px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .command-list {
            margin-top: 20px;
        }
        
        .command {
            background: rgba(0, 0, 0, 0.3);
            padding: 10px 15px;
            border-radius: 8px;
            margin: 10px 0;
            font-family: 'Courier New', monospace;
        }
        
        .update-time {
            text-align: center;
            margin-top: 20px;
            opacity: 0.7;
            font-size: 0.9em;
        }
        
        .refresh-btn {
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            transition: all 0.3s ease;
        }
        
        .refresh-btn:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: scale(1.05);
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>💰 Intelligent Money Bot</h1>
            <p class="subtitle">Real-time Performance Dashboard</p>
        </header>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">
                    <span class="status-indicator" id="status-dot"></span>
                    Status
                </div>
                <div class="stat-value" id="status">Loading...</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">💵 Estimated Earnings</div>
                <div class="stat-value" id="earnings">$0</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">🔍 Issues Analyzed</div>
                <div class="stat-value" id="analyzed">0</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">✅ Issues Solved</div>
                <div class="stat-value" id="solved">0</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">💬 Comments Posted</div>
                <div class="stat-value" id="comments">0</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-label">📈 Success Rate</div>
                <div class="stat-value" id="success">0%</div>
            </div>
        </div>
        
        <div class="info-panel">
            <h2>🎮 Bot Controls</h2>
            <div class="command-list">
                <div class="command">./run_bot.sh start   # Start the bot</div>
                <div class="command">./run_bot.sh stop    # Stop the bot</div>
                <div class="command">./run_bot.sh status  # Check bot status</div>
                <div class="command">./run_bot.sh logs    # View logs</div>
                <div class="command">tail -f bot_intelligent.log  # Follow live logs</div>
            </div>
            
            <div style="text-align: center; margin-top: 20px;">
                <button class="refresh-btn" onclick="updateStats()">🔄 Refresh Stats</button>
            </div>
            
            <div class="update-time" id="update-time">Last updated: Never</div>
        </div>
    </div>
    
    <script>
        function updateStats() {
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {
                    // Update status
                    const statusEl = document.getElementById('status');
                    const statusDot = document.getElementById('status-dot');
                    
                    if (data.status === 'running') {
                        statusEl.textContent = '🟢 Running';
                        statusDot.className = 'status-indicator status-running';
                    } else {
                        statusEl.textContent = '🔴 Offline';
                        statusDot.className = 'status-indicator status-offline';
                    }
                    
                    // Update stats
                    document.getElementById('earnings').textContent = '$' + data.estimated_earnings;
                    document.getElementById('analyzed').textContent = data.issues_analyzed;
                    document.getElementById('solved').textContent = data.issues_solved;
                    document.getElementById('comments').textContent = data.comments_posted;
                    
                    // Calculate success rate
                    const successRate = data.issues_analyzed > 0 
                        ? ((data.issues_solved / data.issues_analyzed) * 100).toFixed(1)
                        : 0;
                    document.getElementById('success').textContent = successRate + '%';
                    
                    // Update time
                    const now = new Date();
                    document.getElementById('update-time').textContent = 
                        'Last updated: ' + now.toLocaleTimeString();
                })
                .catch(error => {
                    console.error('Error fetching stats:', error);
                });
        }
        
        // Update stats every 10 seconds
        updateStats();
        setInterval(updateStats, 10000);
    </script>
</body>
</html>"""
    
    def log_message(self, format, *args):
        """Suppress log messages"""
        pass

def start_dashboard(port=8080):
    """Start the dashboard server"""
    server = HTTPServer(('0.0.0.0', port), DashboardHandler)
    print(f"🎨 Dashboard running at http://localhost:{port}")
    print(f"📊 Access the dashboard to monitor bot activity\n")
    server.serve_forever()

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    
    try:
        start_dashboard(port)
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
