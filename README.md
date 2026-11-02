# Smart Food Delivery & Order Management System

Aplikasi Streamlit untuk UAS Data Structure, Kelompok 2. Ini lanjutan langsung dari project UTS. Semua struktur data inti ditulis sendiri sebagai class, tanpa `heapq`, `queue`, atau `collections.deque`. Penjelasan desain, kompleksitas, dan pseudocode untuk laporan ada di [docs/design.md](docs/design.md).

Dokumentasi lain:

- [docs/panduan-menu.md](docs/panduan-menu.md): cara memakai setiap menu, fungsi yang dipanggil, skenario demo end-to-end, dan contoh pertanyaan Technical Defense.
- [docs/referensi-fungsi.md](docs/referensi-fungsi.md): penjelasan setiap class, fungsi, dan method beserta kompleksitasnya.
- [docs/Laporan_UAS_Kelompok2_Smart_Food_Delivery.docx](docs/Laporan_UAS_Kelompok2_Smart_Food_Delivery.docx): draf laporan IMRAD. Bagian yang disorot kuning wajib diisi kelompok.

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
| `python -m pytest` | 72 tes: 22 skenario uji, 26 tes struktur data, 10 tes data contoh, dan 14 tes halaman app |
| `python cli.py test` | Tabel testing plan (format laporan, Bagian 10 panduan) |
| `python cli.py bench` | Tabel benchmark n = 1.000, 10.000, 100.000 |
| `python cli.py demo` | Alur demo di database sementara, untuk disalin ke laporan |
| `python cli.py check-db` | Jumlah data di database asli |

Halaman **Testing** dan **Benchmark** di aplikasi menampilkan hasil yang sama.

## Struktur folder

Susunan folder mengikuti Bagian 6.1 panduan (Struktur Folder yang Disarankan).

```
smart_food_delivery/
├── app.py                  # entry point Streamlit & navigasi
├── requirements.txt
├── cli.py                  # perintah terminal: test, bench, demo, check-db
├── run_tunnel.sh           # Streamlit + Cloudflare Quick Tunnel
├── core/                   # logika murni (tanpa Streamlit)
│   ├── structures/
│   │   ├── dynamic_array.py
│   │   ├── linked_list.py
│   │   ├── stack.py
│   │   ├── queue.py
│   │   ├── heap.py
│   │   ├── hash_table.py
│   │   ├── bst.py
│   │   └── graph.py
│   ├── algorithms/         # sorting.py, searching.py, recursion.py
│   ├── services.py         # FoodDeliveryService: seluruh fitur sistem
│   ├── models.py           # Restaurant, Menu, Order, konstanta biaya, validasi input
│   ├── database.py         # SQLite dan migrasi kolom
│   ├── seed.py             # membaca data/*.csv, create_service()
│   ├── benchmark.py        # benchmark n = 1.000, 10.000, 100.000
│   └── scenarios.py        # testing plan (23 skenario, 22 otomatis)
├── views/                  # halaman Streamlit per fitur (page_*.py) dan helper tampilan
├── tests/                  # pytest
├── data/                   # data awal CSV: lokasi, jalan, restoran, menu, order demo
├── docs/                   # desain teknis, panduan menu, referensi fungsi
├── assets/                 # CSS dan logo
└── .streamlit/config.toml  # tema
```

| File | Isi | Tim |
|---|---|---|
| `core/structures/dynamic_array.py` | Dynamic Array untuk daftar restoran dan menu (materi UTS) | semua tim |
| `core/structures/linked_list.py` | Singly Linked List untuk daftar order (materi UTS) | semua tim |
| `core/structures/stack.py` | Stack untuk history dan undo (materi UTS) | semua tim |
| `core/structures/queue.py` | Queue FIFO untuk order NORMAL (materi UTS) | semua tim |
| `core/structures/hash_table.py` | Hash Table untuk pencarian ID | Team 1 |
| `core/structures/bst.py` | BST katalog menu berdasarkan harga | Team 1 |
| `core/structures/heap.py` | Min-Heap antrean prioritas | Team 2 |
| `core/structures/graph.py` | Peta, Dijkstra, BFS, DFS | Team 2 |
| `core/algorithms/searching.py` | Linear search, binary search | Team 1 |
| `core/algorithms/sorting.py` | Insertion sort, merge sort | Team 3 |
| `core/algorithms/recursion.py` | Statistik rekursif | Team 3 |
| `core/database.py` | SQLite dan migrasi kolom | Team 1 |
| `core/services.py` | `FoodDeliveryService`, seluruh fitur sistem | semua tim |
| `core/seed.py`, `data/*.csv` | Peta contoh, 4 restoran, 10 menu, dan 10 order demo | Team 1, Team 2 |
| `core/benchmark.py`, `core/scenarios.py` | Benchmark dan testing plan | semua tim |
| `app.py`, `views/`, `assets/`, `.streamlit/`, `run_tunnel.sh` | Antarmuka Streamlit dan deployment | Team 2 |
| `tests/` | `test_scenarios.py` (testing plan), `test_structures.py` (tiap struktur data), `test_seed.py` (data contoh), `test_app.py` (halaman app) | semua tim |

Database SQLite disimpan di `smart_food_delivery.db` di folder utama, bukan di `data/`. Folder `data/` hanya berisi data awal yang dibaca saat aplikasi pertama kali dibuka atau saat tombol **Isi data contoh** ditekan.

Paket `core` tidak meng-import Streamlit, jadi bisa dites tanpa membuka aplikasi.

## Cara membaca kode

Susunannya mirip MVC:

| Peran | File | Isi |
|---|---|---|
| Model | `core/models.py`, `core/database.py` | Class `Restaurant`, `Menu`, `Order`, dan penyimpanan SQLite |
| Struktur data | `core/structures/` | Class biasa yang dipakai service untuk menyimpan data |
| Algoritma | `core/algorithms/` | Fungsi sorting, searching, dan recursion |
| Controller | `core/services.py` | Satu class `FoodDeliveryService`. Setiap fitur adalah satu method |
| View | `views/page_*.py` | Satu fungsi per halaman. Hanya membaca input lalu memanggil method service |

`app.py` hanya membuat satu objek service dan menyusun menu. Setiap halaman mengambil objek itu dari `st.session_state.service`.

**Contoh alur: tombol "Buat Order".**

1. `page_create_order()` di `views/page_create_order.py` memanggil `service.create_order(...)`.
2. `create_order()` di `core/services.py` memvalidasi input, mencari restoran dan menu di Hash Table, lalu membuat `Order`.
3. `_enqueue()` di `core/services.py` memasukkan order NORMAL ke `LinkedQueue.enqueue()` (`core/structures/queue.py`) dan order URGENT/HIGH ke `MinHeap.push()` (`core/structures/heap.py`).
4. `save_order()` di `core/database.py` menyimpan order ke SQLite.

Halaman lain mengikuti pola yang sama. Cari nama method yang dipanggil halaman itu, lalu buka method tersebut di `services.py`.

**Mulai dari mana.**

- Team 1: `core/structures/hash_table.py`, `core/structures/bst.py`, `core/algorithms/searching.py`, lalu method `find_*`, `add_*`, `search_keyword`, dan `menus_in_price_range` di `services.py`.
- Team 2: `core/structures/heap.py`, `core/structures/graph.py`, lalu method `create_order`, `next_order`, `process_delivery`, dan `plan_route` di `services.py`.
- Team 3: `core/algorithms/sorting.py`, `core/algorithms/recursion.py`, lalu method `statistics`, `top_menus`, dan `top_restaurants` di `services.py`.

## Pembagian tugas UAS

| Tim | Anggota | Tanggung jawab | Kode | Halaman app |
|---|---|---|---|---|
| Team 1 | Arif, Mitha (dokumentasi), Sigit, Reza | Database, Searching, Katalog Menu | `hash_table.py`, `bst.py`, `searching.py`, `database.py`, method restoran & menu di `services.py` | Restoran & Menu, Cari & Katalog |
| Team 2 | Lucky, Angelica, Alvi, Ryan | Streamlit, Antrean Prioritas Order, Peta Lokasi & Rute Pengiriman | `heap.py`, `graph.py`, method order & peta di `services.py`, `app.py`, `views/`, `run_tunnel.sh` | Buat Order, Antrean & Delivery, Peta & Rute |
| Team 3 | Arbi, Hafiz, Gilang | Fixing Bug, Ranking & Pengurutan, Dashboard | `sorting.py`, `recursion.py`, method statistik & ranking di `services.py` | Dashboard, Statistik & Ranking |

Benchmark, testing plan, dan halaman Visualisasi Struktur, Riwayat & Undo, Benchmark, dan Testing dikerjakan bersama oleh semua tim.

## Pembagian UTS

| Bagian UTS | Anggota | Struktur data |
|---|---|---|
| Sub 1 Restoran & Menu | Arif, Mitha | Dynamic Array |
| Sub 2 Search & Create Order | Lucky, Angelica | Singly Linked List |
| Sub 3 Cancel Order & History | Hafiz, Sigit | Stack |
| Sub 4 Delivery Queue & Priority | Arbi, Alvi | Queue, Priority Queue |
| Sub 5 Undo & Statistics | Reza, Ryan, Gilang | Stack, Recursion |
| Database SQLite | Arif | SQLite |
