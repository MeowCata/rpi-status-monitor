from flask import Flask, jsonify, render_template
import psutil
import os

app = Flask(__name__)

# 全局运行状态
sim_status = {"running": True}

def get_cpu_temp():
    # 树莓派 CPU 温度存储在系统路径中
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
    return jsonify({
        "cpu": psutil.cpu_percent(interval=None),
        "ram": psutil.virtual_memory().percent,
        "temp": get_cpu_temp(),
        "running": sim_status["running"]
    })

@app.route('/api/toggle', methods=['POST'])
def toggle():
    sim_status["running"] = not sim_status["running"]
    return jsonify({"status": "ok", "running": sim_status["running"]})

if __name__ == '__main__':
    # 监听 5000 端口，允许外部访问
    app.run(host='0.0.0.0', port=5000)
