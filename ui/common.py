"""Helper tampilan bersama semua halaman."""
import pandas as pd
import streamlit as st

from core.models import PRIORITY_FEE


NO_LOCATION = "(tanpa lokasi antar)"
PRIORITIES = ["NORMAL", "HIGH", "URGENT"]
PRIORITY_BADGE = {"URGENT": "red", "HIGH": "orange", "NORMAL": "green"}
PRIORITY_FILL = {"URGENT": "#F6D5D2", "HIGH": "#FBEBC4", "NORMAL": "#DCEBDF"}  # sambal, kunyit, daun
CHAIN_LIMIT = 15   # node linked list/queue/stack yang digambar sebelum diringkas dengan "..."
TREE_LIMIT = 31    # node heap/BST yang digambar; tree besar membuat graphviz sangat lambat
SLOT_LIMIT = 64    # slot Dynamic Array yang ditampilkan di tabel


def warn_recursion():
    # Traversal BST dan DFS rekursif: tree yang sangat miring atau graph berbentuk rantai panjang
    # bisa melewati batas rekursi Python. Pemanggil menangkap RecursionError lalu memanggil ini,
    # supaya halaman tidak crash
    st.warning("Struktur terlalu dalam untuk fungsi rekursif (batas rekursi Python, lihat docs/design.md Bagian 4).")


def flash(message):
    st.session_state["flash"] = message


def show_flash():
    message = st.session_state.pop("flash", None)
    if not message:
        return
    if message.startswith("Gagal"):
        st.error(message)
    elif message.startswith(("Tidak", "Aksi", "Antrean", "Data")):
        st.warning(message)
    else:
        st.success(message)


def flash_and_rerun(message):
    flash(message)
    st.rerun()


def page_header(title, subtitle):
    st.header(title)
    st.caption(subtitle)


def rupiah(value):
    return f"Rp{value:,}".replace(",", ".")  # format Indonesia: Rp41.500


def priority_label(priority):
    fee = PRIORITY_FEE[priority]
    return f"{priority} (+{rupiah(fee)})" if fee else priority


def show_table(frame, empty_message):
    if frame.empty:
        st.info(empty_message)
    else:
        st.dataframe(frame, hide_index=True)


def order_label(order):
    return f"#{order.id} {order.customer} - {order.menu_name} x{order.qty} ({order.priority})"


def order_table(orders):
    rows = []
    for o in orders:
        row = {
            "ID": o.id, "Customer": o.customer, "Restoran": o.restaurant_name, "Menu": o.menu_name,
            "Qty": o.qty, "Ongkir": rupiah(o.delivery_fee), "Total": rupiah(o.total),
            "Prioritas": o.priority, "Status": o.status, "Lokasi antar": o.delivery_location or "-",
            "Jarak": "-", "ETA": "-",
        }
        if o.distance_km is not None:
            row["Jarak"] = f"{o.distance_km:g} km"
            row["ETA"] = f"{o.eta_min:g} menit"
        rows.append(row)
    return pd.DataFrame(rows)


def restaurant_table(restaurants, graph):
    rows = []
    for r in restaurants:
        rows.append({
            "ID": r.id, "Nama": r.name, "Lokasi": r.location, "Kategori": r.category,
            "Ada di peta": graph.find(r.location) is not None,
        })
    return pd.DataFrame(rows)


def menu_table(service, menus, with_restaurant_name=False):
    rows = []
    for m in menus:
        restaurant = service.find_restaurant(m.restaurant_id)
        shown = m.restaurant_id
        if restaurant and with_restaurant_name:
            shown = restaurant.name
        rows.append({"ID": m.id, "Restoran": shown, "Nama": m.name, "Kategori": m.category,
                     "Harga": rupiah(m.price), "Tersedia": m.available})
    return pd.DataFrame(rows)
