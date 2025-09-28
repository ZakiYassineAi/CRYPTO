module.exports = {
  apps: [
    {
      name: 'shadow-hunter-monitor',
      script: 'shadow_monitor.py',
      interpreter: 'python3',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      env: {
        NODE_ENV: 'production'
      },
      error_file: './logs/shadow-error.log',
      out_file: './logs/shadow-out.log',
      log_file: './logs/shadow-combined.log',
      time: true,
      merge_logs: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },
    {
      name: 'shadow-web-server',
      script: 'python3',
      args: '-m http.server 8888 --directory .',
      instances: 1,
      autorestart: true,
      watch: false,
      env: {
        PORT: 8888
      },
      error_file: './logs/web-error.log',
      out_file: './logs/web-out.log'
    }
  ]
};