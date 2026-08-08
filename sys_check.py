import os
import psutil

print("=== SYSTEM HEALTH CHECK ===")
print(f"CPU Usage: {psutil.cpu_percent(interval=1)}%")
mem = psutil.virtual_memory()
print(f"Memory Usage: {mem.percent}% (Used: {mem.used / (1024**2):.2f} MB / Total: {mem.total / (1024**2):.2f} MB)")

print("\n=== RUNNING BOT PROCESSES ===")
found_bot = False
for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent']):
    try:
        cmdline = proc.info['cmdline']
        if cmdline and any('python' in arg or 'QuantBot' in arg for arg in cmdline):
            print(f"PID: {proc.info['pid']} | CPU: {proc.info['cpu_percent']}% | RAM: {proc.info['memory_percent']:.2f}% | Cmd: {' '.join(cmdline)}")
            found_bot = True
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass

if not found_bot:
    print("No active python trading bot processes detected via psutil.")
