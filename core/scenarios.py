"""Testing plan (Bagian 10 panduan), dipakai pytest dan halaman Testing.

Setiap skenario memakai service baru dengan database ":memory:", jadi data asli tidak tersentuh."""
import random
import time

from core.benchmark import benchmark
from core.hash_table import HashTable
from core.models import is_fail
from core.searching import binary_search, linear_search
from core.seed import SEED_LOCATIONS, create_service, seed_demo_data
from core.sorting import insertion_sort, merge_sort


def _demo_service():
    service = create_service(":memory:")
    seed_demo_data(service)
    return service


def _all_failed(results):
    for result in results:
        if not is_fail(result):
            return False
    return True


def _t_valid_input():
    s = create_service(":memory:")
    result = s.add_restaurant("R1", "Warung Nusantara", "Blok M", "Indonesian")
    if is_fail(result):
        return False, result
    name_ok = s.find_restaurant("R1").name == "Warung Nusantara"
    saved_in_db = s.db.count("restaurants") == 1
    return name_ok and saved_in_db, result


def _t_duplicate():
    s = _demo_service()
    results = [s.add_restaurant(" R1 ", "Lain", "Tebet", "Cafe"), s.add_menu("M1", "R1", "Lain", "Makanan", 1000)]
    all_rejected = _all_failed(results)
    restaurants_unchanged = len(s.restaurants) == 4
    menus_unchanged = len(s.menus) == 10
    return all_rejected and restaurants_unchanged and menus_unchanged, " | ".join(results)


def _t_invalid_input():
    s = _demo_service()
    results = [s.add_menu("M99", "R1", "Mie", "Makanan", -5000), s.add_restaurant("R9", "  ", "Blok M", "Cafe"),
               s.create_order("Ani", "R1", "M1", 0)[1], s.create_order("Ani", "R1", "M1", 1, "VIP")[1],
               s.create_order("Ani", "R1", "M4", 1)[1]]
    all_rejected = _all_failed(results)
    no_orders = len(s.orders) == 0
    return all_rejected and no_orders, " | ".join(results)


def _t_empty_queue():
    s = _demo_service()
    order, message = s.process_delivery()
    return order is None and message == "Tidak ada order di antrean." and s.next_order() is None, message


def _t_fifo():
    s = _demo_service()
    ids = []
    for name in ("Ani", "Budi", "Cici"):
        order = s.create_order(name, "R1", "M1", 1)[0]
        ids.append(order.id)
    processed = []
    for _ in ids:
        order = s.process_delivery()[0]
        processed.append(order.id)
    return processed == ids, f"diproses {processed}"


def _t_undo_lifo():
    s = _demo_service()
    order = s.create_order("Ani", "R1", "M1", 1)[0]
    s.process_delivery()
    steps = [s.undo(), s.undo(), s.undo()]
    undo_process = steps[0].startswith("Undo proses")
    undo_create = steps[1].startswith("Undo buat")
    stack_empty = steps[2] == "Tidak ada aksi untuk di-undo."
    order_removed = len(s.orders) == 0 and s.db.count("orders") == 0
    order_pending = order.status == "PENDING"
    return undo_process and undo_create and stack_empty and order_removed and order_pending, " | ".join(steps)


def _t_heap_priority():
    s = _demo_service()
    for name, priority in (("Ani", "NORMAL"), ("Budi", "HIGH"), ("Cici", "URGENT"), ("Dodi", "HIGH")):
        s.create_order(name, "R1", "M1", 1, priority)
    served = []
    for _ in range(4):
        order = s.process_delivery()[0]
        served.append(order.customer)
    return served == ["Cici", "Budi", "Dodi", "Ani"] and s.priority_queue.is_valid(), f"urutan {served}"


def _t_collision():
    table = HashTable(capacity=8)
    bucket_of_m0 = table.bucket_index("M0")
    same_bucket = []
    for i in range(100):
        key = f"M{i}"
        if table.bucket_index(key) == bucket_of_m0:
            same_bucket.append(key)
    pair = same_bucket[:2]
    for key in pair:
        table.insert(key, key.lower())
    found = [table.search(key) for key in pair]
    expected = [key.lower() for key in pair]
    return table.collisions() == 1 and found == expected, f"{pair} di bucket {table.bucket_index(pair[0])}"


def _t_bst_inorder():
    s = _demo_service()
    prices = [m.price for m in s.menu_catalog.traverse("inorder")]
    in_range = [m.price for m in s.menus_in_price_range(15000, 25000)]
    is_ascending = prices == merge_sort(prices)
    range_ok = in_range == [15000, 18000, 22000, 22000, 24000, 25000]
    return is_ascending and len(prices) == 10 and range_ok, f"inorder {prices}"


def _t_shortest_route():
    s = create_service(":memory:")
    route, error = s.route_between("Senayan", "Fatmawati")
    brute = min(_all_path_lengths(s.map, "Senayan", "Fatmawati"))
    if route is None:
        path, distance = None, None
    else:
        path, distance = route["path"], route["distance_km"]
    return error is None and distance == round(brute, 2), f"{path} {distance} km, brute force {brute:.2f} km"


def _all_path_lengths(graph, start, end, seen=None, length=0.0):
    # Brute force rekursif semua jalur sederhana, hanya untuk memeriksa hasil Dijkstra pada peta kecil
    if seen is None:
        seen = set()
    seen = seen | {start}
    if start == end:
        return [length]
    lengths = []
    for edge in graph.adjacency[start]:
        if edge["to"] not in seen:
            lengths += _all_path_lengths(graph, edge["to"], end, seen, length + edge["distance"])
    return lengths


def _t_disconnected():
    s = create_service(":memory:")
    s.add_location("Pulau Seribu", -5.75, 106.6, "CUSTOMER")
    route, error = s.route_between("Senayan", "Pulau Seribu")
    s.add_restaurant("R1", "Warung", "Blok M", "Indonesian")
    s.add_menu("M1", "R1", "Nasi", "Makanan", 10000)
    order, order_error = s.create_order("Ani", "R1", "M1", 1, destination="Pulau Seribu")
    route_rejected = route is None and is_fail(error)
    order_rejected = order is None and is_fail(order_error)
    not_connected = not s.map.is_connected("Senayan", "Pulau Seribu")
    return route_rejected and order_rejected and not_connected, error


def _t_recursion():
    s = _demo_service()
    for customer, restaurant, menu, quantity in (("Ani", "R1", "M1", 2), ("Budi", "R2", "M4", 1),
                                                 ("Cici", "R1", "M2", 3)):
        s.create_order(customer, restaurant, menu, quantity)
    s.process_delivery()
    s.process_delivery()
    s.cancel_order(3)
    stats = s.statistics()
    expected = {"total": 3, "done": 2, "cancelled": 1, "sales": 2 * 25000 + 18000}
    sold = {"Nasi Goreng (Warung Nusantara)": 2, "Kopi Susu (Kopi Senja)": 1}
    numbers_ok = True
    for key, value in expected.items():
        if stats[key] != value:
            numbers_ok = False
    return numbers_ok and stats["menus_sold"] == sold, str({key: stats[key] for key in expected})


def _t_performance():
    start = time.perf_counter()
    benchmark(sizes=(100_000,))
    seconds = time.perf_counter() - start
    return seconds < 120, f"benchmark n=100.000 selesai dalam {seconds:.1f} detik"


def _t_persistence():
    s = _demo_service()
    s.create_order("Ani", "R1", "M1", 1, "URGENT", destination="Pondok Indah")
    s.create_order("Budi", "R2", "M4", 1)
    s.create_order("Cici", "R2", "M4", 1)
    for priority in ("URGENT", "HIGH"):
        s.create_order("Dodi", "R1", "M1", 1, priority)
    for _ in range(3):
        s.process_delivery()  # 3 prioritas berturut-turut: berikutnya giliran NORMAL
    s.update_menu("M2", price=7000)
    before = [(o.id, o.status, o.total, o.route) for o in s.orders]
    history = [o.id for o in s.history]
    upcoming = s.next_order()
    s.load()  # simulasi runtime baru / refresh Streamlit: semua struktur dibangun ulang dari database
    after = [(o.id, o.status, o.total, o.route) for o in s.orders]
    orders_same = after == before
    history_same = [o.id for o in s.history] == history
    queue_same = len(s.normal_queue) == 2 and s.priority_streak == 3 and s.next_order().id == upcoming.id
    menu_updated = s.find_menu("M2").price == 7000
    in_range = [m.price for m in s.menus_in_price_range(7000, 7000)] == [7000]
    return orders_same and history_same and queue_same and menu_updated and in_range, f"{len(after)} order dimuat ulang"


def _t_anti_starvation():
    s = _demo_service()
    priorities = ["URGENT", "URGENT", "URGENT", "URGENT", "URGENT", "NORMAL", "NORMAL"]
    for priority in priorities:
        s.create_order("Ani", "R1", "M1", 1, priority)
    sequence = ""
    for _ in range(7):
        order = s.process_delivery()[0]
        sequence += order.priority[0]
    return sequence == "UUUNUUN", sequence


def _t_cancel_undo_position():
    s = _demo_service()
    orders = []
    for name in ("Ani", "Budi", "Cici"):
        orders.append(s.create_order(name, "R1", "M1", 1)[0])
    s.cancel_order(orders[1].id)
    s.undo()
    queue_ids = [o.id for o in s.normal_queue]
    return queue_ids == [o.id for o in orders] and orders[1].status == "PENDING", str(queue_ids)


def _t_fees():
    s = _demo_service()
    totals = []
    for priority in ("NORMAL", "HIGH", "URGENT"):
        order = s.create_order("Ani", "R1", "M1", 2, priority)[0]
        totals.append(order.total)
    routed = s.create_order("Budi", "R1", "M1", 1, destination="Pondok Indah")[0]
    totals_ok = totals == [50000, 55000, 60000]
    routed_ok = routed.total == 25000 + s.delivery_fee(routed.distance_km) and routed.delivery_fee > 0
    return totals_ok and routed_ok, f"{totals}, ongkir {routed.delivery_fee}"


def _t_sorting():
    rng = random.Random(1)
    data = [rng.randint(0, 99) for _ in range(500)]
    ordered = merge_sort(data)
    sorts_agree = insertion_sort(data) == ordered and ordered == sorted(data)
    found = binary_search(ordered, ordered[123]) >= 0
    missing = binary_search(ordered, 1000) == -1
    linear_ok = linear_search(data, data[42]) <= 42
    return sorts_agree and found and missing and linear_ok, "insertion sort = merge sort = sorted()"


def _t_ranking():
    s = _demo_service()
    for customer, restaurant, menu, quantity in (("Ani", "R1", "M1", 1), ("Budi", "R2", "M4", 5),
                                                 ("Cici", "R1", "M1", 2), ("Dodi", "R3", "M7", 1)):
        s.create_order(customer, restaurant, menu, quantity)
    for _ in range(4):
        s.process_delivery()
    menus_ok = s.top_menus(2) == [("Kopi Susu (Kopi Senja)", 5), ("Nasi Goreng (Warung Nusantara)", 3)]
    restaurants_ok = s.top_restaurants(1) == [("Warung Nusantara", 2)]
    return menus_ok and restaurants_ok, f"{s.top_menus(2)} / {s.top_restaurants(1)}"


def _t_delete_restaurant():
    s = _demo_service()
    order = s.create_order("Ani", "R1", "M1", 1)[0]
    refused = s.delete_restaurant("R1")
    s.cancel_order(order.id)
    deleted = s.delete_restaurant("R1")
    undo = s.undo()  # undo batal order untuk restoran yang sudah dihapus harus ditolak
    refused_then_deleted = is_fail(refused) and not is_fail(deleted)
    undo_refused = is_fail(undo) and order.status == "CANCELLED"
    menus_removed = s.find_menu("M1") is None and len(s.menu_catalog) == 7 and s.db.count("menus") == 7
    history_ok = len(s.history) == 1
    return refused_then_deleted and undo_refused and menus_removed and history_ok, deleted


def _t_hash_resize():
    table = HashTable()
    for i in range(1000):
        table.insert(f"M{i}", i)
    all_found = True
    for i in range(1000):
        if table.search(f"M{i}") != i:
            all_found = False
    load_ok = table.load_factor() <= HashTable.MAX_LOAD_FACTOR
    chain_ok = table.longest_chain() <= 5
    detail = f"{table.capacity} bucket, load factor {table.load_factor():.2f}, chain terpanjang {table.longest_chain()}"
    return load_ok and chain_ok and all_found, detail


def _t_bfs_dfs():
    s = create_service(":memory:")
    hops = dict(s.map.bfs("Senayan"))
    fewest = s.map.bfs_path("Senayan", "Tebet")
    all_reached = len(s.map.dfs("Senayan")) == len(SEED_LOCATIONS)
    return all_reached and hops["Tebet"] == 2 and fewest == ["Senayan", "Kuningan", "Tebet"], f"BFS Senayan -> Tebet: {fewest}"


TEST_SCENARIOS = [
    (1, "Fungsional", "Input data valid", "Data berhasil disimpan", _t_valid_input),
    (2, "Fungsional", "Data duplikat (ID restoran/menu sama)", "Sistem menolak data", _t_duplicate),
    (3, "Fungsional", "Input tidak valid (harga negatif, nama kosong, qty 0, prioritas salah)", "Ditolak dengan pesan jelas", _t_invalid_input),
    (4, "Queue/Heap", "Proses delivery saat antrean kosong", "Pesan informasi, tidak error", _t_empty_queue),
    (5, "Queue", "Beberapa order NORMAL masuk", "FIFO berjalan benar", _t_fifo),
    (6, "Stack", "Undo berulang sampai stack kosong", "LIFO benar, undo stack kosong ditangani", _t_undo_lifo),
    (7, "Heap", "Order dengan prioritas berbeda", "URGENT -> HIGH -> NORMAL, tie-break FIFO", _t_heap_priority),
    (8, "Hash Table", "Dua key menghasilkan collision", "Kedua data tetap ditemukan", _t_collision),
    (9, "BST", "Traversal inorder dan cari rentang harga", "Harga tampil menaik, rentang benar", _t_bst_inorder),
    (10, "Graph", "Rute antara dua titik", "Rute dan jarak terpendek benar (dicek brute force)", _t_shortest_route),
    (11, "Graph", "Titik tidak terhubung", "Informasi rute tidak tersedia, order ditolak", _t_disconnected),
    (12, "Recursion", "Statistik rekursif pada data nyata", "Nilai benar", _t_recursion),
    (13, "Performa", "Benchmark 100.000 elemen", "Selesai tanpa crash", _t_performance),
    (14, "Streamlit", "Refresh / muat ulang data dari database", "Order, urutan linked list, history, antrean, kuota prioritas tetap sama", _t_persistence),
    (16, "Heap", "Anti-starvation: 5 URGENT + 2 NORMAL", "U,U,U,N,U,U,N", _t_anti_starvation),
    (17, "Queue/Stack", "Batal order lalu undo", "Order kembali ke posisi semula", _t_cancel_undo_position),
    (18, "Fungsional", "Biaya prioritas dan ongkir dari jarak Dijkstra", "Total = harga + biaya prioritas + ongkir", _t_fees),
    (19, "Sorting", "Insertion sort vs merge sort, binary vs linear search", "Hasil sama", _t_sorting),
    (20, "Sorting", "Ranking menu terlaris dan restoran teramai", "Urutan menurun benar", _t_ranking),
    (21, "Fungsional", "Hapus restoran yang masih punya order PENDING", "Ditolak; setelah dibatalkan, terhapus beserta menunya; undo order-nya ditolak", _t_delete_restaurant),
    (22, "Hash Table", "1.000 key dan rehash", "Load factor <= 0,75, semua key ditemukan", _t_hash_resize),
    (23, "Graph", "BFS dan DFS dari Senayan", "Semua lokasi terjangkau, transit paling sedikit benar", _t_bfs_dfs),
]
MANUAL_SCENARIOS = [
    (15, "Deployment", "Akses URL Cloudflare dari perangkat lain", "Aplikasi dapat dibuka dan berfungsi"),
]


def run_test_scenarios(skip_slow=False):
    rows = []
    for no, category, scenario, expected, test in TEST_SCENARIOS:
        if skip_slow and test is _t_performance:
            continue
        try:
            passed, detail = test()
        except Exception as error:  # tes yang crash dicatat sebagai gagal, bukan menghentikan semua tes
            passed, detail = False, f"{type(error).__name__}: {error}"
        if passed:
            result = "LULUS"
        else:
            result = "GAGAL"
        rows.append({"No": no, "Kategori": category, "Skenario": scenario, "Expected": expected,
                     "Hasil": result, "Detail": str(detail)})
    for no, category, scenario, expected in MANUAL_SCENARIOS:
        rows.append({"No": no, "Kategori": category, "Skenario": scenario, "Expected": expected,
                     "Hasil": "MANUAL", "Detail": "Buka URL trycloudflare.com dari HP saat demo"})
    return merge_sort(rows, key=lambda row: row["No"])
