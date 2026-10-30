"""Halaman Riwayat & Undo."""
import pandas as pd
import streamlit as st

from ui.common import flash_and_rerun, order_table, page_header, show_table


def reload_from_db(service):
    service.load()
    return "Sukses: Data dimuat ulang dari database."


def undo_rows(service):
    rows = []
    for rank, action in enumerate(service.actions, start=1):
        order = action["order"]
        rows.append({"Posisi": rank, "Aksi": action["type"], "Order": f"#{order.id}",
                     "Customer": order.customer, "Status order": order.status})
    return rows


def page_orders():
    service = st.session_state.service
    page_header("Riwayat & Undo", "Semua order, riwayat order selesai atau batal, dan aksi yang bisa dibatalkan.")
    tab_all, tab_history, tab_search, tab_undo, tab_db = st.tabs(
        ["Semua order", "History", "Cari customer", "Undo", "Database"])
    with tab_all:
        st.caption("Traversal singly linked list dari head ke tail.")
        show_table(order_table(service.orders), "Belum ada order.")
    with tab_history:
        st.caption("History stack: order DONE/CANCELLED, yang terbaru di atas.")
        show_table(order_table(service.history), "Riwayat kosong.")
    with tab_search:
        customer = st.text_input("Nama customer")
        if customer.strip():
            show_table(order_table(service.orders_by_customer(customer)), "Order tidak ditemukan.")
    with tab_undo:
        st.caption("Undo stack (LIFO): aksi terakhir di atas, itu yang dibatalkan oleh tombol Undo.")
        show_table(pd.DataFrame(undo_rows(service)), "Stack undo kosong.")
        if st.button("Undo aksi terakhir", key="undo_history"):
            flash_and_rerun(service.undo())
    with tab_db:
        counts = service.check_db()
        cols = st.columns(len(counts))
        for col, (table, count) in zip(cols, counts.items()):
            col.metric(f"Baris {table}", count)
        if st.button("Muat ulang dari database"):
            flash_and_rerun(reload_from_db(service))
