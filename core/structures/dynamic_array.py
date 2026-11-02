"""Dynamic Array untuk daftar restoran dan menu (materi UTS).

List bawaan Python hanya dipakai sebagai penyimpan dasar (blok memori), sesuai Bagian 3 panduan."""


class DynamicArray:
    """Array berkapasitas tetap yang digandakan saat penuh.
    append O(1) amortized, akses index O(1), hapus di tengah O(n) karena elemen digeser."""

    def __init__(self, capacity=4):
        self._capacity = capacity
        self._data = [None] * capacity
        self._size = 0

    def __len__(self):
        return self._size

    def __iter__(self):
        return iter(self.to_list())

    def __getitem__(self, index):
        if index < 0 or index >= self._size:
            raise IndexError("index di luar jangkauan")
        return self._data[index]

    @property
    def capacity(self):
        return self._capacity

    def slot(self, index):
        # Isi slot mentah, termasuk slot kosong (None) di atas len(). Dipakai halaman visualisasi.
        return self._data[index]

    def append(self, item):
        if self._size == self._capacity:
            self._resize(2 * self._capacity)
        self._data[self._size] = item
        self._size += 1

    def _resize(self, capacity):
        data = [None] * capacity
        for i in range(self._size):
            data[i] = self._data[i]
        self._data = data
        self._capacity = capacity

    def index_of(self, predicate):  # linear search O(n)
        for i in range(self._size):
            if predicate(self._data[i]):
                return i
        return -1

    def find(self, predicate):
        index = self.index_of(predicate)
        if index < 0:
            return None
        return self._data[index]

    def remove_at(self, index):
        item = self[index]
        for i in range(index, self._size - 1):
            self._data[i] = self._data[i + 1]
        self._size -= 1
        self._data[self._size] = None
        return item

    def remove_where(self, predicate):  # satu kali jalan, O(n)
        kept = 0
        for i in range(self._size):
            if not predicate(self._data[i]):
                self._data[kept] = self._data[i]
                kept += 1
        removed = self._size - kept
        for i in range(kept, self._size):
            self._data[i] = None
        self._size = kept
        return removed

    def clear(self):
        self._data = [None] * self._capacity
        self._size = 0

    def to_list(self):
        result = []
        for i in range(self._size):
            result.append(self._data[i])
        return result
