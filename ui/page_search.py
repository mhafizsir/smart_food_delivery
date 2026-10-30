"""Halaman Cari & Katalog: Hash Table, BST, binary search (Team 1)."""
import pandas as pd
import streamlit as st

from core.searching import binary_search, linear_search
from core.sorting import insertion_sort, merge_sort
from ui.common import menu_table, page_header, rupiah, show_table, warn_recursion
from ui.diagrams import bst_dot


def hash_tab(service):
    kind = st.radio("Cari", ["Restoran", "Menu"], horizontal=True)
    if kind == "Restoran":
        table = service.restaurant_index
    else:
        table = service.menu_index
    key = st.text_input(f"ID {kind.lower()}").strip()
    if key:
        if kind == "Restoran":
            found = service.find_restaurant(key)
        else:
            found = service.find_menu(key)
        bucket = table.bucket_index(key)
        if found is None:
            st.warning(f"ID {key} tidak ditemukan (dicek di bucket {bucket}).")
        elif kind == "Restoran":
            st.success(f"Bucket {bucket}: {found.id} - {found.name} ({found.location}, {found.category})")
        else:
            st.success(f"Bucket {bucket}: {found.id} - {found.name}, {rupiah(found.price)} "
                       f"(restoran {found.restaurant_id})")
    c = st.container(border=True).columns(4)
    c[0].metric("Jumlah data", len(table))
    c[1].metric("Jumlah bucket", table.capacity)
    c[2].metric("Load factor", f"{table.load_factor():.2f}")
    c[3].metric("Collision", table.collisions())
    st.caption(f"Separate chaining. Kalau load factor melewati {table.MAX_LOAD_FACTOR}, jumlah bucket "
               "digandakan dan semua key di-rehash.")
    st.dataframe(bucket_frame(table), hide_index=True)


def bucket_frame(table):
    rows = []
    for i, keys in enumerate(table.buckets()):
        names = [str(key) for key in keys]
        rows.append({"Bucket": i, "Isi (chain)": " -> ".join(names) or "-", "Panjang": len(keys)})
    return pd.DataFrame(rows)


def bst_tab(service):
    tree = service.menu_catalog
    if not len(tree):
        st.info("Belum ada menu.")
        return
    prices = [m.price for m in service.menus]
    highest = max(prices)
    c1, c2 = st.columns(2)
    low = c1.number_input("Harga minimum", min_value=0, value=0, step=1000)
    high = c2.number_input("Harga maksimum", min_value=0, value=highest, step=1000)
    st.subheader("Menu di rentang harga")
    if low > high:
        st.warning("Harga minimum lebih besar dari maksimum.")
    try:
        in_range = service.menus_in_price_range(low, high)
    except RecursionError:
        warn_recursion()
        in_range = []
    show_table(menu_table(service, in_range, with_restaurant_name=True),
               "Tidak ada menu di rentang harga ini.")

    st.subheader("Traversal")
    order = st.radio("Urutan", ["inorder", "preorder", "postorder"], horizontal=True)
    try:
        traversed = tree.traverse(order)
    except RecursionError:
        warn_recursion()
        traversed = []
    show_table(menu_table(service, traversed, with_restaurant_name=True), "Belum ada menu.")
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
    st.caption("Key node = harga; menu berharga sama berbagi satu node. Inorder (kiri, akar, kanan) "
               "menghasilkan harga menaik. Rentang harga hanya mengunjungi subtree yang relevan.")


def binary_tab(service):
    algorithms = {"Insertion sort": insertion_sort, "Merge sort": merge_sort}
    choice = st.radio("Algoritma pengurutan", list(algorithms), horizontal=True)
    ids = [m.id for m in service.menus]
    sorted_ids = service.sorted_menu_ids(algorithms[choice])
    st.write("ID menu sebelum diurutkan (urutan Dynamic Array):", ", ".join(ids) or "-")
    st.write(f"ID menu setelah {choice.lower()}:", ", ".join(sorted_ids) or "-")
    target = st.text_input("ID menu yang dicari", key="binary_target").strip()
    if not target:
        return
    c1, c2 = st.container(border=True).columns(2)
    c1.metric("Binary search (data terurut)", binary_search(sorted_ids, target))
    c2.metric("Linear search (data asli)", linear_search(ids, target))
    st.caption("Index -1 berarti tidak ditemukan. Index berbeda karena daftarnya berbeda urutan. "
               "Binary search O(log n) butuh data terurut, linear search O(n) tidak.")


def page_search():
    service = st.session_state.service
    page_header("Cari & Katalog", "Cari restoran dan menu dengan Hash Table, BST, dan binary search.")
    tab_hash, tab_bst, tab_binary = st.tabs(["Hash Table", "BST", "Binary vs Linear"])
    with tab_hash:
        hash_tab(service)
    with tab_bst:
        bst_tab(service)
    with tab_binary:
        binary_tab(service)
