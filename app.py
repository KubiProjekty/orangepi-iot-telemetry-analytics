import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Orange Pi IoT & Radar Dashboard", page_icon="🛰️", layout="wide")

st.title("🛰️ Orange Pi IoT Telemetry & Air Traffic Dashboard")
st.markdown("Interaktywny podgląd danych zbieranych w czasie rzeczywistym przez **Orange Pi PC Plus** (Mińsk Mazowiecki / Radar Annopol).")

base_url = "https://githubusercontent.com"

@st.cache_data(ttl=300)
def wczytaj_dane():
    loty = pd.read_csv(base_url + "historia_lotow.csv")
    pogoda = pd.read_csv(base_url + "historia_pogody.csv")
    zdrowie = pd.read_csv(base_url + "historia_zdrowia.csv")
    
    loty['Data'] = pd.to_datetime(loty['Data'])
    pogoda['Data'] = pd.to_datetime(pogoda['Data'])
    zdrowie['Data'] = pd.to_datetime(zdrowie['Data'])
    
    # Filtrujemy błędy transpondera (> 1200 km/h)
    loty = loty[loty['Predkosc_kmh'] <= 1200].copy()
    return loty, pogoda, zdrowie

df_loty, df_pogoda, df_zdrowie = wczytaj_dane()

# Panel boczny z filtrami
st.sidebar.header("🎛️ Filtry analizy")
wybrane_kraje = st.sidebar.multiselect(
    "Kraj rejestracji samolotu:",
    options=sorted(df_loty['Kraj_Pochodzenia'].dropna().unique()),
    default=["Poland", "Turkey", "Hungary", "Malta"]
)
max_wysokosc = st.sidebar.slider("Maksymalna wysokość lotu [m]:", 0, 14000, 14000, step=500)

loty_filtr = df_loty[(df_loty['Kraj_Pochodzenia'].isin(wybrane_kraje)) & (df_loty['Wysokosc_m'] <= max_wysokosc)]

# Górne kafelki KPI
col1, col2, col3, col4 = st.columns(4)
col1.metric("✈️ Wybrane przeloty", len(loty_filtr))
col2.metric("📏 Średnia wysokość", f"{loty_filtr['Wysokosc_m'].mean():.0f} m" if len(loty_filtr) else "0 m")
col3.metric("⚡ Średnia prędkość", f"{loty_filtr['Predkosc_kmh'].mean():.0f} km/h" if len(loty_filtr) else "0 km/h")
col4.metric("🌡️ Ostatnia temp. CPU", f"{df_zdrowie['Temp_CPU_C'].iloc[-1]:.1f} °C")

st.divider()

# Wykresy interaktywne
c1, c2 = st.columns(2)

with c1:
    st.subheader("Profil wysokości i prędkości lotów")
    fig1 = px.scatter(
        loty_filtr, x="Predkosc_kmh", y="Wysokosc_m", color="Kraj_Pochodzenia",
        hover_data=["Numer_Lotu", "Data"], labels={"Predkosc_kmh": "Prędkość [km/h]", "Wysokosc_m": "Wysokość [m]"}
    )
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    st.subheader("Temperatura procesora Orange Pi w czasie")
    fig2 = px.line(
        df_zdrowie, x="Data", y="Temp_CPU_C", markers=True,
        labels={"Data": "Czas pomiaru", "Temp_CPU_C": "Temp. CPU [°C]"}
    )
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("📋 Ostatnie zarejestrowane przeloty")
st.dataframe(loty_filtr.sort_values("Data", ascending=False).head(15), use_container_width=True)
