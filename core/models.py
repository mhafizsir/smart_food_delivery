"""Model data (Restaurant, Menu, Order), konstanta biaya, dan validasi input."""


PRIORITY_LEVEL = {"URGENT": 0, "HIGH": 1, "NORMAL": 2}
PRIORITY_FEE = {"URGENT": 10000, "HIGH": 5000, "NORMAL": 0}  # dikenakan sekali per order
PRIORITY_STREAK_LIMIT = 3  # anti-starvation: setelah 3 URGENT/HIGH berturut-turut, 1 NORMAL dilayani
LOCATION_KINDS = ("RESTAURANT", "CUSTOMER", "HUB")
AVG_SPEED_KMH = 25  # kecepatan rata-rata kurir di kota
ROAD_FACTOR = 1.3   # jalan asli lebih panjang dari garis lurus
DELIVERY_BASE_FEE = 5000
DELIVERY_FEE_PER_KM = 2000


class Restaurant:
    def __init__(self, id, name, location, category):
        self.id = id
        self.name = name
        self.location = location
        self.category = category


class Menu:
    def __init__(self, id, restaurant_id, name, category, price, available=True):
        self.id = id
        self.restaurant_id = restaurant_id
        self.name = name
        self.category = category
        self.price = price
        self.available = available


class Order:
    def __init__(self, id, customer, restaurant_id, menu_id, qty, total, priority="NORMAL",
                 status="PENDING", restaurant_name="", menu_name=""):
        self.id = id
        self.customer = customer
        self.restaurant_id = restaurant_id
        self.menu_id = menu_id
        self.qty = qty
        self.total = total
        self.priority = priority
        self.status = status  # PENDING -> DONE atau CANCELLED
        self.restaurant_name = restaurant_name  # disalin, jadi history tetap utuh kalau restoran dihapus
        self.menu_name = menu_name
        self.delivery_location = None
        self.route = None
        self.distance_km = None
        self.eta_min = None
        self.delivery_fee = 0

    def __repr__(self):
        return f"Order(#{self.id}, {self.customer!r}, {self.priority}, {self.status}, Rp{self.total:,})"


def priority_key(order):
    # Tie-break: prioritas sama -> ID lebih kecil (order lebih dulu dibuat) keluar duluan, jadi tetap FIFO
    return (PRIORITY_LEVEL[order.priority], order.id)


def parse_text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} tidak boleh kosong dan harus berupa teks.")
    return value.strip()


def parse_identifier(value, label="ID"):
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise ValueError(f"{label} harus berupa teks atau bilangan bulat.")
    return parse_text(str(value), label)


def parse_positive_int(value, label):
    if isinstance(value, str):
        value = value.strip()
        if value.isascii() and value.isdecimal():  # string kosong bukan desimal, jadi tetap ditolak
            value = int(value)
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{label} harus bilangan bulat lebih dari 0.")
    return value


def is_fail(message):
    return isinstance(message, str) and message.startswith("Gagal")
