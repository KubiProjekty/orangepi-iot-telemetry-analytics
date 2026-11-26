import sqlite3
import csv
import os

baza_sciezka = "/mnt/python_skrypty/moje_dane.db"
conn = sqlite3.connect(baza_sciezka)
c = conn.cursor()

# 1. Tabela zdrowia serwera
c.execute("""CREATE TABLE IF NOT EXISTS zdrowie (
    data TEXT, temp_cpu REAL, ram_uzyty REAL, ram_wolny REAL, pendrive_wolne REAL)""")
if os.path.exists("/mnt/python_skrypty/historia_zdrowia.csv"):
    with open("/mnt/python_skrypty/historia_zdrowia.csv", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)
        for r in reader:
            if len(r) == 5:
                c.execute("INSERT INTO zdrowie VALUES (?,?,?,?,?)", r)

# 2. Tabela pogody
c.execute("""CREATE TABLE IF NOT EXISTS pogoda (
    data TEXT, miasto TEXT, temp_c REAL, odczuwalna_c REAL, wilgotnosc REAL, cisnienie REAL, opady REAL, wiatr REAL)""")
if os.path.exists("/mnt/python_skrypty/historia_pogody.csv"):
    with open("/mnt/python_skrypty/historia_pogody.csv", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)
        for r in reader:
            if len(r) == 8:
                c.execute("INSERT INTO pogoda VALUES (?,?,?,?,?,?,?,?)", r)

# 3. Tabela walut
c.execute("""CREATE TABLE IF NOT EXISTS waluty (
    data TEXT, eur REAL, usd REAL)""")
if os.path.exists("/mnt/python_skrypty/historia_walut.csv"):
    with open("/mnt/python_skrypty/historia_walut.csv", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)
        for r in reader:
            if len(r) == 3:
                c.execute("INSERT INTO waluty VALUES (?,?,?)", r)

# 4. Tabela lotów
c.execute("""CREATE TABLE IF NOT EXISTS loty (
    data TEXT, icao24 TEXT, numer_lotu TEXT, kraj_pochodzenia TEXT, wysokosc_m REAL, predkosc_kmh REAL, kierunek_st REAL)""")
if os.path.exists("/mnt/python_skrypty/historia_lotow.csv"):
    with open("/mnt/python_skrypty/historia_lotow.csv", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)
        for r in reader:
            if len(r) == 7:
                c.execute("INSERT INTO loty VALUES (?,?,?,?,?,?,?)", r)

conn.commit()
print("Sukces! Baza moje_dane.db zostala utworzona i zasilona danymi z plikow CSV.")
conn.close()
