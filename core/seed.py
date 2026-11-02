"""Data awal dari folder data/: peta contoh (Team 2), restoran/menu demo (Team 1), dan order demo."""
import csv
from pathlib import Path

from core.database import DB_PATH
from core.models import is_fail
from core.services import FoodDeliveryService


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DEMO_CANCELLED_CUSTOMER = "Dodi"
DEMO_DELIVERIES = 5  # order yang langsung diproses supaya dashboard, history, dan ranking terisi


def read_csv(name):
    """Baca data/<name>.csv menjadi list of dict, satu dict per baris."""
    with open(DATA_DIR / f"{name}.csv", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def seed_map_if_empty(service):
    if len(service.map):
        return False
    for row in read_csv("locations"):
        service.add_location(row["name"], float(row["lat"]), float(row["lon"]), row["kind"])
    for row in read_csv("roads"):
        service.add_road(row["from"], row["to"])
    return True


def seed_demo_data(service):
    """Isi restoran dan menu contoh untuk demo. ID yang sudah ada dilewati."""
    added = 0
    for row in read_csv("restaurants"):
        message = service.add_restaurant(row["id"], row["name"], row["location"], row["category"])
        if not is_fail(message):
            added += 1
    for row in read_csv("menus"):
        message = service.add_menu(row["id"], row["restaurant_id"], row["name"], row["category"], int(row["price"]))
        if not is_fail(message):
            added += 1
    return f"Sukses: {added} data contoh ditambahkan." if added else "Data contoh sudah ada."


def seed_demo_orders(service):
    """Isi order contoh: dibuat, satu dibatalkan, lalu beberapa diproses. Butuh restoran dan menu demo."""
    if len(service.orders):
        return "Sudah ada order, order contoh tidak ditambahkan."
    created = 0
    for row in read_csv("orders"):
        destination = row["destination"] or None  # kosong artinya tanpa rute
        order, error = service.create_order(row["customer"], row["restaurant_id"], row["menu_id"], int(row["qty"]),
                                            row["priority"], destination=destination)
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
