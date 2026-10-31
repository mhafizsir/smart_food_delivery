"""Halaman Dashboard (Team 3)."""
import pandas as pd
import streamlit as st

from core.seed import seed_demo_data, seed_demo_orders
from ui.common import flash_and_rerun, page_header, rupiah


def ranking_bars(ranking, name_label, value_label, empty_message):
    """Tabel ranking (sudah diurutkan merge sort di service) dengan batang di setiap baris."""
    if not ranking:
        st.info(empty_message)
        return
    rows = []
    for name, total in ranking:
        rows.append({name_label: name, value_label: total})
    biggest = ranking[0][1]
    bar = st.column_config.ProgressColumn(value_label, format="%d", min_value=0, max_value=biggest)
    st.dataframe(pd.DataFrame(rows), hide_index=True, column_config={value_label: bar})


def page_dashboard():
    service = st.session_state.service
    page_header("Dashboard", "Ringkasan order dan isi struktur data saat ini.")
    stats = service.statistics()
    cols = st.container(border=True).columns(5)
    cols[0].metric("Total order", stats["total"])
    cols[1].metric("Pending", stats["pending"])
    cols[2].metric("Selesai", stats["done"])
    cols[3].metric("Dibatalkan", stats["cancelled"])
    cols[4].metric("Pendapatan", rupiah(stats["sales"]), help="Dari order selesai, termasuk biaya prioritas dan ongkir.")
    st.caption("Angka di atas dihitung dengan fungsi rekursif (divide and conquer) dari Sub 5.")

    left, right = st.columns(2)
    with left:
        st.subheader("Order per restoran (semua status)")
        restaurants = service.top_restaurants(limit=len(stats["orders_per_restaurant"]))
        ranking_bars(restaurants, "Restoran", "Order", "Belum ada order.")
    with right:
        st.subheader("Menu terjual (porsi)")
        menus = service.top_menus(limit=len(stats["menus_sold"]))
        ranking_bars(menus, "Menu", "Porsi", "Belum ada order yang selesai.")

    st.subheader("Status sistem")
    box = st.container(border=True)
    c = box.columns(4)
    c[0].metric("Restoran", len(service.restaurants))
    c[1].metric("Menu", len(service.menus))
    c[2].metric("Lokasi / jalan", f"{len(service.map)} / {len(service.map.edges())}")
    c[3].metric("Order di linked list", len(service.orders))
    q = box.columns(4)
    q[0].metric("Antrean prioritas (heap)", len(service.priority_queue))
    q[1].metric("Antrean normal (queue)", len(service.normal_queue))
    q[2].metric("History (stack)", len(service.history))
    q[3].metric("Undo (stack)", len(service.actions))

    if st.button("Isi data contoh"):
        flash_and_rerun(f"{seed_demo_data(service)} {seed_demo_orders(service)}")
