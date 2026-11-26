# 🛰️ Orange Pi IoT Telemetry & Air Traffic Analytics (End-to-End Project)

Kompleksowy projekt z pogranicza **Data Engineering, IoT (Edge Computing) oraz Data Analytics**, realizowany na mikrokomputerze **Orange Pi PC Plus** (Armbian Linux / Headless SSH). 

Projekt odwzorowuje pełny cykl życia danych (od fizycznego poboru z API i czujników systemowych, przez czyszczenie w Pythonie i hurtownię SQL, aż po wizualizację BI i predykcję ML) w oparciu o program nowoczesnego bootcampu analitycznego.

---

## 🏗️ 1. Architektura Systemu i Infrastruktura (Edge & Cloud)

* **Serwer zbierający dane:** Orange Pi PC Plus (Linux bez środowiska graficznego, zarządzany zdalnie przez SSH).
* **Magazyn lokalny i sieciowy:** Pendrive zamontowany w `/mnt/python_skrypty/` udostępniony w sieci lokalnej przez serwer **Samba**.
* **Automatyzacja ETL i Backupu:** Harmonogram zadań `cron` uruchamiający cyklicznie skrypty Pythona (`pogoda.py`, `samoloty.py`, `zdrowie_serwera.py`, `kursy_walut.py`) oraz codzienny skrypt `auto_backup.sh` wypychający zaktualizowane pliki CSV do repozytorium GitHub.
* **Monitoring na żywo:** Lokalna baza **SQLite (`moje_dane.db`)** zasilająca 3 dashboardy czasu rzeczywistego w **Grafanie** (port `3000`).
* **Środowisko analityczne:** Google Colab (Jupyter Notebooks) połączone bezpośrednio z repozytorium GitHub.

### Zbierane źródła danych (`/dane`)
1. `historia_lotow.csv` – ruch lotniczy w promieniu 100 km od **Annopola** (API OpenSky Network: ICAO24, numer lotu, kraj pochodzenia, wysokość [m], prędkość [km/h], kurs).
2. `historia_pogody.csv` – warunki meteorologiczne (API Open-Meteo: temperatura, wilgotność, ciśnienie, prędkość wiatru) dla 3 lokalizacji: **Mińsk Mazowiecki** (lokalizacja serwera), **Annopol** (centrum strefy radarowej) oraz **Kraków** (punkt odniesienia na południu Polski).
3. `historia_smogu.csv` – jakość powietrza (pyły zawieszone PM2.5, PM10) dla badanych lokalizacji.
4. `historia_zdrowia.csv` – telemetria sprzętowa Orange Pi PC Plus (temperatura procesora `Temp_CPU_C`, zużycie pamięci `RAM_Uzyty_MB`).
5. `historia_walut.csv` – notowania kursów walut z API NBP.

---

## 🗺️ 2. Mapa Drogowa Projektu (Plan Bootcampu w Praktyce)

- [x] **Moduł 0: Wersjonowanie i Automatyzacja (Git & GitHub)** – konfiguracja repozytorium, tokenów dostępu, struktury folderów oraz automatycznego backupu z Orange Pi (`cron` + `auto_backup.sh`).
- [x] **Moduł 1: Czyszczenie Danych i Eksploracja Statystyczna (Python / Pandas / Seaborn)** – wykrycie błędów transponderów, imputacja/filtrowanie, agregacja czasowa, analiza korelacji i weryfikacja danych ze źródłami zewnętrznymi.
- [ ] **Moduł 2: Hurtownia Danych i Zaawansowany SQL (SQLite / BigQuery)** – zapytania z wykorzystaniem `JOIN`, `CASE WHEN`, `CTE (WITH)` oraz `Window Functions` (`RANK`, `LAG`, średnia krocząca `AVG OVER`).
- [ ] **Moduł 3: Modelowanie i Predykcja (Machine Learning / Scikit-Learn)** – prognozowanie temperatury procesora Orange Pi oraz wpływu warunków pogodowych na natężenie ruchu lotniczego i smog.
- [ ] **Moduł 4: Wizualizacja Biznesowa i Aplikacja Webowa (Power BI + Streamlit)** – model gwiazdy, miary `DAX (CALCULATE)`, zrzuty z Grafany oraz interaktywny dashboard w Streamlit.

---

## 📊 3. Podsumowanie Dotychczasowych Wyników (Moduł 1 – EDA)

Pełny kod oraz wykresy znajdują się w notatniku: [`analiza/01_eksploracja_i_czyszczenie.ipynb`](analiza/01_eksploracja_i_czyszczenie.ipynb).

### 🛠️ Czyszczenie danych i wykrycie anomalii (*Data Quality*)
* Podczas analizy statystycznej (`df.describe()`) dla 676 rekordów lotniczych wykryto, że mediana prędkości wynosi **787.0 km/h** (75. percentyl: **833.2 km/h**), natomiast pojedyncze rekordy osiągały absurdalne wartości (np. **8 262 km/h** dla rejsu `BLX730F` czy **4 122 km/h** dla `RYR2RT`).
* **Diagnoza:** Skrypt przeliczający jednostki z API (`m/s * 3.6`) działał poprawnie, jednak pojedyncze pakiety z transponderów ADS-B zawierały zakłócenia radiowe.
* **Rozwiązanie:** Zamiast sztucznie przeliczać dane, zastosowano filtr domenowy (`Predkosc_kmh <= 1200`), odrzucając **12 uszkodzonych rekordów (1,8%)** i zachowując **664 w 100% wiarygodne przeloty**.

### ✈️ Weryfikacja wiarygodności danych ze zewnętrznymi radarami
Próbkę oczyszczonych rekordów z dnia `2026-11-15 (21:22)` zweryfikowano w publicznych rejestrach lotniczych (FlightAware / Flightradar24):
* **`LOT3TD` (Poland) | Wysokość: 4 572 m | Prędkość: 667 km/h** – potwierdzony rejs **LOT LO438 (Barcelona – Warszawa)** na 19 minut przed planowym lądowaniem na Okęciu (faza zniżania w zasięgu radaru Annopol).
* **`MSC791` (Egypt) | Wysokość: 11 285 m | Prędkość: 468 km/h** – potwierdzony rejs tranzytowy linii **Air Cairo** na standardowym pułapie przelotowym.
* **`RYR8RF` (Ireland) | Wysokość: 5 959 m | Prędkość: 738 km/h** – potwierdzony rejs linii **Ryanair** w fazie wznoszenia/zniżania na trasie krajowej/regionalnej.

### 🔍 Kluczowe wnioski statystyczne (Korelacje)
1. **Ruch lotniczy vs Wysokość przelotu nad Annopolem (`r = -0.53`, silna korelacja ujemna):** 
   W godzinach małego ruchu (2–10 samolotów/h, głównie nocą) średni pułap wynosi **~11 000 m** (ruch tranzytowy). W godzinach szczytu (20–35 samolotów/h) średnia wysokość spada do **6 000–7 500 m**, ponieważ do ruchu dołączają samoloty startujące i lądujące na pobliskich lotniskach (Warszawa, Radom, Lublin, Rzeszów).
2. **Temperatura CPU Orange Pi vs Pogoda w Mińsku Mazowieckim (`r = +0.48`, umiarkowana korelacja dodatnia):** 
   Mimo pracy serwera wewnątrz mieszkania, wzrost temperatury zewnętrznej (z -2°C do +6°C) przekłada się na wzrost temperatury procesora (z ~41°C do ~44–45°C), z pojedynczymi skokami do **47.6°C** podczas cyklicznego uruchamiania zadań `cron`.
3. **Wykrycie korelacji pozornej (*Spurious Correlation*):** 
   Zidentyfikowano silną ujemną korelację między zużyciem RAM a ciśnieniem atmosferycznym (`r = -0.89`), wynikającą z krótkiego okna czasowego próby (jednostajny spadek ciśnienia zbiegł się w czasie ze wzrostem *uptime* systemu), co udokumentowano jako przestrogę przed nadinterpretacją krótkich szeregów czasowych.

---

## 📂 Struktura Repozytorium

```text
├── analiza/
│   └── 01_eksploracja_i_czyszczenie.ipynb   # Moduł 1: EDA, czyszczenie CSV, korelacje i wykresy
├── dane/                                    # Automatycznie aktualizowane pliki CSV z Orange Pi
│   ├── historia_lotow.csv
│   ├── historia_pogody.csv
│   ├── historia_smogu.csv
│   ├── historia_walut.csv
│   └── historia_zdrowia.csv
├── skrypty/                                 # Produkcyjne skrypty Pythona działające na Orange Pi
│   ├── kursy_walut.py
│   ├── migracja_sql.py
│   ├── pogoda.py
│   ├── samoloty.py
│   └── zdrowie_serwera.py
├── auto_backup.sh                           # Skrypt bash automatyzujący git push z crona
└── README.md                                # Dokumentacja projektu i dziennik postępów
```
