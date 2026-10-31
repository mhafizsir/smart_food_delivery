# Desain Teknis Smart Food Delivery (UAS Data Structure, Kelompok 2)

Penjelasan struktur data, kompleksitas, dan pseudocode untuk laporan IMRAD. Rujukan "Bagian N panduan" di kode menunjuk ke Panduan UAS.

## 1. Struktur Data Linear (materi UTS, disempurnakan)
Kode: `core/linear.py`.

| Struktur | Dipakai untuk | Operasi utama |
|---|---|---|
| `DynamicArray` | Daftar restoran dan menu (Sub 1) | `append` O(1) amortized: kapasitas digandakan saat penuh. Akses index O(1). Hapus O(n). |
| `SinglyLinkedList` | Semua order (Sub 2), order terbaru di head | `insert_front` dan `insert_back` O(1) karena ada pointer tail. Search O(n). |
| `Stack` | History order selesai/batal (Sub 3) dan Undo (Sub 5) | `push`/`pop` O(1), LIFO |
| `LinkedQueue` | Antrean delivery NORMAL (Sub 4) | `enqueue`/`dequeue` O(1), FIFO. Versi UTS memakai `list.pop(0)` yang O(n). |

## 2. Min-Heap dan Hash Table
Kode: `core/heap.py`, `core/hash_table.py`.

**Penanggung jawab**: Min-Heap (Antrean Prioritas Order) Team 2 (Lucky, Angelica, Alvi, Ryan). Hash Table (Searching) Team 1 (Arif, Mitha, Sigit, Reza).

**Min-Heap** menyimpan order URGENT dan HIGH. Key = `(level prioritas, ID order)` dengan URGENT=0, HIGH=1. Elemen terkecil selalu di root (index 0).
- *Insert*: taruh di ujung array, lalu **sift up** (tukar dengan parent selama lebih kecil). O(log n).
- *Extract*: ambil root, pindahkan elemen terakhir ke root, lalu **sift down** (tukar dengan anak terkecil). O(log n). Proses perbaikan ini disebut **heapify**, ada di method `_sift_up` dan `_sift_down`.
- **Tie-break**: dua order dengan prioritas sama dibandingkan dengan ID. ID lebih kecil berarti dibuat lebih dulu, jadi keluar lebih dulu (FIFO).
- **Anti-starvation**: setelah 3 order URGENT/HIGH berturut-turut diproses, 1 order NORMAL yang menunggu dilayani dulu. Kuota ini dihitung ulang dari history saat data dimuat dari database.
- **Kenapa order NORMAL tidak masuk heap**: semua order NORMAL punya prioritas sama, jadi di heap urutannya hanya ditentukan ID, persis FIFO. Queue memberi urutan yang sama dengan biaya O(1), bukan O(log n). Antrean terpisah juga yang membuat aturan anti-starvation bisa langsung mengambil order NORMAL terdepan. Urutan keseluruhan tetap URGENT → HIGH → NORMAL.

**Hash Table** mencari restoran dan menu berdasarkan ID dalam O(1) rata-rata.
- Fungsi hash: *polynomial rolling hash* `h = (h * 31 + kode_karakter) mod 1.000.000.007`, lalu `mod jumlah_bucket`.
- **Collision** ditangani dengan *separate chaining*: setiap bucket berisi list pasangan key-value.
- **Load factor** = jumlah data / jumlah bucket. Kalau melewati 0,75, jumlah bucket digandakan dan semua key di-*rehash*, sehingga chain tetap pendek. Kalau load factor dibiarkan tinggi, chain memanjang dan pencarian turun menuju O(n).

## 3. Binary Search Tree dan Graph
Kode: `core/bst.py`, `core/graph.py`.

**Penanggung jawab**: BST (Katalog Menu) Team 1 (Arif, Mitha, Sigit, Reza). Graph (Peta Lokasi dan Rute Pengiriman) Team 2 (Lucky, Angelica, Alvi, Ryan).

**BST** menyimpan katalog menu dengan key = harga. Menu berharga sama berada di satu node (list `items`).
- Inorder (kiri, akar, kanan) menghasilkan harga menaik. Preorder dan postorder juga tersedia untuk visualisasi.
- `search_range(min, max)` hanya mengunjungi subtree yang mungkin berisi harga di rentang itu: O(h + k), dengan h = tinggi tree dan k = jumlah hasil.
- Kalau menu dimasukkan dalam urutan harga yang sudah terurut, tree menjadi miring seperti linked list: tinggi = n, operasi menjadi O(n). Insert dan delete ditulis iteratif supaya tree miring tidak membuat crash; traversal tetap rekursif dan kedalamannya = tinggi tree.

**Graph** memodelkan peta: node = lokasi (restoran, hub, area customer), edge = jalan dengan bobot jarak (km) dan waktu (menit). Graph tidak berarah dengan **adjacency list**, karena peta jalan renggang (setiap lokasi hanya terhubung ke beberapa lokasi): memori O(V + E), sedangkan adjacency matrix O(V²).
- **Dijkstra** mencari rute jarak terpendek memakai `MinHeap` buatan sendiri: O((V + E) log V). Jaraknya dipakai untuk estimasi waktu dan **ongkir** (Rp5.000 + Rp2.000/km, dibulatkan ke Rp500).
- **BFS** (memakai `LinkedQueue`) mencari rute dengan transit paling sedikit.
- **DFS** rekursif mencari semua lokasi yang terhubung, dipakai untuk mendeteksi lokasi yang tidak bisa dijangkau.

## 4. Sorting, Searching, dan Recursion
Kode: `core/sorting.py`, `core/searching.py`, `core/recursion.py`.

**Penanggung jawab**: Sorting dan statistik rekursif (Ranking & Pengurutan, Dashboard) Team 3 (Arbi, Hafiz, Gilang). Linear dan binary search (Searching) Team 1 (Arif, Mitha, Sigit, Reza).

| Algoritma | Kompleksitas | Dipakai untuk |
|---|---|---|
| Insertion sort | Ω(n), Θ(n²), O(n²) | Pembanding O(n²) di benchmark, opsi pengurutan ID menu |
| Merge sort | Θ(n log n) semua kasus, memori O(n) | Ranking menu terlaris dan restoran teramai, urutan history saat load |
| Linear search | Ω(1), Θ(n), O(n) | Pencarian kata kunci UTS, pembanding |
| Binary search | Ω(1), Θ(log n), O(log n), data wajib terurut | Mencari ID menu pada daftar ID yang sudah diurutkan |

**Desain recursion** (Bagian 9 panduan):
| Fungsi | Base case | Recursive case | Input | Output | Kompleksitas |
|---|---|---|---|---|---|
| `recursive_sum` (statistik order) | rentang kosong → 0; satu order → nilainya | jumlah paruh kiri + paruh kanan | array order, fungsi nilai | total (jumlah order, penjualan) | waktu O(n), kedalaman stack O(log n) |
| `recursive_group` (order per restoran, menu terjual) | sama seperti di atas | gabungkan dict paruh kiri dan kanan | array order | dict nama → total | waktu O(n · k), stack O(log n) |
| `BST._walk` (traversal) | node kosong | kunjungi subtree kiri dan kanan | root | list menu | waktu O(n), stack O(h) |
| `Graph._dfs` | semua tetangga sudah dikunjungi | kunjungi tetangga yang belum | lokasi awal | lokasi terjangkau | waktu O(V + E), stack sampai O(V) |
| `merge_sort` | panjang ≤ 1 | urutkan dua paruh lalu gabung | list | list terurut | waktu O(n log n), stack O(log n) |

**Alasan memakai recursion**: statistik, traversal tree, DFS, dan merge sort secara alami memecah masalah menjadi submasalah yang sama bentuknya. **Batas call stack**: Python menghentikan rekursi di kedalaman sekitar 1.000 (`RecursionError`). Versi UTS menghitung statistik dengan maju satu index per panggilan, sehingga kedalamannya n dan untuk data di atas sekitar 1.000 order akan mencapai batas itu. Versi UAS membagi dua rentang setiap panggilan, jadi 100.000 order hanya butuh kedalaman sekitar 17. Traversal BST dan DFS tetap bisa melewati batas itu pada tree yang sangat miring atau graph berbentuk rantai panjang.

## 5. Model Data dan Database
Kode: `core/models.py`, `core/database.py`.

**Penanggung jawab**: Database Team 1 (Arif, Mitha, Sigit, Reza).

`Restaurant`, `Menu`, dan `Order` adalah data. Validasi input dilakukan di batas sistem (method publik service), jadi struktur data di dalam tidak perlu memeriksa ulang. Skema SQLite sama dengan versi UTS. Kolom baru untuk rute dan ongkir ditambahkan dengan migrasi `ALTER TABLE`, sehingga database lama tetap terbaca tanpa kehilangan data.

## 6. Service: Seluruh Fitur Sistem
Kode: `core/service.py`, `core/seed.py`.

`FoodDeliveryService` menyimpan semua struktur data dalam satu objek. Streamlit cukup menyimpan objek ini, dan tes membuat objek baru dengan database `":memory:"`.

| Fitur | Method | Struktur data | Tim |
|---|---|---|---|
| Registrasi restoran, kelola menu | `add_restaurant`, `delete_restaurant`, `add_menu`, `update_menu`, `delete_menu` | Dynamic Array + Hash Table + BST, ID duplikat ditolak | Team 1 |
| Pencarian restoran/menu | `search_keyword` (UTS), `find_restaurant`/`find_menu` (Hash Table), `menus_in_price_range` (BST), `sorted_menu_ids` + `binary_search` | | Team 1 |
| Load dari database | `load` | semua struktur dibangun ulang | Team 1 |
| Buat order | `create_order` | Linked List, Queue/Heap, rute Dijkstra | Team 2 |
| Batal order | `cancel_order` | Queue/Heap, Stack history | Team 2 |
| Delivery Queue dan prioritas | `next_order`, `process_delivery` | LinkedQueue + Min-Heap, anti-starvation | Team 2 |
| Order History | `history` | Stack | Team 2 |
| Undo Last Action | `undo` (buat order, batal order, proses delivery) | Stack | Team 2 |
| Peta dan rute | `add_location`, `add_road`, `route_between`, `plan_route`, `map.bfs_path`, `map.dfs` | Graph | Team 2 |
| Statistik | `statistics` | Recursion | Team 3 |
| Ranking | `top_menus`, `top_restaurants` | Merge sort | Team 3 |

Data awal (peta contoh Jakarta Selatan, restoran dan menu demo) dan `create_service()` ada di `core/seed.py`. Tombol **Isi data contoh** di Dashboard juga menambahkan 10 order demo dengan semua prioritas. Satu order dibatalkan dan lima diproses, sehingga dashboard, history, antrean, dan ranking langsung berisi data. Undo stack dikosongkan setelahnya, jadi order demo tidak bisa di-undo. `python cli.py demo` menjalankan alur demo pada database sementara, sehingga hasilnya bisa disalin ke laporan.

## 7. Benchmark
Kode: `core/benchmark.py`, halaman `ui/page_benchmark.py`.

**Penanggung jawab**: semua tim.

Benchmark membandingkan struktur dan algoritma pada n = 1.000, 10.000, dan 100.000 (Bagian 8 panduan). Pencarian diukur per query (rata-rata 200 query). Algoritma O(n²) (insertion sort dan antrean list terurut ala UTS) diukur sampai n = 10.000; nilai untuk n = 100.000 adalah **estimasi** dari hasil n = 10.000 dikali (100.000/10.000)² = 100, karena pengukuran langsung butuh beberapa menit. Ini ditandai di kolom Keterangan.

Cara membaca: kalau n naik 10 kali, O(n) naik sekitar 10 kali, O(n log n) sedikit di atas 10 kali, O(n²) sekitar 100 kali, sedangkan O(1) dan O(log n) hampir tetap. Kesesuaian dengan teori dinilai dari rasio 1.000 → 10.000 yang **diukur**; nilai estimasi hanya ilustrasi dan tidak dipakai sebagai bukti.

Catatan untuk Discussion: pembanding antrean "List + sort ulang (cara UTS)" memakai `list.sort()` bawaan Python yang berjalan di C dan sangat cepat untuk list yang hampir terurut. Karena itu pada n = 1.000 cara UTS bisa lebih cepat daripada Min-Heap yang ditulis dalam Python. Konstanta C jauh lebih kecil, tetapi pertumbuhannya tetap kuadrat, jadi Min-Heap menang mulai sekitar n = 10.000 dan selisihnya terus melebar. Baris "BST (data terurut, tree miring)" menunjukkan kasus terburuk BST: tinggi tree = n, sehingga membangun katalog menjadi O(n²).

## 8. Testing Plan
Kode: `core/scenarios.py`, `tests/`, halaman `ui/page_testing.py`.

**Penanggung jawab**: semua tim, setiap tim menguji fiturnya sendiri. Skenario ini juga alat utama Team 3 (Fixing Bug): bug yang ditemukan dibuatkan skenario baru agar tidak muncul lagi.

22 skenario otomatis mencakup seluruh contoh di Bagian 10 panduan (fungsional, struktur data, kasus batas, performa, refresh data), ditambah skenario tambahan untuk anti-starvation, undo batal order, biaya, sorting, ranking, hapus restoran, rehash, BFS/DFS. Skenario 15 (akses URL Cloudflare dari perangkat lain) dicek manual saat demo. Tabel yang sama tampil di halaman **Testing** aplikasi dan di `python cli.py test`. `python -m pytest` menjalankan skenario yang sama sebagai unit test, ditambah tes unit untuk setiap struktur data (`tests/test_structures.py`), tes data contoh (`tests/test_seed.py`), dan tes render setiap halaman (`tests/test_app.py`).

## 9. Streamlit dan Deployment Cloudflare
Kode: `app.py`, `ui/`, `run_tunnel.sh`.

**Penanggung jawab**: Streamlit dan deployment Team 2 (Lucky, Angelica, Alvi, Ryan). Halaman Dashboard dan Statistik & Ranking Team 3 (Arbi, Hafiz, Gilang). Halaman Restoran & Menu dan Cari & Katalog Team 1 (Arif, Mitha, Sigit, Reza).

`app.py` hanya membuat service bersama dan memilih halaman. Setiap halaman ada di `ui/page_*.py` dan setiap tombol hanya memanggil method `FoodDeliveryService`. `run_tunnel.sh` menjalankan Streamlit di port 8501 lalu membuka **Cloudflare Quick Tunnel** (`cloudflared tunnel --url http://localhost:8501`). Link `https://xxxx.trycloudflare.com` muncul di terminal.

**Kenapa service disimpan dengan `st.cache_resource` dan `st.session_state`.** Streamlit menjalankan ulang `app.py` dari atas setiap kali ada klik. Tanpa penyimpanan, semua struktur data akan dibuat ulang dan isinya hilang. `st.cache_resource` membuat satu objek service yang dipakai bersama semua pengunjung, sehingga penguji dan presenter melihat data yang sama dan ID order tidak bentrok. Objek yang sama juga disimpan di `st.session_state.service` seperti kerangka di panduan.

**Kelemahan Quick Tunnel**: URL berubah setiap dijalankan, tidak ada jaminan uptime, dan link mati saat komputer yang menjalankan aplikasi mati. Named Tunnel dengan akun dan domain Cloudflare memberi URL tetap.

## Lampiran A. Justifikasi Struktur Data (Bagian 5 panduan)
| Fitur | Data Structure | Alternatif yang ditolak | Alasan |
|---|---|---|---|
| Daftar restoran dan menu | Dynamic Array | Linked List | Akses index O(1) dan tampilan tabel berurutan. Data jarang dihapus, jadi biaya geser O(n) saat hapus dapat diterima. |
| Pencarian ID restoran/menu | Hash Table (chaining) | Linear search di array, BST | Rata-rata O(1) per pencarian, dibanding O(n) linear search dan O(log n) BST. Urutan tidak diperlukan untuk pencarian berdasarkan ID. |
| Katalog menu terurut harga | BST | Array yang diurutkan ulang | Insert O(log n) rata-rata tanpa mengurutkan ulang seluruh array (O(n log n)), inorder langsung memberi urutan harga, dan cari rentang harga O(log n + k). |
| Daftar order | Singly Linked List | Array | Order baru masuk di head O(1) tanpa menggeser elemen; data hanya ditelusuri berurutan. |
| Antrean NORMAL | Queue berbasis node | List dengan `pop(0)` | Enqueue dan dequeue O(1). `pop(0)` menggeser semua elemen, O(n). |
| Antrean URGENT/HIGH | Min-Heap | List yang diurutkan setiap insert (versi UTS) | Insert dan extract O(log n), dibanding sort ulang O(n) sampai O(n log n) per insert dan `pop(0)` O(n) di versi UTS. Benchmark: heap menang mulai n ≈ 10.000. |
| Order NORMAL | Queue, bukan heap | Satu heap untuk semua prioritas | Order NORMAL setara, jadi heap hanya mengurutkan per ID (FIFO); queue memberi urutan sama dalam O(1) dan memungkinkan anti-starvation. |
| History dan Undo | Stack | Queue | Undo membatalkan aksi terakhir lebih dulu: LIFO. |
| Peta dan rute | Graph adjacency list | Adjacency matrix | Peta jalan renggang (rata-rata 3 jalan per lokasi): memori O(V + E), sedangkan matrix O(V²) dengan sebagian besar sel kosong. Iterasi tetangga O(derajat), bukan O(V). |
| Ranking | Merge sort | Insertion sort | O(n log n) di semua kasus dan stabil. |

## Lampiran B. Analisis Kompleksitas (Bagian 8.1 panduan)
| Operasi | Struktur | Best | Average | Worst | Space | Kondisi best/worst |
|---|---|---|---|---|---|---|
| Append | Dynamic Array | Ω(1) | Θ(1) amortized | O(n) | O(n) | Worst saat kapasitas penuh dan array disalin ke kapasitas 2x |
| Hapus | Dynamic Array | Ω(1) | Θ(n) | O(n) | O(1) | Best kalau elemen terakhir |
| Search | Linked List | Ω(1) | Θ(n) | O(n) | O(1) | Best kalau data di head |
| Enqueue / Dequeue | LinkedQueue | Ω(1) | Θ(1) | O(1) | O(n) | |
| Push / Pop | Stack | Ω(1) | Θ(1) | O(1) | O(n) | |
| Insert | Min-Heap | Ω(1) | Θ(1) rata-rata data acak | O(log n) | O(1) | Best: elemen baru tidak lebih kecil dari parent. Worst: elemen baru terkecil, naik sampai root |
| Extract min | Min-Heap | Ω(1) | Θ(log n) | O(log n) | O(1) | Best: elemen pengganti root berhenti setelah satu tukar. Worst: turun sampai daun |
| Lookup / Insert | Hash Table | Ω(1) | Θ(1) | O(n) | O(n) | Worst kalau semua key collision di satu bucket |
| Insert / Search | BST | Ω(1) | Θ(log n) | O(n) | O(1) | Best: key ada di root atau langsung mengisi anak kosong root. Worst: data masuk terurut sehingga tree miring (terlihat di benchmark) |
| Range search | BST | Ω(log n + k) | Θ(log n + k) | O(n) | O(k) | k = jumlah hasil |
| Traversal | BST | Ω(n) | Θ(n) | O(n) | O(h) stack | h = tinggi tree |
| Dijkstra | Graph + Min-Heap | Ω(1) | Θ((V + E) log V) | O((V + E) log V) | O(V + E) | Best kalau start = tujuan. Heap bisa berisi entri lama (lazy deletion), jadi ruangnya O(V + E) |
| BFS / DFS | Graph | Ω(1) | Θ(V + E) | O(V + E) | O(V) | |
| Insertion sort | Array | Ω(n) | Θ(n²) | O(n²) | O(1) | Best kalau data sudah terurut |
| Merge sort | Array | Ω(n log n) | Θ(n log n) | O(n log n) | O(n) | |
| Linear search | Array | Ω(1) | Θ(n) | O(n) | O(1) | |
| Binary search | Array terurut | Ω(1) | Θ(log n) | O(log n) | O(1) | Best kalau target di tengah |

## Lampiran C. Pseudocode Fitur Utama
```
HASH_SEARCH(table, key)
    i ← HASH(key) mod jumlah_bucket
    untuk setiap (k, v) di bucket[i]
        jika k = key: kembalikan v
    kembalikan TIDAK_ADA

HASH_INSERT(table, key, value)
    i ← HASH(key) mod jumlah_bucket
    jika key sudah ada di bucket[i]: ganti value, selesai
    tambahkan (key, value) ke bucket[i]
    jika jumlah_data / jumlah_bucket > 0.75: REHASH ke 2 × jumlah_bucket

BST_RANGE(node, min, max, hasil)
    jika node kosong: selesai
    jika node.harga > min: BST_RANGE(node.kiri, min, max, hasil)
    jika min ≤ node.harga ≤ max: tambahkan menu node ke hasil
    jika node.harga < max: BST_RANGE(node.kanan, min, max, hasil)

PROSES_DELIVERY()
    jika heap tidak kosong DAN queue NORMAL tidak kosong DAN streak ≥ 3: order ← DEQUEUE(queue NORMAL)
    selain itu jika heap tidak kosong: order ← EXTRACT_MIN(heap)      // key (prioritas, ID)
    selain itu: order ← DEQUEUE(queue NORMAL)
    jika order kosong: tampilkan "Tidak ada order di antrean", selesai
    PUSH(stack undo, aksi PROCESS beserta streak lama)
    streak ← 0 jika order NORMAL, selain itu streak + 1
    order.status ← DONE; PUSH(stack history, order); simpan ke database

BST_INSERT(tree, menu)
    node ← root; parent ← kosong
    selama node tidak kosong
        jika menu.harga = node.harga: tambahkan menu ke node.items, selesai
        parent ← node; node ← kiri kalau menu.harga < node.harga, selain itu kanan
    buat node baru sebagai anak kiri/kanan parent (atau root kalau tree kosong)

BST_INORDER(node, hasil)
    jika node kosong: selesai                      // base case
    BST_INORDER(node.kiri, hasil)
    tambahkan semua menu node ke hasil
    BST_INORDER(node.kanan, hasil)

HEAP_PUSH(heap, x)
    tambahkan x di ujung array; i ← index terakhir
    selama i > 0 dan key(A[i]) < key(A[parent(i)]): tukar A[i] dan A[parent(i)]; i ← parent(i)   // sift up

HEAP_EXTRACT_MIN(heap)
    min ← A[0]; A[0] ← elemen terakhir; hapus elemen terakhir; i ← 0
    selama anak terkecil c dari i ada dan key(A[c]) < key(A[i]): tukar A[i] dan A[c]; i ← c        // sift down
    kembalikan min

DIJKSTRA(graph, start, tujuan)
    jarak[v] ← ∞ untuk semua lokasi v; jarak[start] ← 0; PUSH(heap, (0, start))
    selama heap tidak kosong
        (d, u) ← EXTRACT_MIN(heap)
        jika u sudah dikunjungi: lanjut; tandai u dikunjungi
        jika u = tujuan: berhenti
        untuk setiap jalan (u, v, km, menit)
            jika d + km < jarak[v]: jarak[v] ← d + km; asal[v] ← u; PUSH(heap, (jarak[v], v))
    jika tujuan belum dikunjungi: kembalikan "rute tidak tersedia"
    susun rute dari tujuan mengikuti asal[] sampai start, lalu balik urutannya

BFS_RUTE(graph, start, tujuan)                     // ruas jalan paling sedikit
    ENQUEUE(queue, start); asal[start] ← kosong
    selama queue tidak kosong
        u ← DEQUEUE(queue)
        jika u = tujuan: susun rute mengikuti asal[], selesai
        untuk setiap tetangga v yang belum punya asal: asal[v] ← u; ENQUEUE(queue, v)
    kembalikan "rute tidak tersedia"

DFS(graph, u, dikunjungi)
    tandai u dikunjungi
    untuk setiap tetangga v yang belum dikunjungi: DFS(graph, v, dikunjungi)   // base case: tidak ada tetangga baru

BINARY_SEARCH(A terurut, target)
    low ← 0; high ← panjang(A) - 1
    selama low ≤ high
        mid ← (low + high) div 2
        jika A[mid] = target: kembalikan mid
        jika A[mid] < target: low ← mid + 1, selain itu high ← mid - 1
    kembalikan -1

MERGE_SORT(A)
    jika panjang(A) ≤ 1: kembalikan A
    kiri ← MERGE_SORT(paruh pertama A); kanan ← MERGE_SORT(paruh kedua A)
    gabungkan kiri dan kanan dengan selalu mengambil elemen terdepan yang lebih kecil

UNDO()
    aksi ← POP(stack undo); jika kosong: tampilkan "Tidak ada aksi"
    jika aksi = BUAT_ORDER: hapus order dari antrean, linked list, dan database
    selain itu: POP(stack history); order.status ← PENDING
        kembalikan order ke heap (posisi dari key) atau ke posisi lamanya di queue NORMAL
```

## Lampiran D. Perubahan Desain UTS → UAS (untuk bagian Discussion laporan)
| Bagian | UTS | UAS | Alasan |
|---|---|---|---|
| Restoran & menu | `list` Python | `DynamicArray` buatan sendiri | Struktur inti wajib diimplementasikan sendiri (Bagian 3) |
| Cari ID restoran/menu | Linear search O(n) | Hash Table O(1) rata-rata, ID duplikat ditolak | Fitur wajib UAS no. 1 |
| Katalog menu | Tidak ada | BST berdasarkan harga, cari rentang | Fitur wajib UAS no. 2 |
| Insert order di tail | O(n), menelusuri sampai ujung | O(1) dengan pointer tail | Order baru langsung ditaruh di akhir list |
| Antrean NORMAL | `list.pop(0)` O(n) | Queue berbasis node O(1) | Dequeue tidak menggeser elemen |
| Antrean prioritas | List diurutkan ulang setiap insert, `pop(0)` saat dequeue | Min-Heap O(log n) + aturan tie-break dan anti-starvation | Fitur wajib UAS no. 3; benchmark: heap menang mulai n ≈ 10.000 |
| Statistik rekursif | Maju satu index per panggilan, kedalaman O(n) | Divide and conquer, kedalaman O(log n) | Tetap aman untuk data besar (100.000 order hanya butuh kedalaman sekitar 17) |
| Undo | Batal order dan proses delivery | Ditambah undo buat order | Semua aksi order bisa dibatalkan |
| Peta & rute | Tidak ada | Graph adjacency list, Dijkstra (heap sendiri), BFS, DFS, ongkir dari jarak | Fitur wajib UAS no. 4 |
| Ranking | Tidak ada | Merge sort menu terlaris dan restoran teramai | Fitur wajib UAS no. 5 |
| Antarmuka | CLI `input()` | Streamlit + Cloudflare Tunnel | Ketentuan UAS |
| Struktur kode | Fungsi terpisah per sub-bagian | Satu `FoodDeliveryService`, tes memakai database `:memory:` | Semua struktur data ada di satu objek, mudah diuji dan disimpan di Streamlit |
| Update menu | Validasi per field | Semua field divalidasi dulu, baru disimpan | Input yang tidak valid tidak mengubah data |
| Masukan dosen UTS | | *(diisi kelompok)* | Bagian 3 panduan mewajibkan tindak lanjut masukan dosen dilaporkan |

## Lampiran E. Pembagian Kontribusi
| Tim | Anggota | Tanggung jawab tim | Kontribusi individu |
|---|---|---|---|
| Team 1 | Arif | Database, Searching, Katalog Menu | |
| Team 1 | Mitha | Dokumentasi (laporan IMRAD, slide) | |
| Team 1 | Sigit | Database, Searching, Katalog Menu | |
| Team 1 | Reza | Database, Searching, Katalog Menu | |
| Team 2 | Lucky | Streamlit, Antrean Prioritas Order, Peta Lokasi & Rute | |
| Team 2 | Angelica | Streamlit, Antrean Prioritas Order, Peta Lokasi & Rute | |
| Team 2 | Alvi | Streamlit, Antrean Prioritas Order, Peta Lokasi & Rute | |
| Team 2 | Ryan | Streamlit, Antrean Prioritas Order, Peta Lokasi & Rute | |
| Team 3 | Arbi | Fixing Bug, Ranking & Pengurutan, Dashboard | |
| Team 3 | Hafiz | Fixing Bug, Ranking & Pengurutan, Dashboard | |
| Team 3 | Gilang | Fixing Bug, Ranking & Pengurutan, Dashboard | |

Benchmark (Bagian 7), Testing Plan (Bagian 8), dan halaman Visualisasi Struktur, Riwayat & Undo, Benchmark, dan Testing dikerjakan bersama oleh semua tim. Kolom kontribusi individu diisi masing-masing anggota.

Penggunaan alat bantu AI dinyatakan di laporan sesuai Bagian 18 panduan.
