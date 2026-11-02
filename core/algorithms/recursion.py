"""Statistik rekursif divide and conquer untuk dashboard (Team 3)."""


def recursive_sum(items, value, low=0, high=None):
    """Jumlahkan value(item) secara rekursif divide and conquer.
    Base case: rentang kosong (0) atau satu elemen. Recursive case: jumlah paruh kiri + paruh kanan.
    Kedalaman call stack O(log n), jadi 100.000 order tetap aman dari batas rekursi Python (1000).
    Versi UTS maju satu index per panggilan (kedalaman O(n)); membagi dua rentang membuatnya aman untuk data besar."""
    if high is None:
        high = len(items)
    if high - low == 0:
        return 0
    if high - low == 1:
        return value(items[low])
    middle = (low + high) // 2
    return recursive_sum(items, value, low, middle) + recursive_sum(items, value, middle, high)


def recursive_group(items, group, amount, low=0, high=None):
    """Seperti recursive_sum, tetapi per kelompok: hasil dict kelompok -> total."""
    if high is None:
        high = len(items)
    if high - low == 0:
        return {}
    if high - low == 1:
        name = group(items[low])
        if name is None:  # item tanpa kelompok tidak dihitung
            return {}
        return {name: amount(items[low])}
    middle = (low + high) // 2
    left = recursive_group(items, group, amount, low, middle)
    for name, total in recursive_group(items, group, amount, middle, high).items():
        left[name] = left.get(name, 0) + total
    return left
