"""Singly Linked List untuk daftar order (materi UTS)."""


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
