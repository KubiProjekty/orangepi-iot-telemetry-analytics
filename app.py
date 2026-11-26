import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Orange Pi IoT & Radar Dashboard", page_icon="🛰️", layout="wide")

st.title("🛰️ Orange Pi IoT Telemetry & Air Traffic Dashboard")
st.markdown("Interaktywny podgląd danych zbieranych w czasie rzeczywistym przez **Orange Pi PC Plus** (Mińsk Mazowiecki / Annopol / Kraków).")

base_url = "https://raw" + chr(46) + "githubusercontent" + chr(46) + "com/KubiProjekty/orangepi-iot-telemetry-analytics/main/dane/"

@st.cache_data(ttl=300)
def wczytaj_dane():
    loty = pd.read_csv(base_url + "historia_lotow.csv")
    pogoda = pd.read_csv(base_url + "historia_pogody.csv")
    smog = pd.read_csv(base_url + "historia_smogu.csv")
    zdrowie = pd.read_csv(base_url + "historia_zdrowia.csv")
    
    for df in [loty, pogoda, smog, zdrowie]:
        df['Data'] = pd.to_datetime(df['Data']); df['Miasto'] = df['Miasto'].astype(str).str.replace('_', ' ') if 'Miasto' in df.columns else None
        
    loty = loty[loty['Predkosc_kmh'] <= 1200].copy()
    return loty, pogoda, smog, zdrowie

df_loty, df_pogoda, df_smog, df_zdrowie = wczytaj_dane()

tab1, tab2 = st.tabs(["✈️ Radar Lotniczy & Orange Pi", "🌤️ Pogoda & Smog (3 Miasta)"])

# === ZAKŁADKA 1: LOTY I TELEMETRIA CPU ===
with tab1:
    st.sidebar.header("🎛️ Filtry radaru lotniczego")
    wybrane_kraje = st.sidebar.multiselect(
        "Kraj rejestracji samolotu:",
        options=sorted(df_loty['Kraj_Pochodzenia'].dropna().unique()),
        default=["Poland", "Turkey", "Hungary", "Malta"]
    )
    max_wysokosc = st.sidebar.slider("Maksymalna wysokość lotu [m]:", 0, 14000, 14000, step=500)

    loty_filtr = df_loty[(df_loty['Kraj_Pochodzenia'].isin(wybrane_kraje)) & (df_loty['Wysokosc_m'] <= max_wysokosc)]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("✈️ Wybrane przeloty", len(loty_filtr))
    col2.metric("📏 Średnia wysokość", f"{loty_filtr['Wysokosc_m'].mean():.0f} m" if len(loty_filtr) else "0 m")
    col3.metric("⚡ Średnia prędkość", f"{loty_filtr['Predkosc_kmh'].mean():.0f} km/h" if len(loty_filtr) else "0 km/h")
    col4.metric("🌡️ Ostatnia temp. CPU", f"{df_zdrowie['Temp_CPU_C'].iloc[-1]:.1f} °C")

    st.divider()
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

# === ZAKŁADKA 2: POGODA I SMOG (ODWZOROWANIE GRAFANY) ===
with tab2:
    st.subheader("🌡️ Aktualne warunki pogodowe i jakość powietrza (ostatni odczyt)")
    ostatnia_pogoda = df_pogoda.sort_values("Data").groupby("Miasto").last().reset_index()
    ostatni_smog = df_smog.sort_values("Data").groupby("Miasto").last().reset_index()
    
    cols = st.columns(len(ostatnia_pogoda))
    for idx, row in ostatnia_pogoda.iterrows():
        miasto = row['Miasto']
        pm25_wiersz = ostatni_smog[ostatni_smog['Miasto'] == miasto]
        pm25_val = f" | Smog PM2.5: {pm25_wiersz['PM2_5'].values[0]:.1f} µg/m³" if len(pm25_wiersz) and 'PM2_5' in pm25_wiersz else ""
        with cols[idx]:
            st.metric(
                label=f"📍 {miasto}",
                value=f"{row['Temp_C']:.1f} °C",
                delta=f"Wiatr: {row['Wiatr_kmh']} km/h | {row['Cisnienie_hPa']} hPa{pm25_val}",
                delta_color="off"
            )

    st.divider()
    g1, g2 = st.columns(2)
    with g1:
        st.subheader("Temperatura w miastach w czasie [°C]")
        fig_temp = px.line(df_pogoda, x="Data", y="Temp_C", color="Miasto", markers=True)
        st.plotly_chart(fig_temp, use_container_width=True)
    with g2:
        st.subheader("Statystyki temperatur: Średnia / Min / Max")
        stat_temp = df_pogoda.groupby("Miasto")['Temp_C'].agg(['min', 'mean', 'max']).reset_index().melt(id_vars='Miasto', var_name='Miara', value_name='Temp_C')
        fig_bar = px.bar(stat_temp, x="Miasto", y="Temp_C", color="Miara", barmode="group")
        st.plotly_chart(fig_bar, use_container_width=True)

    if 'PM2_5' in df_smog.columns:
        st.subheader("🌫️ Stężenie pyłu zawieszonego PM2.5 w czasie [µg/m³]")
        fig_smog = px.line(df_smog, x="Data", y="PM2_5", color="Miasto", markers=True)
        st.plotly_chart(fig_smog, use_container_width=True)
