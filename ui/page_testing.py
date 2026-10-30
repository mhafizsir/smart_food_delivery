"""Halaman Testing."""
import pandas as pd
import streamlit as st

from core.scenarios import run_test_scenarios
from ui.common import page_header


def page_testing():
    page_header("Testing", "Setiap skenario memakai service baru dengan database :memory:, jadi data asli tidak tersentuh.")
    skip_slow = st.checkbox("lewati tes performa (lebih cepat)")
    if st.button("Jalankan tes", type="primary"):
        with st.spinner("Menjalankan skenario..."):
            st.session_state["test_rows"] = run_test_scenarios(skip_slow=skip_slow)
    rows = st.session_state.get("test_rows")
    if not rows:
        st.info("Belum ada hasil. Tekan tombol di atas.")
        return
    counts = {"LULUS": 0, "GAGAL": 0, "MANUAL": 0}
    for row in rows:
        counts[row["Hasil"]] += 1
    columns = st.columns(3)
    for column, label in zip(columns, counts):
        column.metric(label, counts[label])
    st.dataframe(pd.DataFrame(rows), hide_index=True)
