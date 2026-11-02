# Referensi Fungsi

Dokumen ini menjelaskan setiap class, fungsi, dan method di project, dikelompokkan per file. Setiap baris menyebut kegunaannya, input dan hasilnya, serta kompleksitasnya. Untuk penjelasan per menu aplikasi, lihat [Panduan menu](panduan-menu.md).

Istilah yang dipakai:

- **n** = jumlah data di struktur itu. **V** = jumlah lokasi, **E** = jumlah jalan di peta. **h** = tinggi tree. **k** = jumlah hasil.
- **Pesan** = string yang diawali `Sukses:` atau `Gagal:`. Halaman menampilkannya sebagai notifikasi hijau atau merah.
- **(hasil, error)** = tuple dua nilai. Kalau berhasil, `error` berisi `None`. Kalau gagal, `hasil` berisi `None` dan `error` berisi pesan `Gagal: ...`.
- **key** = fungsi yang memberi tahu struktur data nilai apa yang dibandingkan. Contoh: `key=lambda menu: menu.price` membuat menu dibandingkan berdasarkan harga.

## Struktur data (`core/structures/`)

Empat file pertama adalah materi UTS.

### `core/structures/dynamic_array.py`

**`DynamicArray`**: array berkapasitas tetap yang digandakan saat penuh. Dipakai untuk daftar restoran dan menu.

| Method | Kegunaan | Hasil | Kompleksitas |
|---|---|---|---|
| `append(item)` | Tambah di akhir. Kalau penuh, kapasitas digandakan dulu (`_resize`). | - | O(1) amortized, O(n) saat resize |
| `array[i]` (`__getitem__`) | Ambil elemen ke-i. Index di luar `len` menimbulkan `IndexError`. | elemen | O(1) |
| `index_of(predicate)` | Linear search: index elemen pertama yang cocok. | index, atau -1 | O(n) |
| `find(predicate)` | Seperti `index_of`, tetapi mengembalikan elemennya. | elemen, atau `None` | O(n) |
| `remove_at(index)` | Hapus elemen ke-i, elemen sesudahnya digeser ke kiri. | elemen yang dihapus | O(n) |
| `remove_where(predicate)` | Hapus semua elemen yang cocok dalam satu kali jalan. | jumlah yang dihapus | O(n) |
| `capacity` | Kapasitas saat ini (property, dibaca tanpa kurung). | angka | O(1) |
| `slot(index)` | Isi slot mentah, termasuk slot kosong. Dipakai halaman Visualisasi. | elemen atau `None` | O(1) |
| `to_list()`, `clear()`, `len()`, `for x in array` | Salin ke list, kosongkan, jumlah elemen, telusuri. | | O(n), O(1), O(1), O(n) |

### `core/structures/linked_list.py`

**`SinglyLinkedList`**: rantai node dengan pointer `head` dan `tail`. Dipakai untuk semua order.

| Method | Kegunaan | Hasil | Kompleksitas |
|---|---|---|---|
| `insert_front(data)` | Tambah node baru di head. | - | O(1) |
| `insert_back(data)` | Tambah node baru di tail. Dipakai `LinkedQueue.enqueue`. | - | O(1) karena ada pointer tail |
| `search(predicate)` | Telusuri dari head, kembalikan data pertama yang cocok. | data, atau `None` | O(n) |
| `find_all(predicate)` | Semua data yang cocok. | list | O(n) |
| `remove_front()` | Hapus node head. | data, atau `None` | O(1) |
| `remove(predicate)` | Hapus node pertama yang cocok dan perbaiki pointer tail. | data, atau `None` | O(n) |
| `to_list()`, `clear()`, `is_empty()` | Salin ke list, kosongkan, cek kosong. | | O(n), O(1), O(1) |

### `core/structures/stack.py`

**`Stack`**: LIFO. Dipakai untuk history order dan undo.

| Method | Kegunaan | Hasil | Kompleksitas |
|---|---|---|---|
| `push(item)` | Taruh di puncak. | - | O(1) |
| `pop()` | Ambil dan hapus dari puncak. | item, atau `None` kalau kosong | O(1) |
| `peek()` | Lihat puncak tanpa menghapus. | item, atau `None` | O(1) |
| `to_list()` | Isi dari puncak ke dasar. `for x in stack` memakai urutan yang sama. | list | O(n) |

### `core/structures/queue.py`

**`LinkedQueue`**: FIFO berbasis `SinglyLinkedList`. Dipakai untuk antrean order NORMAL dan untuk BFS.

| Method | Kegunaan | Hasil | Kompleksitas |
|---|---|---|---|
| `enqueue(item)` | Masuk di belakang (rear). | - | O(1) |
| `dequeue()` | Keluar dari depan (front). | item, atau `None` | O(1) |
| `peek()` | Lihat item terdepan. | item, atau `None` | O(1) |
| `remove(item)` | Keluarkan item tertentu. Dipakai saat order dibatalkan. | posisi lama, atau -1 | O(n) |
| `insert_at(position, item)` | Kembalikan item ke posisi tertentu. Dipakai undo. | - | O(n) |

### `core/structures/heap.py`

**`MinHeap(key)`**: binary min-heap di atas array. Key terkecil selalu di index 0. Anak index i ada di 2i + 1 dan 2i + 2, parent-nya di (i - 1) // 2. Dipakai untuk antrean URGENT dan HIGH (key = `priority_key`) dan untuk Dijkstra (key = jarak).

| Method | Kegunaan | Hasil | Kompleksitas |
|---|---|---|---|
| `push(item)` | Tambah di akhir array, lalu `_sift_up`. | - | O(log n) |
| `pop()` | Ambil akar (key terkecil). Elemen terakhir dipindah ke akar, lalu `_sift_down`. | item, atau `None` | O(log n) |
| `peek()` | Lihat akar. | item, atau `None` | O(1) |
| `remove(item)` | Hapus item tertentu. Dipakai saat order dibatalkan. | item, atau `None` | O(n) cari + O(log n) perbaiki |
| `in_order()` | Urutan keluar tanpa mengubah heap asli. Bekerja pada salinan. | list | O(n log n) |
| `as_array()` | Isi array apa adanya, untuk gambar heap. | list | O(n) |
| `is_valid()` | Cek setiap parent tidak lebih besar dari anaknya. Dipakai tes. | bool | O(n) |
| `_sift_up(i)` | Heapify ke atas: tukar dengan parent selama key lebih kecil. | - | O(log n) |
| `_sift_down(i)` | Heapify ke bawah: tukar dengan anak terkecil sampai urutan benar. | - | O(log n) |

### `core/structures/hash_table.py`

**`HashTable(capacity=8)`**: separate chaining. Setiap bucket berisi list pasangan `[key, value]`. Dipakai untuk indeks ID restoran dan ID menu.

| Method | Kegunaan | Hasil | Kompleksitas |
|---|---|---|---|
| `bucket_index(key)` | Nomor bucket. Polynomial rolling hash: untuk setiap karakter, kode = kode x 31 + nilai karakter, lalu modulo jumlah bucket. Hasilnya selalu sama di setiap proses, berbeda dengan `hash()` bawaan Python. | angka | O(panjang key) |
| `insert(key, value)` | Simpan. Kalau key sudah ada, nilainya diganti. Kalau load factor > 0,75, jumlah bucket digandakan (`_resize`). | - | O(1) rata-rata |
| `search(key)` | Cari di bucket yang sesuai. `key in table` memakai method ini. | value, atau `None` | O(1) rata-rata, O(n) terburuk |
| `delete(key)` | Hapus. | value lama, atau `None` | O(1) rata-rata |
| `load_factor()` | Jumlah data / jumlah bucket. | angka | O(1) |
| `collisions()` | Jumlah data yang berbagi bucket dengan data lain. | angka | O(jumlah bucket) |
| `longest_chain()` | Panjang bucket terpanjang. | angka | O(jumlah bucket) |
| `buckets()` | Daftar key di setiap bucket, untuk tabel visualisasi. | list | O(n + jumlah bucket) |
| `_resize(capacity)` | Rehash: pindahkan semua pasangan ke bucket baru. | - | O(n) |

### `core/structures/bst.py`

**`BST(key)`**: Binary Search Tree. Setiap `BSTNode` menyimpan satu key dan list `items` berisi semua data dengan key itu. Dipakai untuk katalog menu dengan key harga.

| Method | Kegunaan | Hasil | Kompleksitas |
|---|---|---|---|
| `insert(item)` | Iteratif. Turun ke kiri kalau key lebih kecil, ke kanan kalau lebih besar. Key yang sama masuk ke node yang sudah ada. | - | O(log n) rata-rata, O(n) terburuk |
| `search(key)` | Cari node dengan key itu. | list item, atau list kosong | O(h) |
| `delete(item, key=None)` | Hapus satu item. Kalau node menjadi kosong, node dilepas. Node dengan dua anak diganti successor (node terkecil di subtree kanan). Isi `key` kalau key item sudah berubah, seperti saat harga diubah. | bool | O(h) |
| `traverse(order)` | Rekursif. `"inorder"` (kiri, node, kanan) menghasilkan urutan menaik. `"preorder"` dimulai dari akar. `"postorder"` berakhir di akar. | list item | O(n), kedalaman O(h) |
| `search_range(low, high)` | Rekursif. Semua item dengan key di antara low dan high, menaik. Subtree di luar rentang tidak dikunjungi. | list item | O(h + k) |
| `height()` | Rekursif. Tinggi tree. Tree kosong = 0. | angka | O(n) |
| `len(tree)`, `node_count` | Jumlah item, jumlah node. | angka | O(1) |

### `core/structures/graph.py`

**`haversine_km(a, b)`**: jarak garis lurus antara dua koordinat (lat, lon) di permukaan bumi, dalam km. Dipakai untuk menghitung jarak jalan baru secara otomatis.

**`Graph`**: graph tidak berarah berbobot dengan adjacency list. `adjacency` memetakan nama lokasi ke list edge `{"to", "distance", "minutes"}`.

| Method | Kegunaan | Hasil | Kompleksitas |
|---|---|---|---|
| `add_node(name, lat, lon, kind)` | Tambah lokasi dengan koordinat dan tipe (RESTAURANT, CUSTOMER, HUB). | - | O(1) |
| `add_edge(a, b, distance, minutes)` | Tambah jalan dua arah. | - | O(1) |
| `find(text)` | Cari nama lokasi tanpa membedakan huruf besar dan kecil. | nama, atau `None` | O(V) |
| `has_edge(a, b)` | Cek jalan sudah ada. | bool | O(derajat a) |
| `edges()` | Semua jalan, masing-masing sekali. | list `(a, b, km, menit)` | O(V + E) |
| `nodes()` | Semua nama lokasi. | list | O(V) |
| `dijkstra(start, end)` | Rute jarak terpendek, memakai `MinHeap` buatan sendiri. Entri lama yang sudah diperbaiki dilewati. | `(path, km, menit)`, atau `None` kalau tidak terhubung | O((V + E) log V) |
| `bfs(start)` | Breadth-First Search memakai `LinkedQueue`. | list `(lokasi, jumlah_hop)` | O(V + E) |
| `bfs_path(start, end)` | Rute dengan ruas jalan paling sedikit, bukan jarak terpendek. | list lokasi, atau `None` | O(V + E) |
| `dfs(start)` | Depth-First Search rekursif. Semua lokasi yang terhubung dengan start. | list lokasi | O(V + E), kedalaman sampai V |
| `is_connected(a, b)` | Cek b terjangkau dari a, memakai `dfs`. | bool | O(V + E) |

## Algoritma (`core/algorithms/`)

### `core/algorithms/sorting.py`

| Fungsi | Kegunaan | Kompleksitas |
|---|---|---|
| `insertion_sort(items, key)` | Ambil satu elemen, geser elemen yang lebih besar ke kanan, sisipkan di tempatnya. Bekerja pada salinan, jadi data asli tidak berubah. Stabil. | O(n²), O(n) kalau data sudah terurut |
| `merge_sort(items, key)` | Rekursif. Bagi dua, urutkan setiap paruh, lalu gabungkan. Base case: 0 atau 1 elemen. Stabil. | O(n log n) di semua kasus, memori O(n) |

Stabil artinya dua data dengan key sama tetap dalam urutan aslinya.

### `core/algorithms/searching.py`

| Fungsi | Kegunaan | Hasil | Kompleksitas |
|---|---|---|---|
| `linear_search(items, target, key)` | Cek satu per satu dari awal. Data tidak perlu terurut. | index, atau -1 | O(n) |
| `binary_search(sorted_items, target, key)` | Bandingkan dengan elemen tengah, buang separuh yang tidak mungkin. Data wajib terurut. | index, atau -1 | O(log n) |
| `binary_search_first(sorted_items, target, key)` | Lower bound: index elemen pertama yang key-nya tidak lebih kecil dari target. Dipakai untuk mencari menu berdasarkan awalan nama. | index (0 sampai n) | O(log n) |

### `core/algorithms/recursion.py`

| Fungsi | Kegunaan | Base case | Recursive case | Kompleksitas |
|---|---|---|---|---|
| `recursive_sum(items, value)` | Jumlahkan `value(item)` untuk semua item. | Rentang kosong = 0. Satu elemen = nilainya. | Jumlah paruh kiri + jumlah paruh kanan. | O(n) waktu, kedalaman O(log n) |
| `recursive_group(items, group, amount)` | Seperti `recursive_sum`, tetapi per kelompok. Item yang `group`-nya `None` tidak dihitung. | Rentang kosong = `{}`. Satu elemen = `{kelompok: nilai}`. | Gabungkan dict paruh kiri dan kanan. | O(n) waktu, kedalaman O(log n) |

Membagi dua rentang setiap panggilan membuat kedalaman call stack hanya sekitar 17 untuk 100.000 order. Versi UTS maju satu index per panggilan, jadi kedalamannya n dan gagal di atas sekitar 1.000 order.

## Model dan penyimpanan (`core/`)

### `core/models.py`

| Nama | Kegunaan |
|---|---|
| `Restaurant` | Data restoran: `id`, `name`, `location` (nama titik di peta), `category`. |
| `Menu` | Data menu: `id`, `restaurant_id`, `name`, `category`, `price`, `available`. |
| `Order` | Data order: `id`, `customer`, restoran, menu, `qty`, `total`, `priority`, `status` (PENDING, DONE, CANCELLED), dan data rute (`route`, `distance_km`, `eta_min`, `delivery_fee`). Nama restoran dan menu disalin, jadi history tetap utuh kalau restoran dihapus. |
| `priority_key(order)` | Key heap: `(level prioritas, ID)`. URGENT = 0, HIGH = 1, NORMAL = 2. ID sebagai tie-break membuat prioritas sama tetap FIFO. |
| `parse_text(value, label)` | Validasi teks tidak kosong. Gagal: `ValueError` dengan pesan yang jelas. |
| `parse_identifier(value, label)` | Validasi ID berupa teks atau bilangan bulat. |
| `parse_positive_int(value, label)` | Validasi bilangan bulat lebih dari 0. Teks angka seperti `"3"` diterima. |
| `is_fail(message)` | Cek pesan diawali `Gagal`. |
| Konstanta | `PRIORITY_FEE` (URGENT Rp10.000, HIGH Rp5.000), `PRIORITY_STREAK_LIMIT` = 3, `AVG_SPEED_KMH` = 25, `ROAD_FACTOR` = 1,3, `DELIVERY_BASE_FEE` = Rp5.000, `DELIVERY_FEE_PER_KM` = Rp2.000. |

### `core/database.py`

**`Database(path)`**: penyimpanan permanen SQLite. Path `":memory:"` membuat database sementara di memori, dipakai oleh tes. Lokasi file diatur variabel lingkungan `SFD_DB_PATH`.

| Method | Kegunaan |
|---|---|
| `__init__` | Buat tabel `restaurants`, `menus`, `orders`, `locations`, `roads` kalau belum ada. Kolom rute di tabel `orders` ditambahkan dengan `ALTER TABLE`, supaya database versi UTS tetap terbaca. |
| `save_restaurant`, `save_menu`, `save_location`, `save_road` | Simpan atau perbarui satu baris. |
| `save_order(order)` | Simpan order. Order DONE atau CANCELLED diberi `history_seq` (urutan masuk history), supaya stack history bisa disusun ulang saat load. |
| `delete_restaurant(id)` | Hapus restoran beserta semua menunya. |
| `delete_menu(id)`, `delete_order(id)` | Hapus satu baris. |
| `rows(sql)`, `count(table)` | Jalankan query baca, hitung baris tabel. |

## Service (`core/services.py`)

**`FoodDeliveryService(db_path)`**: satu objek yang memegang semua struktur data dan semua fitur. Tidak memakai Streamlit, jadi bisa dites tanpa membuka aplikasi.

Atribut utama:

| Atribut | Struktur | Isi |
|---|---|---|
| `restaurants`, `menus` | `DynamicArray` | Data utama, urut pendaftaran |
| `restaurant_index`, `menu_index` | `HashTable` | ID ke objek |
| `menu_catalog` | `BST` | Menu dengan key harga |
| `orders` | `SinglyLinkedList` | Semua order, terbaru di head |
| `normal_queue` | `LinkedQueue` | Order NORMAL yang PENDING |
| `priority_queue` | `MinHeap` | Order URGENT dan HIGH yang PENDING |
| `history` | `Stack` | Order DONE dan CANCELLED, terbaru di puncak |
| `actions` | `Stack` | Aksi yang bisa di-undo |
| `map` | `Graph` | Lokasi dan jalan |
| `priority_streak` | angka | Order prioritas yang diproses berturut-turut |

**Load (Team 1).**

| Method | Kegunaan |
|---|---|
| `load()` | Kosongkan semua struktur, lalu bangun ulang dari database. Order dimuat urut ID ke head linked list. Order PENDING masuk antrean lagi. History disusun dari `history_seq`. Kuota prioritas dihitung ulang dari history. Dipanggil otomatis saat service dibuat. |

**Restoran dan menu (Team 1).** Semua method yang mengubah data mengembalikan pesan.

| Method | Kegunaan | Struktur yang dipakai |
|---|---|---|
| `find_restaurant(id)`, `find_menu(id)` | Cari per ID. Hasil: objek, atau `None`. | Hash Table, O(1) |
| `add_restaurant(id, name, location, category)` | Validasi, tolak ID duplikat, simpan. Nama lokasi disesuaikan dengan penulisan di peta. | Array, Hash Table |
| `delete_restaurant(id)` | Tolak kalau ada order PENDING. Hapus restoran dan semua menunya. | Linked List (cek order), Hash Table, BST, Array |
| `add_menu(id, restaurant_id, name, category, price)` | Validasi, tolak ID duplikat dan restoran yang tidak ada, simpan. | Array, Hash Table, BST |
| `update_menu(id, name, category, price, available)` | Validasi semua field dulu, baru ubah. Kalau harga berubah, node dipindah di BST. | Hash Table, BST |
| `delete_menu(id)` | Hapus menu. | Array, Hash Table, BST |
| `search_keyword(keyword)` | Pencarian UTS pada ID, nama, kategori, dan lokasi. Hasil: `(restoran, menu)`. | Linear search, O(n) |
| `menus_in_price_range(low, high)` | Menu di rentang harga, menaik. | BST `search_range` |
| `menus_sorted_by_name(algorithm)` | Semua menu diurutkan berdasarkan nama, tanpa membedakan huruf besar dan kecil. Default `merge_sort`. | Sorting |

**Peta dan rute (Team 2).**

| Method | Kegunaan |
|---|---|
| `add_location(name, lat, lon, kind)` | Validasi koordinat dan tipe, simpan lokasi. Hasil: pesan. |
| `add_road(a, b, distance, minutes)` | Validasi, tolak jalan ganda. Jarak kosong dihitung dari haversine x 1,3. Waktu kosong dihitung dari 25 km per jam. Hasil: pesan. |
| `delivery_fee(km)` | Rp5.000 + Rp2.000 per km, dibulatkan ke Rp500 terdekat. |
| `route_between(start, end)` | Dijkstra antar dua lokasi. Hasil: `(route, error)`. `route` berisi `path`, `distance_km`, `eta_min`, `fee`. |
| `plan_route(restaurant_id, destination)` | Seperti `route_between`, dimulai dari lokasi restoran. |

**Order dan antrean (Team 2).**

| Method | Kegunaan | Hasil |
|---|---|---|
| `create_order(customer, restaurant_id, menu_id, qty, priority, destination)` | Validasi, hitung total dan rute, simpan di head linked list, masukkan ke antrean, catat undo, simpan ke database. | `(order, error)` |
| `find_order(id)` | Cari order per ID di linked list. | order, atau `None` |
| `orders_by_customer(name)` | Semua order milik satu customer. | list |
| `cancel_order(id)` | Hanya untuk order PENDING. Keluarkan dari antrean, status CANCELLED, push ke history, catat undo beserta posisi lama. | pesan |
| `is_normal_turn()` | Benar kalau kuota prioritas sudah 3 dan kedua antrean sama-sama berisi. | bool |
| `next_order()` | Order yang akan diproses berikutnya, tanpa mengeluarkannya. | order, atau `None` |
| `process_delivery()` | Ambil order berikutnya (heap atau queue sesuai aturan), status DONE, push ke history, catat undo, perbarui kuota. | `(order, error)` |
| `undo()` | Batalkan aksi terakhir di stack `actions`. Lihat [Riwayat & Undo](panduan-menu.md#riwayat--undo). | pesan |
| `_enqueue(order)` | NORMAL ke `normal_queue`, URGENT dan HIGH ke `priority_queue`. | - |

**Statistik dan ranking (Team 3).**

| Method | Kegunaan |
|---|---|
| `orders_array()` | Salin linked list order ke `DynamicArray`, urut ID dengan `merge_sort`. Dipakai sebagai input rekursi. |
| `statistics()` | Dict berisi `total`, `pending`, `done`, `cancelled`, `sales` (dari order DONE), `orders_per_restaurant` (semua status), `menus_sold` (porsi dari order DONE). Dihitung dengan `recursive_sum` dan `recursive_group`. |
| `top_menus(limit)`, `top_restaurants(limit)` | Hasil statistik diurutkan menurun dengan `merge_sort`, diambil `limit` teratas. |
| `check_db()` | Jumlah baris setiap tabel database. |

Fungsi kecil di akhir file (`count_pending`, `count_done`, `count_cancelled`, `sales_of`, `restaurant_of`, `count_one`, `menu_label_if_done`, `quantity_of`) dipakai sebagai parameter `value` dan `group` untuk fungsi rekursif. `contains_keyword` dipakai `search_keyword`. `menu_name_key` adalah key pengurutan nama menu.

## Data contoh, benchmark, dan tes (`core/`)

### `core/seed.py`

| Nama | Kegunaan |
|---|---|
| `read_csv(name)` | Baca `data/<name>.csv` menjadi list of dict, satu dict per baris. |
| `data/locations.csv`, `data/roads.csv` | Peta contoh Jakarta Selatan: 12 lokasi dan 17 jalan. |
| `data/restaurants.csv`, `data/menus.csv` | 4 restoran dan 10 menu contoh. |
| `data/orders.csv` | 10 order contoh dengan semua prioritas, 7 di antaranya dengan lokasi antar. Kolom `destination` kosong artinya tanpa rute. |
| `DEMO_CANCELLED_CUSTOMER`, `DEMO_DELIVERIES` | Order Dodi dibatalkan, lalu 5 order diproses. |
| `create_service(db_path)` | Buat service dan isi peta contoh kalau peta masih kosong. Dipakai `app.py`, `cli.py`, dan tes. |
| `seed_demo_data(service)` | Tambah restoran dan menu contoh. ID yang sudah ada dilewati. Hasil: pesan. |
| `seed_demo_orders(service)` | Buat 10 order contoh, batalkan order Dodi, proses 5 order, lalu kosongkan stack undo. Dilewati kalau sudah ada order. Hasil: pesan. |

### `core/benchmark.py`

| Nama | Kegunaan |
|---|---|
| `benchmark(sizes, seed)` | Ukur semua operasi untuk n = 1.000, 10.000, 100.000. Hasil: list baris tabel. |
| `record(...)` | Tambah satu baris hasil, waktu dalam milidetik. |
| `record_quadratic(...)` | Ukur operasi O(n²) sampai n = 10.000. Di atas itu waktunya diestimasi dari (n / 10.000)². |
| `uts_list_queue(data)` | Antrean prioritas cara UTS (list diurutkan ulang setiap insert), sebagai pembanding heap. |
| `sorted_bst(data)` | BST dari data terurut (kasus terburuk, tree miring). |
| `heap_queue(data)` | n push lalu n pop pada `MinHeap`. |

### `core/scenarios.py`

`TEST_SCENARIOS` berisi 22 skenario otomatis. Setiap baris berisi nomor, kategori, skenario, hasil yang diharapkan, dan fungsi tes `_t_*`. Setiap fungsi tes membuat service baru dengan database `:memory:` dan mengembalikan `(lulus, detail)`. `run_test_scenarios(skip_slow)` menjalankan semuanya untuk halaman Testing dan `cli.py test`. Skenario 15 (akses URL Cloudflare) dicek manual saat demo.

## Antarmuka (`app.py` dan `views/`)

### `app.py`

| Nama | Kegunaan |
|---|---|
| `get_service()` | Buat `FoodDeliveryService` satu kali (`@st.cache_resource`). Semua pengunjung memakai service dan database yang sama, jadi ID order tidak bentrok. |
| `pages` | Daftar menu sidebar per kelompok (Operasional, Restoran, Struktur Data), dibuat dengan `st.Page` dan `st.navigation`. |

Setiap kali halaman dibuka, `app.py` menyimpan service ke `st.session_state.service`, menampilkan notifikasi dari aksi sebelumnya (`show_flash`), lalu menjalankan halaman yang dipilih.

### `views/common.py`

| Fungsi | Kegunaan |
|---|---|
| `page_header(title, subtitle)` | Judul dan keterangan halaman. |
| `section_picker(sections, key)` | Tombol pilihan bagian di bawah judul halaman. Pilihan disimpan di `st.session_state`, jadi halaman tetap di bagian yang sama setelah rerun. Dipakai sebagai pengganti `st.tabs`, yang kadang kembali ke tab pertama. |
| `show_table(frame, empty_message)` | Tampilkan tabel, atau pesan kalau kosong. Kolom Harga, Ongkir, dan Total diberi format Rupiah. Kolom Jarak dan ETA diberi satuan. Isinya tetap angka, jadi klik judul kolom mengurutkan sebagai angka. |
| `order_table`, `menu_table`, `restaurant_table` | Ubah list data menjadi tabel pandas. |
| `rupiah(value)` | Format angka menjadi `Rp41.500`. |
| `flash(message)`, `flash_and_rerun(message)`, `show_flash()` | Simpan pesan, jalankan ulang halaman, lalu tampilkan pesan sebagai notifikasi hijau, kuning, atau merah. |
| `order_label`, `priority_label` | Teks pilihan di dropdown order dan prioritas. |
| `warn_recursion()` | Peringatan kalau traversal rekursif melewati batas rekursi Python. |

### `views/map_view.py` dan `views/diagrams.py`

| Fungsi | Kegunaan |
|---|---|
| `build_map`, `show_map` | Gambar peta folium: jalan abu-abu, rute hijau, penanda lokasi. |
| `path_km(graph, path)` | Total jarak satu rute, untuk tabel pembanding BFS. |
| `show_chain` | Gambar linked list, stack, atau queue sebagai rantai node (graphviz). |
| `show_heap` | Gambar heap sebagai tree, ditambah tabel isi array beserta index-nya. |
| `bst_dot` | Gambar BST sebagai tree. Node digambar per level memakai `LinkedQueue` buatan sendiri. |

### `views/page_*.py`

Setiap file berisi satu fungsi halaman tanpa parameter, misalnya `page_dashboard()`. Fungsi itu mengambil service dari `st.session_state.service`, menampilkan form dan tabel, lalu memanggil method service saat tombol ditekan. Penjelasan setiap halaman ada di [Panduan menu](panduan-menu.md).

## Perintah terminal (`cli.py`)

| Perintah | Kegunaan |
|---|---|
| `python cli.py demo` | Alur demo di database sementara. Hasilnya bisa disalin ke laporan. |
| `python cli.py bench` | Tabel benchmark. |
| `python cli.py test` | Tabel testing plan. |
| `python cli.py check-db` | Jumlah baris di database asli. |
