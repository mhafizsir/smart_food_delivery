"""Halaman Buat Order (Team 2)."""
import streamlit as st

from core.models import PRIORITY_FEE
from ui.common import NO_LOCATION, PRIORITIES, flash, page_header, priority_label, rupiah
from ui.map_view import show_map


def cost_breakdown(subtotal, priority, route):
    fee = PRIORITY_FEE[priority]
    delivery = route["fee"] if route else 0
    c = st.container(border=True).columns(4)
    c[0].metric("Subtotal", rupiah(subtotal))
    c[1].metric("Biaya prioritas", rupiah(fee))
    c[2].metric("Ongkir", rupiah(delivery))
    c[3].metric("Total", rupiah(subtotal + fee + delivery))


def route_preview(service, restaurant_id, destination):
    """Gambar rute. Hasil: route kalau valid, None kalau tidak (order dengan lokasi antar tidak bisa dibuat)."""
    route, error = service.plan_route(restaurant_id, destination)
    if error:
        st.error(f"{error} Order dengan lokasi antar tidak bisa dibuat. "
                 f"Pilih '{NO_LOCATION}' atau tambahkan lokasi restoran di peta.")
        return None
    m1, m2 = st.container(border=True).columns(2)
    m1.metric("Jarak (Dijkstra)", f"{route['distance_km']:g} km")
    m2.metric("Estimasi waktu", f"{route['eta_min']:g} menit")
    st.caption("Rute: " + " -> ".join(route["path"]))
    show_map(service, route["path"], key="preview_map", height=380)
    return route


def page_create_order():
    service = st.session_state.service
    page_header("Buat Order", "Pilih menu, prioritas, dan lokasi antar. Ongkir dihitung dari rute terpendek.")
    if not len(service.restaurants):
        st.info("Belum ada restoran. Tambahkan dulu di halaman Restoran & Menu.")
        return
    labels = {}
    for r in service.restaurants:
        label = f"{r.name} ({r.location})"
        if not service.map.find(r.location):
            label += " - tidak ada di peta"
        labels[r.id] = label
    c1, c2 = st.columns(2)
    restaurant_id = c1.selectbox("Restoran", list(labels), format_func=labels.get)
    menus = [m for m in service.menus if m.restaurant_id == restaurant_id and m.available]
    menu_labels = {m.id: f"{m.name} - {rupiah(m.price)}" for m in menus}
    if menus:
        menu_id = c2.selectbox("Menu", list(menu_labels), format_func=menu_labels.get)
    else:
        menu_id = None
        c2.warning("Restoran ini belum punya menu yang tersedia.")
    customer = c1.text_input("Nama customer")
    qty = c2.number_input("Jumlah", min_value=1, value=1, step=1)
    priority = c1.selectbox("Prioritas", PRIORITIES, format_func=priority_label)
    destination = c2.selectbox("Lokasi antar", [NO_LOCATION] + service.map.nodes())
    insert_at = st.radio("Posisi di linked list", ["head", "tail"], horizontal=True,
                         help="Ada pointer tail, jadi insert di head maupun tail sama-sama O(1).")

    route = None
    has_destination = destination != NO_LOCATION
    if has_destination:
        route = route_preview(service, restaurant_id, destination)
    if menu_id:
        cost_breakdown(service.find_menu(menu_id).price * int(qty), priority, route)

    blocked = menu_id is None or (has_destination and route is None)
    if st.button("Buat order", type="primary", disabled=blocked):
        delivery_location = None
        if has_destination:
            delivery_location = destination
        order, error = service.create_order(customer, restaurant_id, menu_id, int(qty), priority,
                                            delivery_location, insert_at)
        if error:
            flash(error)
        else:
            extra = ""
            if order.route:
                extra = f", {order.distance_km:g} km, ETA {order.eta_min:g} menit"
            flash(f"Sukses: Order #{order.id} ({order.priority}) dibuat, total {rupiah(order.total)}{extra}.")
        st.rerun()
