"""Smart Food Delivery & Order Management System (Kelompok 2). Jalankan: streamlit run app.py

Logika ada di paket core, halaman di paket ui. File ini hanya membuat service bersama,
memasang tampilan, dan menyusun menu navigasi."""
from pathlib import Path

import streamlit as st

from core.seed import create_service
from ui.common import show_flash
from ui.page_benchmark import page_benchmark
from ui.page_create_order import page_create_order
from ui.page_dashboard import page_dashboard
from ui.page_map import page_map
from ui.page_orders import page_orders
from ui.page_queue import page_queue
from ui.page_restaurants import page_restaurants
from ui.page_search import page_search
from ui.page_statistics import page_statistics
from ui.page_structures import page_structures
from ui.page_testing import page_testing

ASSETS = Path(__file__).parent / "assets"

st.set_page_config(page_title="Smart Food Delivery", page_icon="🛵", layout="wide")


@st.cache_resource
def get_service():
    # Satu service untuk semua pengunjung: satu database, tidak ada ID order yang bentrok antar sesi
    return create_service()


service = get_service()
st.session_state.service = service  # kerangka panduan (6.2) menyimpan service di session_state

st.logo(str(ASSETS / "logo.svg"), size="large")
st.markdown(f"<style>{(ASSETS / 'style.css').read_text()}</style>", unsafe_allow_html=True)

pages = {
    "Operasional": [
        st.Page(page_dashboard, title="Dashboard", icon=":material/space_dashboard:", url_path="dashboard",
                default=True),
        st.Page(page_create_order, title="Buat Order", icon=":material/add_shopping_cart:", url_path="buat-order"),
        st.Page(page_queue, title="Antrean & Delivery", icon=":material/delivery_dining:", url_path="antrean"),
        st.Page(page_map, title="Peta & Rute", icon=":material/map:", url_path="peta"),
        st.Page(page_orders, title="Riwayat & Undo", icon=":material/history:", url_path="riwayat"),
    ],
    "Restoran": [
        st.Page(page_restaurants, title="Restoran & Menu", icon=":material/storefront:", url_path="restoran"),
        st.Page(page_search, title="Cari & Katalog", icon=":material/search:", url_path="cari"),
        st.Page(page_statistics, title="Statistik & Ranking", icon=":material/leaderboard:", url_path="statistik"),
    ],
    "Struktur Data": [
        st.Page(page_structures, title="Visualisasi Struktur", icon=":material/account_tree:", url_path="struktur"),
        st.Page(page_benchmark, title="Benchmark", icon=":material/speed:", url_path="benchmark"),
        st.Page(page_testing, title="Testing", icon=":material/fact_check:", url_path="testing"),
    ],
}
page = st.navigation(pages, expanded=True)

with st.sidebar:
    st.caption(f"{len(service.restaurants)} restoran, {len(service.menus)} menu, {len(service.orders)} order")
    st.caption(f"Antrean: {len(service.priority_queue)} prioritas, {len(service.normal_queue)} normal")
show_flash()
page.run()
