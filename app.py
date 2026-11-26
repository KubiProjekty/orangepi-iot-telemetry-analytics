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
        df['Data'] = pd.to_datetime(df['Data'])
        if 'Miasto' in df.columns:
            df['Miasto'] = df['Miasto'].astype(str).str.replace('_', ' ')
        
    loty = loty[loty['Predkosc_kmh'] <= 1200].copy()
    return loty, pogoda, smog, zdrowie

df_loty, df_pogoda, df_smog, df_zdrowie = wczytaj_dane()

# === WSPÓLNY FILTR CZASU NA PASKU BOCZNYM (DLA OBU ZAKŁADEK) ===
st.sidebar.header("⏱️ Zakres czasu (obie zakładki)")
zakres = st.sidebar.selectbox(
    "Pokaż dane z okresu:",
    ["Wszystkie dane", "Ostatnie 3 godziny", "Ostatnie 12 godzin", "Ostatnie 24 godziny", "Ostatnie 3 dni"],
    index=0
)

def filtruj_czas(df):
    if zakres == "Wszystkie dane" or len(df) == 0:
        return df
    ostatni_czas = df['Data'].max()
    godziny = {"Ostatnie 3 godziny": 3, "Ostatnie 12 godzin": 12, "Ostatnie 24 godziny": 24, "Ostatnie 3 dni": 72}[zakres]
    return df[df['Data'] >= ostatni_czas - pd.Timedelta(hours=godziny)]

df_loty_czas = filtruj_czas(df_loty)
df_pogoda_czas = filtruj_czas(df_pogoda)
df_smog_czas = filtruj_czas(df_smog)
df_zdrowie_czas = filtruj_czas(df_zdrowie)

st.sidebar.divider()
st.sidebar.header("✈️ Filtry radaru lotniczego")
wybrane_kraje = st.sidebar.multiselect(
    "Kraj rejestracji samolotu:",
    options=sorted(df_loty['Kraj_Pochodzenia'].dropna().unique()),
    default=["Poland", "Turkey", "Hungary", "Malta"]
)
zakres_wys = st.sidebar.slider("Zakres wysokości lotu [m]:", 0, 14000, (0, 14000), step=500)

st.sidebar.divider()
st.sidebar.header("🌤️ Filtry pogody i smogu")
wybrane_miasta = st.sidebar.multiselect(
    "Wybierz miasta:",
    options=sorted(df_pogoda['Miasto'].dropna().unique()),
    default=sorted(df_pogoda['Miasto'].dropna().unique())
)

tab1, tab2 = st.tabs(["✈️ Radar Lotniczy & Orange Pi", "🌤️ Pogoda & Smog (3 Miasta)"])

# === ZAKŁADKA 1: LOTY I TELEMETRIA CPU ===
with tab1:
    loty_filtr = df_loty_czas[
        (df_loty_czas['Kraj_Pochodzenia'].isin(wybrane_kraje)) & 
        (df_loty_czas['Wysokosc_m'].between(*zakres_wys))
    ]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("✈️ Wybrane przeloty", len(loty_filtr))
    col2.metric("📏 Średnia wysokość", f"{loty_filtr['Wysokosc_m'].mean():.0f} m" if len(loty_filtr) else "0 m")
    col3.metric("⚡ Średnia prędkość", f"{loty_filtr['Predkosc_kmh'].mean():.0f} km/h" if len(loty_filtr) else "0 km/h")
    col4.metric("🌡️ Ostatnia temp. CPU", f"{df_zdrowie_czas['Temp_CPU_C'].iloc[-1]:.1f} °C" if len(df_zdrowie_czas) else "Brak")

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
            df_zdrowie_czas, x="Data", y="Temp_CPU_C", markers=True,
            labels={"Data": "Czas pomiaru", "Temp_CPU_C": "Temp. CPU [°C]"}
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("📋 Ostatnie zarejestrowane przeloty")
    st.dataframe(loty_filtr.sort_values("Data", ascending=False).head(15), use_container_width=True)

# === ZAKŁADKA 2: POGODA I SMOG ===
with tab2:
    pogoda_filtr = df_pogoda_czas[df_pogoda_czas['Miasto'].isin(wybrane_miasta)]
    smog_filtr = df_smog_czas[df_smog_czas['Miasto'].isin(wybrane_miasta)]

    if len(pogoda_filtr) > 0:
        ostatnia_pogoda = pogoda_filtr.sort_values("Data").groupby("Miasto").last().reset_index()
        ostatni_smog = smog_filtr.sort_values("Data").groupby("Miasto").last().reset_index()
        
        st.subheader("🌡️ Aktualna Temperatura (°C)")
        cols_t = st.columns(len(ostatnia_pogoda))
        for idx, row in ostatnia_pogoda.iterrows():
            cols_t[idx].metric(label=row['Miasto'], value=f"{row['Temp_C']:.1f} °C")

        st.divider()
        g1, g2 = st.columns(2)
        with g1:
            st.subheader("Temperatura w miastach w czasie [°C]")
            fig_temp = px.line(pogoda_filtr, x="Data", y="Temp_C", color="Miasto", markers=True)
            st.plotly_chart(fig_temp, use_container_width=True)
        with g2:
            st.subheader("Statystyki temperatur: Średnia / Min / Max")
            stat_temp = pogoda_filtr.groupby("Miasto")['Temp_C'].agg(['min', 'mean', 'max']).reset_index().melt(id_vars='Miasto', var_name='Miara', value_name='Temp_C')
            fig_bar = px.bar(stat_temp, x="Miasto", y="Temp_C", color="Miara", barmode="group")
            st.plotly_chart(fig_bar, use_container_width=True)

        if 'PM2_5' in smog_filtr.columns and len(ostatni_smog) > 0:
            st.divider()
            st.subheader("🌫️ Aktualny Smog PM2.5 (µg/m³)")
            cols_s = st.columns(len(ostatni_smog))
            for idx, row in ostatni_smog.iterrows():
                cols_s[idx].metric(label=row['Miasto'], value=f"{row['PM2_5']:.1f} µg/m³")
                
            fig_smog = px.line(smog_filtr, x="Data", y="PM2_5", color="Miasto", markers=True)
            st.plotly_chart(fig_smog, use_container_width=True)

        st.divider()
        st.subheader("🔽 Aktualne Ciśnienie (hPa)")
        cols_p = st.columns(len(ostatnia_pogoda))
        for idx, row in ostatnia_pogoda.iterrows():
            cols_p[idx].metric(label=row['Miasto'], value=f"{row['Cisnienie_hPa']:.0f} hPa")

        st.subheader("💨 Aktualny Wiatr (km/h)")
        cols_w = st.columns(len(ostatnia_pogoda))
        for idx, row in ostatnia_pogoda.iterrows():
            cols_w[idx].metric(label=row['Miasto'], value=f"{row['Wiatr_kmh']:.1f} km/h")

        if 'Wilgotnosc_proc' in ostatnia_pogoda.columns:
            st.subheader("💧 Aktualna Wilgotność (%)")
            cols_h = st.columns(len(ostatnia_pogoda))
            for idx, row in ostatnia_pogoda.iterrows():
                cols_h[idx].metric(label=row['Miasto'], value=f"{row['Wilgotnosc_proc']:.0f} %")
    else:
        st.warning("Brak danych dla wybranych filtrów czasu lub miast.")
