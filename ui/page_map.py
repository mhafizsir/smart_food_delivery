"""Halaman Peta & Rute (Team 2)."""
import pandas as pd
import streamlit as st

from core.models import LOCATION_KINDS
from ui.common import flash_and_rerun, page_header, rupiah, show_table, warn_recursion
from ui.map_view import path_km, show_map


def map_order_mode(service):
    routed = service.orders.find_all(lambda o: o.route)
    if not routed:
        st.info("Belum ada order dengan lokasi antar.")
        return None
    labels = {o.id: f"#{o.id} {o.customer}: {o.restaurant_name} -> {o.delivery_location} ({o.status})"
              for o in routed}
    order_id = st.selectbox("Order", list(labels), format_func=labels.get)
    order = service.find_order(order_id)
    m = st.container(border=True).columns(4)
    m[0].metric("Jarak", f"{order.distance_km:g} km")
    m[1].metric("Estimasi waktu", f"{order.eta_min:g} menit")
    m[2].metric("Ongkir", rupiah(order.delivery_fee))
    m[3].metric("Status", order.status)
    return order.route


def map_search_mode(service, names):
    if len(names) < 2:
        st.info("Butuh minimal 2 lokasi untuk mencari rute.")
        return None
    c1, c2 = st.columns(2)
    start = c1.selectbox("Dari", names)
    end = c2.selectbox("Ke", names, index=len(names) - 1)
    route, error = service.route_between(start, end)
    try:
        reachable = service.map.dfs(start)
    except RecursionError:
        warn_recursion()
        reachable = []
    if error:
        st.error(error)
    else:
        m = st.container(border=True).columns(3)
        m[0].metric("Jarak (Dijkstra)", f"{route['distance_km']:g} km")
        m[1].metric("Estimasi waktu", f"{route['eta_min']:g} menit")
        m[2].metric("Ongkir", rupiah(route["fee"]))
    transit = service.map.bfs_path(start, end)
    comparison = []
    if route:
        comparison.append({"Algoritma": "Dijkstra (jarak terpendek)", "Rute": " -> ".join(route["path"]),
                           "Ruas jalan": len(route["path"]) - 1, "Jarak (km)": route["distance_km"]})
    if transit:
        comparison.append({"Algoritma": "BFS (ruas jalan tersedikit)", "Rute": " -> ".join(transit),
                           "Ruas jalan": len(transit) - 1, "Jarak (km)": path_km(service.map, transit)})
    show_table(pd.DataFrame(comparison), "Tidak ada rute antara dua lokasi ini.")
    st.caption(f"DFS dari {start}: {len(reachable)} dari {len(names)} lokasi terjangkau "
               f"({', '.join(reachable)}).")
    return route["path"] if route else None


def map_edit_expander(service, names):
    with st.expander("Tambah lokasi atau jalan"):
        left, right = st.columns(2)
        with left.form("add_location", clear_on_submit=True):
            st.write("Lokasi baru (node)")
            name = st.text_input("Nama lokasi")
            lat = st.number_input("Latitude", value=-6.25, format="%.6f")
            lon = st.number_input("Longitude", value=106.80, format="%.6f")
            kind = st.selectbox("Tipe", list(LOCATION_KINDS))
            if st.form_submit_button("Simpan lokasi"):
                flash_and_rerun(service.add_location(name, lat, lon, kind))
        with right.form("add_road", clear_on_submit=True):
            st.write("Jalan baru (edge)")
            start = st.selectbox("Dari", names, key="road_from")
            end = st.selectbox("Ke", names, key="road_to")
            distance = st.number_input("Jarak km (0 = hitung dari koordinat)", min_value=0.0, value=0.0)
            minutes = st.number_input("Waktu menit (0 = dari kecepatan rata-rata)", min_value=0.0, value=0.0)
            if st.form_submit_button("Simpan jalan"):
                flash_and_rerun(service.add_road(start, end, distance or None, minutes or None))


def page_map():
    service = st.session_state.service
    page_header("Peta & Rute", "Lihat rute pengiriman order atau cari rute antar lokasi.")
    names = service.map.nodes()
    mode = st.radio("Tampilkan", ["Rute order", "Cari rute"], horizontal=True)
    if mode == "Rute order":
        path = map_order_mode(service)
    else:
        path = map_search_mode(service, names)
    if path:
        st.caption("Rute: " + " -> ".join(path))
    show_map(service, path, key="main_map")
    st.caption("Merah = restoran, biru = area customer, abu-abu = persimpangan, hijau = tujuan.")
    map_edit_expander(service, names)
    with st.expander("Daftar jalan (edge graph)"):
        rows = []
        for start, end, distance, minutes in service.map.edges():
            rows.append({"Dari": start, "Ke": end, "Jarak (km)": distance, "Waktu (menit)": minutes})
        show_table(pd.DataFrame(rows), "Belum ada jalan.")
