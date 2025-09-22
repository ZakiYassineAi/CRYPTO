module.exports = {
  apps: [
    {
      name: 'REAL-MONEY-BOT-V2',
      script: 'python3',
      args: 'real_money_maker_bot.py',
      cwd: '/home/user/webapp',
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'production',
        PYTHONUNBUFFERED: '1'
      },
      error_file: './logs/real-bot-error.log',
      out_file: './logs/real-bot-out.log',
      time: true,
      merge_logs: true,
      min_uptime: '10s',
      max_restarts: 100,
      restart_delay: 4000,
      kill_timeout: 5000,
      instances: 1,
      exec_mode: 'fork'
    }
  ]
};