"""Min-Heap untuk antrean prioritas order (Team 2)."""


class MinHeap:
    """Binary min-heap berbasis array: key terkecil selalu di index 0.
    Anak index i ada di 2i+1 dan 2i+2, parent di (i-1)//2. push/pop O(log n), peek O(1)."""

    def __init__(self, key=lambda item: item):
        self._key = key
        self._data = []

    def __len__(self):
        return len(self._data)

    def is_empty(self):
        return not self._data

    def key_of(self, item):
        return self._key(item)

    def _less(self, i, j):
        return self._key(self._data[i]) < self._key(self._data[j])

    def _swap(self, i, j):
        self._data[i], self._data[j] = self._data[j], self._data[i]

    def _sift_up(self, i):  # heapify ke atas setelah insert
        while i > 0:
            parent = (i - 1) // 2
            if not self._less(i, parent):
                break
            self._swap(i, parent)
            i = parent

    def _sift_down(self, i):  # heapify ke bawah setelah extract
        n = len(self._data)
        while True:
            smallest = i
            for child in (2 * i + 1, 2 * i + 2):
                if child < n and self._less(child, smallest):
                    smallest = child
            if smallest == i:
                return
            self._swap(i, smallest)
            i = smallest

    def push(self, item):
        self._data.append(item)
        self._sift_up(len(self._data) - 1)

    def peek(self):
        if not self._data:
            return None
        return self._data[0]

    def pop(self):
        if not self._data:
            return None
        return self._pop_at(0)

    def _pop_at(self, index):
        last = self._data.pop()
        if index == len(self._data):
            return last
        item = self._data[index]
        self._data[index] = last
        self._sift_down(index)
        self._sift_up(index)
        return item

    def remove(self, item):  # cari O(n), perbaiki heap O(log n); dipakai cancel order
        for index, current in enumerate(self._data):
            if current is item:
                return self._pop_at(index)
        return None

    def clear(self):
        self._data = []

    def as_array(self):  # isi array internal apa adanya, untuk visualisasi
        return list(self._data)

    def in_order(self):  # urutan keluar, tanpa mengubah heap asli: O(n log n)
        copy = MinHeap(self._key)
        copy._data = list(self._data)
        result = []
        while not copy.is_empty():
            result.append(copy.pop())
        return result

    def is_valid(self):
        for i in range(1, len(self._data)):
            parent = (i - 1) // 2
            if self._less(i, parent):
                return False
        return True
