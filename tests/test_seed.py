"""Tes data contoh: peta, restoran, menu, dan order demo."""
from core.seed import create_service, seed_demo_data, seed_demo_orders
from core.service import FoodDeliveryService
from core.sorting import insertion_sort


def demo_service(db_path=":memory:"):
    service = create_service(db_path)
    seed_demo_data(service)
    seed_demo_orders(service)
    return service


def statuses(service):
    result = {}
    for order in service.orders_array():
        result[order.customer] = order.status
    return result


def test_map_seed_has_locations_and_roads():
    service = create_service(":memory:")
    assert len(service.map) == 12
    assert len(service.map.edges()) == 17


def test_demo_restaurants_and_menus_only_added_once():
    service = create_service(":memory:")
    assert seed_demo_data(service) == "Sukses: 14 data contoh ditambahkan."
    assert seed_demo_data(service) == "Data contoh sudah ada."
    assert len(service.restaurants) == 4
    assert len(service.menus) == 10


def test_demo_orders_need_restaurants_first():
    service = create_service(":memory:")
    assert seed_demo_orders(service) == "Gagal: Restoran dan menu contoh belum ada. Isi data contoh dulu."
    assert len(service.orders) == 0


def test_demo_orders_have_every_status():
    service = demo_service()
    assert statuses(service) == {
        "Ani": "DONE", "Budi": "DONE", "Cici": "DONE", "Dodi": "CANCELLED", "Eka": "DONE",
        "Fajar": "PENDING", "Gita": "DONE", "Hana": "PENDING", "Indra": "PENDING", "Joko": "PENDING",
    }
    stats = service.statistics()
    assert (stats["total"], stats["pending"], stats["done"], stats["cancelled"]) == (10, 4, 5, 1)


def test_demo_orders_follow_priority_and_anti_starvation():
    service = demo_service()
    # URGENT Budi, URGENT Gita, HIGH Cici, lalu kuota 3 habis sehingga NORMAL Ani, lalu HIGH Eka
    assert [order.customer for order in service.history] == ["Eka", "Ani", "Cici", "Gita", "Budi", "Dodi"]
    assert [order.customer for order in service.priority_queue.in_order()] == ["Joko"]
    assert [order.customer for order in service.normal_queue] == ["Fajar", "Hana", "Indra"]
    assert service.next_order().customer == "Joko"


def test_demo_order_totals():
    service = demo_service()
    orders = {}
    for order in service.orders_array():
        orders[order.customer] = order
    assert orders["Gita"].total == 45000 + 10000  # Sate Kambing x1 + biaya URGENT, tanpa rute
    assert orders["Indra"].total == 4 * 15000  # Pangsit Goreng x4, NORMAL, tanpa rute
    assert orders["Ani"].route[0] == "Blok M"
    assert orders["Ani"].route[-1] == "Pondok Indah"
    assert orders["Ani"].total == 2 * 25000 + orders["Ani"].delivery_fee


def test_demo_orders_cannot_be_undone():
    service = demo_service()
    assert len(service.actions) == 0
    assert service.undo() == "Tidak ada aksi untuk di-undo."


def test_demo_orders_only_added_once():
    service = demo_service()
    assert seed_demo_orders(service) == "Sudah ada order, order contoh tidak ditambahkan."
    assert len(service.orders) == 10


def test_demo_orders_survive_reload(tmp_path):
    db_path = str(tmp_path / "demo.db")
    before = demo_service(db_path)
    after = FoodDeliveryService(db_path)
    assert statuses(after) == statuses(before)
    assert [order.customer for order in after.history] == ["Eka", "Ani", "Cici", "Gita", "Budi", "Dodi"]
    assert [order.customer for order in after.normal_queue] == ["Fajar", "Hana", "Indra"]
    assert after.next_order().customer == "Joko"


def test_menus_sorted_by_name_ignores_case():
    service = demo_service()
    expected = ["Bakmi Ayam", "Croissant", "Es Teh Manis", "Kopi Susu", "Matcha Latte", "Nasi Goreng",
                "Pangsit Goreng", "Sate Ayam", "Sate Kambing", "Soto Ayam"]
    assert [m.name for m in service.menus_sorted_by_name()] == expected
    assert [m.name for m in service.menus_sorted_by_name(insertion_sort)] == expected
