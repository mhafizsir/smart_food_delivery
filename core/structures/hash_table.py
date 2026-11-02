"""Hash Table untuk pencarian ID restoran dan menu (Team 1)."""


class HashTable:
    """Hash Table dengan separate chaining: tiap bucket berisi list pasangan [key, value].
    Load factor = jumlah data / jumlah bucket. Di atas MAX_LOAD_FACTOR jumlah bucket digandakan (rehash).
    search/insert/delete rata-rata O(1), terburuk O(n) kalau semua key jatuh di satu bucket."""

    MAX_LOAD_FACTOR = 0.75

    def __init__(self, capacity=8):
        self._buckets = [[] for _ in range(capacity)]
        self._size = 0

    def __len__(self):
        return self._size

    def __contains__(self, key):
        return self.search(key) is not None

    @property
    def capacity(self):
        return len(self._buckets)

    def bucket_index(self, key):
        # Polynomial rolling hash buatan sendiri. hash() bawaan Python untuk str berubah setiap
        # proses, jadi posisi bucket di tes dan di app bisa berbeda.
        code = 0
        for char in str(key):
            code = (code * 31 + ord(char)) % 1_000_000_007
        return code % len(self._buckets)

    def load_factor(self):
        return self._size / len(self._buckets)

    def insert(self, key, value):
        bucket = self._buckets[self.bucket_index(key)]
        for pair in bucket:
            if pair[0] == key:
                pair[1] = value
                return
        bucket.append([key, value])
        self._size += 1
        if self.load_factor() > self.MAX_LOAD_FACTOR:
            self._resize(2 * len(self._buckets))

    def search(self, key):
        for stored, value in self._buckets[self.bucket_index(key)]:
            if stored == key:
                return value
        return None

    def delete(self, key):
        bucket = self._buckets[self.bucket_index(key)]
        for i, (stored, value) in enumerate(bucket):
            if stored == key:
                bucket.pop(i)
                self._size -= 1
                return value
        return None

    def _resize(self, capacity):  # O(n), jarang terjadi, jadi insert tetap O(1) amortized
        pairs = []
        for bucket in self._buckets:
            for pair in bucket:
                pairs.append(pair)
        self._buckets = [[] for _ in range(capacity)]
        for pair in pairs:
            self._buckets[self.bucket_index(pair[0])].append(pair)

    def clear(self):
        self._buckets = [[] for _ in range(8)]
        self._size = 0

    def buckets(self):  # key di tiap bucket, untuk visualisasi
        result = []
        for bucket in self._buckets:
            keys = []
            for pair in bucket:
                keys.append(pair[0])
            result.append(keys)
        return result

    def collisions(self):
        total = 0
        for bucket in self._buckets:
            if len(bucket) > 1:
                total += len(bucket) - 1
        return total

    def longest_chain(self):
        longest = 0
        for bucket in self._buckets:
            if len(bucket) > longest:
                longest = len(bucket)
        return longest
