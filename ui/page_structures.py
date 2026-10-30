"""Halaman Visualisasi Struktur."""
import pandas as pd
import streamlit as st

from ui.common import SLOT_LIMIT, page_header, rupiah, show_table, warn_recursion
from ui.diagrams import action_node, bst_dot, order_node, show_chain, show_heap
from ui.page_search import bucket_frame


def slot_frame(array, describe):
    rows = []
    for i in range(min(array.capacity, SLOT_LIMIT)):
        item = array._data[i]
        text = "(kosong)"
        if item is not None:
            text = describe(item)
        rows.append({"Slot": i, "Isi": text})
    return pd.DataFrame(rows)


def show_array(title, array, describe):
    st.markdown(f"**{title}**")
    c = st.columns(2)
    c[0].metric("Terisi (len)", len(array))
    c[1].metric("Kapasitas", array.capacity)
    st.dataframe(slot_frame(array, describe), hide_index=True)
    if array.capacity > SLOT_LIMIT:
        st.caption(f"Menampilkan {SLOT_LIMIT} slot pertama dari {array.capacity}.")


def graph_frame(graph):
    rows = []
    for name, edges in graph.adjacency.items():
        neighbors = []
        for edge in edges:
            neighbors.append(f"{edge['to']} ({edge['distance']:g})")
        rows.append({"Lokasi": name, "Tipe": graph.kinds.get(name, "-"),
                     "Tetangga (km)": ", ".join(neighbors) or "-"})
    return pd.DataFrame(rows)


def show_hash_table(column, title, table):
    column.markdown(f"**{title}**: {len(table)} data, {table.capacity} bucket, "
                    f"load factor {table.load_factor():.2f}, collision {table.collisions()}")
    column.dataframe(bucket_frame(table), hide_index=True)


def page_structures():
    service = st.session_state.service
    page_header("Visualisasi Struktur", "Isi nyata semua struktur data buatan sendiri, dibaca langsung dari service yang sedang berjalan.")

    st.subheader("1. Dynamic Array (restoran dan menu)")
    st.caption("Kapasitas digandakan saat penuh: append O(1) amortized, akses index O(1), hapus di tengah O(n).")
    left, right = st.columns(2)
    with left:
        show_array("Array restoran", service.restaurants, lambda r: f"{r.id} {r.name}")
    with right:
        show_array("Array menu", service.menus, lambda m: f"{m.id} {m.name} ({rupiah(m.price)})")

    st.subheader("2. Singly Linked List (semua order)")
    st.caption("Ada pointer head dan tail: insert di head atau tail O(1), search dan hapus O(n).")
    show_chain(service.orders, order_node, "HEAD", "TAIL", "Belum ada order.", end_null=True)

    st.subheader("3. Stack (history dan undo)")
    st.caption("LIFO: push, pop, dan peek O(1). Panah mengarah dari puncak ke dasar.")
    left, right = st.columns(2)
    with left:
        st.markdown("**History** (puncak = order selesai/batal terbaru)")
        show_chain(service.history, order_node, "TOP", "BOTTOM", "History kosong.", rankdir="TB")
    with right:
        st.markdown("**Undo** (puncak = aksi terakhir)")
        show_chain(service.actions, action_node, "TOP", "BOTTOM", "Stack undo kosong.", rankdir="TB")

    st.subheader("4. Linked Queue (antrean NORMAL)")
    st.caption("FIFO: enqueue di rear dan dequeue di front, keduanya O(1).")
    show_chain(service.normal_queue, order_node, "FRONT", "REAR", "Antrean normal kosong.")

    st.subheader("5. Min-Heap (antrean URGENT / HIGH)")
    st.caption("Array biner: push dan pop O(log n), peek O(1). Anak index i ada di 2i+1 dan 2i+2.")
    show_heap(service.priority_queue)

    st.subheader("6. Hash Table (indeks ID restoran dan menu)")
    st.caption("Separate chaining: search, insert, delete rata-rata O(1), terburuk O(n).")
    left, right = st.columns(2)
    show_hash_table(left, "Restoran", service.restaurant_index)
    show_hash_table(right, "Menu", service.menu_index)

    st.subheader("7. Binary Search Tree (katalog menu per harga)")
    st.caption("Key = harga. Insert, delete, search rata-rata O(log n), terburuk O(n) kalau tree miring.")
    tree = service.menu_catalog
    if len(tree):
        st.graphviz_chart(bst_dot(tree.root))
        try:
            height = tree.height()
        except RecursionError:
            warn_recursion()
            height = None
        st.caption(f"{len(tree)} menu, {tree.node_count} node, tinggi {height}.")
    else:
        st.info("Belum ada menu.")

    st.subheader("8. Graph (peta lokasi)")
    st.caption("Adjacency list: memori O(V + E). Dijkstra O((V + E) log V), BFS dan DFS O(V + E).")
    show_table(graph_frame(service.map), "Peta masih kosong.")
