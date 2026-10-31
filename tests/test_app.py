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
from ui.{module} import {module}

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
from ui.common import show_flash
from ui.page_dashboard import page_dashboard

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
