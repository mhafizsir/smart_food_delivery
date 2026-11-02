"""Queue FIFO untuk Delivery Queue order NORMAL (materi UTS)."""
from core.structures.linked_list import SinglyLinkedList


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
