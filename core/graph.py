"""Graph peta lokasi dan rute pengiriman: Dijkstra, BFS, DFS (Team 2)."""
import math

from core.heap import MinHeap
from core.linear import LinkedQueue


def haversine_km(a, b):
    lat1 = math.radians(a[0])
    lon1 = math.radians(a[1])
    lat2 = math.radians(b[0])
    lon2 = math.radians(b[1])
    delta_lat = math.sin((lat2 - lat1) / 2) ** 2
    delta_lon = math.sin((lon2 - lon1) / 2) ** 2
    h = delta_lat + math.cos(lat1) * math.cos(lat2) * delta_lon
    return 2 * 6371 * math.asin(math.sqrt(h))


class Graph:
    """Graph tidak berarah berbobot dengan adjacency list: nama lokasi -> list edge.
    dict dipakai sebagai penyimpan dasar adjacency list (diizinkan Bagian 3); Hash Table yang dinilai
    ada di fitur pencarian ID. Adjacency list dipilih karena peta jalan graph renggang: memori O(V + E),
    bukan O(V^2) seperti adjacency matrix."""

    def __init__(self):
        self.adjacency = {}
        self.coords = {}  # nama -> (lat, lon)
        self.kinds = {}   # nama -> RESTAURANT / CUSTOMER / HUB

    def __len__(self):
        return len(self.adjacency)

    def nodes(self):
        return list(self.adjacency)

    def add_node(self, name, lat=None, lon=None, kind="HUB"):
        if name not in self.adjacency:
            self.adjacency[name] = []
        if lat is not None and lon is not None:
            self.coords[name] = (float(lat), float(lon))
        self.kinds[name] = kind

    def find(self, text):  # nama lokasi dicocokkan tanpa beda huruf besar/kecil
        key = str(text).strip().casefold()
        for name in self.adjacency:
            if name.casefold() == key:
                return name
        return None

    def has_edge(self, a, b):
        for edge in self.adjacency.get(a, []):
            if edge["to"] == b:
                return True
        return False

    def add_edge(self, a, b, distance, minutes):
        self.adjacency[a].append({"to": b, "distance": distance, "minutes": minutes})
        self.adjacency[b].append({"to": a, "distance": distance, "minutes": minutes})

    def edges(self):  # tiap jalan tersimpan dua kali (tidak berarah), ambil satu arah saja
        seen = set()
        result = []
        for a, edges in self.adjacency.items():
            for edge in edges:
                if (edge["to"], a) not in seen:  # jalan a-b sudah dicatat dari arah b-a
                    seen.add((a, edge["to"]))
                    result.append((a, edge["to"], edge["distance"], edge["minutes"]))
        return result

    def clear(self):
        self.adjacency = {}
        self.coords = {}
        self.kinds = {}

    def dijkstra(self, start, end):
        """Rute jarak terpendek memakai MinHeap buatan sendiri. O((V + E) log V).
        Hasil: (path, total_km, total_menit) atau None kalau tidak terhubung."""
        if start not in self.adjacency or end not in self.adjacency:
            return None
        best = {start: 0.0}
        previous = {}
        heap = MinHeap(key=lambda entry: entry[0])
        heap.push((0.0, start))
        visited = set()
        while not heap.is_empty():
            distance, node = heap.pop()
            if node in visited:
                continue  # entri lama yang jaraknya sudah diperbaiki
            visited.add(node)
            if node == end:
                break
            for edge in self.adjacency[node]:
                candidate = distance + edge["distance"]
                if candidate < best.get(edge["to"], math.inf):
                    best[edge["to"]] = candidate
                    previous[edge["to"]] = (node, edge["minutes"])
                    heap.push((candidate, edge["to"]))
        if end not in visited:
            return None
        path, minutes, node = [end], 0.0, end
        while node != start:
            node, edge_minutes = previous[node]
            minutes += edge_minutes
            path.append(node)
        path.reverse()
        return path, round(best[end], 2), round(minutes, 1)

    def bfs(self, start):
        """Breadth-First Search: lokasi diurutkan per jumlah transit dari start. O(V + E).
        Hasil: list (lokasi, jumlah_hop)."""
        if start not in self.adjacency:
            return []
        queue = LinkedQueue()
        queue.enqueue(start)
        hops = {start: 0}
        order = []
        while not queue.is_empty():
            node = queue.dequeue()
            order.append((node, hops[node]))
            for edge in self.adjacency[node]:
                if edge["to"] not in hops:
                    hops[edge["to"]] = hops[node] + 1
                    queue.enqueue(edge["to"])
        return order

    def bfs_path(self, start, end):  # rute dengan transit paling sedikit (bukan jarak terpendek)
        if start not in self.adjacency or end not in self.adjacency:
            return None
        queue = LinkedQueue()
        queue.enqueue(start)
        previous = {start: None}
        while not queue.is_empty():
            node = queue.dequeue()
            if node == end:
                path = []
                while node is not None:
                    path.append(node)
                    node = previous[node]
                path.reverse()
                return path
            for edge in self.adjacency[node]:
                if edge["to"] not in previous:
                    previous[edge["to"]] = node
                    queue.enqueue(edge["to"])
        return None

    def dfs(self, start):
        """Depth-First Search rekursif: semua lokasi yang terhubung dengan start, urut kunjungan. O(V + E).
        Kedalaman rekursi bisa sampai V, jadi graph sangat besar bisa melewati batas rekursi Python."""
        if start not in self.adjacency:
            return []
        order = []
        self._dfs(start, set(), order)
        return order

    def _dfs(self, node, seen, order):
        seen.add(node)
        order.append(node)
        for edge in self.adjacency[node]:  # base case: semua tetangga sudah dikunjungi
            if edge["to"] not in seen:
                self._dfs(edge["to"], seen, order)  # recursive case

    def is_connected(self, a, b):
        return b in self.dfs(a)
