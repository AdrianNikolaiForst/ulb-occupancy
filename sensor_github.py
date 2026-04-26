#!/usr/bin/env python3
"""
VL53L1X → GitHub Pages
Liest den Sensor aus und pusht den Wert alle 30 Sekunden zu GitHub.
"""

import VL53L1X
import time
import json
import os
import subprocess
from datetime import datetime

# --- Konfiguration ---
RANGING_MODE  = 1         # 1=Short, 2=Medium, 3=Long
PUSH_INTERVAL = 30        # Sekunden zwischen GitHub-Pushes
REPO_PATH     = "/home/pi/pi-sensor"   # Pfad zum geklonten Repo
# ---------------------

def push_to_github(distanz_mm):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # JSON-Datei schreiben
    data = {
        "distanz_mm": distanz_mm,
        "distanz_cm": round(distanz_mm / 10, 1),
        "timestamp": timestamp
    }
    with open(f"{REPO_PATH}/data.json", "w") as f:
        json.dump(data, f)

    # Git push
    os.chdir(REPO_PATH)
    subprocess.run(["git", "add", "data.json"])
    subprocess.run(["git", "commit", "-m", f"Update: {distanz_mm}mm @ {timestamp}"])
    subprocess.run(["git", "push"])
    print(f"  → GitHub aktualisiert: {distanz_mm}mm ({timestamp})")

def main():
    print("VL53L1X → GitHub Pages")
    print("─" * 50)

    tof = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=0x29)

    try:
        tof.open()
        tof.set_timing(66000, 70)
        tof.start_ranging(RANGING_MODE)

        last_push = 0

        while True:
            distanz = tof.get_distance()

            if distanz > 0:
                print(f"  {distanz:>5} mm  ({distanz/10:.1f} cm)")

                # Alle 30 Sekunden pushen
                if time.time() - last_push >= PUSH_INTERVAL:
                    push_to_github(distanz)
                    last_push = time.time()

            time.sleep(0.07)

    except KeyboardInterrupt:
        print("\nBeendet.")
    finally:
        try:
            tof.stop_ranging()
            tof.close()
        except:
            pass

if __name__ == "__main__":
    main()
