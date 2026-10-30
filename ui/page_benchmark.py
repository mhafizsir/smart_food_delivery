"""Halaman Benchmark."""
import altair as alt
import pandas as pd
import streamlit as st

from core.benchmark import benchmark
from ui.common import page_header


def point_kind(note):
    if note.startswith("estimasi"):
        return "estimasi"
    return "diukur"


def benchmark_chart(frame, operation):
    data = frame[frame["Operasi"] == operation].copy()
    data["Waktu grafik"] = data["Waktu (ms)"].clip(lower=0.0001)  # skala log tidak bisa menggambar 0
    data["Jenis"] = data["Keterangan"].map(point_kind)
    base = alt.Chart(data).encode(
        x=alt.X("n:Q", scale=alt.Scale(type="log"), title="n (jumlah data)"),
        y=alt.Y("Waktu grafik:Q", scale=alt.Scale(type="log"), title="Waktu (ms)"),
        color=alt.Color("Struktur:N", legend=alt.Legend(orient="bottom")))
    lines = base.mark_line()
    points = base.mark_point(size=90, filled=True).encode(
        shape=alt.Shape("Jenis:N", scale=alt.Scale(domain=["diukur", "estimasi"], range=["circle", "cross"])),
        tooltip=["Struktur", "Kompleksitas", "n", "Waktu (ms)", "Keterangan"])
    return (lines + points).properties(height=280)


def page_benchmark():
    page_header("Benchmark", "Mengukur struktur buatan sendiri dengan data acak (seed tetap), n = 1.000, 10.000, 100.000. "
               "Berjalan 10 sampai 20 detik.")
    if st.button("Jalankan benchmark", type="primary"):
        with st.spinner("Mengukur waktu, mohon tunggu..."):
            st.session_state["benchmark_rows"] = benchmark()
    rows = st.session_state.get("benchmark_rows")
    if not rows:
        st.info("Belum ada hasil. Tekan tombol di atas.")
        return
    frame = pd.DataFrame(rows)
    st.dataframe(frame, hide_index=True)
    for operation in frame["Operasi"].unique():
        st.subheader(operation)
        st.altair_chart(benchmark_chart(frame, operation), use_container_width=True)
    st.caption("Titik silang = estimasi. O(n^2) di atas n=10.000 terlalu lama dijalankan, jadi waktunya dihitung "
               "dari hasil ukur n=10.000 dikali (n / 10.000)^2. Sumbu x dan y berskala log.")
