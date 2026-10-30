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
# Setiap halaman dijalankan sendiri dengan service berisi data contoh dan dua order
PAGE_SCRIPT = """
import streamlit as st
from core.seed import create_service, seed_demo_data
from ui.{module} import {module}

if "service" not in st.session_state:
    service = create_service(":memory:")
    seed_demo_data(service)
    service.create_order("Ani", "R1", "M1", 2, "NORMAL", destination="Pondok Indah")
    service.create_order("Budi", "R2", "M4", 1, "URGENT")
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
