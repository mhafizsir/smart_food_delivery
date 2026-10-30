"""Halaman Statistik & Ranking (Team 3)."""
import pandas as pd
import streamlit as st

from ui.common import page_header, rupiah, show_table


def page_statistics():
    service = st.session_state.service
    page_header("Statistik & Ranking", "Menu terlaris dan restoran teramai, diurutkan dengan merge sort.")
    stats = service.statistics()
    c = st.container(border=True).columns(5)
    c[0].metric("Total order", stats["total"])
    c[1].metric("Pending", stats["pending"])
    c[2].metric("Selesai", stats["done"])
    c[3].metric("Dibatalkan", stats["cancelled"])
    c[4].metric("Pendapatan", rupiah(stats["sales"]), help="Dari order selesai, termasuk biaya prioritas dan ongkir.")
    st.caption("Dihitung dengan recursive_sum dan recursive_group (divide and conquer, kedalaman O(log n)).")
    left, right = st.columns(2)
    with left:
        st.subheader("Menu terlaris")
        menu_rows = []
        for rank, (name, total) in enumerate(service.top_menus(), start=1):
            menu_rows.append({"Peringkat": rank, "Menu": name, "Porsi terjual": total})
        show_table(pd.DataFrame(menu_rows), "Belum ada order yang selesai.")
    with right:
        st.subheader("Restoran dengan order terbanyak (semua status)")
        restaurant_rows = []
        for rank, (name, total) in enumerate(service.top_restaurants(), start=1):
            restaurant_rows.append({"Peringkat": rank, "Restoran": name, "Jumlah order": total})
        show_table(pd.DataFrame(restaurant_rows), "Belum ada order.")
    st.caption("Ranking diurutkan dengan merge sort buatan sendiri, O(n log n).")
