## rpi-status-monitor

So I don't wanna install **[Nezha Monitor](https://github.com/nezhahq/nezha)** on my Raspberry Pi...

Using `DeepSeek v3.2 Chat` model from DeepSeek API while experiencing the joy of *vibe coding*, this project was finished.

Follow these easy steps below to install for your RPi or something equipped with Linux

## Setup
I used `RPi OS Lite(64-bit, Legacy)`, namely **Debian 12 (Bookworm)** as RPi system, with `python3` and `flask` installed

If you're encountering connection issues with `deb.debian.org`, consider using TUNA source for downloading dependencies:

```bash
sudo nano /etc/apt/sources.list
```

<img width="1148" height="224" alt="ce110d3a89ed151a4ce186ed195f26cc" src="https://github.com/user-attachments/assets/02e6e880-2f26-4b74-acd8-fec6cbf64ebe" />

<br></br>

> [!IMPORTANT]
> Before you start: be aware that not all commands listed below can be executed straightly, please replace contents placed within `< >` to your real info
> 
> For example, my RPi username is `meowcata`, so I replace `/home/<username>/rpi-monitor` in the command to `/home/meowcata/rpi-monitor` before executing

First you clone this repo:
```bash
git clone https://github.com/MeowCata/rpi-status-monitor.git
cd rpi-status-monitor
```
Send the files to Raspberry Pi using `WinSCP`:

Create `/rpi-monitor/` & `/rpi-monitor/templates/` folder on RPi via SSH first, then execute on Windows:
```bash
scp app.py <username>@<your-rpi-ip>:/home/<username>/rpi-monitor/app.py

scp ./templates/index.html <username>@<your-rpi-ip>:/home/<username>/rpi-monitor/templates/index.html
```

Your folder tree might be like this:
```
/home/<username>
  /rpi-monitor
    app.py
    /templates
      index.html
```

After all the files transferred, run:
```python
python3 app.py
```

Output may be:
```bash
 * Serving Flask app 'app'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://<your-rpi.ip>:5000
Press CTRL+C to quit
```
Congrats! Now load this address on your `Cloudflare Tunnel` and check it out on your domain!

## RPi Optimize
Maybe you want this app to be auto-started with RPi, please execute on RPi:
```bash
sudo nano /etc/systemd/system/rpi-monitor.service
```

In the console editor you type:
```bash
[Unit]
Description=RPi Status Web Page
After=network.target

[Service]
WorkingDirectory=/home/<username>/rpi-monitor
ExecStart=/usr/bin/python3 app.py
User=<username>
Restart=always
RestartSec=5
# activate these if no logs are needed to debug
# StandardOutput=null
# StandardError=null

[Install]
WantedBy=multi-user.target
```
Press `CTRL+S`,then `CTRL+X` to quit.

And execute:
```bash
# reload system services
sudo systemctl daemon-reload

# set as autostart
sudo systemctl enable rpi-monitor.service

# start now
sudo systemctl start rpi-monitor.service
```

## Something to emphasize
1.For some reason the `Processor` on RPi can't be read by Linux, so edit [Line 494 in index.html](https://github.com/MeowCata/rpi-status-monitor/blob/main/templates/index.html#L494) to match your real CPU Model

2.Near 5M tokens are used (Cline's literally burning tokens😡), but costing only ~2.1 CNY, so cheap!

3.Using `ZRAM` for swap is recommended if you don't wanna exert your poor SD card and let it die when it's still young

## Screenshot:
<img width="1544" height="854" alt="image" src="https://github.com/user-attachments/assets/270fe9b9-5e6e-4d4e-9fe7-e4146707dca5" />
<br></br>
<img width="364" height="22" alt="image" src="https://github.com/user-attachments/assets/1eaf370e-c5bc-4934-a5fc-b2173af4c0d3" />

Runs perfectly on my `RPi Zero 2 W` while consuming ~30MB memory, maybe not that good on memory-intensive devices? (Zero 2 W has only 512MB, and 464MB can be used)

Anyway, that's fine for me and I'm gonna use it as my RPi status monitor
