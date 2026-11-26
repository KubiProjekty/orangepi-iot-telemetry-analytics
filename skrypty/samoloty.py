import requests
import sqlite3
from datetime import datetime, timedelta
import os
import json

baza = "https://" + "opensky-network" + ".org/api/states/all"
parametry = {
    "lamin": 50.00,
    "lamax": 51.80,
    "lomin": 20.40,
    "lomax": 23.30
}
naglowki = {"User-Agent": "Mozilla/5.0"}

teraz = datetime.now()
teraz_str = teraz.strftime("%Y-%m-%d %H:%M:%S")
plik_csv = "/mnt/python_skrypty/historia_lotow.csv"
plik_pamiec = "/mnt/python_skrypty/pamiec_lotow.json"
plik_db = "/mnt/python_skrypty/moje_dane.db"

pamiec = {}
if os.path.exists(plik_pamiec):
    try:
        with open(plik_pamiec, "r", encoding="utf-8") as f:
            pamiec = json.load(f)
    except Exception:
        pamiec = {}

granica = (teraz - timedelta(minutes=90)).timestamp()
pamiec = {k: v for k, v in pamiec.items() if v > granica}

try:
    odpowiedz = requests.get(baza, params=parametry, headers=naglowki, timeout=15).json()
    samoloty = odpowiedz.get("states") or []
except Exception as e:
    print(f"Blad polaczenia: {e}")
    samoloty = []

nowe_loty = 0
conn = sqlite3.connect(plik_db)

with open(plik_csv, "a", encoding="utf-8") as f:
    for s in samoloty:
        if s[8]:
            continue

        icao = s[0]
        if icao in pamiec:
            pamiec[icao] = teraz.timestamp()
            continue

        pamiec[icao] = teraz.timestamp()
        lot = (s[1] or "BRAK").strip()
        kraj = s[2] or "Nieznany"
        wysokosc = round(s[7]) if s[7] is not None else 0
        predkosc = round(s[9] * 3.6) if s[9] is not None else 0
        kierunek = round(s[10]) if s[10] is not None else 0

        f.write(f"{teraz_str},{icao},{lot},{kraj},{wysokosc},{predkosc},{kierunek}\n")
        conn.execute("INSERT INTO loty VALUES (?,?,?,?,?,?,?)", (teraz_str, icao, lot, kraj, wysokosc, predkosc, kierunek))
        nowe_loty += 1

conn.commit()
conn.close()

with open(plik_pamiec, "w", encoding="utf-8") as f:
    json.dump(pamiec, f)

print(f"{teraz_str} | Zapisano nowych przelotow do CSV i SQLite: {nowe_loty}")
