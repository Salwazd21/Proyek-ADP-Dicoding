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

datetime_columns = ["dteday"]
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

persentase_bulanan_all = persentase_pengguna_sepeda_bulanan_all(all_df)
puncak_all = puncak_penyewaan_sepeda_all(all_df)
rfm_all = create_rfm_df(all_df)

st.title("Analisis Data PYTHON")
st.image("https://raw.githubusercontent.com/Salwazd21/Progres-Belajar/main/logo.png")
st.write("Proyek analisis data Coding Camp 2025")
st.write("Salwa Zahrah Dasuki")

st.header("Hasil Analisis Data")

tab1, tab2, tab3 = st.tabs(["Persentase Pengguna Sepeda Bulanan", "Puncak Penyewaan Sepeda", "Analisis RFM"])

with tab1:
    st.subheader("Visualisasi Persentase Pengguna Sepeda Bulanan")
    if not persentase_bulanan_all.empty:
        persentase_bulanan_str = pd.DataFrame({
            'bulan': persentase_bulanan_all.index.strftime('%Y-%m'),
            'persentase': persentase_bulanan_all.values
        })
        fig_persentase = px.line(persentase_bulanan_str, x='bulan', y='persentase', title="Tren Persentase Pengguna Sepeda Bulanan")
        st.plotly_chart(fig_persentase)
    else:
        st.write("Tidak ada data untuk ditampilkan.")

with tab2:
    st.subheader("Visualisasi Puncak Penyewaan Sepeda")
    if not all_df.empty:
        fig_puncak = px.bar(all_df.groupby("dteday")["cnt"].sum(), title="Jumlah Penyewaan Sepeda per Hari")
        st.plotly_chart(fig_puncak)
    else:
        st.write("Tidak ada data untuk ditampilkan.")

with tab3:
    st.subheader("Analisis RFM")
    if not rfm_all.empty:
        col1, col2, col3 = st.columns(3)
        fig_rfm_recency = px.histogram(rfm_all, x="recency", title="Distribusi Recency")
        col1.plotly_chart(fig_rfm_recency)
        fig_rfm_frequency = px.histogram(rfm_all, x="frequency", title="Distribusi Frequency")
        col2.plotly_chart(fig_rfm_frequency)
        fig_rfm_monetary = px.histogram(rfm_all, x="monetary", title="Distribusi Monetary")
        col3.plotly_chart(fig_rfm_monetary)
    else:
        st.write("Tidak ada data untuk ditampilkan.")