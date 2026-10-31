"""Data awal: peta contoh (Team 2), restoran/menu demo (Team 1), dan order demo."""
from core.database import DB_PATH
from core.models import is_fail
from core.service import FoodDeliveryService


# Peta contoh Jakarta Selatan (dipakai kalau database belum punya lokasi)
SEED_LOCATIONS = [
    ("Senayan", -6.2186, 106.8023, "RESTAURANT"), ("Blok M", -6.2443, 106.8001, "RESTAURANT"),
    ("Kemang", -6.2607, 106.8136, "RESTAURANT"), ("Tebet", -6.2260, 106.8530, "RESTAURANT"),
    ("Kuningan", -6.2297, 106.8296, "HUB"), ("Mampang", -6.2425, 106.8250, "HUB"),
    ("Pancoran", -6.2430, 106.8440, "HUB"), ("Cipete", -6.2770, 106.8010, "HUB"),
    ("Kebayoran Lama", -6.2449, 106.7766, "HUB"), ("Pondok Indah", -6.2655, 106.7838, "CUSTOMER"),
    ("Fatmawati", -6.2920, 106.7966, "CUSTOMER"), ("Cilandak", -6.2903, 106.8075, "CUSTOMER"),
]
SEED_ROADS = [
    ("Senayan", "Blok M"), ("Senayan", "Kuningan"), ("Senayan", "Kebayoran Lama"),
    ("Blok M", "Kebayoran Lama"), ("Blok M", "Mampang"), ("Blok M", "Cipete"),
    ("Kemang", "Mampang"), ("Kemang", "Cipete"), ("Kemang", "Cilandak"),
    ("Cipete", "Fatmawati"), ("Fatmawati", "Cilandak"), ("Fatmawati", "Pondok Indah"),
    ("Pondok Indah", "Kebayoran Lama"), ("Mampang", "Kuningan"), ("Mampang", "Pancoran"),
    ("Kuningan", "Tebet"), ("Pancoran", "Tebet"),
]
DEMO_RESTAURANTS = [
    ("R1", "Warung Nusantara", "Blok M", "Indonesian"), ("R2", "Kopi Senja", "Kemang", "Cafe"),
    ("R3", "Sate Senayan", "Senayan", "Indonesian"), ("R4", "Bakmi Tebet", "Tebet", "Chinese"),
]
DEMO_MENUS = [
    ("M1", "R1", "Nasi Goreng", "Makanan", 25000), ("M2", "R1", "Es Teh Manis", "Minuman", 5000),
    ("M3", "R1", "Soto Ayam", "Makanan", 22000), ("M4", "R2", "Kopi Susu", "Minuman", 18000),
    ("M5", "R2", "Croissant", "Makanan", 22000), ("M6", "R2", "Matcha Latte", "Minuman", 28000),
    ("M7", "R3", "Sate Ayam", "Makanan", 30000), ("M8", "R3", "Sate Kambing", "Makanan", 45000),
    ("M9", "R4", "Bakmi Ayam", "Makanan", 24000), ("M10", "R4", "Pangsit Goreng", "Makanan", 15000),
]


# (customer, restoran, menu, jumlah, prioritas, lokasi antar). None artinya tanpa rute.
DEMO_ORDERS = [
    ("Ani", "R1", "M1", 2, "NORMAL", "Pondok Indah"), ("Budi", "R2", "M4", 1, "URGENT", "Cilandak"),
    ("Cici", "R3", "M7", 3, "HIGH", "Fatmawati"), ("Dodi", "R1", "M2", 2, "NORMAL", None),
    ("Eka", "R4", "M9", 1, "HIGH", "Pondok Indah"), ("Fajar", "R2", "M6", 2, "NORMAL", "Fatmawati"),
    ("Gita", "R3", "M8", 1, "URGENT", None), ("Hana", "R1", "M3", 1, "NORMAL", "Cilandak"),
    ("Indra", "R4", "M10", 4, "NORMAL", None), ("Joko", "R2", "M5", 2, "HIGH", "Cilandak"),
]
DEMO_CANCELLED_CUSTOMER = "Dodi"
DEMO_DELIVERIES = 5  # order yang langsung diproses supaya dashboard, history, dan ranking terisi


def seed_map_if_empty(service):
    if len(service.map):
        return False
    for name, lat, lon, kind in SEED_LOCATIONS:
        service.add_location(name, lat, lon, kind)
    for a, b in SEED_ROADS:
        service.add_road(a, b)
    return True


def seed_demo_data(service):
    """Isi restoran dan menu contoh untuk demo. ID yang sudah ada dilewati."""
    added = 0
    for id, name, location, category in DEMO_RESTAURANTS:
        message = service.add_restaurant(id, name, location, category)
        if not is_fail(message):
            added += 1
    for id, restaurant_id, name, category, price in DEMO_MENUS:
        message = service.add_menu(id, restaurant_id, name, category, price)
        if not is_fail(message):
            added += 1
    return f"Sukses: {added} data contoh ditambahkan." if added else "Data contoh sudah ada."


def seed_demo_orders(service):
    """Isi order contoh: dibuat, satu dibatalkan, lalu beberapa diproses. Butuh restoran dan menu demo."""
    if len(service.orders):
        return "Sudah ada order, order contoh tidak ditambahkan."
    created = 0
    for customer, restaurant_id, menu_id, qty, priority, destination in DEMO_ORDERS:
        order, error = service.create_order(customer, restaurant_id, menu_id, qty, priority, destination=destination)
        if error is None:
            created += 1
    if created == 0:
        return "Gagal: Restoran dan menu contoh belum ada. Isi data contoh dulu."
    for order in service.orders_by_customer(DEMO_CANCELLED_CUSTOMER):
        service.cancel_order(order.id)
    for _ in range(DEMO_DELIVERIES):
        service.process_delivery()
    service.actions.clear()  # undo hanya untuk aksi pengguna, bukan untuk data contoh
    return f"Sukses: {created} order contoh ditambahkan."


def create_service(db_path=DB_PATH):
    service = FoodDeliveryService(db_path)
    seed_map_if_empty(service)
    return service
