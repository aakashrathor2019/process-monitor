import configparser
import json
import socket
import sys
import time
from datetime import datetime, timezone

import psutil
import requests

def load_config():
    cfg = configparser.ConfigParser()
    cfg.read('config.ini')
    return {
        "backend_url": cfg.get('agent', 'backend_url', fallback='http://127.0.0.1:8000/api/v1/ingest'),
        "api_key": cfg.get('agent', 'api_key', fallback='CHANGEME'),
        "interval_seconds": cfg.getint('agent', 'interval_seconds', fallback=0),
    }

def collect_processes():
    # Warm up for cpu_percent
    for p in psutil.process_iter(['pid']):
        try:
            p.cpu_percent(None)
        except Exception:
            pass
    time.sleep(0.1)

    procs = []
    for p in psutil.process_iter(['pid', 'ppid', 'name', 'memory_info']):
        try:
            info = p.info
            cpu = p.cpu_percent(None)
            mem = info.get('memory_info')
            procs.append({
                "pid": int(info.get('pid')),
                "ppid": int(info.get('ppid')),
                "name": (info.get('name') or ""),
                "cpu_percent": float(cpu) if cpu is not None else 0.0,
                "mem_rss": int(mem.rss) if mem else 0,
                "mem_vms": int(mem.vms) if mem else 0,
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return procs

def payload():
    return {
        "hostname": socket.gethostname(),
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "processes": collect_processes()
    }

def send_once(url, api_key, data):
    headers = {"Content-Type": "application/json", "X-API-Key": api_key}
    resp = requests.post(url, headers=headers, data=json.dumps(data), timeout=15)
    resp.raise_for_status()
    return resp.json()

def main():
    cfg = load_config()
    interval = cfg["interval_seconds"]
    url = cfg["backend_url"]
    key = cfg["api_key"]

    if not key or key == "CHANGEME":
        print("Please set api_key in config.ini")
        sys.exit(1)

    if interval <= 0:
        print("Sending snapshot...")
        try:
            print(send_once(url, key, payload()))
        except Exception as e:
            print("Error:", e)
    else:
        while True:
            try:
                print(send_once(url, key, payload()))
            except Exception as e:
                print("Error:", e)
            time.sleep(interval)

if __name__ == "__main__":
    main()
