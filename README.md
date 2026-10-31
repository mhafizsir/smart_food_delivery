# Smart Food Delivery & Order Management System

Aplikasi Streamlit untuk UAS Data Structure, Kelompok 2. Ini lanjutan langsung dari project UTS. Semua struktur data inti ditulis sendiri sebagai class, tanpa `heapq`, `queue`, atau `collections.deque`. Penjelasan desain, kompleksitas, dan pseudocode untuk laporan ada di [docs/design.md](docs/design.md).

## Menjalankan

Butuh Python 3.9 atau lebih baru.

```
pip install -r requirements.txt
streamlit run app.py
```

Aplikasi terbuka di `http://localhost:8501`. Untuk membuka link publik lewat Cloudflare Quick Tunnel, jalankan `./run_tunnel.sh`. Skrip ini menjalankan Streamlit, lalu mencetak link `https://xxxx.trycloudflare.com`. Di macOS, pasang `cloudflared` dulu dengan `brew install cloudflared`. Di Linux, skrip mengunduhnya sendiri.

Database SQLite dibuat di `smart_food_delivery.db` di folder ini. Untuk memakai file lain, set `SFD_DB_PATH`. Database dari project UTS langsung terbaca, jadi cukup salin file lama ke folder ini.

## Tes, benchmark, dan demo

| Perintah | Hasil |
|---|---|
| `python -m pytest` | 69 tes: 22 skenario uji, 25 tes struktur data, 9 tes data contoh, dan 13 tes halaman app |
| `python cli.py test` | Tabel testing plan (format laporan, Bagian 10 panduan) |
| `python cli.py bench` | Tabel benchmark n = 1.000, 10.000, 100.000 |
| `python cli.py demo` | Alur demo di database sementara, untuk disalin ke laporan |
| `python cli.py check-db` | Jumlah data di database asli |

Halaman **Testing** dan **Benchmark** di aplikasi menampilkan hasil yang sama.

## Struktur folder

| File | Isi | Tim |
|---|---|---|
| `app.py` | Membuat service bersama dan menyusun menu navigasi (`st.navigation`) | Team 2 |
| `.streamlit/config.toml` | Tema: warna, font, sidebar | Team 2 |
| `assets/style.css`, `assets/logo.svg` | Sedikit CSS (jarak halaman, ukuran angka) dan logo | Team 2 |
| `core/linear.py` | Dynamic Array, Singly Linked List, Stack, Queue (materi UTS) | |
| `core/hash_table.py` | Hash Table untuk pencarian ID | Team 1 |
| `core/bst.py` | BST katalog menu berdasarkan harga | Team 1 |
| `core/searching.py` | Linear search, binary search | Team 1 |
| `core/database.py` | SQLite dan migrasi kolom | Team 1 |
| `core/heap.py` | Min-Heap antrean prioritas | Team 2 |
| `core/graph.py` | Peta, Dijkstra, BFS, DFS | Team 2 |
| `core/sorting.py` | Insertion sort, merge sort | Team 3 |
| `core/recursion.py` | Statistik rekursif | Team 3 |
| `core/models.py` | Restaurant, Menu, Order, konstanta biaya, validasi input | |
| `core/service.py` | `FoodDeliveryService`, seluruh fitur sistem | semua tim |
| `core/seed.py` | Peta contoh, restoran dan menu demo, 10 order demo, `create_service()` | Team 1, Team 2 |
| `core/benchmark.py` | Benchmark | semua tim |
| `core/scenarios.py` | Testing plan | semua tim |
| `ui/common.py`, `ui/map_view.py`, `ui/diagrams.py` | Helper tampilan, peta folium, gambar graphviz | Team 2 |
| `ui/page_*.py` | Satu file per halaman | lihat tabel tim |
| `tests/` | pytest: `test_scenarios.py` (testing plan), `test_structures.py` (tiap struktur data), `test_seed.py` (data contoh), `test_app.py` (halaman app) | |
| `cli.py` | Perintah terminal di atas | |
| `run_tunnel.sh` | Streamlit dan Cloudflare Quick Tunnel | Team 2 |

Paket `core` tidak meng-import Streamlit, jadi bisa dites tanpa membuka aplikasi.

## Cara membaca kode

Susunannya mirip MVC:

| Peran | File | Isi |
|---|---|---|
| Model | `core/models.py`, `core/database.py` | Class `Restaurant`, `Menu`, `Order`, dan penyimpanan SQLite |
| Struktur data | `core/linear.py`, `core/heap.py`, `core/hash_table.py`, `core/bst.py`, `core/graph.py` | Class biasa yang dipakai service untuk menyimpan data |
| Controller | `core/service.py` | Satu class `FoodDeliveryService`. Setiap fitur adalah satu method |
| View | `ui/page_*.py` | Satu fungsi per halaman. Hanya membaca input lalu memanggil method service |

`app.py` hanya membuat satu objek service dan menyusun menu. Setiap halaman mengambil objek itu dari `st.session_state.service`.

**Contoh alur: tombol "Buat Order".**

1. `page_create_order()` di `ui/page_create_order.py` memanggil `service.create_order(...)`.
2. `create_order()` di `core/service.py` memvalidasi input, mencari restoran dan menu di Hash Table, lalu membuat `Order`.
3. `_enqueue()` di `core/service.py` memasukkan order NORMAL ke `LinkedQueue.enqueue()` (`core/linear.py`) dan order URGENT/HIGH ke `MinHeap.push()` (`core/heap.py`).
4. `save_order()` di `core/database.py` menyimpan order ke SQLite.

Halaman lain mengikuti pola yang sama. Cari nama method yang dipanggil halaman itu, lalu buka method tersebut di `service.py`.

**Mulai dari mana.**

- Team 1: `core/hash_table.py`, `core/bst.py`, `core/searching.py`, lalu method `find_*`, `add_*`, `search_keyword`, dan `menus_in_price_range` di `service.py`.
- Team 2: `core/heap.py`, `core/graph.py`, lalu method `create_order`, `next_order`, `process_delivery`, dan `plan_route` di `service.py`.
- Team 3: `core/sorting.py`, `core/recursion.py`, lalu method `statistics`, `top_menus`, dan `top_restaurants` di `service.py`.

## Pembagian tugas UAS

| Tim | Anggota | Tanggung jawab | Kode | Halaman app |
|---|---|---|---|---|
| Team 1 | Arif, Mitha (dokumentasi), Sigit, Reza | Database, Searching, Katalog Menu | `hash_table.py`, `bst.py`, `searching.py`, `database.py`, method restoran & menu di `service.py` | Restoran & Menu, Cari & Katalog |
| Team 2 | Lucky, Angelica, Alvi, Ryan | Streamlit, Antrean Prioritas Order, Peta Lokasi & Rute Pengiriman | `heap.py`, `graph.py`, method order & peta di `service.py`, `app.py`, `ui/`, `run_tunnel.sh` | Buat Order, Antrean & Delivery, Peta & Rute |
| Team 3 | Arbi, Hafiz, Gilang | Fixing Bug, Ranking & Pengurutan, Dashboard | `sorting.py`, `recursion.py`, method statistik & ranking di `service.py` | Dashboard, Statistik & Ranking |

Benchmark, testing plan, dan halaman Visualisasi Struktur, Riwayat & Undo, Benchmark, dan Testing dikerjakan bersama oleh semua tim. Kontribusi individu diisi di Lampiran E [docs/design.md](docs/design.md).

## Pembagian UTS

| Bagian UTS | Anggota | Struktur data |
|---|---|---|
| Sub 1 Restoran & Menu | Arif, Mitha | Dynamic Array |
| Sub 2 Search & Create Order | Lucky, Angelica | Singly Linked List |
| Sub 3 Cancel Order & History | Hafiz, Sigit | Stack |
| Sub 4 Delivery Queue & Priority | Arbi, Alvi | Queue, Priority Queue |
| Sub 5 Undo & Statistics | Reza, Ryan, Gilang | Stack, Recursion |
| Database SQLite | Arif | SQLite |
