import sqlite3, os, shutil
from datetime import datetime

teraz = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
with open("/sys/class/thermal/thermal_zone0/temp") as f:
    temp = round(int(f.read().strip()) / 1000, 1)

with open("/proc/meminfo") as f:
    mem = {l.split(":")[0]: int(l.split()[1]) for l in f}
ram_caly = round(mem["MemTotal"] / 1024, 1)
ram_wolny = round(mem["MemAvailable"] / 1024, 1)
ram_uzyty = round(ram_caly - ram_wolny, 1)
dysk_wolny = round(shutil.disk_usage("/mnt").free / (1024**3), 2)

with open("/mnt/python_skrypty/historia_zdrowia.csv", "a", encoding="utf-8") as f:
    f.write(f"{teraz},{temp},{ram_uzyty},{ram_wolny},{dysk_wolny}\n")

conn = sqlite3.connect("/mnt/python_skrypty/moje_dane.db")
conn.execute("INSERT INTO zdrowie VALUES (?,?,?,?,?)", (teraz, temp, ram_uzyty, ram_wolny, dysk_wolny))
conn.commit()
conn.close()
