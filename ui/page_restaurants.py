"""Halaman Restoran & Menu (Team 1)."""
import streamlit as st

from ui.common import flash_and_rerun, menu_table, page_header, restaurant_table, show_table


def restaurant_tab(service, locations):
    form_column, list_column = st.columns([1, 2], gap="large")
    with list_column:
        show_table(restaurant_table(service.restaurants, service.map), "Belum ada restoran.")
    with form_column:
        with st.form("add_restaurant", clear_on_submit=True):
            st.subheader("Registrasi restoran")
            restaurant_id = st.text_input("ID restoran")
            name = st.text_input("Nama")
            location = st.selectbox("Lokasi (titik di peta)", locations)
            category = st.text_input("Kategori")
            if st.form_submit_button("Tambah restoran", type="primary"):
                flash_and_rerun(service.add_restaurant(restaurant_id, name, location or "", category))
        if len(service.restaurants):
            with st.container(border=True):
                delete_restaurant_panel(service)


def delete_restaurant_panel(service):
    st.subheader("Hapus restoran")
    labels = {r.id: f"{r.id} - {r.name}" for r in service.restaurants}
    restaurant_id = st.selectbox("Restoran yang dihapus", list(labels), format_func=labels.get)
    menu_count = 0
    for m in service.menus:
        if m.restaurant_id == restaurant_id:
            menu_count += 1
    pending = service.orders.find_all(lambda o: o.restaurant_id == restaurant_id and o.status == "PENDING")
    if pending:
        st.warning(f"Masih ada {len(pending)} order PENDING. Proses atau batalkan dulu "
                   "sebelum restoran bisa dihapus.")
    else:
        st.info(f"{menu_count} menu ikut terhapus. Order yang sudah selesai/dibatalkan tetap "
                "tersimpan di history.")
    confirmed = st.checkbox("Saya yakin ingin menghapus", key=f"confirm_delete_{restaurant_id}")
    if st.button("Hapus restoran", disabled=not confirmed):
        flash_and_rerun(service.delete_restaurant(restaurant_id))


def menu_tab(service):
    restaurant_labels = {r.id: f"{r.id} - {r.name}" for r in service.restaurants}
    if not restaurant_labels:
        st.info("Tambahkan restoran dulu.")
        return
    form_column, list_column = st.columns([1, 2], gap="large")
    with list_column:
        show_table(menu_table(service, service.menus), "Belum ada menu.")
    with form_column:
        with st.form("add_menu", clear_on_submit=True):
            st.subheader("Tambah menu")
            menu_id = st.text_input("ID menu")
            restaurant_id = st.selectbox("Restoran", list(restaurant_labels), format_func=restaurant_labels.get)
            name = st.text_input("Nama menu")
            category = st.text_input("Kategori")
            price = st.number_input("Harga", min_value=1, value=10000, step=1000)
            if st.form_submit_button("Tambah menu", type="primary"):
                flash_and_rerun(service.add_menu(menu_id, restaurant_id, name, category, int(price)))
        if len(service.menus):
            edit_menu_form(service)


def edit_menu_form(service):
    labels = {m.id: f"{m.id} - {m.name}" for m in service.menus}
    with st.container(border=True):
        st.subheader("Ubah / hapus menu")
        selected = st.selectbox("Pilih menu", list(labels), format_func=labels.get)
    menu = service.find_menu(selected)
    with st.form(f"edit_menu_{menu.id}"):
        name = st.text_input("Nama", menu.name)
        category = st.text_input("Kategori", menu.category)
        price = st.number_input("Harga", min_value=1, value=menu.price, step=1000)
        available = st.checkbox("Tersedia", menu.available)
        save, delete = st.columns(2)
        if save.form_submit_button("Simpan perubahan"):
            flash_and_rerun(service.update_menu(menu.id, name, category, int(price), available))
        if delete.form_submit_button("Hapus menu"):
            flash_and_rerun(service.delete_menu(menu.id))


def keyword_tab(service):
    st.caption("Pencarian UTS: linear search O(n) pada ID, nama, kategori, dan lokasi.")
    keyword = st.text_input("Cari kata kunci")
    if not keyword.strip():
        return
    restaurants, menus = service.search_keyword(keyword)
    st.write("Restoran")
    show_table(restaurant_table(restaurants, service.map), "Restoran tidak ditemukan.")
    st.write("Menu")
    show_table(menu_table(service, menus), "Menu tidak ditemukan.")


def page_restaurants():
    service = st.session_state.service
    page_header("Restoran & Menu", "Daftarkan restoran dan kelola menunya.")
    tab_restaurant, tab_menu, tab_search = st.tabs(["Restoran", "Menu", "Cari kata kunci"])
    with tab_restaurant:
        restaurant_tab(service, service.map.nodes())
    with tab_menu:
        menu_tab(service)
    with tab_search:
        keyword_tab(service)
