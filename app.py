from flask import Flask, jsonify, render_template
import psutil
import time
import platform
import subprocess
import os

app = Flask(__name__)

# Record system boot time for calculating uptime
boot_time = psutil.boot_time()

def get_cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return round(int(f.read()) / 1000, 1)
    except:
        return 0.0

def get_ssh_users():
    """Get current SSH user count - improved version"""
    try:
        # Method 1: Use w command to find active SSH users (most accurate)
        result = subprocess.run(['w', '-h'], capture_output=True, text=True)
        ssh_count = 0
        for line in result.stdout.splitlines():
            # w command shows active users with their processes
            # SSH connections typically show pts terminals
            if 'pts/' in line:
                ssh_count += 1
        
        # Method 2: If w command fails or returns no results, try using who command
        if ssh_count == 0:
            result = subprocess.run(['who'], capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if 'pts/' in line:  # SSH connections usually use pts terminal
                    ssh_count += 1
        
        # Method 3: As a last resort, check for active sshd client processes
        # This filters out the parent sshd process and only counts client sessions
        if ssh_count == 0:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            for line in result.stdout.splitlines():
                # Look for sshd: processes that are client sessions (not the parent daemon)
                if 'sshd:' in line and '@pts' in line:
                    ssh_count += 1
        
        return ssh_count
    except Exception as e:
        print(f"Error getting SSH users: {e}")
        return 0

def get_neofetch():
    """Get neofetch system information"""
    try:
        # Run neofetch command with minimal output
        result = subprocess.run(['neofetch', '--stdout'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            # Fallback to basic system info if neofetch fails
            return f"System: {platform.system()}\nVersion: {platform.version()}\nMachine: {platform.machine()}\nProcessor: {platform.processor()}"
    except Exception as e:
        print(f"Error getting neofetch: {e}")
        return f"System: {platform.system()}\nVersion: {platform.version()}\nMachine: {platform.machine()}\nProcessor: {platform.processor()}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/stats')
def stats():
    # Get system load average (1min, 5min, 15min)
    load1, load5, load15 = psutil.getloadavg()
    
    # Memory and swap
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    # Root directory disk usage
    disk = psutil.disk_usage('/')
    
    # Network IO (total counters, frontend can calculate real-time speed from differences)
    net = psutil.net_io_counters()
    
    # Get current data
    cpu_percent = psutil.cpu_percent(interval=None)
    mem_percent = mem.percent
    swap_percent = swap.percent if swap.total > 0 else 0
    procs = len(psutil.pids())
    temp = get_cpu_temp()
    
    current_time = time.time()
    
    # Get more system information
    cpu_freq = psutil.cpu_freq()
    cpu_count = psutil.cpu_count()
    
    # Handle case where CPU frequency might be None (e.g., Raspberry Pi Zero 2W)
    cpu_freq_current = 0
    cpu_freq_max = 0
    if cpu_freq:
        cpu_freq_current = cpu_freq.current if cpu_freq.current else 0
        cpu_freq_max = cpu_freq.max if cpu_freq.max else 0
    
    # Get SSH user count
    ssh_users = get_ssh_users()
    
    return jsonify({
        "system": platform.system(),
        "system_version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "uptime": int(current_time - boot_time),
        "load": f"{load1:.2f} / {load5:.2f} / {load15:.2f}",
        "cpu_percent": cpu_percent,
        "cpu_count": cpu_count,
        "cpu_freq_current": cpu_freq_current,
        "cpu_freq_max": cpu_freq_max,
        "temp": temp,
        "mem_percent": mem_percent,
        "mem_used": round(mem.used / (1024 * 1024), 2),
        "mem_total": round(mem.total / (1024 * 1024), 2),
        "swap_percent": swap_percent,
        "swap_used": round(swap.used / (1024 * 1024), 2),
        "swap_total": round(swap.total / (1024 * 1024), 2),
        "disk_percent": disk.percent,
        "disk_used": round(disk.used / (1024 * 1024 * 1024), 2),
        "disk_total": round(disk.total / (1024 * 1024 * 1024), 2),
        "net_sent": net.bytes_sent,
        "net_recv": net.bytes_recv,
        "procs": procs,
        "ssh_users": ssh_users,
        "timestamp": current_time
    })

@app.route('/api/neofetch')
def neofetch():
    """Get neofetch system information (only fetched once on page load)"""
    neofetch_output = get_neofetch()
    return jsonify({
        "neofetch": neofetch_output
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
