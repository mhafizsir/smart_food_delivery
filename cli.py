"""Perintah terminal untuk laporan: python cli.py demo | bench | test | check-db"""
import argparse
import sys

import pandas as pd

from core.benchmark import benchmark
from core.scenarios import run_test_scenarios
from core.seed import create_service, seed_demo_data


def demo():
    service = create_service(":memory:")
    print(seed_demo_data(service))
    orders = (("Ani", "R1", "M1", 2, "NORMAL", "Pondok Indah"), ("Budi", "R2", "M4", 1, "URGENT", "Cilandak"),
              ("Cici", "R3", "M7", 3, "HIGH", None), ("Dodi", "R1", "M2", 1, "NORMAL", None))
    for customer, restaurant, menu, quantity, priority, destination in orders:
        order, error = service.create_order(customer, restaurant, menu, quantity, priority, destination=destination)
        if error:
            print(error)
            continue
        line = f"Order #{order.id} {order.customer} {order.priority}: Rp{order.total:,}"
        if order.route:
            line += (f", rute {' -> '.join(order.route)} ({order.distance_km} km, {order.eta_min} menit, "
                     f"ongkir Rp{order.delivery_fee:,})")
        print(line)
    print("Isi heap (urutan keluar):", [f"#{o.id} {o.priority}" for o in service.priority_queue.in_order()])
    print("Queue NORMAL (front -> rear):", [f"#{o.id}" for o in service.normal_queue])
    print(service.cancel_order(4))
    print("Proses:", service.process_delivery()[0])
    print(service.undo())
    print("Proses:", service.process_delivery()[0], "| Proses:", service.process_delivery()[0])
    print("History (atas -> bawah):", [f"#{o.id} {o.status}" for o in service.history])
    print("Statistik:", service.statistics())
    print("Menu Rp15.000-Rp25.000 (BST):", [(m.name, m.price) for m in service.menus_in_price_range(15000, 25000)])
    print("Menu M7 (Hash Table, bucket", service.menu_index.bucket_index("M7"), "):", service.find_menu("M7").name)
    print("Ranking menu:", service.top_menus())
    print("BFS Senayan -> Tebet:", service.map.bfs_path("Senayan", "Tebet"))


def bench():
    frame = pd.DataFrame(benchmark())
    table = frame.pivot_table(index=["Operasi", "Struktur", "Kompleksitas"], columns="n", values="Waktu (ms)")
    print(table.to_string())


def test():
    rows = run_test_scenarios()
    print(pd.DataFrame(rows)[["No", "Kategori", "Skenario", "Hasil", "Detail"]].to_string(index=False))
    failed = [row["No"] for row in rows if row["Hasil"] == "GAGAL"]
    passed_count = 0
    for row in rows:
        if row["Hasil"] == "LULUS":
            passed_count += 1
    print(f"{passed_count} skenario LULUS, {len(failed)} GAGAL.")
    if failed:
        return 1
    return 0


def check_db():
    print(create_service().check_db())


COMMANDS = {"demo": demo, "bench": bench, "test": test, "check-db": check_db}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=COMMANDS)
    sys.exit(COMMANDS[parser.parse_args().command]())
