# 1. zdrowie_serwera.py (zapis do CSV + SQLite)
kod_zdrowie = """import sqlite3, os, shutil
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
    f.write(f"{teraz},{temp},{ram_uzyty},{ram_wolny},{dysk_wolny}\\n")

conn = sqlite3.connect("/mnt/python_skrypty/moje_dane.db")
conn.execute("INSERT INTO zdrowie VALUES (?,?,?,?,?)", (teraz, temp, ram_uzyty, ram_wolny, dysk_wolny))
conn.commit()
conn.close()
"""

# 2. kursy_walut.py (zapis do CSV + SQLite)
kod_waluty = """import requests, sqlite3
from datetime import datetime

teraz = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
eur = requests.get("https://nbp.pl", timeout=10).json()["rates"][0]["mid"]
usd = requests.get("https://nbp.pl", timeout=10).json()["rates"][0]["mid"]

with open("/mnt/python_skrypty/historia_walut.csv", "a", encoding="utf-8") as f:
    f.write(f"{teraz},{eur},{usd}\\n")

conn = sqlite3.connect("/mnt/python_skrypty/moje_dane.db")
conn.execute("INSERT INTO waluty VALUES (?,?,?)", (teraz, eur, usd))
conn.commit()
conn.close()
"""

# 3. pogoda.py (zapis do CSV + SQLite)
kod_pogoda = """import requests, sqlite3
from datetime import datetime

miasta = {
    "Annopol": (50.8842, 21.8594),
    "Krakow": (50.0647, 19.9450),
    "Minsk Mazowiecki": (52.1794, 21.5725)
}
teraz = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
conn = sqlite3.connect("/mnt/python_skrypty/moje_dane.db")

with open("/mnt/python_skrypty/historia_pogody.csv", "a", encoding="utf-8") as f:
    for nazwa, (lat, lon) in miasta.items():
        url = f"https://open-meteo.com{lat}&longitude={lon}&current=temperature_2m,apparent_temperature,relative_humidity_2m,surface_pressure,precipitation,wind_speed_10m"
        d = requests.get(url, timeout=15).json()["current"]
        wiersz = (teraz, nazwa, d["temperature_2m"], d["apparent_temperature"], d["relative_humidity_2m"], d["surface_pressure"], d["precipitation"], d["wind_speed_10m"])
        f.write(",".join(map(str, wiersz)) + "\\n")
        conn.execute("INSERT INTO pogoda VALUES (?,?,?,?,?,?,?,?)", wiersz)

conn.commit()
conn.close()
"""

with open("/mnt/python_skrypty/zdrowie_serwera.py", "w", encoding="utf-8") as f: f.write(kod_zdrowie)
with open("/mnt/python_skrypty/kursy_walut.py", "w", encoding="utf-8") as f: f.write(kod_waluty)
with open("/mnt/python_skrypty/pogoda.py", "w", encoding="utf-8") as f: f.write(kod_pogoda)
print("Zaktualizowano skrypty: zdrowie, waluty i pogoda!")
