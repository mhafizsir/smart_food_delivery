"""Struktur data linear: Dynamic Array, Singly Linked List, Stack, Queue (materi UTS).

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


class Node:
    def __init__(self, data, next_node=None):
        self.data = data
        self.next = next_node


class SinglyLinkedList:
    """Daftar order. Ada pointer tail, jadi insert di head maupun tail O(1); search O(n)."""

    def __init__(self):
        self.head = None
        self.tail = None
        self._size = 0

    def __len__(self):
        return self._size

    def __iter__(self):
        return iter(self.to_list())

    def to_list(self):
        result = []
        node = self.head
        while node is not None:
            result.append(node.data)
            node = node.next
        return result

    def is_empty(self):
        return self.head is None

    def insert_front(self, data):
        self.head = Node(data, self.head)
        if self.tail is None:
            self.tail = self.head
        self._size += 1

    def insert_back(self, data):
        node = Node(data)
        if self.tail is None:
            self.head = node
            self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self._size += 1

    def search(self, predicate):
        node = self.head
        while node is not None:
            if predicate(node.data):
                return node.data
            node = node.next
        return None

    def find_all(self, predicate):
        return [data for data in self if predicate(data)]

    def remove_front(self):  # hapus node head, O(1)
        if self.head is None:
            return None
        data = self.head.data
        self.head = self.head.next
        if self.head is None:
            self.tail = None
        self._size -= 1
        return data

    def remove(self, predicate):  # hapus node pertama yang cocok, O(n)
        previous = None
        node = self.head
        while node is not None and not predicate(node.data):
            previous = node
            node = node.next
        if node is None:
            return None
        if previous is None:
            self.head = node.next
        else:
            previous.next = node.next
        if node is self.tail:
            self.tail = previous
        self._size -= 1
        return node.data

    def clear(self):
        self.head = None
        self.tail = None
        self._size = 0


class Stack:
    """LIFO. push/pop/peek O(1) di ujung list penyimpan."""

    def __init__(self):
        self._items = []

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return iter(self.to_list())

    def to_list(self):  # dari atas (terbaru) ke bawah
        result = []
        for i in range(len(self._items) - 1, -1, -1):
            result.append(self._items[i])
        return result

    def is_empty(self):
        return not self._items

    def push(self, item):
        self._items.append(item)

    def pop(self):
        if not self._items:
            return None
        return self._items.pop()

    def peek(self):
        if not self._items:
            return None
        return self._items[-1]

    def clear(self):
        self._items = []


class LinkedQueue:
    """FIFO berbasis node: enqueue di rear dan dequeue di front, keduanya O(1).
    (Versi UTS memakai list.pop(0) yang O(n) karena semua elemen bergeser.)"""

    def __init__(self):
        self._items = SinglyLinkedList()

    def __len__(self):
        return len(self._items)

    def __iter__(self):  # front ke rear
        return iter(self._items)

    def is_empty(self):
        return self._items.is_empty()

    def enqueue(self, item):
        self._items.insert_back(item)

    def dequeue(self):
        if self._items.is_empty():
            return None
        return self._items.remove_front()

    def peek(self):
        if self._items.is_empty():
            return None
        return self._items.head.data

    def remove(self, item):  # dipakai cancel order; mengembalikan posisi lama, O(n)
        for position, current in enumerate(self._items):
            if current is item:
                self._items.remove(lambda data: data is item)
                return position
        return -1

    def insert_at(self, position, item):  # dipakai undo untuk mengembalikan order ke posisinya, O(n)
        items = SinglyLinkedList()
        for index, current in enumerate(self._items):
            if index == position:
                items.insert_back(item)
            items.insert_back(current)
        if len(items) == len(self._items):
            items.insert_back(item)
        self._items = items

    def clear(self):
        self._items.clear()
