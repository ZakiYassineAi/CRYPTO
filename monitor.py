#!/usr/bin/env python3
"""
Advanced Performance Monitor for Money Maker Bot
Tracks real-time metrics and generates reports
"""

import json
import time
import subprocess
from datetime import datetime, timedelta
from github import Github

class BotMonitor:
    def __init__(self):
        with open('.github_token', 'r') as f:
            self.token = f.read().strip()
        self.github = Github(self.token)
        self.user = self.github.get_user()
        
    def get_bot_status(self):
        """Check if bot is running via PM2"""
        try:
            result = subprocess.run(
                ['npx', 'pm2', 'jlist'],
                capture_output=True,
                text=True
            )
            processes = json.loads(result.stdout)
            
            for proc in processes:
                if proc['name'] == 'MONEY-BOT':
                    return {
                        'status': proc['pm2_env']['status'],
                        'uptime': self.format_uptime(proc['pm2_env']['pm_uptime']),
                        'restarts': proc['pm2_env']['restart_time'],
                        'memory': f"{proc['monit']['memory'] / 1048576:.1f}MB",
                        'cpu': f"{proc['monit']['cpu']}%"
                    }
        except:
            pass
        return None
    
    def get_github_activity(self):
        """Get recent GitHub activity"""
        events = self.user.get_events()
        
        activity = {
            'comments': 0,
            'issues': 0,
            'prs': 0,
            'recent': []
        }
        
        for event in events[:30]:
            if event.type == 'IssueCommentEvent':
                activity['comments'] += 1
                activity['recent'].append({
                    'type': 'comment',
                    'repo': event.repo.name,
                    'time': event.created_at
                })
            elif event.type == 'IssuesEvent':
                activity['issues'] += 1
            elif event.type == 'PullRequestEvent':
                activity['prs'] += 1
                
        return activity
    
    def analyze_performance(self):
        """Analyze bot performance metrics"""
        try:
            # Read PM2 logs
            with subprocess.Popen(
                ['npx', 'pm2', 'logs', 'MONEY-BOT', '--nostream', '--lines', '500'],
                stdout=subprocess.PIPE,
                text=True
            ) as proc:
                logs = proc.stdout.read()
            
            # Extract metrics from logs
            metrics = {
                'issues_found': logs.count('Found'),
                'solutions_posted': logs.count('Solution posted'),
                'errors': logs.count('Error') + logs.count('Failed'),
                'rate_limits': logs.count('Rate limit'),
                'bounties': self.extract_bounties(logs)
            }
            
            # Calculate success rate
            if metrics['issues_found'] > 0:
                metrics['success_rate'] = (
                    metrics['solutions_posted'] / metrics['issues_found'] * 100
                )
            else:
                metrics['success_rate'] = 0
                
            return metrics
            
        except Exception as e:
            return {'error': str(e)}
    
    def extract_bounties(self, logs):
        """Extract bounty amounts from logs"""
        import re
        
        bounties = []
        pattern = r'\$(\d+(?:\.\d+)?)'
        
        for match in re.finditer(pattern, logs):
            try:
                amount = float(match.group(1))
                if amount > 0 and amount < 10000:  # Reasonable bounds
                    bounties.append(amount)
            except:
                pass
                
        return {
            'total': sum(bounties),
            'count': len(bounties),
            'average': sum(bounties) / len(bounties) if bounties else 0,
            'max': max(bounties) if bounties else 0,
            'min': min(bounties) if bounties else 0
        }
    
    def format_uptime(self, timestamp):
        """Format uptime nicely"""
        if not timestamp:
            return "Unknown"
            
        start = datetime.fromtimestamp(timestamp / 1000)
        delta = datetime.now() - start
        
        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def generate_report(self):
        """Generate comprehensive performance report"""
        print("=" * 60)
        print(" MONEY MAKER BOT - PERFORMANCE REPORT ".center(60))
        print("=" * 60)
        print(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Bot Status
        status = self.get_bot_status()
        if status:
            print(f"\n🤖 BOT STATUS:")
            print(f"   Status: {status['status']}")
            print(f"   Uptime: {status['uptime']}")
            print(f"   Restarts: {status['restarts']}")
            print(f"   Memory: {status['memory']}")
            print(f"   CPU: {status['cpu']}")
        
        # GitHub Activity
        activity = self.get_github_activity()
        print(f"\n📊 GITHUB ACTIVITY (Last 24h):")
        print(f"   Comments Posted: {activity['comments']}")
        print(f"   Issues Created: {activity['issues']}")
        print(f"   PRs Created: {activity['prs']}")
        
        # Performance Metrics
        metrics = self.analyze_performance()
        if 'error' not in metrics:
            print(f"\n📈 PERFORMANCE METRICS:")
            print(f"   Issues Found: {metrics['issues_found']}")
            print(f"   Solutions Posted: {metrics['solutions_posted']}")
            print(f"   Success Rate: {metrics['success_rate']:.1f}%")
            print(f"   Errors: {metrics['errors']}")
            print(f"   Rate Limits Hit: {metrics['rate_limits']}")
            
            if metrics['bounties']['count'] > 0:
                print(f"\n💰 BOUNTY STATISTICS:")
                print(f"   Total Value: ${metrics['bounties']['total']:.2f}")
                print(f"   Bounties Found: {metrics['bounties']['count']}")
                print(f"   Average: ${metrics['bounties']['average']:.2f}")
                print(f"   Highest: ${metrics['bounties']['max']:.2f}")
                print(f"   Lowest: ${metrics['bounties']['min']:.2f}")
        
        print("\n" + "=" * 60)
        
    def continuous_monitor(self, interval=60):
        """Monitor continuously and update stats"""
        print("Starting continuous monitoring...")
        print(f"Updates every {interval} seconds\n")
        
        while True:
            try:
                self.generate_report()
                time.sleep(interval)
                print("\n" * 2)  # Clear space for next report
                
            except KeyboardInterrupt:
                print("\nMonitoring stopped by user")
                break
            except Exception as e:
                print(f"Monitor error: {e}")
                time.sleep(interval)

if __name__ == "__main__":
    monitor = BotMonitor()
    
    # Generate single report
    monitor.generate_report()
    
    # Optional: Start continuous monitoring
    # monitor.continuous_monitor(60)