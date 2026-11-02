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


def section_picker(sections, key):
    """Pengganti st.tabs. Pilihan disimpan di session_state, jadi setelah rerun (misalnya setelah mengetik
    di kotak pencarian) halaman tetap di bagian yang sama. st.tabs kadang kembali ke tab pertama."""
    last = key + "_last"
    if key not in st.session_state:
        st.session_state[key] = sections[0]

    def keep_one_selected():
        # Mengklik bagian yang sedang aktif membuat pilihan kosong; kembalikan ke bagian terakhir
        if st.session_state[key] is None:
            st.session_state[key] = st.session_state.get(last, sections[0])
        st.session_state[last] = st.session_state[key]

    return st.segmented_control("Bagian", sections, key=key, on_change=keep_one_selected,
                                label_visibility="collapsed")


def page_header(title, subtitle):
    st.header(title)
    st.caption(subtitle)


def rupiah(value):
    return f"Rp{value:,}".replace(",", ".")  # format Indonesia: Rp41.500


def priority_label(priority):
    fee = PRIORITY_FEE[priority]
    return f"{priority} (+{rupiah(fee)})" if fee else priority


# Kolom ini berisi angka asli, supaya klik judul kolom mengurutkan sebagai angka (Rp5.000 sebelum Rp15.000).
# Format Rupiah, km, dan menit hanya ditambahkan saat ditampilkan.
MONEY_COLUMNS = ("Harga", "Ongkir", "Total")


def km_text(value):
    return f"{value:g} km"


def minutes_text(value):
    return f"{value:g} menit"


UNIT_COLUMNS = {"Jarak": km_text, "ETA": minutes_text}


def show_table(frame, empty_message):
    if frame.empty:
        st.info(empty_message)
        return
    formats = {}
    widths = {}
    for column in frame.columns:
        if column in MONEY_COLUMNS:
            formats[column] = rupiah
        elif column in UNIT_COLUMNS:
            formats[column] = UNIT_COLUMNS[column]
        if column in formats:
            # Lebar kolom dihitung dari angka asli, jadi diberi lebar tetap supaya teks "Rp22.000" tidak terpotong
            widths[column] = st.column_config.Column(width=100)
    st.dataframe(frame.style.format(formats, na_rep="-"), hide_index=True, column_config=widths)


def order_label(order):
    return f"#{order.id} {order.customer} - {order.menu_name} x{order.qty} ({order.priority})"


def order_table(orders):
    rows = []
    for o in orders:
        rows.append({
            "ID": o.id, "Customer": o.customer, "Restoran": o.restaurant_name, "Menu": o.menu_name,
            "Qty": o.qty, "Ongkir": o.delivery_fee, "Total": o.total,
            "Prioritas": o.priority, "Status": o.status, "Lokasi antar": o.delivery_location or "-",
            "Jarak": o.distance_km, "ETA": o.eta_min,
        })
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
                     "Harga": m.price, "Tersedia": m.available})
    return pd.DataFrame(rows)
