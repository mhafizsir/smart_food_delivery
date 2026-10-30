"""Data awal: peta contoh (Team 2) dan restoran/menu demo (Team 1)."""
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


def create_service(db_path=DB_PATH):
    service = FoodDeliveryService(db_path)
    seed_map_if_empty(service)
    return service
