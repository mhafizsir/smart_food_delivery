"""FoodDeliveryService: seluruh fitur sistem, tanpa Streamlit.

Semua state ada di satu objek FoodDeliveryService. Streamlit cukup menyimpan satu objek ini,
dan tes membuat objek baru dengan database ":memory:" tanpa menyentuh data asli."""
from core.bst import BST
from core.database import DB_PATH, Database
from core.graph import Graph, haversine_km
from core.hash_table import HashTable
from core.heap import MinHeap
from core.linear import DynamicArray, LinkedQueue, SinglyLinkedList, Stack
from core.models import (
    AVG_SPEED_KMH, DELIVERY_BASE_FEE, DELIVERY_FEE_PER_KM, LOCATION_KINDS, Menu, Order, PRIORITY_FEE,
    PRIORITY_LEVEL, PRIORITY_STREAK_LIMIT, ROAD_FACTOR, Restaurant, parse_identifier, parse_positive_int,
    parse_text, priority_key,
)
from core.recursion import recursive_group, recursive_sum
from core.sorting import merge_sort


class FoodDeliveryService:
    def __init__(self, db_path=DB_PATH):
        self.db = Database(db_path)
        self.restaurants = DynamicArray()          # Sub 1: data utama restoran
        self.menus = DynamicArray()                # Sub 1: data utama menu
        self.restaurant_index = HashTable()        # Fitur UAS: cari restoran per ID, O(1)
        self.menu_index = HashTable()              # Fitur UAS: cari menu per ID, O(1)
        self.menu_catalog = BST(key=lambda menu: menu.price)  # Fitur UAS: katalog terurut harga
        self.orders = SinglyLinkedList()           # Sub 2: semua order, terbaru di head
        self.normal_queue = LinkedQueue()          # Sub 4: order NORMAL, FIFO
        self.priority_queue = MinHeap(key=priority_key)  # Sub 4 + UAS: order URGENT/HIGH
        self.history = Stack()                     # Sub 3: order DONE/CANCELLED, terbaru di atas
        self.actions = Stack()                     # Sub 5: aksi yang bisa di-undo
        self.map = Graph()                         # Fitur UAS: peta lokasi dan jalan
        self.order_counter = 0
        self.priority_streak = 0                   # jumlah URGENT/HIGH yang diproses berturut-turut
        self.load()

    # ---------- load dari database (Team 1) ----------

    def load(self):
        for collection in (self.restaurants, self.menus, self.restaurant_index, self.menu_index, self.orders,
                           self.normal_queue, self.priority_queue, self.history, self.actions, self.map):
            collection.clear()
        self.menu_catalog = BST(key=lambda menu: menu.price)
        self.priority_streak = 0
        for id_, name, location, category in self.db.rows(
                "SELECT id, name, location, category FROM restaurants ORDER BY rowid"):
            self._index_restaurant(Restaurant(id_, name, location, category))
        for id_, restaurant_id, name, category, price, available in self.db.rows(
                "SELECT id, restaurant_id, name, category, price, available FROM menus ORDER BY rowid"):
            self._index_menu(Menu(id_, restaurant_id, name, category, price, bool(available)))
        for name, lat, lon, kind in self.db.rows("SELECT name, lat, lon, type FROM locations ORDER BY rowid"):
            self.map.add_node(name, lat, lon, kind)
        for a, b, distance, minutes in self.db.rows(
                "SELECT from_loc, to_loc, distance, travel_time FROM roads ORDER BY rowid"):
            if a in self.map.adjacency and b in self.map.adjacency:
                self.map.add_edge(a, b, distance, minutes)
        finished = []
        for row in self.db.rows("""
                SELECT id, customer, restaurant_id, menu_id, qty, total, priority, status, restaurant_name,
                       menu_name, history_seq, delivery_location, distance_km, eta_min, route, delivery_fee
                FROM orders ORDER BY id"""):
            order = Order(*row[:10])
            seq = row[10]
            order.delivery_location = row[11]
            order.distance_km = row[12]
            order.eta_min = row[13]
            if row[14]:
                order.route = row[14].split("|")
            else:
                order.route = None
            order.delivery_fee = row[15] or 0
            self.orders.insert_front(order)  # dimuat urut ID, jadi order terbaru kembali di head
            if order.status == "PENDING":
                self._enqueue(order)
            elif seq is not None:
                finished.append((seq, order))
        for _, order in merge_sort(finished, key=lambda pair: pair[0]):
            self.history.push(order)
        # Kuota anti-starvation dihitung ulang dari history: order URGENT/HIGH yang selesai
        # berturut-turut sejak order NORMAL terakhir yang selesai
        for order in self.history:
            if order.status == "DONE":
                if order.priority == "NORMAL":
                    break
                self.priority_streak += 1
        self.order_counter = self.db.rows("SELECT COALESCE(MAX(id), 0) FROM orders")[0][0]

    def _index_restaurant(self, restaurant):
        self.restaurants.append(restaurant)
        self.restaurant_index.insert(restaurant.id, restaurant)

    def _index_menu(self, menu):
        self.menus.append(menu)
        self.menu_index.insert(menu.id, menu)
        self.menu_catalog.insert(menu)

    # ---------- restoran & menu (Team 1) ----------

    def find_restaurant(self, restaurant_id):
        try:
            return self.restaurant_index.search(parse_identifier(restaurant_id))
        except ValueError:
            return None

    def find_menu(self, menu_id):
        try:
            return self.menu_index.search(parse_identifier(menu_id))
        except ValueError:
            return None

    def add_restaurant(self, id, name, location, category):
        try:
            id = parse_identifier(id, "ID restoran")
            name = parse_text(name, "Nama")
            category = parse_text(category, "Kategori")
            location = parse_text(location, "Lokasi")
        except ValueError as error:
            return f"Gagal: {error}"
        if id in self.restaurant_index:
            return f"Gagal: ID restoran {id} sudah terdaftar."
        map_name = self.map.find(location)  # pakai penulisan nama yang ada di peta
        if map_name:
            location = map_name
        restaurant = Restaurant(id, name, location, category)
        self._index_restaurant(restaurant)
        self.db.save_restaurant(restaurant)
        return f"Sukses: Restoran {name} ditambahkan."

    def delete_restaurant(self, restaurant_id):
        restaurant = self.find_restaurant(restaurant_id)
        if restaurant is None:
            return "Gagal: Restoran tidak ditemukan."
        pending = self.orders.find_all(lambda o: o.restaurant_id == restaurant.id and o.status == "PENDING")
        if pending:
            ids = ", ".join(f"#{o.id}" for o in pending)
            return f"Gagal: Restoran masih punya order PENDING ({ids}). Proses atau batalkan dulu."
        owned = [m for m in self.menus if m.restaurant_id == restaurant.id]
        for menu in owned:
            self.menu_index.delete(menu.id)
            self.menu_catalog.delete(menu)
        self.menus.remove_where(lambda m: m.restaurant_id == restaurant.id)
        self.restaurants.remove_where(lambda r: r is restaurant)
        self.restaurant_index.delete(restaurant.id)
        self.db.delete_restaurant(restaurant.id)
        return f"Sukses: Restoran {restaurant.name} dan {len(owned)} menu dihapus."

    def add_menu(self, id, restaurant_id, name, category, price):
        try:
            id = parse_identifier(id, "ID menu")
            name = parse_text(name, "Nama")
            category = parse_text(category, "Kategori")
            price = parse_positive_int(price, "Harga")
        except ValueError as error:
            return f"Gagal: {error}"
        if id in self.menu_index:
            return f"Gagal: ID menu {id} sudah terdaftar."
        restaurant = self.find_restaurant(restaurant_id)
        if restaurant is None:
            return "Gagal: Restoran tidak ditemukan."
        menu = Menu(id, restaurant.id, name, category, price)
        self._index_menu(menu)
        self.db.save_menu(menu)
        return f"Sukses: Menu {name} ditambahkan."

    def update_menu(self, menu_id, name=None, category=None, price=None, available=None):
        menu = self.find_menu(menu_id)
        if menu is None:
            return "Gagal: Menu tidak ditemukan."
        try:  # validasi semua field dulu, jadi perubahan tidak setengah jalan
            if name is None:
                name = menu.name
            else:
                name = parse_text(name, "Nama")
            if category is None:
                category = menu.category
            else:
                category = parse_text(category, "Kategori")
            if price is None:
                price = menu.price
            else:
                price = parse_positive_int(price, "Harga")
        except ValueError as error:
            return f"Gagal: {error}"
        old_price = menu.price
        menu.name = name
        menu.category = category
        menu.price = price
        if available is not None:
            menu.available = bool(available)
        if price != old_price:  # harga adalah key BST: pindahkan node
            self.menu_catalog.delete(menu, key=old_price)
            self.menu_catalog.insert(menu)
        self.db.save_menu(menu)
        return f"Sukses: Menu {menu.id} diperbarui."

    def delete_menu(self, menu_id):
        menu = self.find_menu(menu_id)
        if menu is None:
            return "Gagal: Menu tidak ditemukan."
        self.menus.remove_where(lambda m: m is menu)
        self.menu_index.delete(menu.id)
        self.menu_catalog.delete(menu)
        self.db.delete_menu(menu.id)
        return f"Sukses: Menu {menu.id} dihapus."

    def search_keyword(self, keyword):
        """Pencarian UTS: linear search pada ID, nama, kategori, dan lokasi. Hasil: (restoran, menu)."""
        key = str(keyword).strip().casefold()
        if not key:
            return [], []
        restaurants = []
        for r in self.restaurants:
            if contains_keyword(key, (r.id, r.name, r.category, r.location)):
                restaurants.append(r)
        menus = []
        for m in self.menus:
            if contains_keyword(key, (m.id, m.name, m.category)):
                menus.append(m)
        return restaurants, menus

    def menus_in_price_range(self, low, high):
        return self.menu_catalog.search_range(low, high)

    def sorted_menu_ids(self, algorithm=merge_sort):
        ids = []
        for m in self.menus:
            ids.append(m.id)
        return algorithm(ids)

    # ---------- peta & rute (Team 2) ----------

    def add_location(self, name, lat, lon, kind="HUB"):
        try:
            name = parse_text(name, "Nama lokasi")
            lat = float(lat)
            lon = float(lon)
            lat_ok = lat >= -90 and lat <= 90
            lon_ok = lon >= -180 and lon <= 180
            if not (lat_ok and lon_ok):
                raise ValueError("Koordinat tidak valid.")
            kind = parse_text(kind, "Tipe lokasi").upper()
            if kind not in LOCATION_KINDS:
                raise ValueError("Tipe lokasi harus RESTAURANT, CUSTOMER, atau HUB.")
        except (TypeError, ValueError) as error:
            return f"Gagal: {error}"
        map_name = self.map.find(name)  # pakai penulisan nama yang sudah ada di peta
        if map_name:
            name = map_name
        self.map.add_node(name, lat, lon, kind)
        self.db.save_location(name, lat, lon, kind)
        return f"Sukses: Lokasi {name} disimpan."

    def add_road(self, a, b, distance=None, minutes=None):
        start = self.map.find(a)
        end = self.map.find(b)
        if start is None or end is None:
            return "Gagal: Lokasi awal atau tujuan tidak terdaftar di peta."
        if start == end:
            return "Gagal: Lokasi awal dan tujuan tidak boleh sama."
        if self.map.has_edge(start, end):
            return "Gagal: Jalan tersebut sudah ada."
        try:
            if distance is None:  # jarak otomatis dari koordinat (garis lurus x faktor jalan)
                distance = round(haversine_km(self.map.coords[start], self.map.coords[end]) * ROAD_FACTOR, 2)
            distance = float(distance)
            if minutes is None:
                minutes = round(distance / AVG_SPEED_KMH * 60, 1)
            else:
                minutes = float(minutes)
            if distance <= 0 or minutes <= 0:
                raise ValueError("Jarak dan waktu harus lebih dari 0.")
        except (KeyError, TypeError, ValueError) as error:
            return f"Gagal: {error}"
        self.map.add_edge(start, end, distance, minutes)
        self.db.save_road(start, end, distance, minutes)
        return f"Sukses: Jalan {start} - {end} ({distance:g} km) ditambahkan."

    @staticmethod
    def delivery_fee(distance_km):
        return DELIVERY_BASE_FEE + round(distance_km * DELIVERY_FEE_PER_KM / 500) * 500

    def route_between(self, start, end):
        """Rute Dijkstra antar dua lokasi. Hasil: (route, error)."""
        a = self.map.find(start)
        b = self.map.find(end)
        if a is None or b is None:
            return None, "Gagal: Lokasi awal atau tujuan tidak terdaftar di peta."
        result = self.map.dijkstra(a, b)
        if result is None:
            return None, f"Gagal: Tidak ada jalan yang menghubungkan {a} dan {b}."
        path, distance, minutes = result
        return {"path": path, "distance_km": distance, "eta_min": minutes,
                "fee": self.delivery_fee(distance)}, None

    def plan_route(self, restaurant_id, destination):
        restaurant = self.find_restaurant(restaurant_id)
        if restaurant is None:
            return None, "Gagal: Restoran tidak ditemukan."
        if self.map.find(restaurant.location) is None:
            return None, f"Gagal: Lokasi restoran '{restaurant.location}' belum ada di peta."
        return self.route_between(restaurant.location, destination)

    # ---------- order (Team 2) ----------

    def _enqueue(self, order):
        if order.priority == "NORMAL":
            self.normal_queue.enqueue(order)
        else:
            self.priority_queue.push(order)

    def find_order(self, order_id):
        try:
            order_id = parse_positive_int(order_id, "ID order")
        except ValueError:
            return None
        return self.orders.search(lambda o: o.id == order_id)

    def orders_by_customer(self, customer):
        key = str(customer).strip().casefold()
        return self.orders.find_all(lambda o: o.customer.casefold() == key)

    def create_order(self, customer, restaurant_id, menu_id, qty, priority="NORMAL", destination=None):
        """Hasil: (order, None) kalau berhasil, (None, pesan) kalau gagal."""
        try:
            customer = parse_text(customer, "Nama customer")
            qty = parse_positive_int(qty, "Jumlah")
            priority = parse_text(priority, "Prioritas").upper()
            if priority not in PRIORITY_LEVEL:
                raise ValueError("Prioritas harus URGENT, HIGH, atau NORMAL.")
        except ValueError as error:
            return None, f"Gagal: {error}"
        restaurant = self.find_restaurant(restaurant_id)
        menu = self.find_menu(menu_id)
        if restaurant is None:
            return None, "Gagal: Restoran tidak ditemukan."
        if menu is None:
            return None, "Gagal: Menu tidak ditemukan."
        if menu.restaurant_id != restaurant.id:
            return None, "Gagal: Menu bukan milik restoran yang dipilih."
        if not menu.available:
            return None, "Gagal: Menu sedang tidak tersedia."
        route = None
        if destination:
            route, error = self.plan_route(restaurant.id, destination)
            if error:
                return None, error
        self.order_counter += 1
        order = Order(self.order_counter, customer, restaurant.id, menu.id, qty, menu.price * qty, priority,
                      restaurant_name=restaurant.name, menu_name=menu.name)
        order.total += PRIORITY_FEE[priority]
        if route:
            order.delivery_location = route["path"][-1]
            order.route = route["path"]
            order.distance_km = route["distance_km"]
            order.eta_min = route["eta_min"]
            order.delivery_fee = route["fee"]
            order.total += route["fee"]
        self.orders.insert_front(order)  # order terbaru selalu di head, O(1)
        self._enqueue(order)
        self.actions.push({"type": "CREATE_ORDER", "order": order})
        self.db.save_order(order)
        return order, None

    def cancel_order(self, order_id):
        order = self.find_order(order_id)
        if order is None:
            return "Gagal: Order tidak ditemukan."
        if order.status != "PENDING":
            return f"Gagal: Order #{order.id} sudah {order.status}."
        position = None  # posisi hanya berarti untuk FIFO; di heap posisi ditentukan key
        if order.priority == "NORMAL":
            position = self.normal_queue.remove(order)
        else:
            self.priority_queue.remove(order)
        order.status = "CANCELLED"
        self.history.push(order)
        self.actions.push({"type": "CANCEL_ORDER", "order": order, "position": position})
        self.db.save_order(order)
        return f"Sukses: Order #{order.id} dibatalkan."

    def is_normal_turn(self):
        if self.priority_queue.is_empty() or self.normal_queue.is_empty():
            return False
        return self.priority_streak >= PRIORITY_STREAK_LIMIT

    def next_order(self):
        if self.is_normal_turn() or self.priority_queue.is_empty():
            return self.normal_queue.peek()
        return self.priority_queue.peek()

    def process_delivery(self):
        """Ambil order berikutnya: URGENT -> HIGH -> NORMAL, dengan kuota anti-starvation."""
        if self.is_normal_turn() or self.priority_queue.is_empty():
            order = self.normal_queue.dequeue()
        else:
            order = self.priority_queue.pop()
        if order is None:
            return None, "Tidak ada order di antrean."
        self.actions.push({"type": "PROCESS_DELIVERY", "order": order, "streak": self.priority_streak})
        if order.priority == "NORMAL":
            self.priority_streak = 0
        else:
            self.priority_streak += 1
        order.status = "DONE"
        self.history.push(order)
        self.db.save_order(order)
        return order, None

    def undo(self):
        action = self.actions.pop()
        if action is None:
            return "Tidak ada aksi untuk di-undo."
        order = action["order"]
        if action["type"] == "CREATE_ORDER":
            if order.priority == "NORMAL":
                self.normal_queue.remove(order)
            else:
                self.priority_queue.remove(order)
            self.orders.remove(lambda o: o is order)
            self.db.delete_order(order.id)
            if order.id == self.order_counter:
                self.order_counter -= 1
            return f"Undo buat order: Order #{order.id} dihapus."
        if self.find_restaurant(order.restaurant_id) is None:
            return f"Gagal: Restoran order #{order.id} sudah dihapus, aksi ini tidak bisa di-undo."
        self.history.pop()  # LIFO: order dari aksi terakhir pasti ada di puncak history
        order.status = "PENDING"
        if order.priority != "NORMAL":
            self.priority_queue.push(order)  # posisi di heap ditentukan key (prioritas, ID)
        elif action["type"] == "CANCEL_ORDER":
            self.normal_queue.insert_at(action["position"], order)
        else:
            self.normal_queue.insert_at(0, order)  # order yang diproses selalu dari depan antrean
        if action["type"] == "PROCESS_DELIVERY":
            self.priority_streak = action["streak"]
        self.db.save_order(order)
        label = "batal order" if action["type"] == "CANCEL_ORDER" else "proses delivery"
        return f"Undo {label}: Order #{order.id} kembali PENDING."

    # ---------- statistik (rekursif) & ranking (merge sort) (Team 3) ----------

    def statistics(self):
        orders = self.orders_array()
        return {
            "total": len(orders),
            "pending": recursive_sum(orders, count_pending),
            "done": recursive_sum(orders, count_done),
            "cancelled": recursive_sum(orders, count_cancelled),
            "sales": recursive_sum(orders, sales_of),
            "orders_per_restaurant": recursive_group(orders, restaurant_of, count_one),
            "menus_sold": recursive_group(orders, menu_label_if_done, quantity_of),
        }

    def orders_array(self):  # linked list -> array, dari order terlama
        array = DynamicArray()
        for order in self.orders:
            array.append(order)
        return merge_sort(array, key=lambda o: o.id)

    def top_menus(self, limit=5):
        sold = self.statistics()["menus_sold"]
        return merge_sort(sold.items(), key=lambda pair: -pair[1])[:limit]

    def top_restaurants(self, limit=5):
        counts = self.statistics()["orders_per_restaurant"]
        return merge_sort(counts.items(), key=lambda pair: -pair[1])[:limit]

    def check_db(self):
        counts = {}
        for table in ("restaurants", "menus", "orders", "locations", "roads"):
            counts[table] = self.db.count(table)
        return counts


# Fungsi kecil untuk statistics() dan search_keyword(), dipakai sebagai parameter value/group
def count_pending(order):
    if order.status == "PENDING":
        return 1
    return 0


def count_done(order):
    if order.status == "DONE":
        return 1
    return 0


def count_cancelled(order):
    if order.status == "CANCELLED":
        return 1
    return 0


def sales_of(order):
    if order.status == "DONE":
        return order.total
    return 0


def restaurant_of(order):
    return order.restaurant_name


def count_one(order):
    return 1


def menu_label_if_done(order):
    # Dikelompokkan per menu + restoran, karena dua restoran bisa punya menu dengan nama sama
    if order.status == "DONE":
        return f"{order.menu_name} ({order.restaurant_name})"
    return None  # order yang belum DONE tidak masuk menus_sold


def quantity_of(order):
    return order.qty


def contains_keyword(key, values):
    for value in values:
        if key in value.casefold():
            return True
    return False
