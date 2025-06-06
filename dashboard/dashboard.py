import pandas as pd
import plotly.express as px
import streamlit as st

def persentase_pengguna_sepeda_bulanan_all(df):
    df['dteday'] = pd.to_datetime(df['dteday'])
    df['bulan'] = df['dteday'].dt.to_period('M')
    pengguna_bulanan = df.groupby('bulan')['cnt'].sum()
    total_pengguna = pengguna_bulanan.sum()
    persentase_bulanan = (pengguna_bulanan / total_pengguna) * 100
    return persentase_bulanan

def puncak_penyewaan_sepeda_all(df):
    df['dteday'] = pd.to_datetime(df['dteday'])
    tahun_terakhir = df[df['dteday'] >= df['dteday'].max() - pd.DateOffset(years=1)]
    puncak = tahun_terakhir.groupby('dteday')['cnt'].sum().idxmax()
    return puncak

def create_rfm_df(df):
    rfm_df = df.groupby(by="weekday", as_index=False).agg({
        "dteday": "max",
        "instant": "nunique",
        "cnt": "sum"
    })
    rfm_df.columns = ["weekday", "max_order_timestamp", "frequency", "monetary"]
    rfm_df["max_order_timestamp"] = pd.to_datetime(rfm_df["max_order_timestamp"]).dt.date
    recent_date = df["dteday"].max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (pd.to_datetime(recent_date).date() - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    return rfm_df

all_df = pd.read_csv("https://raw.githubusercontent.com/Salwazd21/Proyek-ADP-Dicoding/refs/heads/main/dashboard/all_df.csv")
all_df["dteday"] = pd.to_datetime(all_df["dteday"])

with st.sidebar:
    st.title("Analisis Data PYTHON")
    st.image("https://raw.githubusercontent.com/Salwazd21/Progres-Belajar/main/logo.png")
    st.write("Proyek analisis data Coding Camp 2025")
    st.write("Salwa Zahrah Dasuki")

    filter_kategori = st.selectbox("Pilih Filter:", ["Semua", "Bulan", "Musim", "Cuaca","Tanggal"])

    if filter_kategori == "Bulan":
        all_df['bulan_str'] = all_df['dteday'].dt.strftime('%Y-%m')
        bulan_options = sorted(all_df['bulan_str'].unique())
        bulan_terpilih = st.multiselect("Pilih Bulan (bisa lebih dari satu):", bulan_options, default=bulan_options[:1])

        if bulan_terpilih:
            df_filtered = all_df[all_df['bulan_str'].isin(bulan_terpilih)]
        else:
            df_filtered = all_df.iloc[0:0]

    elif filter_kategori == "Musim":
        season_map = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
        all_df['season_str'] = all_df['season'].map(season_map)
        musim_terpilih = st.selectbox("Pilih Musim:", all_df['season_str'].unique())
        df_filtered = all_df[all_df['season_str'] == musim_terpilih]

    elif filter_kategori == "Cuaca":
        cuaca_map = {
            1: 'Clear, Few clouds',
            2: 'Mist + Cloudy',
            3: 'Light Snow or Rain',
            4: 'Heavy Rain or Snow'
        }
        all_df['cuaca_str'] = all_df['weathersit'].map(cuaca_map)
        cuaca_terpilih = st.selectbox("Pilih Cuaca:", all_df['cuaca_str'].unique())
        df_filtered = all_df[all_df['cuaca_str'] == cuaca_terpilih]
        
    elif filter_kategori == "Tanggal":
        min_date = all_df['dteday'].min().date()
        max_date = all_df['dteday'].max().date()
        start_date, end_date = st.date_input(
            "Pilih Rentang Tanggal:",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
            )
        
        if isinstance(start_date, tuple):
            start_date, end_date = start_date
        df_filtered = all_df[(all_df['dteday'].dt.date >= start_date) & (all_df['dteday'].dt.date <= end_date)]

    else:
        df_filtered = all_df.copy()

st.header("Hasil Analisis Data")

st.subheader("Persentase Pengguna Sepeda - 6 Bulan Terakhir")
all_df['bulan'] = all_df['dteday'].dt.to_period('M')
six_months = all_df['bulan'].sort_values().unique()[-6:]
df_last_6_months = all_df[all_df['bulan'].isin(six_months)]

pengguna_casual_6m = df_last_6_months['casual'].sum()
pengguna_registered_6m = df_last_6_months['registered'].sum()

if pengguna_casual_6m + pengguna_registered_6m > 0:
    fig_pie_6_months = px.pie(
        names=['Casual', 'Registered'],
        values=[pengguna_casual_6m, pengguna_registered_6m],
        title='Persentase Pengguna Sepeda (6 Bulan Terakhir)'
    )
    st.plotly_chart(fig_pie_6_months)
else:
    st.write("Tidak ada data untuk ditampilkan dalam 6 bulan terakhir.")

st.subheader("Puncak Penyewaan Sepeda - 1 Tahun Terakhir")
df_last_year = all_df[all_df['dteday'] >= all_df['dteday'].max() - pd.DateOffset(years=1)]
df_harian_last_year = df_last_year.groupby("dteday")["cnt"].sum().reset_index()
puncak_penyewaan = df_harian_last_year['cnt'].max()
fig_line_year = px.line(df_harian_last_year, x="dteday", y="cnt", title="Penyewaan Sepeda per Hari (1 Tahun Terakhir)")

st.write(f"Puncak Penyewaan Sepeda: {puncak_penyewaan} pada {df_harian_last_year.loc[df_harian_last_year['cnt'] == puncak_penyewaan, 'dteday'].values[0]}")
st.plotly_chart(fig_line_year)

tab1, tab2, tab3 = st.tabs(["Persentase Pengguna Sepeda", "Puncak Penyewaan Sepeda", "Distribusi"])
with tab1:
    st.subheader("Visualisasi Persentase Pengguna Sepeda")

    pengguna_casual = df_filtered['casual'].sum()
    pengguna_registered = df_filtered['registered'].sum()

    if pengguna_casual + pengguna_registered > 0:
        fig_pie = px.pie(
            names=['Casual', 'Registered'],
            values=[pengguna_casual, pengguna_registered],
            title='Persentase Pengguna Sepeda: Casual vs Registered'
        )
        st.plotly_chart(fig_pie)
    else:
        st.write("Tidak ada data untuk ditampilkan.")

with tab2:
    st.subheader("Visualisasi Puncak Penyewaan Sepeda")
    if not df_filtered.empty:
        df_harian = df_filtered.groupby("dteday")["cnt"].sum().reset_index()
        fig = px.line(df_harian, x="dteday", y="cnt", title="Jumlah Penyewaan Sepeda per Hari")
        st.plotly_chart(fig)
    else:
        st.write("Tidak ada data untuk ditampilkan.")

with tab3:
    st.subheader("Distribusi Jumlah Penyewaan Sepeda")
    if not df_filtered.empty:
        col1, col2 = st.columns(2)

        weekday_map = {0: 'Senin', 1: 'Selasa', 2: 'Rabu', 3: 'Kamis', 4: 'Jumat', 5: 'Sabtu', 6: 'Minggu'}
        df_filtered['hari'] = df_filtered['weekday'].map(weekday_map)
        df_by_hari = df_filtered.groupby('hari')['cnt'].sum().reindex(['Senin','Selasa','Rabu','Kamis','Jumat','Sabtu','Minggu']).reset_index()
        fig_hari = px.bar(df_by_hari, x='hari', y='cnt', title='Distribusi Penyewaan Berdasarkan Hari')
        col1.plotly_chart(fig_hari)

        cuaca_map = {
            1: 'Clear, Few clouds',
            2: 'Mist + Cloudy',
            3: 'Light Snow or Rain',
            4: 'Heavy Rain or Snow'
        }
        df_filtered['cuaca_str'] = df_filtered['weathersit'].map(cuaca_map)
        df_by_cuaca = df_filtered.groupby('cuaca_str')['cnt'].sum().reset_index()
        fig_cuaca = px.pie(df_by_cuaca, names='cuaca_str', values='cnt', title='Distribusi Penyewaan Berdasarkan Cuaca')
        col2.plotly_chart(fig_cuaca)
    else:
        st.write("Tidak ada data untuk ditampilkan.")