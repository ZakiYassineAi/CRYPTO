#!/usr/bin/env python3
"""
📊 ADVANCED REAL-TIME DASHBOARD
===============================
لوحة تحكم متقدمة مع:
- Real-time monitoring
- Performance analytics
- Earnings tracker
- Competitive insights
- AI recommendations
"""

from flask import Flask, render_template, jsonify, send_from_directory
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ultra-bounty-hunter-2025'

# ============================================================================
# DATA STORAGE
# ============================================================================

class DataStore:
    """Stockage centralisé des données"""
    
    def __init__(self):
        self.stats_file = 'stats.json'
        self.bounties_file = 'bounties.json'
        self.earnings_file = 'earnings.json'
        self.load_data()
    
    def load_data(self):
        """Charge les données depuis les fichiers"""
        self.stats = self._load_json(self.stats_file, {
            'total_bounties_found': 0,
            'total_analyzed': 0,
            'total_comments': 0,
            'total_prs': 0,
            'total_earnings': 0.0,
            'success_rate': 0.0,
            'avg_bounty_value': 0.0,
            'last_updated': datetime.now().isoformat()
        })
        
        self.bounties = self._load_json(self.bounties_file, [])
        self.earnings = self._load_json(self.earnings_file, [])
    
    def _load_json(self, filename, default):
        """Charge un fichier JSON avec fallback"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logging.error(f"Error loading {filename}: {e}")
        return default
    
    def save_stats(self):
        """Sauvegarde les statistiques"""
        self.stats['last_updated'] = datetime.now().isoformat()
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def add_bounty(self, bounty):
        """Ajoute une bounty découverte"""
        self.bounties.append(bounty)
        with open(self.bounties_file, 'w') as f:
            json.dump(self.bounties[-100:], f, indent=2)  # Keep last 100
        
        self.stats['total_bounties_found'] = len(self.bounties)
        self.save_stats()
    
    def add_earning(self, earning):
        """Ajoute un gain"""
        self.earnings.append(earning)
        with open(self.earnings_file, 'w') as f:
            json.dump(self.earnings, f, indent=2)
        
        self.stats['total_earnings'] = sum(e['amount'] for e in self.earnings)
        self.stats['total_prs'] += 1
        self.save_stats()
    
    def get_analytics(self):
        """Calcule les analytics"""
        now = datetime.now()
        
        # Bounties par plateforme
        platform_stats = defaultdict(lambda: {'count': 0, 'total_value': 0.0})
        for b in self.bounties:
            platform = b.get('platform', 'unknown')
            platform_stats[platform]['count'] += 1
            platform_stats[platform]['total_value'] += b.get('bounty_amount', 0)
        
        # Gains par période
        daily_earnings = defaultdict(float)
        for e in self.earnings:
            date = datetime.fromisoformat(e['date']).date().isoformat()
            daily_earnings[date] += e['amount']
        
        # Catégories les plus rentables
        category_stats = defaultdict(lambda: {'count': 0, 'success': 0, 'earnings': 0.0})
        for b in self.bounties:
            cat = b.get('category', 'unknown')
            category_stats[cat]['count'] += 1
        
        for e in self.earnings:
            cat = e.get('category', 'unknown')
            category_stats[cat]['success'] += 1
            category_stats[cat]['earnings'] += e['amount']
        
        # Calcul du success rate
        if self.stats['total_comments'] > 0:
            self.stats['success_rate'] = (self.stats['total_prs'] / self.stats['total_comments']) * 100
        
        # Moyenne des bounties
        if self.bounties:
            self.stats['avg_bounty_value'] = sum(b.get('bounty_amount', 0) for b in self.bounties) / len(self.bounties)
        
        return {
            'platform_stats': dict(platform_stats),
            'daily_earnings': dict(daily_earnings),
            'category_stats': dict(category_stats),
            'top_bounties': sorted(self.bounties, key=lambda x: x.get('bounty_amount', 0), reverse=True)[:10],
            'recent_earnings': self.earnings[-10:],
        }

data_store = DataStore()

# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    """Page d'accueil du dashboard"""
    return render_template('dashboard.html')

@app.route('/api/stats')
def get_stats():
    """Renvoie les statistiques générales"""
    return jsonify(data_store.stats)

@app.route('/api/analytics')
def get_analytics():
    """Renvoie les analytics détaillées"""
    return jsonify(data_store.get_analytics())

@app.route('/api/bounties/recent')
def get_recent_bounties():
    """Renvoie les bounties récentes"""
    return jsonify(data_store.bounties[-20:])

@app.route('/api/earnings/recent')
def get_recent_earnings():
    """Renvoie les gains récents"""
    return jsonify(data_store.earnings[-20:])

@app.route('/api/refresh')
def refresh_data():
    """Force le rafraîchissement des données"""
    data_store.load_data()
    return jsonify({'status': 'success', 'message': 'Data refreshed'})

# ============================================================================
# TEMPLATE
# ============================================================================

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Ultra Bounty Hunter Dashboard</title>
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
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        header h1 {
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        header p {
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
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        
        .stat-card h3 {
            font-size: 0.9em;
            opacity: 0.8;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .stat-card .value {
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .stat-card .label {
            font-size: 0.9em;
            opacity: 0.7;
        }
        
        .charts-section {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        
        .chart-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .chart-card h2 {
            margin-bottom: 20px;
            font-size: 1.3em;
        }
        
        .bounty-list {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .bounty-item {
            background: rgba(255, 255, 255, 0.05);
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 10px;
            border-left: 4px solid #4CAF50;
        }
        
        .bounty-item h4 {
            margin-bottom: 8px;
            font-size: 1.1em;
        }
        
        .bounty-meta {
            display: flex;
            gap: 15px;
            font-size: 0.9em;
            opacity: 0.8;
        }
        
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
        }
        
        .badge-success {
            background: #4CAF50;
        }
        
        .badge-warning {
            background: #FF9800;
        }
        
        .badge-info {
            background: #2196F3;
        }
        
        .status {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(76, 175, 80, 0.9);
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: bold;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        
        .refresh-btn {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(33, 150, 243, 0.9);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 30px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .refresh-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 20px rgba(33, 150, 243, 0.5);
        }
    </style>
</head>
<body>
    <div class="status">🟢 LIVE</div>
    
    <div class="container">
        <header>
            <h1>🚀 Ultra Bounty Hunter v4.0</h1>
            <p>Real-Time Intelligent Bounty Monitoring System</p>
        </header>
        
        <div class="stats-grid" id="stats-grid">
            <div class="stat-card">
                <h3>Total Bounties Found</h3>
                <div class="value" id="total-bounties">0</div>
                <div class="label">opportunities discovered</div>
            </div>
            
            <div class="stat-card">
                <h3>Total Analyzed</h3>
                <div class="value" id="total-analyzed">0</div>
                <div class="label">deep analysis completed</div>
            </div>
            
            <div class="stat-card">
                <h3>Comments Posted</h3>
                <div class="value" id="total-comments">0</div>
                <div class="label">bounty claims</div>
            </div>
            
            <div class="stat-card">
                <h3>PRs Merged</h3>
                <div class="value" id="total-prs">0</div>
                <div class="label">successful contributions</div>
            </div>
            
            <div class="stat-card">
                <h3>Total Earnings</h3>
                <div class="value" id="total-earnings">$0</div>
                <div class="label">real money earned</div>
            </div>
            
            <div class="stat-card">
                <h3>Success Rate</h3>
                <div class="value" id="success-rate">0%</div>
                <div class="label">conversion rate</div>
            </div>
        </div>
        
        <div class="charts-section">
            <div class="chart-card">
                <h2>📊 Platform Distribution</h2>
                <div id="platform-chart">Loading...</div>
            </div>
            
            <div class="chart-card">
                <h2>💰 Daily Earnings</h2>
                <div id="earnings-chart">Loading...</div>
            </div>
        </div>
        
        <div class="bounty-list">
            <h2>🎯 Top Bounties (Last 24h)</h2>
            <div id="bounty-list">Loading...</div>
        </div>
    </div>
    
    <button class="refresh-btn" onclick="refreshData()">🔄 Refresh</button>
    
    <script>
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                
                document.getElementById('total-bounties').textContent = stats.total_bounties_found;
                document.getElementById('total-analyzed').textContent = stats.total_analyzed;
                document.getElementById('total-comments').textContent = stats.total_comments;
                document.getElementById('total-prs').textContent = stats.total_prs;
                document.getElementById('total-earnings').textContent = '$' + stats.total_earnings.toFixed(2);
                document.getElementById('success-rate').textContent = stats.success_rate.toFixed(1) + '%';
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }
        
        async function loadBounties() {
            try {
                const response = await fetch('/api/bounties/recent');
                const bounties = await response.json();
                
                const container = document.getElementById('bounty-list');
                if (bounties.length === 0) {
                    container.innerHTML = '<p style="opacity: 0.5;">No bounties found yet...</p>';
                    return;
                }
                
                container.innerHTML = bounties.reverse().slice(0, 5).map(b => `
                    <div class="bounty-item">
                        <h4>${b.title || 'Untitled'}</h4>
                        <div class="bounty-meta">
                            <span><strong>$${b.bounty_amount || 0}</strong></span>
                            <span class="badge badge-info">${b.platform || 'unknown'}</span>
                            <span class="badge badge-warning">${b.category || 'unknown'}</span>
                            <span>${b.repo || 'unknown repo'}</span>
                        </div>
                    </div>
                `).join('');
            } catch (error) {
                console.error('Error loading bounties:', error);
            }
        }
        
        async function loadAnalytics() {
            try {
                const response = await fetch('/api/analytics');
                const analytics = await response.json();
                
                // Platform chart (simple text for now)
                const platformChart = document.getElementById('platform-chart');
                const platforms = Object.entries(analytics.platform_stats);
                if (platforms.length === 0) {
                    platformChart.innerHTML = '<p style="opacity: 0.5;">No data yet...</p>';
                } else {
                    platformChart.innerHTML = platforms.map(([name, data]) => `
                        <div style="margin-bottom: 10px;">
                            <strong>${name}:</strong> ${data.count} bounties ($${data.total_value.toFixed(2)})
                        </div>
                    `).join('');
                }
                
                // Earnings chart
                const earningsChart = document.getElementById('earnings-chart');
                const earnings = Object.entries(analytics.daily_earnings);
                if (earnings.length === 0) {
                    earningsChart.innerHTML = '<p style="opacity: 0.5;">No earnings yet...</p>';
                } else {
                    earningsChart.innerHTML = earnings.slice(-7).map(([date, amount]) => `
                        <div style="margin-bottom: 10px;">
                            <strong>${date}:</strong> $${amount.toFixed(2)}
                        </div>
                    `).join('');
                }
            } catch (error) {
                console.error('Error loading analytics:', error);
            }
        }
        
        async function refreshData() {
            await fetch('/api/refresh');
            loadStats();
            loadBounties();
            loadAnalytics();
        }
        
        // Load data on page load
        loadStats();
        loadBounties();
        loadAnalytics();
        
        // Auto-refresh every 30 seconds
        setInterval(() => {
            loadStats();
            loadBounties();
            loadAnalytics();
        }, 30000);
    </script>
</body>
</html>
"""

# ============================================================================
# TEMPLATE SETUP
# ============================================================================

@app.route('/templates/dashboard.html')
def serve_template():
    """Serve the dashboard template"""
    return HTML_TEMPLATE

# Ensure templates directory exists and create dashboard.html
os.makedirs('templates', exist_ok=True)
with open('templates/dashboard.html', 'w') as f:
    f.write(HTML_TEMPLATE)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 ULTRA BOUNTY HUNTER DASHBOARD")
    print("=" * 60)
    print("📊 Dashboard: http://localhost:8080")
    print("🔄 Auto-refresh: Every 30 seconds")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=8080, debug=True)
