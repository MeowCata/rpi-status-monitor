from flask import Flask, jsonify, render_template
import psutil
import time
import platform

app = Flask(__name__)

# 记录系统启动时间，用于计算运行时间
boot_time = psutil.boot_time()

def get_cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            return round(int(f.read()) / 1000, 1)
    except:
        return 0.0

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/stats')
def stats():
    # 获取系统平均负载 (1分钟, 5分钟, 15分钟)
    load1, load5, load15 = psutil.getloadavg()
    
    # 内存与交换区
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    # 根目录磁盘使用情况
    disk = psutil.disk_usage('/')
    
    # 网络 IO (这里取总计数，前端可以通过差值计算实时网速)
    net = psutil.net_io_counters()
    
    # 获取当前数据
    cpu_percent = psutil.cpu_percent(interval=None)
    mem_percent = mem.percent
    swap_percent = swap.percent if swap.total > 0 else 0
    procs = len(psutil.pids())
    temp = get_cpu_temp()
    
    current_time = time.time()
    
    # 获取更多系统信息
    cpu_freq = psutil.cpu_freq()
    cpu_count = psutil.cpu_count()
    
    # 处理CPU频率可能为None的情况（如Raspberry Pi Zero 2W）
    cpu_freq_current = 0
    cpu_freq_max = 0
    if cpu_freq:
        cpu_freq_current = cpu_freq.current if cpu_freq.current else 0
        cpu_freq_max = cpu_freq.max if cpu_freq.max else 0
    
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
        "timestamp": current_time
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)