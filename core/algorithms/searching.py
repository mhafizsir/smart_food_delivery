"""Linear search dan binary search (Team 1)."""


def linear_search(items, target, key=lambda item: item):
    """O(n). Data tidak perlu terurut. Hasil: index atau -1."""
    for index, item in enumerate(items):
        if key(item) == target:
            return index
    return -1


def binary_search(sorted_items, target, key=lambda item: item):
    """O(log n). Data wajib sudah terurut menurut key. Hasil: index atau -1."""
    low = 0
    high = len(sorted_items) - 1
    while low <= high:
        middle = (low + high) // 2
        middle_key = key(sorted_items[middle])
        if middle_key == target:
            return middle
        if middle_key < target:
            low = middle + 1
        else:
            high = middle - 1
    return -1


def binary_search_first(sorted_items, target, key=lambda item: item):
    """O(log n). Index item pertama yang key-nya >= target (lower bound). Data wajib sudah terurut.
    Dipakai untuk mencari awalan nama: semua nama yang diawali target letaknya berurutan mulai index ini."""
    low = 0
    high = len(sorted_items)
    while low < high:
        middle = (low + high) // 2
        if key(sorted_items[middle]) < target:
            low = middle + 1
        else:
            high = middle
    return low
