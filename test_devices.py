import base64, json, random, requests
from datetime import datetime

host = "192.168.1.241"
password = "12345678"

# Auth
pw_b64 = base64.b64encode(password.encode()).decode()
now = datetime.now()
time_str = f"{now.year};{now.month};{now.day};{now.hour};{now.minute};{now.second}"
payload = {"sysLogin": {"username": "admin", "password": pw_b64, "logoff": False, "timeZone": 12, "time": time_str}}
r = requests.post(f"http://{host}/goform/modules?{random.random()}", json=payload, timeout=10, allow_redirects=False)
cookies = r.cookies

# Get devices
r = requests.post(f"http://{host}/goform/modules?{random.random()}", json={"wifiClientList": {}}, cookies=cookies, timeout=10, allow_redirects=False)
data = r.json()

devices = data.get("wifiClientList", [])
print(f"Dispositivi trovati: {len(devices)}")
print()
for d in devices:
    sec = int(d.get("connectTime", 0))
    h = sec // 3600
    m = (sec % 3600) // 60
    t = f"{h}h {m}m" if h > 0 else f"{m}m"
    sn = d.get("signNoise", "")
    sig = sn.split("/")[0] if "/" in sn else ""
    mac = d["mac"]
    ip = d["ip"]
    tx = d["txRate"]
    rx = d["rxRate"]
    print(f"  {mac:>17} | IP: {ip:>15} | Connesso da: {t:>8} | TX: {tx:>6} Mbps | RX: {rx:>6} Mbps | Segnale: {sig}")
