# Add crontab entry to run the resource watchdog every 5 minutes to manage idle states automatically
(crontab -l 2>/dev/null; echo "*/5 * * * * cd /root/QuantBot && /root/QuantBot/venv/bin/python3 resource_watchdog.py >> /root/QuantBot/watchdog.log 2>&1") | crontab -
echo "Resource watchdog automation configured successfully via cron."
