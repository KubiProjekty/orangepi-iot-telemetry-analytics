import requests
import sqlite3
import os
from datetime import datetime

miasta = {
    "Annopol": (50.8842, 21.8594),
    "Krakow": (50.0647, 19.9450),
    "Minsk Mazowiecki": (52.1794, 21.5725)
}
teraz = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
conn = sqlite3.connect("/mnt/python_skrypty/moje_dane.db")
conn.execute("CREATE TABLE IF NOT EXISTS smog (data TEXT, miasto TEXT, pm2_5 REAL, pm10 REAL)")

url_pogoda = "https://" + "api." + "open-meteo.com" + "/v1/forecast"
url_smog = "https://" + "air-quality-api." + "open-meteo.com" + "/v1/air-quality"

plik_smog = "/mnt/python_skrypty/historia_smogu.csv"
czy_nowy_smog = not os.path.exists(plik_smog)

with open("/mnt/python_skrypty/historia_pogody.csv", "a", encoding="utf-8") as fp, \
     open(plik_smog, "a", encoding="utf-8") as fs:

    if czy_nowy_smog:
        fs.write("Data,Miasto,PM2_5,PM10\n")

    for nazwa, (lat, lon) in miasta.items():
        # 1. Pogoda
        p_pogoda = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,apparent_temperature,relative_humidity_2m,surface_pressure,precipitation,wind_speed_10m"
        }
        d = requests.get(url_pogoda, params=p_pogoda, timeout=15).json()["current"]
        w_pogoda = (teraz, nazwa, d["temperature_2m"], d["apparent_temperature"], d["relative_humidity_2m"], d["surface_pressure"], d["precipitation"], d["wind_speed_10m"])
        fp.write(",".join(map(str, w_pogoda)) + "\n")
        conn.execute("INSERT INTO pogoda VALUES (?,?,?,?,?,?,?,?)", w_pogoda)

        # 2. Czystosc powietrza (PM2.5 i PM10)
        p_smog = {
            "latitude": lat,
            "longitude": lon,
            "current": "pm2_5,pm10"
        }
        s = requests.get(url_smog, params=p_smog, timeout=15).json()["current"]
        w_smog = (teraz, nazwa, s["pm2_5"], s["pm10"])
        fs.write(",".join(map(str, w_smog)) + "\n")
        conn.execute("INSERT INTO smog VALUES (?,?,?,?)", w_smog)

conn.commit()
conn.close()
print(f"{teraz} | Zapisano pogode oraz czystosc powietrza (PM2.5/PM10).")
