from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")
PAGES = [
    ("page_dashboard", "Dashboard"), ("page_create_order", "Buat Order"), ("page_queue", "Antrean & Delivery"),
    ("page_map", "Peta & Rute"), ("page_orders", "Riwayat & Undo"), ("page_restaurants", "Restoran & Menu"),
    ("page_search", "Cari & Katalog"), ("page_statistics", "Statistik & Ranking"),
    ("page_structures", "Visualisasi Struktur"), ("page_benchmark", "Benchmark"), ("page_testing", "Testing"),
]
# Setiap halaman dijalankan sendiri dengan service berisi data contoh dan order demo
PAGE_SCRIPT = """
import streamlit as st
from core.seed import create_service, seed_demo_data, seed_demo_orders
from views.{module} import {module}

if "service" not in st.session_state:
    service = create_service(":memory:")
    seed_demo_data(service)
    seed_demo_orders(service)
    st.session_state.service = service
{module}()
"""


def test_app_opens_dashboard():
    app = AppTest.from_file(APP, default_timeout=120).run()
    assert [e.value for e in app.exception] == []
    assert app.header[0].value == "Dashboard"


@pytest.mark.parametrize("module, title", PAGES)
def test_page_renders(module, title):
    app = AppTest.from_string(PAGE_SCRIPT.format(module=module), default_timeout=120).run()
    assert [e.value for e in app.exception] == []
    assert app.header[0].value == title


EMPTY_DASHBOARD = """
import streamlit as st
from core.seed import create_service
from views.common import show_flash
from views.page_dashboard import page_dashboard

if "service" not in st.session_state:
    st.session_state.service = create_service(":memory:")
show_flash()
page_dashboard()
"""


def test_dashboard_button_fills_demo_data_and_orders():
    app = AppTest.from_string(EMPTY_DASHBOARD, default_timeout=120).run()
    [button] = [b for b in app.button if b.label == "Isi data contoh"]
    app = button.click().run()
    assert [e.value for e in app.exception] == []
    assert app.success[0].value == "Sukses: 14 data contoh ditambahkan. Sukses: 10 order contoh ditambahkan."
    service = app.session_state.service
    assert (len(service.restaurants), len(service.menus), len(service.orders)) == (4, 10, 10)


def rerun(app):
    # Bug AppTest 1.50: nilai segmented_control mode single (string) dibaca per huruf saat rerun.
    # Mengisinya ulang sebagai list sebelum setiap rerun menghindari ValueError tersebut.
    for group in app.button_group:
        if isinstance(group.value, str):
            group.set_value([group.value])
    return app.run()


def open_section(app, name):
    app.button_group[0].set_value([name])
    return app.run()


def type_into(app, label, text):
    for box in app.text_input:
        if box.label == label:
            box.input(text)
    return rerun(app)


def test_search_page_finds_restaurant_by_id_and_menus_by_name_prefix():
    app = AppTest.from_string(PAGE_SCRIPT.format(module="page_search"), default_timeout=120).run()
    app = open_section(app, "Cari berdasarkan ID")
    app = type_into(app, "ID restoran", "R1")
    assert app.success[0].value == "**Warung Nusantara** (R1), lokasi Blok M, kategori Indonesian. Ditemukan di bucket 7."
    app = open_section(app, "Urutkan & cari nama")
    app = type_into(app, "Cari nama menu", "SATE")
    assert app.success[0].value == "2 menu ditemukan: Sate Ayam, Sate Kambing."
    app = type_into(app, "Cari nama menu", "pizza")
    assert app.warning[0].value == 'Tidak ada menu yang namanya diawali "pizza".'
