"""Sorting untuk ranking: insertion sort O(n^2) dan merge sort O(n log n) (Team 3)."""


def insertion_sort(items, key=lambda item: item):
    """O(n^2) rata-rata dan terburuk, O(n) kalau data sudah terurut. Stabil, in-place pada salinan."""
    result = list(items)
    for i in range(1, len(result)):
        current = result[i]
        current_key = key(current)
        j = i - 1
        while j >= 0 and key(result[j]) > current_key:
            result[j + 1] = result[j]
            j -= 1
        result[j + 1] = current
    return result


def merge_sort(items, key=lambda item: item):
    """O(n log n) di semua kasus, memori tambahan O(n). Stabil. Rekursif dengan kedalaman O(log n)."""
    items = list(items)
    if len(items) <= 1:  # base case
        return items
    middle = len(items) // 2
    left = merge_sort(items[:middle], key)  # recursive case: urutkan dua paruh
    right = merge_sort(items[middle:], key)
    merged = []
    i = 0
    j = 0
    while i < len(left) and j < len(right):
        if key(right[j]) < key(left[i]):
            merged.append(right[j])
            j += 1
        else:
            merged.append(left[i])
            i += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged
