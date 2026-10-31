"""Halaman Cari & Katalog: cari ID (Hash Table), katalog harga (BST), urutkan dan cari nama (sorting + binary search). Team 1."""
import pandas as pd
import streamlit as st

from core.searching import binary_search, linear_search
from core.service import menu_name_key
from core.sorting import insertion_sort, merge_sort
from ui.common import menu_table, page_header, rupiah, show_table, warn_recursion
from ui.diagrams import bst_dot


def bucket_frame(table, searched=None):
    rows = []
    for i, keys in enumerate(table.buckets()):
        names = [str(key) for key in keys]
        row = {"Bucket": i, "Isi (chain)": " -> ".join(names) or "-", "Panjang": len(keys)}
        if searched is not None:
            row["Dicari"] = "<- di sini" if i == searched else ""
        rows.append(row)
    return pd.DataFrame(rows)


def id_tab(service):
    st.caption("Ketik ID untuk langsung menemukan restoran atau menu. Pencarian memakai Hash Table, rata-rata O(1).")
    c1, c2 = st.columns([1, 3])
    kind = c1.radio("Jenis", ["Restoran", "Menu"], horizontal=True)
    if kind == "Restoran":
        table = service.restaurant_index
        example = "R1"
    else:
        table = service.menu_index
        example = "M4"
    key = c2.text_input(f"ID {kind.lower()}", placeholder=f"contoh: {example}").strip()

    searched = None
    if key:
        searched = table.bucket_index(key)
        found = table.search(key)
        if found is None:
            st.warning(f"ID {key} tidak ditemukan. Sudah dicek di bucket {searched}.")
        elif kind == "Restoran":
            st.success(f"**{found.name}** ({found.id}), lokasi {found.location}, kategori {found.category}. "
                       f"Ditemukan di bucket {searched}.")
        else:
            st.success(f"**{found.name}** ({found.id}), {rupiah(found.price)}, restoran {found.restaurant_id}. "
                       f"Ditemukan di bucket {searched}.")

    st.subheader("Isi Hash Table")
    c = st.container(border=True).columns(4)
    c[0].metric("Jumlah data", len(table))
    c[1].metric("Jumlah bucket", table.capacity)
    c[2].metric("Load factor", f"{table.load_factor():.2f}")
    c[3].metric("Collision", table.collisions())
    st.caption(f"Bucket dihitung dari ID. Kalau dua ID jatuh di bucket yang sama (collision), keduanya disimpan "
               f"berantai di bucket itu (separate chaining). Kalau load factor melewati {table.MAX_LOAD_FACTOR}, "
               "jumlah bucket digandakan dan semua ID dihitung ulang (rehash).")
    st.dataframe(bucket_frame(table, searched), hide_index=True)


def catalog_tab(service):
    tree = service.menu_catalog
    if not len(tree):
        st.info("Belum ada menu.")
        return
    st.caption("Daftar menu dari yang termurah. Katalog disimpan di Binary Search Tree dengan harga sebagai key.")
    highest = max(m.price for m in service.menus)
    c1, c2 = st.columns(2)
    low = c1.number_input("Harga minimum", min_value=0, value=0, step=1000)
    high = c2.number_input("Harga maksimum", min_value=0, value=highest, step=1000)
    if low > high:
        st.warning("Harga minimum lebih besar dari maksimum.")
    try:
        in_range = service.menus_in_price_range(low, high)
    except RecursionError:
        warn_recursion()
        in_range = []
    st.write(f"{len(in_range)} menu di rentang {rupiah(low)} sampai {rupiah(high)}:")
    show_table(menu_table(service, in_range, with_restaurant_name=True), "Tidak ada menu di rentang harga ini.")

    st.subheader("Isi BST")
    m = st.container(border=True).columns(3)
    m[0].metric("Jumlah menu", len(tree))
    m[1].metric("Jumlah node", tree.node_count)
    try:
        height = tree.height()
    except RecursionError:
        warn_recursion()
        height = None
    m[2].metric("Tinggi tree", height)
    st.graphviz_chart(bst_dot(tree.root))
    st.caption("Setiap node berisi menu dengan harga yang sama. Harga lebih kecil ke kiri, lebih besar ke kanan.")

    order = st.radio("Urutan traversal", ["inorder", "preorder", "postorder"], horizontal=True)
    try:
        prices = []
        for menu in tree.traverse(order):
            if rupiah(menu.price) not in prices:
                prices.append(rupiah(menu.price))
        st.write(" → ".join(prices))
    except RecursionError:
        warn_recursion()
    st.caption("Inorder (kiri, node, kanan) selalu menghasilkan harga menaik. Preorder dimulai dari akar. "
               "Postorder berakhir di akar.")


def sorted_frame(service, menus):
    rows = []
    for position, m in enumerate(menus, start=1):
        restaurant = service.find_restaurant(m.restaurant_id)
        rows.append({"Posisi": position, "Nama": m.name, "Restoran": restaurant.name if restaurant else m.restaurant_id,
                     "Harga": rupiah(m.price)})
    return pd.DataFrame(rows)


def name_tab(service):
    st.caption("Urutkan menu berdasarkan nama, lalu cari satu menu dengan binary search.")
    algorithms = {"Merge sort, O(n log n)": merge_sort, "Insertion sort, O(n²)": insertion_sort}
    choice = st.radio("Algoritma pengurutan", list(algorithms), horizontal=True)
    menus = service.menus_sorted_by_name(algorithms[choice])
    show_table(sorted_frame(service, menus), "Belum ada menu.")
    st.caption("Kedua algoritma menghasilkan urutan yang sama. Bedanya ada di kecepatan, lihat halaman Benchmark.")

    name = st.text_input("Nama menu yang dicari", placeholder="contoh: Kopi Susu").strip()
    if not name:
        return
    target = name.casefold()
    sorted_index = binary_search(menus, target, key=menu_name_key)
    original_index = linear_search(service.menus.to_list(), target, key=menu_name_key)
    if sorted_index < 0:
        st.warning(f"Menu \"{name}\" tidak ditemukan. Nama harus sama persis (huruf besar/kecil tidak masalah).")
        return
    st.success(f"**{menus[sorted_index].name}** ditemukan.")
    c1, c2 = st.container(border=True).columns(2)
    c1.metric("Binary search", f"posisi {sorted_index + 1}")
    c1.caption("Di daftar terurut di atas. O(log n): setiap langkah membuang separuh daftar.")
    c2.metric("Linear search", f"posisi {original_index + 1}")
    c2.caption("Di Dynamic Array, urutan menu saat didaftarkan. O(n): dicek satu per satu dari awal.")


def page_search():
    service = st.session_state.service
    page_header("Cari & Katalog", "Cari restoran dan menu, lihat katalog harga, dan urutkan menu.")
    tab_id, tab_catalog, tab_name = st.tabs(["Cari berdasarkan ID", "Katalog harga", "Urutkan & cari nama"])
    with tab_id:
        id_tab(service)
    with tab_catalog:
        catalog_tab(service)
    with tab_name:
        name_tab(service)
