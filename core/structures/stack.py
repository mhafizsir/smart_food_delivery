"""Stack untuk history order dan undo (materi UTS)."""


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
