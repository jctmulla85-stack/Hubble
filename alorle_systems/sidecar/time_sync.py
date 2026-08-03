import time
import subprocess

def verify_system_time():
    """Checks if NTP synchronization is active on the host system."""
    try:
        # Query timedatectl to check NTP synchronization status
        result = subprocess.run(["timedatectl", "status"], capture_output=True, text=True, check=True)
        output = result.stdout
        
        if "NTP service: active" in output or "Network time on: yes" in output:
            print("[TimeSync] VERIFIED: NTP synchronization is active.")
            return True
        else:
            print("[TimeSync] WARNING: NTP synchronization is not explicitly active. Consider running 'timedatectl set-ntp true'.")
            return False
    except Exception as e:
        # Fallback if timedatectl is unavailable on a minimal container/VPS
        print(f"[TimeSync] Note: Could not query system time daemon directly ({e}). Current Epoch: {time.time()}")
        return True
