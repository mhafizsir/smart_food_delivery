"""Benchmark n = 1.000, 10.000, 100.000 (Bagian 8 panduan)."""
import random
import time

from core.bst import BST
from core.hash_table import HashTable
from core.heap import MinHeap
from core.linear import DynamicArray
from core.searching import binary_search, linear_search
from core.sorting import insertion_sort, merge_sort


BENCHMARK_SIZES = (1_000, 10_000, 100_000)
QUADRATIC_LIMIT = 10_000  # O(n^2) di atas ini terlalu lama untuk demo; waktunya diestimasi dari n^2
SEARCH_QUERIES = 200


def time_call(function, data):
    """Waktu (detik) untuk menjalankan function(data) satu kali."""
    start = time.perf_counter()
    function(data)
    return time.perf_counter() - start


def record(rows, operation, structure, complexity, n, seconds, note="diukur"):
    milliseconds = float(f"{seconds * 1000:.3g}")  # dibulatkan ke 3 angka penting
    rows.append({"Operasi": operation, "Struktur": structure, "Kompleksitas": complexity, "n": n,
                 "Waktu (ms)": milliseconds, "Keterangan": note})


def record_quadratic(rows, measured, operation, structure, values, run):
    """Catat satu baris O(n^2). Di atas QUADRATIC_LIMIT waktunya diestimasi dari hasil ukur n=QUADRATIC_LIMIT."""
    n = len(values)
    if n <= QUADRATIC_LIMIT:
        seconds = time_call(run, values)
        measured[operation] = (n, seconds)
        record(rows, operation, structure, "O(n^2)", n, seconds)
        return
    if operation not in measured:
        measured[operation] = (QUADRATIC_LIMIT, time_call(run, values[:QUADRATIC_LIMIT]))
    base_n, base_seconds = measured[operation]
    estimate = base_seconds * (n / base_n) ** 2
    record(rows, operation, structure, "O(n^2)", n, estimate, f"estimasi n^2 dari n={base_n:,}")


def heap_queue(data):
    heap = MinHeap()
    for value in data:
        heap.push(value)
    while not heap.is_empty():
        heap.pop()


def uts_list_queue(data):  # cara UTS: append lalu sort ulang setiap enqueue, dequeue pop(0)
    queue = []
    for value in data:
        queue.append(value)
        queue.sort()
    while queue:
        queue.pop(0)


def sorted_bst(data):  # kasus terburuk: data masuk terurut, tree jadi rantai setinggi n
    skewed = BST()
    for value in merge_sort(data):
        skewed.insert(value)


def benchmark(sizes=BENCHMARK_SIZES, seed=42):
    """Hasil: list baris {Operasi, Struktur, Kompleksitas, n, Waktu (ms), Keterangan}."""
    rng = random.Random(seed)
    rows = []
    measured = {}

    for n in sizes:
        values = [rng.randint(0, 10 * n) for _ in range(n)]
        keys = [f"M{i}" for i in range(n)]
        targets = [keys[rng.randrange(n)] for _ in range(SEARCH_QUERIES)]

        array = DynamicArray()
        table = HashTable()
        for key in keys:
            array.append(key)
            table.insert(key, key)

        start = time.perf_counter()
        for target in targets:
            table.search(target)
        seconds = time.perf_counter() - start
        record(rows, "Cari ID (per query)", "Hash Table", "O(1)", n, seconds / SEARCH_QUERIES)

        start = time.perf_counter()
        for target in targets:
            array.index_of(lambda key: key == target)
        seconds = time.perf_counter() - start
        record(rows, "Cari ID (per query)", "Dynamic Array + linear search", "O(n)", n, seconds / SEARCH_QUERIES)

        sorted_values = merge_sort(values)
        value_targets = [values[rng.randrange(n)] for _ in range(SEARCH_QUERIES)]

        start = time.perf_counter()
        for target in value_targets:
            binary_search(sorted_values, target)
        seconds = time.perf_counter() - start
        record(rows, "Cari nilai (per query)", "Binary search (data terurut)", "O(log n)", n,
               seconds / SEARCH_QUERIES)

        start = time.perf_counter()
        for target in value_targets:
            linear_search(values, target)
        seconds = time.perf_counter() - start
        record(rows, "Cari nilai (per query)", "Linear search", "O(n)", n, seconds / SEARCH_QUERIES)

        seconds = time_call(merge_sort, values)
        record(rows, "Sorting n data", "Merge sort", "O(n log n)", n, seconds)
        record_quadratic(rows, measured, "Sorting n data", "Insertion sort", values, insertion_sort)

        seconds = time_call(heap_queue, values)
        record(rows, "Antrean prioritas: n insert + n extract", "Min-Heap", "O(n log n)", n, seconds)
        record_quadratic(rows, measured, "Antrean prioritas: n insert + n extract",
                         "List + sort ulang (cara UTS)", values, uts_list_queue)

        tree = BST()
        start = time.perf_counter()
        for value in values:
            tree.insert(value)
        seconds = time.perf_counter() - start
        record(rows, "Bangun katalog n data", "BST (data acak)", "O(n log n)", n, seconds)
        record_quadratic(rows, measured, "Bangun katalog n data", "BST (data terurut, tree miring)",
                         values, sorted_bst)

        start = time.perf_counter()
        tree.search_range(5 * n, 5 * n + n // 10)
        seconds = time.perf_counter() - start
        record(rows, "Cari rentang 1% data", "BST search_range", "O(log n + k)", n, seconds)
    return rows
