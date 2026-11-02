# Panduan Menu Smart Food Delivery

Dokumen ini menjelaskan setiap menu aplikasi dari sisi pengguna sampai ke kode. Untuk setiap menu, ada cara memakainya, fungsi yang dipanggil, struktur data yang bekerja, dan contoh pertanyaan Technical Defense beserta jawabannya.

Gunakan dokumen ini bersama dua dokumen lain:

- [Referensi fungsi](referensi-fungsi.md) menjelaskan setiap fungsi dan method satu per satu.
- [Desain teknis](design.md) berisi justifikasi struktur data, tabel kompleksitas, dan pseudocode untuk laporan.

Semua angka contoh di dokumen ini berasal dari data contoh. Untuk mengisinya, buka **Dashboard** lalu tekan **Isi data contoh** pada database yang masih kosong.

## Cara kerja satu klik

Setiap menu bekerja dengan pola yang sama:

1. Pengguna mengisi form atau menekan tombol di halaman `views/page_*.py`.
2. Halaman memanggil satu method `FoodDeliveryService` di `core/services.py`.
3. Method service memvalidasi input, lalu mengubah struktur data (Hash Table, Heap, Linked List, dan lainnya).
4. Method service menyimpan perubahan ke SQLite lewat `core/database.py`.
5. Method service mengembalikan pesan `Sukses: ...` atau `Gagal: ...`. Halaman menampilkan pesan itu, lalu Streamlit menjalankan ulang halaman (rerun) supaya tabel menampilkan data terbaru.

Objek service hanya dibuat satu kali oleh `get_service()` di `app.py` (memakai `@st.cache_resource`). Setiap halaman mengambilnya dari `st.session_state.service`. Karena itu data tidak hilang saat pengguna pindah menu atau halaman di-refresh.

## Skenario demo end-to-end

Urutan ini menunjukkan semua struktur data dalam sekitar 10 menit (Bagian 14 panduan). Mulailah dari database kosong dan ikuti langkahnya berurutan, karena angka di kolom "Yang terlihat" bergantung pada langkah sebelumnya.

| No | Menu | Langkah | Yang terlihat | Struktur data |
|---|---|---|---|---|
| 1 | Dashboard | Tekan **Isi data contoh**. | 4 restoran, 10 menu, 10 order. 5 selesai, 1 batal, 4 pending. | Semua |
| 2 | Restoran & Menu | Bagian **Restoran**, isi semua kolom dengan ID `R1`, lalu tekan **Tambah restoran**. | Ditolak: `ID restoran R1 sudah terdaftar.` | Hash Table |
| 3 | Cari & Katalog | Bagian **Cari berdasarkan ID**, pilih Menu, ketik `M10`. | Ditemukan di bucket 12. Bucket 12 berisi `M9 -> M10`, jadi ada 1 collision. | Hash Table |
| 4 | Cari & Katalog | Bagian **Katalog harga**, isi rentang 20.000 sampai 30.000. | 6 menu, urut dari termurah. Gambar BST dengan akar Rp25.000. | BST |
| 5 | Cari & Katalog | Bagian **Urutkan & cari nama**, ketik `sate`. | Sate Ayam dan Sate Kambing. Binary search melompat ke posisi 8. | Sorting, Binary search |
| 6 | Buat Order | Buat order Warung Nusantara, Nasi Goreng, prioritas URGENT, lokasi antar Pondok Indah. Lalu buat order kedua: Kopi Senja, Kopi Susu, prioritas HIGH, tanpa lokasi antar. | Order pertama: rute Blok M -> Kebayoran Lama -> Pondok Indah, 6.53 km, ongkir Rp18.000. | Graph (Dijkstra) |
| 7 | Antrean & Delivery | Tekan **Proses order** 3 kali. Perhatikan panel kuota setiap kali. | Keluar berurutan: order URGENT baru, Joko (HIGH), lalu Fajar (NORMAL), walaupun order HIGH kedua masih menunggu. Sebelum Fajar, kuota menunjukkan 3 / 3 dan ada peringatan giliran NORMAL (anti-starvation). | Min-Heap, Queue |
| 8 | Antrean & Delivery | Tekan **Undo aksi terakhir**. | Fajar kembali PENDING di depan antrean NORMAL dan kuota kembali 3 / 3. | Stack |
| 9 | Peta & Rute | Mode **Cari rute** dari Kuningan ke Pondok Indah. | Dijkstra (12.08 km, 4 ruas jalan) berbeda dengan BFS (3 ruas jalan). | Graph (Dijkstra, BFS, DFS) |
| 10 | Statistik & Ranking | Lihat ranking. | Menu terlaris: Nasi Goreng dan Sate Ayam (3 porsi). Restoran teramai: Warung Nusantara dan Kopi Senja (4 order). Nilai yang sama tetap urut seperti aslinya karena merge sort stabil. | Recursion, Merge sort |
| 11 | Visualisasi Struktur | Gulir dari atas ke bawah. | Isi nyata 8 struktur data. | Semua |
| 12 | Benchmark | Tekan **Jalankan benchmark**. | Tabel dan grafik untuk n = 1.000, 10.000, 100.000. | Semua |
| 13 | Testing | Tekan **Jalankan tes**. | 22 skenario LULUS, 1 MANUAL (akses URL Cloudflare). | Semua |

## Operasional

### Dashboard

**Pemilik**: Team 3. **File**: `views/page_dashboard.py`.

**Untuk apa.** Ringkasan kondisi sistem dalam satu layar: jumlah order per status, pendapatan, ranking, dan isi setiap struktur data.

**Cara pakai.**

1. Buka **Dashboard**. Halaman ini juga halaman pertama saat aplikasi dibuka.
2. Baca kotak ringkasan di atas: Total order, Pending, Selesai, Dibatalkan, dan Pendapatan.
3. Baca dua grafik batang: order per restoran dan menu terjual.
4. Baca **Status sistem** untuk melihat jumlah isi setiap struktur data.
5. Pada database kosong, tekan **Isi data contoh** untuk mengisi restoran, menu, dan order contoh.

**Alur kode.**

- Kotak ringkasan memanggil `service.statistics()`. Method ini mengubah linked list order menjadi array (`orders_array()`), lalu menghitung setiap angka dengan `recursive_sum` dan `recursive_group`.
- Grafik batang memanggil `service.top_restaurants()` dan `service.top_menus()`. Keduanya mengurutkan hasil statistik dengan `merge_sort`.
- Tombol **Isi data contoh** memanggil `seed_demo_data()` lalu `seed_demo_orders()` dari `core/seed.py`.

**Struktur data dan kompleksitas.**

| Bagian | Struktur | Kompleksitas |
|---|---|---|
| Statistik | Recursion divide and conquer | O(n) waktu, kedalaman O(log n) |
| Ranking | Merge sort | O(k log k), k = jumlah restoran atau menu |

**Catatan.**

- Pendapatan hanya menghitung order DONE, termasuk biaya prioritas dan ongkir.
- "Order per restoran" menghitung semua status. "Menu terjual" hanya menghitung order DONE.
- Data contoh hanya ditambahkan sekali. Kalau sudah ada order, order contoh dilewati.
- Order contoh tidak bisa di-undo, karena stack undo dikosongkan setelah data contoh dibuat.

**Pertanyaan defense.**

- *Kenapa statistik memakai recursion, bukan loop biasa?* Statistik adalah materi recursion dari UTS. Versi UAS membagi data menjadi dua bagian setiap panggilan (divide and conquer), jadi kedalaman call stack hanya O(log n). 100.000 order hanya butuh kedalaman sekitar 17, jauh di bawah batas rekursi Python (1.000).
- *Apa base case `recursive_sum`?* Rentang kosong menghasilkan 0. Rentang berisi satu elemen menghasilkan nilai elemen itu.

### Buat Order

**Pemilik**: Team 2. **File**: `views/page_create_order.py`.

**Untuk apa.** Membuat order baru. Ongkir dihitung dari rute terpendek antara restoran dan lokasi antar.

**Cara pakai.**

1. Pilih **Restoran**. Restoran yang lokasinya belum ada di peta diberi tanda "tidak ada di peta".
2. Pilih **Menu**. Hanya menu milik restoran itu yang berstatus tersedia yang muncul.
3. Isi **Nama customer** dan **Jumlah**.
4. Pilih **Prioritas**. URGENT menambah Rp10.000 dan HIGH menambah Rp5.000.
5. Pilih **Lokasi antar**, atau pilih "(tanpa lokasi antar)" untuk order tanpa pengiriman.
6. Periksa rute, jarak, estimasi waktu, dan rincian biaya yang muncul.
7. Tekan **Buat order**.

**Alur kode.**

1. Saat lokasi antar dipilih, `route_preview()` memanggil `service.plan_route()`. Method ini mencari lokasi restoran di peta, lalu memanggil `route_between()`, yang menjalankan `Graph.dijkstra()`.
2. Tombol **Buat order** memanggil `service.create_order()`. Method ini:
   - memvalidasi nama, jumlah, dan prioritas;
   - mencari restoran dan menu di Hash Table (`find_restaurant`, `find_menu`);
   - menghitung total: harga x jumlah + biaya prioritas + ongkir;
   - memasukkan order ke head linked list `orders`;
   - memasukkan order ke antrean (`_enqueue`): NORMAL ke `LinkedQueue`, URGENT dan HIGH ke `MinHeap`;
   - mencatat aksi `CREATE_ORDER` di stack undo;
   - menyimpan order ke database.

**Struktur data dan kompleksitas.**

| Langkah | Struktur | Kompleksitas |
|---|---|---|
| Cari restoran dan menu | Hash Table | O(1) rata-rata |
| Rute terpendek | Graph + Dijkstra dengan Min-Heap | O((V + E) log V) |
| Simpan order | Singly Linked List, insert di head | O(1) |
| Masuk antrean | Queue O(1), atau Min-Heap O(log n) | |
| Catat undo | Stack, push | O(1) |

**Rumus biaya.**

- Ongkir = Rp5.000 + Rp2.000 per km, dibulatkan ke Rp500 terdekat.
- Estimasi waktu = jumlah waktu setiap ruas jalan di rute.
- Total = harga menu x jumlah + biaya prioritas + ongkir.

**Pesan yang mungkin muncul.**

| Pesan | Penyebab |
|---|---|
| `Nama customer tidak boleh kosong...` | Nama customer dikosongkan. |
| `Lokasi restoran '...' belum ada di peta.` | Lokasi restoran tidak terdaftar sebagai titik di peta. |
| `Tidak ada jalan yang menghubungkan ...` | Restoran dan lokasi antar tidak terhubung jalan (graph tidak terhubung). |
| `Menu sedang tidak tersedia.` | Menu ditandai tidak tersedia di **Restoran & Menu**. |

Tombol **Buat order** dinonaktifkan kalau rute tidak ditemukan, jadi order dengan lokasi antar yang tidak terjangkau tidak bisa dibuat.

**Pertanyaan defense.**

- *Kenapa order NORMAL tidak masuk heap?* Semua order NORMAL punya prioritas sama, jadi di heap urutannya hanya ditentukan ID, sama dengan FIFO. Queue memberi urutan yang sama dengan biaya O(1). Antrean terpisah juga memungkinkan aturan anti-starvation.
- *Kenapa order baru dimasukkan di head linked list?* Insert di head O(1) tanpa menggeser elemen, dan order terbaru muncul paling atas di riwayat.

### Antrean & Delivery

**Pemilik**: Team 2. **File**: `views/page_queue.py`.

**Untuk apa.** Memproses pengiriman sesuai prioritas, membatalkan order, dan membatalkan aksi terakhir (undo).

**Cara pakai.**

1. Lihat kotak **Order berikutnya**. Ini order yang akan diproses kalau tombol ditekan.
2. Tekan **Proses order** untuk mengantar order itu. Statusnya menjadi DONE.
3. Lihat **Kuota prioritas berturut-turut**. Setelah 3 order URGENT atau HIGH berturut-turut, order NORMAL yang menunggu dilayani dulu.
4. Lihat dua tabel antrean: URGENT/HIGH (min-heap) dan NORMAL (FIFO queue).
5. Lihat gambar **Isi heap** untuk menjelaskan posisi setiap order di array heap.
6. Untuk membatalkan, pilih order di **Batalkan order** lalu tekan **Batalkan**.
7. Tekan **Undo aksi terakhir** untuk membatalkan aksi buat, batal, atau proses yang terakhir.

**Alur kode.**

- **Order berikutnya** memanggil `service.next_order()`. Method ini hanya melihat (peek), tidak mengeluarkan order.
- **Proses order** memanggil `service.process_delivery()`:
  1. Kalau `is_normal_turn()` benar atau heap kosong, ambil dari queue NORMAL (`dequeue`). Kalau tidak, ambil dari heap (`pop`).
  2. Catat aksi `PROCESS_DELIVERY` beserta nilai kuota lama di stack undo.
  3. Ubah kuota: order NORMAL mengembalikan kuota ke 0, order prioritas menambah 1.
  4. Ubah status menjadi DONE, push ke stack history, lalu simpan ke database.
- **Batalkan** memanggil `service.cancel_order()`. Order dikeluarkan dari queue atau heap, statusnya menjadi CANCELLED, dan posisi lamanya di queue dicatat untuk undo.
- **Undo** memanggil `service.undo()`. Lihat penjelasan di menu **Riwayat & Undo**.

**Aturan prioritas dan tie-break.**

- Key heap adalah pasangan `(level prioritas, ID order)`. URGENT = 0, HIGH = 1, NORMAL = 2. Key terkecil keluar duluan.
- Dua order dengan prioritas sama dibandingkan dengan ID. ID lebih kecil berarti dibuat lebih dulu, jadi keluar lebih dulu (FIFO).
- Anti-starvation: setelah 3 order URGENT atau HIGH berturut-turut diproses, 1 order NORMAL yang menunggu dilayani dulu. Aturan ini hanya berlaku kalau kedua antrean sama-sama berisi.

**Struktur data dan kompleksitas.**

| Operasi | Struktur | Kompleksitas |
|---|---|---|
| Lihat order berikutnya | Heap peek, Queue peek | O(1) |
| Ambil order prioritas | Min-Heap pop (sift down) | O(log n) |
| Ambil order NORMAL | Queue dequeue | O(1) |
| Batalkan order | Queue remove O(n), Heap remove O(n) cari + O(log n) perbaiki | |
| Catat history dan undo | Stack push | O(1) |

**Pertanyaan defense.**

- *Jelaskan proses heapify dan tunjukkan di kode.* `_sift_up` di `core/structures/heap.py` menukar elemen baru dengan parent-nya selama key-nya lebih kecil. `_sift_down` menukar akar dengan anak terkecil sampai urutan heap benar lagi. Parent index i ada di (i - 1) // 2, anaknya di 2i + 1 dan 2i + 2.
- *Berapa kompleksitas extract?* O(log n), karena `_sift_down` turun paling banyak setinggi tree, yaitu log n.

### Peta & Rute

**Pemilik**: Team 2. **File**: `views/page_map.py`, `views/map_view.py`.

**Untuk apa.** Melihat rute pengiriman order, mencari rute antar dua lokasi, dan menambah lokasi atau jalan di peta.

**Cara pakai.**

1. Pilih mode **Rute order**, lalu pilih order. Peta menampilkan rute, jarak, estimasi waktu, ongkir, dan status order.
2. Pilih mode **Cari rute**, lalu pilih **Dari** dan **Ke**. Tabel membandingkan rute Dijkstra dan BFS. Keterangan di bawah tabel menunjukkan lokasi yang terjangkau menurut DFS.
3. Buka **Tambah lokasi atau jalan** untuk menambah titik (node) atau jalan (edge). Kalau jarak dan waktu diisi 0, nilainya dihitung otomatis dari koordinat.
4. Buka **Daftar jalan (edge graph)** untuk melihat semua jalan.

Warna penanda di peta: oranye = restoran, biru = area customer, abu-abu = persimpangan, hijau = tujuan.

**Alur kode.**

- **Cari rute** memanggil `service.route_between()` (Dijkstra), `Graph.bfs_path()` (rute dengan ruas jalan paling sedikit), dan `Graph.dfs()` (semua lokasi yang terjangkau).
- **Simpan lokasi** memanggil `service.add_location()`. **Simpan jalan** memanggil `service.add_road()`.
- Jarak otomatis = jarak garis lurus (rumus haversine) x 1,3, karena jalan asli lebih panjang dari garis lurus. Waktu otomatis = jarak / 25 km per jam.

**Struktur data dan kompleksitas.**

| Operasi | Struktur | Kompleksitas |
|---|---|---|
| Simpan peta | Graph adjacency list | Memori O(V + E) |
| Rute terpendek | Dijkstra dengan Min-Heap | O((V + E) log V) |
| Rute transit tersedikit | BFS dengan LinkedQueue | O(V + E) |
| Lokasi terjangkau | DFS rekursif | O(V + E), kedalaman sampai V |

**Contoh untuk demo.** Dari Kuningan ke Pondok Indah, Dijkstra memilih rute 12.08 km lewat 4 ruas jalan (Mampang, Blok M, Kebayoran Lama). BFS memilih rute lewat 3 ruas jalan (Senayan, Kebayoran Lama), yang lebih sedikit ruasnya tetapi lebih jauh. Contoh ini menunjukkan perbedaan "jarak terpendek" dan "transit paling sedikit".

**Pertanyaan defense.**

- *Kenapa adjacency list, bukan adjacency matrix?* Peta jalan adalah graph renggang, rata-rata sekitar 3 jalan per lokasi. Adjacency list butuh memori O(V + E), sedangkan matrix O(V²) dengan sebagian besar sel kosong.
- *Apa yang terjadi kalau lokasi tidak terhubung?* `dijkstra()` mengembalikan `None`, service mengembalikan pesan `Tidak ada jalan yang menghubungkan ...`, dan order dengan lokasi itu tidak bisa dibuat (skenario uji 11).
- *Apa risiko DFS rekursif untuk data besar?* Kedalaman rekursi bisa sampai jumlah lokasi. Graph berbentuk rantai panjang (lebih dari sekitar 1.000 lokasi) bisa melewati batas rekursi Python dan menimbulkan `RecursionError`. Halaman menangkap error itu dan menampilkan peringatan.

### Riwayat & Undo

**Pemilik**: bersama semua tim. **File**: `views/page_orders.py`.

**Untuk apa.** Melihat semua order, riwayat order selesai atau batal, mencari order per customer, melihat isi stack undo, dan memuat ulang data dari database.

**Cara pakai.** Pilih salah satu bagian di bawah judul halaman:

| Bagian | Isi |
|---|---|
| Semua order | Semua order dari head ke tail linked list. Order terbaru di atas. |
| History | Isi stack history. Order yang terakhir selesai atau dibatalkan ada di atas. |
| Cari customer | Ketik nama customer. Huruf besar dan kecil tidak dibedakan. |
| Undo | Isi stack undo. Baris pertama adalah aksi yang akan dibatalkan. Tekan **Undo aksi terakhir**. |
| Database | Jumlah baris setiap tabel SQLite. Tekan **Muat ulang dari database** untuk membangun ulang semua struktur dari database. |

Klik judul kolom di tabel untuk mengurutkan. Kolom Harga, Ongkir, Total, Jarak, dan ETA diurutkan sebagai angka.

**Alur kode.**

- **Cari customer** memanggil `service.orders_by_customer()`, yang menelusuri linked list dengan `find_all` (linear search).
- **Undo aksi terakhir** memanggil `service.undo()`:
  - `CREATE_ORDER`: order dihapus dari antrean, linked list, dan database.
  - `CANCEL_ORDER`: order kembali PENDING di posisi lamanya di queue NORMAL, atau kembali ke heap.
  - `PROCESS_DELIVERY`: order kembali PENDING di depan queue NORMAL atau kembali ke heap. Kuota anti-starvation dikembalikan ke nilai sebelumnya.
  - Undo ditolak kalau restoran order itu sudah dihapus.
- **Muat ulang dari database** memanggil `service.load()`. Method ini mengosongkan semua struktur, lalu membangunnya ulang dari tabel SQLite. Urutan linked list, isi history, isi antrean, dan kuota prioritas kembali sama persis (skenario uji 14).

**Struktur data dan kompleksitas.**

| Operasi | Struktur | Kompleksitas |
|---|---|---|
| Tampilkan semua order | Linked List traversal | O(n) |
| Cari customer | Linear search di Linked List | O(n) |
| History dan undo | Stack push dan pop | O(1) |

**Pertanyaan defense.**

- *Kenapa undo memakai stack, bukan queue?* Undo harus membatalkan aksi terakhir lebih dulu. Itu urutan LIFO, dan stack memberi push dan pop O(1) di ujung yang sama.
- *Apa yang terjadi kalau undo ditekan saat stack kosong?* `actions.pop()` mengembalikan `None` dan service mengembalikan pesan `Tidak ada aksi untuk di-undo.` Aplikasi tidak error (skenario uji 6).

## Restoran

### Restoran & Menu

**Pemilik**: Team 1. **File**: `views/page_restaurants.py`.

**Untuk apa.** Mendaftarkan restoran, mengelola menu, dan mencari dengan kata kunci (fitur UTS).

**Cara pakai.** Pilih salah satu bagian:

- **Restoran.**
  1. Isi ID, nama, lokasi (titik di peta), dan kategori, lalu tekan **Tambah restoran**.
  2. Untuk menghapus, pilih restoran, centang **Saya yakin ingin menghapus**, lalu tekan **Hapus restoran**. Semua menunya ikut terhapus.
- **Menu.**
  1. Isi ID menu, restoran, nama, kategori, dan harga, lalu tekan **Tambah menu**.
  2. Untuk mengubah, pilih menu di **Ubah / hapus menu**, ubah isinya, lalu tekan **Simpan perubahan**. Hilangkan centang **Tersedia** supaya menu tidak bisa dipesan.
  3. Tekan **Hapus menu** untuk menghapus menu.
- **Cari kata kunci.** Ketik kata, misalnya `sate`. Pencarian mencocokkan ID, nama, kategori, dan lokasi.

**Alur kode.**

| Tombol | Method service | Yang terjadi |
|---|---|---|
| Tambah restoran | `add_restaurant()` | Validasi input, tolak ID duplikat lewat Hash Table, append ke Dynamic Array, insert ke Hash Table, simpan ke database. |
| Hapus restoran | `delete_restaurant()` | Tolak kalau masih ada order PENDING. Hapus semua menunya dari Hash Table, BST, dan array, lalu hapus restorannya. |
| Tambah menu | `add_menu()` | Validasi, tolak ID duplikat, masukkan ke Dynamic Array, Hash Table, dan BST katalog. |
| Simpan perubahan | `update_menu()` | Validasi semua field dulu. Kalau harga berubah, node menu dipindah di BST karena harga adalah key BST. |
| Hapus menu | `delete_menu()` | Hapus dari array, Hash Table, BST, dan database. |
| Cari kata kunci | `search_keyword()` | Linear search pada semua restoran dan menu. |

**Struktur data dan kompleksitas.**

| Operasi | Struktur | Kompleksitas |
|---|---|---|
| Tambah data | Dynamic Array append | O(1) amortized |
| Cek ID duplikat | Hash Table search | O(1) rata-rata |
| Hapus dari array | Dynamic Array remove_where | O(n), elemen digeser |
| Simpan ke katalog | BST insert | O(log n) rata-rata, O(n) terburuk |
| Cari kata kunci | Linear search | O(n) |

**Pesan yang mungkin muncul.**

| Pesan | Penyebab |
|---|---|
| `ID restoran R1 sudah terdaftar.` | ID sudah ada di Hash Table (skenario uji 2). |
| `Harga harus bilangan bulat lebih dari 0.` | Harga 0, negatif, atau bukan angka (skenario uji 3). |
| `Restoran masih punya order PENDING (#...).` | Restoran yang punya order PENDING tidak boleh dihapus (skenario uji 21). |

**Pertanyaan defense.**

- *Kenapa restoran dan menu disimpan di dua struktur (array dan Hash Table)?* Dynamic Array menjaga urutan pendaftaran untuk ditampilkan. Hash Table memberi pencarian per ID O(1) dan penolakan ID duplikat. Keduanya menunjuk ke objek yang sama, jadi data tidak tersalin.
- *Kenapa update harga harus memindahkan node di BST?* Key BST adalah harga. Kalau harga berubah tanpa dipindah, menu berada di posisi yang salah dan pencarian rentang harga akan melewatkannya.

### Cari & Katalog

**Pemilik**: Team 1 (Hash Table, BST, searching), Team 3 (sorting). **File**: `views/page_search.py`.

**Untuk apa.** Tiga cara mencari data. Setiap bagian menunjukkan struktur data di baliknya.

**Cara pakai.**

- **Cari berdasarkan ID.**
  1. Pilih Restoran atau Menu, lalu ketik ID, misalnya `R1` atau `M10`.
  2. Hasilnya menyebut nama data dan nomor bucket tempat data ditemukan.
  3. Di bawahnya, **Isi Hash Table** menampilkan jumlah data, jumlah bucket, load factor, collision, dan isi setiap bucket. Bucket yang dicari ditandai "<- di sini".
- **Katalog harga.**
  1. Isi harga minimum dan maksimum. Tabel menampilkan menu di rentang itu, dari yang termurah.
  2. **Isi BST** menampilkan gambar tree. Setiap node berisi menu dengan harga yang sama.
  3. Pilih urutan traversal (inorder, preorder, postorder) untuk melihat urutan kunjungan node.
- **Urutkan & cari nama.**
  1. Pilih algoritma pengurutan. Tabel menampilkan menu yang diurutkan berdasarkan nama.
  2. Ketik awal nama menu, misalnya `sate` atau `kopi`. Semua menu yang namanya diawali teks itu ditampilkan.

**Alur kode.**

| Bagian | Fungsi | Struktur |
|---|---|---|
| Cari berdasarkan ID | `HashTable.bucket_index()`, `HashTable.search()` | Hash Table separate chaining |
| Katalog harga | `service.menus_in_price_range()` lalu `BST.search_range()`, `BST.traverse()` | BST dengan key harga |
| Urutkan & cari nama | `service.menus_sorted_by_name()` lalu `merge_sort` atau `insertion_sort`, lalu `binary_search_first()` | Sorting dan binary search |

**Cara kerja setiap struktur.**

- **Hash Table.** Nomor bucket dihitung dari ID dengan polynomial rolling hash (setiap karakter: kode = kode x 31 + nilai karakter), lalu dimodulo jumlah bucket. Dua ID di bucket yang sama (collision) disimpan berantai dalam satu bucket. Kalau load factor (jumlah data / jumlah bucket) melewati 0,75, jumlah bucket digandakan dan semua ID dihitung ulang (rehash).
- **BST.** Harga lebih kecil disimpan ke kiri, lebih besar ke kanan. Pencarian rentang hanya mengunjungi subtree yang mungkin berisi harga di rentang itu. Inorder (kiri, node, kanan) selalu menghasilkan harga menaik.
- **Binary search.** `binary_search_first()` mencari posisi nama pertama yang tidak lebih kecil dari teks yang dicari (lower bound). Karena daftar terurut, semua nama yang diawali teks yang sama letaknya berurutan mulai posisi itu.

**Contoh untuk demo.**

- ID menu `M10` ada di bucket 12 bersama `M9`. Ini contoh collision yang tetap bisa ditemukan (skenario uji 8).
- Tabel menu punya 10 data di 16 bucket, load factor 0,62. Tabel ini pernah di-rehash dari 8 bucket saat data ke-7 masuk.
- BST data contoh berisi 10 menu di 9 node, dengan tinggi 5 dan akar Rp25.000. Soto Ayam dan Croissant sama-sama Rp22.000, jadi berbagi satu node.

**Pertanyaan defense.**

- *Kenapa pencarian ID memakai Hash Table, bukan BST?* Pencarian ID hanya butuh kecocokan persis. Hash Table memberi O(1) rata-rata. BST memberi O(log n) dan baru berguna kalau butuh urutan, seperti katalog harga.
- *Apa yang terjadi kalau load factor terlalu tinggi?* Rantai di setiap bucket memanjang, jadi pencarian mendekati O(n). Karena itu bucket digandakan saat load factor melewati 0,75.
- *Apa yang terjadi pada BST kalau data masuk dalam keadaan terurut?* Tree menjadi miring seperti rantai, tingginya n, dan operasinya menjadi O(n). Halaman Benchmark mengukur kasus ini ("BST data terurut, tree miring").
- *Kenapa binary search butuh data terurut?* Setiap langkah membuang separuh daftar dengan asumsi semua elemen di kiri lebih kecil dan di kanan lebih besar. Asumsi itu hanya benar kalau data terurut.

### Statistik & Ranking

**Pemilik**: Team 3. **File**: `views/page_statistics.py`.

**Untuk apa.** Statistik order lengkap dan ranking menu terlaris serta restoran dengan order terbanyak.

**Cara pakai.** Buka halaman. Kotak atas menampilkan statistik. Tabel kiri menampilkan menu terlaris (porsi dari order DONE). Tabel kanan menampilkan restoran dengan order terbanyak (semua status).

**Alur kode.**

1. `service.statistics()` menghitung angka dengan `recursive_sum` dan `recursive_group`.
2. `service.top_menus()` dan `service.top_restaurants()` mengurutkan hasilnya menurun dengan `merge_sort`, lalu mengambil 5 teratas.

**Struktur data dan kompleksitas.**

| Operasi | Algoritma | Kompleksitas |
|---|---|---|
| Hitung statistik | Recursion divide and conquer | O(n) waktu, kedalaman O(log n) |
| Ranking | Merge sort | O(k log k) |

**Pertanyaan defense.**

- *Kenapa ranking memakai merge sort, bukan insertion sort?* Merge sort O(n log n) di semua kasus dan stabil. Insertion sort O(n²) dan hanya cepat kalau data hampir terurut. Halaman Benchmark membandingkan keduanya.
- *Apa artinya merge sort stabil?* Dua data dengan nilai sama tetap dalam urutan aslinya. Restoran dengan jumlah order sama tetap tampil dalam urutan yang konsisten.

## Struktur Data

### Visualisasi Struktur

**Pemilik**: bersama semua tim. **File**: `views/page_structures.py`, `views/diagrams.py`.

**Untuk apa.** Menunjukkan isi nyata setiap struktur data yang sedang dipakai aplikasi. Penguji perlu melihat bahwa struktur data benar-benar bekerja, bukan hanya tabel biasa (Bagian 6.3 panduan).

**Cara pakai.** Gulir dari atas ke bawah. Setiap bagian membaca langsung dari service yang sedang berjalan:

| No | Struktur | Yang ditampilkan | Dipakai untuk |
|---|---|---|---|
| 1 | Dynamic Array | Slot terisi dan slot kosong, kapasitas | Daftar restoran dan menu |
| 2 | Singly Linked List | Rantai node dari HEAD ke TAIL | Semua order |
| 3 | Stack | Rantai dari TOP ke BOTTOM | History dan undo |
| 4 | Linked Queue | Rantai dari FRONT ke REAR | Antrean NORMAL |
| 5 | Min-Heap | Gambar tree dan array | Antrean URGENT dan HIGH |
| 6 | Hash Table | Isi setiap bucket, load factor, collision | Indeks ID restoran dan menu |
| 7 | BST | Gambar tree | Katalog menu per harga |
| 8 | Graph | Daftar tetangga setiap lokasi | Peta lokasi |

**Tips demo.** Buat satu order di **Buat Order**, lalu buka halaman ini. Order baru muncul di HEAD linked list, di antrean, dan sebagai aksi teratas di stack undo.

### Benchmark

**Pemilik**: bersama semua tim. **File**: `views/page_benchmark.py`, `core/benchmark.py`.

**Untuk apa.** Mengukur waktu eksekusi untuk n = 1.000, 10.000, dan 100.000, lalu membandingkannya dengan analisis teoritis (Bagian 8 panduan).

**Cara pakai.** Tekan **Jalankan benchmark** dan tunggu 10 sampai 20 detik. Hasilnya berupa tabel dan grafik per operasi. Sumbu grafik berskala log.

**Yang dibandingkan.**

| Operasi | Dibandingkan | Yang diharapkan |
|---|---|---|
| Cari ID | Hash Table O(1) vs linear search O(n) | Hash Table hampir konstan, linear search naik sebanding n |
| Cari nilai | Binary search O(log n) vs linear search O(n) | Binary search jauh lebih cepat untuk n besar |
| Sorting | Merge sort O(n log n) vs insertion sort O(n²) | Insertion sort naik sekitar 100 kali setiap n naik 10 kali |
| Antrean prioritas | Min-Heap vs list yang diurutkan ulang (cara UTS) | Heap menang mulai n sekitar 10.000 |
| Bangun katalog | BST data acak vs BST data terurut (tree miring) | Tree miring jauh lebih lambat |
| Cari rentang | BST search_range | O(log n + k) |

**Catatan.**

- Data acak memakai seed tetap (42), jadi hasilnya bisa diulang.
- Waktu pencarian adalah rata-rata dari 200 kali pencarian.
- Operasi O(n²) di atas n = 10.000 terlalu lama dijalankan. Waktunya diestimasi dari hasil n = 10.000 dikali (n / 10.000)². Di grafik, titik estimasi berbentuk silang.

**Pertanyaan defense.**

- *Kenapa hasil benchmark kadang tidak persis sesuai teori?* Waktu nyata dipengaruhi overhead Python, cache CPU, dan proses lain di komputer. Yang dibandingkan adalah pola kenaikannya, bukan angka mutlak.
- *Apa yang terjadi kalau data menjadi 1.000.000?* Operasi O(1) dan O(log n) tetap cepat. Insertion sort O(n²) akan butuh waktu sekitar 100 kali lipat dari n = 100.000. Rekursi statistik tetap aman karena kedalamannya O(log n).

### Testing

**Pemilik**: bersama semua tim. **File**: `views/page_testing.py`, `core/scenarios.py`.

**Untuk apa.** Menjalankan testing plan (Bagian 10 panduan) langsung dari aplikasi.

**Cara pakai.** Tekan **Jalankan tes**. Hasilnya berupa jumlah LULUS, GAGAL, dan MANUAL, beserta tabel semua skenario. Hasil normal adalah 22 LULUS dan 1 MANUAL. Centang **lewati tes performa** untuk hasil lebih cepat. Skenario 13 (benchmark 100.000 data) kemudian dilewati, jadi hasilnya 21 LULUS dan 1 MANUAL.

**Alur kode.** `run_test_scenarios()` menjalankan setiap skenario di `TEST_SCENARIOS`. Setiap skenario memakai service baru dengan database `:memory:`, jadi data asli tidak tersentuh. Skenario 15 (akses URL Cloudflare dari perangkat lain) ditandai MANUAL karena harus dicek dengan membuka URL dari HP saat demo.

Skenario yang sama juga dijalankan oleh `python -m pytest` dan `python cli.py test`.

## Menu ke tim

| Menu | Team 1 | Team 2 | Team 3 |
|---|---|---|---|
| Dashboard | | | Pemilik |
| Buat Order | | Pemilik | |
| Antrean & Delivery | | Pemilik | |
| Peta & Rute | | Pemilik | |
| Riwayat & Undo | Bersama | Bersama | Bersama |
| Restoran & Menu | Pemilik | | |
| Cari & Katalog | Pemilik | | Sorting |
| Statistik & Ranking | | | Pemilik |
| Visualisasi Struktur | Bersama | Bersama | Bersama |
| Benchmark | Bersama | Bersama | Bersama |
| Testing | Bersama | Bersama | Bersama |

Setiap anggota tetap harus bisa menjelaskan semua menu, karena nilai Technical Defense bersifat individual (Bagian 15 panduan).
