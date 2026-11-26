# 🛰️ Orange Pi IoT Telemetry & Air Traffic Analytics (End-to-End Project)

🌐 **Aplikacja webowa na żywo (Live Dashboard):** [Otwórz interaktywny dashboard w Streamlit](https://orangepi-iot-radar.streamlit.app/)

Kompleksowy projekt z pogranicza **Data Engineering, IoT (Edge Computing), Data Analytics oraz Machine Learning**, zrealizowany na mikrokomputerze **Orange Pi PC Plus** (Armbian Linux / Headless SSH). 

Projekt odwzorowuje pełny cykl życia danych: od automatycznego poboru z API i czujników systemowych, przez czyszczenie w Pythonie i hurtownię SQL, aż po model predykcyjny AI i publikację żywej aplikacji webowej.

---

## 🏗️ 1. Architektura Systemu i Infrastruktura (Edge & Cloud)

* **Serwer zbierający dane:** Orange Pi PC Plus (Linux bez środowiska graficznego, zarządzany zdalnie przez SSH).
* **Magazyn lokalny i sieciowy:** Pendrive zamontowany w `/mnt/python_skrypty/` udostępniony w sieci lokalnej przez serwer **Samba**.
* **Automatyzacja ETL i Backupu:** Harmonogram zadań `cron` uruchamiający cyklicznie skrypty Pythona (`pogoda.py`, `samoloty.py`, `zdrowie_serwera.py`, `kursy_walut.py`) oraz codzienny skrypt `auto_backup.sh` (`git pull --rebase` + `git push`) aktualizujący repozytorium GitHub.
* **Monitoring na żywo:** Lokalna baza **SQLite (`moje_dane.db`)** zasilająca 3 dashboardy czasu rzeczywistego w **Grafanie** (port `3000`) oraz publiczny dashboard w **Streamlit Community Cloud**.

### Zbierane źródła danych (`/dane`)
1. `historia_lotow.csv` – ruch lotniczy w promieniu 100 km od **Annopola** (API OpenSky Network: ICAO24, numer lotu, kraj pochodzenia, wysokość [m], prędkość [km/h], kurs).
2. `historia_pogody.csv` – warunki meteorologiczne (API Open-Meteo: temperatura, wilgotność, ciśnienie, prędkość wiatru) dla 3 miast: **Mińsk Mazowiecki** (lokalizacja serwera), **Annopol** (centrum radaru) oraz **Kraków**.
3. `historia_smogu.csv` – jakość powietrza (pyły zawieszone PM2.5, PM10).
4. `historia_zdrowia.csv` – telemetria sprzętowa Orange Pi PC Plus (`Temp_CPU_C`, `RAM_Uzyty_MB`).
5. `historia_walut.csv` – notowania kursów walut z API NBP.

---

## ✅ 2. Zrealizowane Moduły Projektu

- [x] **Moduł 0: Wersjonowanie i Automatyzacja (Git & GitHub)** – konfiguracja repozytorium, tokenów dostępu, struktury folderów oraz w pełni zautomatyzowanego backupu z Orange Pi (`cron` + `auto_backup.sh`).
- [x] **Moduł 1: Czyszczenie Danych i Eksploracja Statystyczna (Python / Pandas / Seaborn)** – wykrycie zakłóceń transponderów ADS-B, analiza korelacji i weryfikacja danych ze zewnętrznymi radarami (`analiza/01_eksploracja_i_czyszczenie.ipynb`).
- [x] **Moduł 2: Hurtownia Danych i Zaawansowany SQL (SQLite)** – agregacja czasowa, eliminacja błędu *fan-out* przy złączeniach, `CASE WHEN`, `CTE (WITH)` oraz funkcje okna `RANK() OVER`, `LAG() OVER` i średnia krocząca `AVG() OVER` (`analiza/02_zaawansowany_sql.ipynb`).
- [x] **Moduł 3: Modelowanie i Predykcja (Machine Learning / Scikit-Learn)** – klasyfikacja profilu operacji lotniczych z wykorzystaniem algorytmu `RandomForestClassifier` z wynikiem **90.5% skuteczności** (`analiza/03_machine_learning_predykcja.ipynb`).
- [x] **Moduł 4: Interaktywna Aplikacja Webowa (Streamlit + Plotly)** – wdrożenie publicznego dashboardu z dynamicznymi filtrami i automatycznym odświeżaniem danych z repozytorium (`app.py`).

---

## 📊 3. Kluczowe Odkrycia i Wnioski z Danych

### 🛠️ Moduł 1: Data Quality, Weryfikacja Radarowa i Korelacje
* **Wykrycie anomalii transponderów:** Analiza `df.describe()` wykazała, że 98,2% lotów mieści się w realnych granicach (mediana **787.0 km/h**), natomiast 12 rekordów zawierało zakłócenia radiowe powyżej 1200 km/h (np. `8 262 km/h`). Zastosowano filtr domenowy (`Predkosc_kmh <= 1200`), odrzucając 12 uszkodzonych pakietów bez sztucznego zniekształcania reszty zbioru.
* **Weryfikacja ze zewnętrznymi bazami lotniczymi:** Próbkę lotów zweryfikowano z publicznymi danymi FlightAware/Flightradar24 – m.in. rejs **`LOT3TD`** (potwierdzony lot LOT LO438 Barcelona–Warszawa zniżający na wysokości 4 572 m na 19 minut przed lądowaniem na Okęciu) oraz tranzytowy **`MSC791`** (Air Cairo na pułapie 11 285 m).
* **Korelacja ruch vs pułap (`r = -0.53`):** Wzrost liczby samolotów nad Annopolem obniża średnią wysokość przelotu z ~11 000 m (nocny tranzyt) do 6 000–7 500 m (włączenie się ruchu regionalnego startującego i lądującego w Warszawie, Radomiu, Lublinie i Rzeszowie).
* **Telemetria Orange Pi (`r = +0.48`):** Temperatura procesora w mieszkaniu w Mińsku Mazowieckim wykazuje umiarkowaną dodatnią korelację z temperaturą zewnętrzną (od ~41°C przy -2°C na zewnątrz do ~45°C przy +6°C), ze skokami do 47.6°C podczas wykonywania zadań `cron`.

### 🗄️ Moduł 2: Wnioski z Zaawansowanego SQL
* **Dobowy cykl ruchu lotniczego (`CASE WHEN`):** Szczyt operacji na niskim pułapie (< 6 km) przypada na godziny popołudniowe (12:00–17:00), natomiast w nocy (23:00–05:00) średni pułap rośnie powyżej 10 000 m.
* **Nocna zmiana na niebie (`CTE` + `RANK() OVER`):** W ciągu dnia dominują maszyny zarejestrowane w **Polsce**, **Węgrzech** i na **Malcie** (LOT, Wizz Air, Ryanair), natomiast w nocy (23:00–05:00) na pierwsze miejsce pod względem liczby przelotów wysuwa się **Turcja** (32 maszyny) oraz **Egipt** (13 maszyn) obsługujące korytarze tranzytowe północ–południe.
* **Rozwiązanie problemu *fan-out* przy `JOIN`:** Wykryto powielanie wierszy przy łączeniu telemetrii CPU z pogodą o różnej częstotliwości zapisu i wyeliminowano je poprzez wstępną agregację godzinową w `CTE` przed wykonaniem `INNER JOIN` oraz funkcji `LAG()`.

### 🤖 Moduł 3: Machine Learning (`RandomForestClassifier`)
* Zbudowano model klasyfikujący, czy dany samolot wykonuje **przelot tranzytowy (>= 9 km)**, czy **operację wznoszenia/zniżania (< 9 km)** bez dostępu do wskazań wysokościomierza – wyłącznie na podstawie prędkości, kursu, pory dnia oraz pogody w Annopolu.
* **Wynik:** Model osiągnął **90.5% skuteczności (Accuracy)** na zbiorze testowym (67 trafień na 74 loty), samodzielnie identyfikując kluczową rolę aerodynamiki: **prędkość przelotowa (65% wagi cechy)** oraz **kurs geograficzny (15% wagi)** okazały się najważniejszymi predyktorami profilu lotu.

---

## 📂 Struktura Repozytorium

```text
├── analiza/
│   ├── 01_eksploracja_i_czyszczenie.ipynb   # Moduł 1: EDA, czyszczenie CSV, korelacje i wykresy
│   ├── 02_zaawansowany_sql.ipynb            # Moduł 2: SQLite, CTE, RANK, LAG, AVG OVER
│   └── 03_machine_learning_predykcja.ipynb  # Moduł 3: Random Forest Classifier (90.5% accuracy)
├── dane/                                    # Automatycznie aktualizowane pliki CSV z Orange Pi
├── skrypty/                                 # Skrypty zbierające dane na Orange Pi PC Plus
├── app.py                                   # Moduł 4: Interaktywny dashboard webowy Streamlit
├── auto_backup.sh                           # Skrypt bash automatyzujący synchronizację z GitHub
├── requirements.txt                         # Zależności dla chmury Streamlit
└── README.md                                # Dokumentacja projektu
```
