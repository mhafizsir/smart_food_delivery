"""Penyimpanan permanen SQLite (Team 1)."""
import os
from pathlib import Path
import sqlite3


DB_PATH = os.environ.get("SFD_DB_PATH", str(Path(__file__).resolve().parent.parent / "smart_food_delivery.db"))


class Database:
    """Penyimpanan permanen. Skema sama dengan notebook UTS, jadi file database lama
    tetap bisa dipakai; kolom baru ditambahkan lewat migrasi tanpa menghapus data."""

    ORDER_COLUMNS = (("delivery_location", "TEXT"), ("distance_km", "REAL"), ("eta_min", "REAL"),
                     ("route", "TEXT"), ("delivery_fee", "INTEGER"), ("list_insert", "TEXT"))

    def __init__(self, path):
        self.conn = sqlite3.connect(path, check_same_thread=False)  # Streamlit memakai banyak thread
        self.conn.execute("PRAGMA foreign_keys = ON")
        with self.conn:
            self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS restaurants (
                id TEXT PRIMARY KEY, name TEXT NOT NULL, location TEXT NOT NULL, category TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS menus (
                id TEXT PRIMARY KEY, restaurant_id TEXT NOT NULL REFERENCES restaurants(id),
                name TEXT NOT NULL, category TEXT NOT NULL, price INTEGER NOT NULL,
                available INTEGER NOT NULL DEFAULT 1);
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY, customer TEXT NOT NULL, restaurant_id TEXT NOT NULL,
                menu_id TEXT NOT NULL, qty INTEGER NOT NULL, total INTEGER NOT NULL,
                priority TEXT NOT NULL, status TEXT NOT NULL, restaurant_name TEXT NOT NULL,
                menu_name TEXT NOT NULL, history_seq INTEGER);
            CREATE TABLE IF NOT EXISTS locations (
                name TEXT PRIMARY KEY, lat REAL NOT NULL, lon REAL NOT NULL, type TEXT NOT NULL DEFAULT 'HUB');
            CREATE TABLE IF NOT EXISTS roads (
                from_loc TEXT NOT NULL REFERENCES locations(name), to_loc TEXT NOT NULL REFERENCES locations(name),
                distance REAL NOT NULL, travel_time REAL NOT NULL, PRIMARY KEY (from_loc, to_loc));
            """)
            existing = []
            for info in self.conn.execute("PRAGMA table_info(orders)"):
                existing.append(info[1])  # kolom ke-1 = nama kolom
            for column, sql_type in self.ORDER_COLUMNS:
                if column not in existing:
                    self.conn.execute(f"ALTER TABLE orders ADD COLUMN {column} {sql_type}")

    def save_restaurant(self, r):
        with self.conn:
            self.conn.execute("""
                INSERT INTO restaurants (id, name, location, category) VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET name = excluded.name, location = excluded.location,
                    category = excluded.category""", (r.id, r.name, r.location, r.category))

    def delete_restaurant(self, restaurant_id):
        with self.conn:  # satu transaksi; menu dulu karena ada foreign key menus -> restaurants
            self.conn.execute("DELETE FROM menus WHERE restaurant_id = ?", (restaurant_id,))
            self.conn.execute("DELETE FROM restaurants WHERE id = ?", (restaurant_id,))

    def save_menu(self, m):
        with self.conn:
            self.conn.execute("""
                INSERT INTO menus (id, restaurant_id, name, category, price, available) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET name = excluded.name, category = excluded.category,
                    price = excluded.price, available = excluded.available""",
                (m.id, m.restaurant_id, m.name, m.category, m.price, int(m.available)))

    def delete_menu(self, menu_id):
        with self.conn:
            self.conn.execute("DELETE FROM menus WHERE id = ?", (menu_id,))

    def save_order(self, o):
        # history_seq = urutan masuk history stack, dipakai untuk menyusun ulang stack saat load
        seq = None
        if o.status in ("DONE", "CANCELLED"):
            row = self.conn.execute("SELECT history_seq FROM orders WHERE id = ?", (o.id,)).fetchone()
            if row and row[0]:
                seq = row[0]
            else:
                seq = self.conn.execute("SELECT COALESCE(MAX(history_seq), 0) + 1 FROM orders").fetchone()[0]
        route_text = None
        if o.route:
            route_text = "|".join(o.route)
        with self.conn:
            self.conn.execute("""
                INSERT INTO orders (id, customer, restaurant_id, menu_id, qty, total, priority, status,
                    restaurant_name, menu_name, history_seq, delivery_location, distance_km, eta_min,
                    route, delivery_fee, list_insert)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET status = excluded.status, history_seq = excluded.history_seq""",
                (o.id, o.customer, o.restaurant_id, o.menu_id, o.qty, o.total, o.priority, o.status,
                 o.restaurant_name, o.menu_name, seq, o.delivery_location, o.distance_km, o.eta_min,
                 route_text, o.delivery_fee, o.insert_at))

    def delete_order(self, order_id):
        with self.conn:
            self.conn.execute("DELETE FROM orders WHERE id = ?", (order_id,))

    def save_location(self, name, lat, lon, kind):
        with self.conn:
            self.conn.execute("""
                INSERT INTO locations (name, lat, lon, type) VALUES (?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET lat = excluded.lat, lon = excluded.lon, type = excluded.type""",
                (name, lat, lon, kind))

    def save_road(self, a, b, distance, minutes):
        with self.conn:
            self.conn.execute("""
                INSERT INTO roads (from_loc, to_loc, distance, travel_time) VALUES (?, ?, ?, ?)
                ON CONFLICT(from_loc, to_loc) DO UPDATE SET distance = excluded.distance,
                    travel_time = excluded.travel_time""", (a, b, distance, minutes))

    def rows(self, sql):
        return self.conn.execute(sql).fetchall()

    def count(self, table):
        return self.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    def close(self):
        self.conn.close()
