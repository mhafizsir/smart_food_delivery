"""Halaman Antrean & Delivery (Team 2)."""
import pandas as pd
import streamlit as st

from core.models import PRIORITY_STREAK_LIMIT
from ui.common import PRIORITY_BADGE, flash, flash_and_rerun, order_label, page_header, rupiah, show_table
from ui.diagrams import show_heap


def queue_table(orders):
    """Versi ringkas tabel order, supaya muat di setengah lebar halaman."""
    rows = []
    for position, order in enumerate(orders, start=1):
        rows.append({"Urutan": position, "ID": order.id, "Customer": order.customer, "Menu": order.menu_name,
                     "Qty": order.qty, "Total": rupiah(order.total)})
    return pd.DataFrame(rows)


def streak_panel(service):
    limit = PRIORITY_STREAK_LIMIT
    q1, q2 = st.columns([1, 3])
    q1.metric("Kuota prioritas berturut-turut", f"{min(service.priority_streak, limit)} / {limit}")
    if service._normal_turn():
        q2.warning(f"Sudah {service.priority_streak} order URGENT/HIGH berturut-turut: "
                   "giliran order NORMAL dulu supaya tidak antre terus.")
    else:
        q2.caption(f"Setelah {limit} order URGENT/HIGH berturut-turut, 1 order NORMAL yang menunggu "
                   "dilayani dulu (anti-starvation). Kuota kembali ke 0 setiap order NORMAL diproses.")


def process_next(service):
    order, error = service.process_delivery()
    if error:
        flash(error)
    else:
        extra = ""
        if order.route:
            extra = f", {order.distance_km:g} km, ETA {order.eta_min:g} menit"
        flash(f"Sukses: Order #{order.id} ({order.priority}) diantar{extra}.")
    st.rerun()


def cancel_panel(service):
    st.subheader("Batalkan order")
    pending = service.orders.find_all(lambda o: o.status == "PENDING")
    if not pending:
        st.info("Tidak ada order PENDING.")
        return
    labels = {o.id: order_label(o) for o in pending}
    order_id = st.selectbox("Order PENDING", list(labels), format_func=labels.get)
    if st.button("Batalkan"):
        flash_and_rerun(service.cancel_order(order_id))


def page_queue():
    service = st.session_state.service
    page_header("Antrean & Delivery", "Order diproses sesuai prioritas: URGENT, lalu HIGH, lalu NORMAL.")
    next_order = service.next_order()
    with st.container(border=True):
        info, process, undo = st.columns([3, 1, 1], vertical_alignment="center")
        info.caption("Order berikutnya")
        if next_order:
            info.markdown(f"**{order_label(next_order)}**")
            info.badge(next_order.priority, color=PRIORITY_BADGE[next_order.priority])
        else:
            info.markdown("**Antrean kosong.**")
        if process.button("Proses order", type="primary", use_container_width=True):
            process_next(service)
        if undo.button("Undo aksi terakhir", use_container_width=True):
            flash_and_rerun(service.undo())
    streak_panel(service)

    left, right = st.columns(2)
    with left:
        st.subheader("URGENT / HIGH (min-heap)")
        st.caption("Urutan proses: key (prioritas, ID) terkecil keluar duluan.")
        show_table(queue_table(service.priority_queue.in_order()), "Antrean prioritas kosong.")
    with right:
        st.subheader("NORMAL (FIFO queue)")
        st.caption(f"Dilayani minimal 1 order setiap {PRIORITY_STREAK_LIMIT} order prioritas.")
        show_table(queue_table(service.normal_queue), "Antrean normal kosong.")

    st.subheader("Isi heap")
    show_heap(service.priority_queue)
    cancel_panel(service)
