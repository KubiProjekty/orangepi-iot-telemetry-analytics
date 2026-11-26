import requests
import sqlite3
from datetime import datetime

teraz = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
url_eur = "https://" + "api." + "nbp.pl" + "/api/exchangerates/rates/a/eur/?format=json"
url_usd = "https://" + "api." + "nbp.pl" + "/api/exchangerates/rates/a/usd/?format=json"

eur = requests.get(url_eur, timeout=10).json()["rates"][0]["mid"]
usd = requests.get(url_usd, timeout=10).json()["rates"][0]["mid"]

with open("/mnt/python_skrypty/historia_walut.csv", "a", encoding="utf-8") as f:
    f.write(f"{teraz},{eur},{usd}\n")

conn = sqlite3.connect("/mnt/python_skrypty/moje_dane.db")
conn.execute("INSERT INTO waluty VALUES (?,?,?)", (teraz, eur, usd))
conn.commit()
conn.close()
print(f"{teraz} | Zapisano waluty: EUR={eur}, USD={usd}")
