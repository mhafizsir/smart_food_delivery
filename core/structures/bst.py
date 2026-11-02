"""Binary Search Tree untuk katalog menu berdasarkan harga (Team 1)."""


class BSTNode:
    def __init__(self, key, item):
        self.key = key
        self.items = [item]  # semua data dengan key sama (misalnya menu berharga sama) ada di satu node
        self.left = None
        self.right = None


class BST:
    """Binary Search Tree. Untuk katalog menu, key = harga. insert/delete/search rata-rata O(log n),
    terburuk O(n) kalau tree miring (data dimasukkan dalam keadaan sudah terurut).
    insert dan delete iteratif; traversal, range search, dan height rekursif (kedalaman = tinggi tree)."""

    def __init__(self, key=lambda item: item):
        self._key = key
        self.root = None
        self._size = 0
        self._nodes = 0

    def __len__(self):
        return self._size

    @property
    def node_count(self):
        return self._nodes

    def insert(self, item):
        key = self._key(item)
        parent = None
        node = self.root
        while node is not None:
            if key == node.key:
                node.items.append(item)
                self._size += 1
                return
            parent = node
            if key < node.key:
                node = node.left
            else:
                node = node.right
        new_node = BSTNode(key, item)
        if parent is None:
            self.root = new_node
        elif key < parent.key:
            parent.left = new_node
        else:
            parent.right = new_node
        self._size += 1
        self._nodes += 1

    def search(self, key):
        node = self.root
        while node is not None and node.key != key:
            if key < node.key:
                node = node.left
            else:
                node = node.right
        if node is None:
            return []
        return list(node.items)

    def delete(self, item, key=None):
        # key boleh diberikan kalau key item sudah berubah (misalnya harga menu baru saja diubah)
        if key is None:
            key = self._key(item)
        parent = None
        node = self.root
        while node is not None and node.key != key:
            parent = node
            if key < node.key:
                node = node.left
            else:
                node = node.right
        if node is None:
            return False
        found = False
        for current in node.items:
            if current is item:
                found = True
        if not found:
            return False
        node.items = [current for current in node.items if current is not item]
        self._size -= 1
        if node.items:
            return True
        if node.left is not None and node.right is not None:
            # Dua anak: salin node terkecil di subtree kanan (successor), lalu hapus node successor
            parent = node
            successor = node.right
            while successor.left is not None:
                parent = successor
                successor = successor.left
            node.key = successor.key
            node.items = successor.items
            node = successor
        if node.left is not None:
            child = node.left
        else:
            child = node.right
        if parent is None:
            self.root = child
        elif parent.left is node:
            parent.left = child
        else:
            parent.right = child
        self._nodes -= 1
        return True

    def traverse(self, order="inorder"):
        result = []
        self._walk(self.root, order, result)
        return result

    def _walk(self, node, order, result):
        if node is None:  # base case: subtree kosong
            return
        if order == "preorder":
            result.extend(node.items)
        self._walk(node.left, order, result)  # recursive case: subtree kiri, lalu kanan
        if order == "inorder":
            result.extend(node.items)
        self._walk(node.right, order, result)
        if order == "postorder":
            result.extend(node.items)

    def search_range(self, low, high):  # O(h + k): subtree di luar rentang tidak dikunjungi
        result = []
        self._range(self.root, low, high, result)
        return result

    def _range(self, node, low, high, result):
        if node is None:
            return
        if node.key > low:
            self._range(node.left, low, high, result)
        if node.key >= low and node.key <= high:
            result.extend(node.items)
        if node.key < high:
            self._range(node.right, low, high, result)

    def height(self):
        return self._height(self.root)

    def _height(self, node):
        if node is None:
            return 0
        return 1 + max(self._height(node.left), self._height(node.right))
