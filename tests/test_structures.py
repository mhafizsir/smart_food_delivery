"""Tes unit untuk setiap struktur data dan algoritma di core, tanpa service dan database."""
import pytest

from core.bst import BST
from core.graph import Graph
from core.hash_table import HashTable
from core.heap import MinHeap
from core.linear import DynamicArray, LinkedQueue, SinglyLinkedList, Stack
from core.recursion import recursive_group, recursive_sum
from core.searching import binary_search, linear_search
from core.sorting import insertion_sort, merge_sort


class Item:
    def __init__(self, name, price):
        self.name = name
        self.price = price


def test_dynamic_array_doubles_capacity_when_full():
    array = DynamicArray(capacity=4)
    for value in [10, 20, 30, 40, 50]:
        array.append(value)
    assert len(array) == 5
    assert array.capacity == 8
    assert array.to_list() == [10, 20, 30, 40, 50]
    assert array[4] == 50
    assert array.slot(5) is None


def test_dynamic_array_remove_shifts_items_left():
    array = DynamicArray()
    for value in [10, 20, 30, 40]:
        array.append(value)
    assert array.remove_at(1) == 20
    assert array.to_list() == [10, 30, 40]
    assert array.remove_where(lambda value: value > 20) == 2
    assert array.to_list() == [10]


def test_dynamic_array_search():
    array = DynamicArray()
    for value in [10, 20, 30]:
        array.append(value)
    assert array.index_of(lambda value: value == 30) == 2
    assert array.index_of(lambda value: value == 99) == -1
    assert array.find(lambda value: value > 15) == 20
    assert array.find(lambda value: value > 99) is None


def test_dynamic_array_rejects_index_outside_size():
    array = DynamicArray()
    array.append(10)
    with pytest.raises(IndexError):
        array[1]


def test_linked_list_insert_front_and_back():
    items = SinglyLinkedList()
    items.insert_back("B")
    items.insert_front("A")
    items.insert_back("C")
    assert items.to_list() == ["A", "B", "C"]
    assert len(items) == 3
    assert items.search(lambda value: value == "B") == "B"
    assert items.find_all(lambda value: value != "B") == ["A", "C"]


def test_linked_list_remove_keeps_tail_correct():
    items = SinglyLinkedList()
    for value in ["A", "B", "C"]:
        items.insert_back(value)
    assert items.remove(lambda value: value == "C") == "C"
    items.insert_back("D")
    assert items.to_list() == ["A", "B", "D"]
    assert items.remove_front() == "A"
    assert items.remove(lambda value: value == "Z") is None
    assert items.to_list() == ["B", "D"]


def test_stack_is_last_in_first_out():
    stack = Stack()
    for value in [1, 2, 3]:
        stack.push(value)
    assert stack.to_list() == [3, 2, 1]
    assert stack.pop() == 3
    assert stack.peek() == 2
    assert stack.pop() == 2
    assert stack.pop() == 1
    assert stack.pop() is None
    assert stack.is_empty()


def test_queue_is_first_in_first_out():
    queue = LinkedQueue()
    for value in ["A", "B", "C"]:
        queue.enqueue(value)
    assert queue.peek() == "A"
    assert queue.dequeue() == "A"
    assert queue.dequeue() == "B"
    assert list(queue) == ["C"]
    assert queue.dequeue() == "C"
    assert queue.dequeue() is None


def test_queue_remove_and_insert_back_at_same_position():
    queue = LinkedQueue()
    items = [Item("A", 1), Item("B", 2), Item("C", 3)]
    for item in items:
        queue.enqueue(item)
    position = queue.remove(items[1])
    assert position == 1
    assert [item.name for item in queue] == ["A", "C"]
    queue.insert_at(position, items[1])
    assert [item.name for item in queue] == ["A", "B", "C"]
    assert queue.remove(Item("X", 0)) == -1


def test_min_heap_pops_smallest_first():
    heap = MinHeap()
    for value in [5, 3, 8, 1, 9, 2]:
        heap.push(value)
    assert heap.peek() == 1
    assert heap.in_order() == [1, 2, 3, 5, 8, 9]
    assert len(heap) == 6
    popped = []
    while not heap.is_empty():
        popped.append(heap.pop())
    assert popped == [1, 2, 3, 5, 8, 9]
    assert heap.pop() is None


def test_min_heap_uses_key_and_stays_valid_after_remove():
    heap = MinHeap(key=lambda item: item.price)
    items = [Item("Kopi", 18000), Item("Teh", 5000), Item("Sate", 30000), Item("Soto", 22000)]
    for item in items:
        heap.push(item)
    assert heap.remove(items[1]).name == "Teh"
    assert heap.is_valid()
    assert [item.name for item in heap.in_order()] == ["Kopi", "Soto", "Sate"]


def test_hash_table_insert_search_update_delete():
    table = HashTable()
    table.insert("R1", "Warung Nusantara")
    table.insert("R2", "Kopi Senja")
    table.insert("R1", "Warung Baru")
    assert len(table) == 2
    assert table.search("R1") == "Warung Baru"
    assert "R2" in table
    assert table.delete("R2") == "Kopi Senja"
    assert "R2" not in table
    assert table.delete("R2") is None


def test_hash_table_keeps_both_keys_on_collision():
    table = HashTable(capacity=8)
    table.insert("a", 1)  # ord("a") = 97, 97 % 8 = 1
    table.insert("i", 2)  # ord("i") = 105, 105 % 8 = 1
    assert table.buckets()[1] == ["a", "i"]
    assert table.collisions() == 1
    assert table.longest_chain() == 2
    assert table.search("a") == 1
    assert table.search("i") == 2


def test_hash_table_doubles_buckets_above_load_factor():
    table = HashTable(capacity=8)
    for number in range(6):
        table.insert(f"K{number}", number)
    assert table.capacity == 8  # 6 / 8 = 0.75, belum lebih dari batas
    table.insert("K6", 6)
    assert table.capacity == 16  # 7 / 8 = 0.875, rehash
    for number in range(7):
        assert table.search(f"K{number}") == number


def build_bst():
    tree = BST()
    for value in [50, 30, 70, 20, 40, 60, 80]:
        tree.insert(value)
    return tree


def test_bst_traversals():
    tree = build_bst()
    assert tree.traverse("inorder") == [20, 30, 40, 50, 60, 70, 80]
    assert tree.traverse("preorder") == [50, 30, 20, 40, 70, 60, 80]
    assert tree.traverse("postorder") == [20, 40, 30, 60, 80, 70, 50]
    assert tree.height() == 3


def test_bst_search_and_range():
    tree = build_bst()
    assert tree.search(40) == [40]
    assert tree.search(45) == []
    assert tree.search_range(30, 60) == [30, 40, 50, 60]


def test_bst_same_key_items_share_one_node():
    tree = BST(key=lambda item: item.price)
    tree.insert(Item("Croissant", 22000))
    tree.insert(Item("Soto Ayam", 22000))
    tree.insert(Item("Kopi Susu", 18000))
    assert len(tree) == 3
    assert tree.node_count == 2
    assert [item.name for item in tree.search(22000)] == ["Croissant", "Soto Ayam"]


def test_bst_delete_node_with_two_children():
    tree = build_bst()
    assert tree.delete(30) is True
    assert tree.traverse("inorder") == [20, 40, 50, 60, 70, 80]
    assert tree.delete(30) is False
    assert tree.delete(50) is True
    assert tree.traverse("inorder") == [20, 40, 60, 70, 80]
    assert tree.root.key == 60


def build_graph():
    graph = Graph()
    for name in ["A", "B", "C", "D"]:
        graph.add_node(name)
    graph.add_edge("A", "B", 1, 2)
    graph.add_edge("B", "C", 1, 2)
    graph.add_edge("A", "C", 5, 10)
    return graph


def test_graph_dijkstra_picks_shortest_distance():
    graph = build_graph()
    assert graph.dijkstra("A", "C") == (["A", "B", "C"], 2.0, 4.0)
    assert graph.dijkstra("A", "D") is None


def test_graph_bfs_counts_hops_and_dfs_visits_in_depth_order():
    graph = build_graph()
    assert graph.bfs("A") == [("A", 0), ("B", 1), ("C", 1)]
    assert graph.bfs_path("A", "C") == ["A", "C"]
    assert graph.dfs("A") == ["A", "B", "C"]
    assert graph.is_connected("A", "C")
    assert not graph.is_connected("A", "D")


def test_graph_counts_each_road_once():
    graph = build_graph()
    assert len(graph) == 4
    assert len(graph.edges()) == 3
    assert graph.has_edge("C", "B")
    assert graph.find("  b ") == "B"


def test_sorting_algorithms_give_same_stable_result():
    items = [Item("Kopi", 18000), Item("Teh", 5000), Item("Croissant", 22000), Item("Soto", 22000)]
    expected = ["Teh", "Kopi", "Croissant", "Soto"]
    assert [item.name for item in insertion_sort(items, key=lambda item: item.price)] == expected
    assert [item.name for item in merge_sort(items, key=lambda item: item.price)] == expected
    assert [item.name for item in items] == ["Kopi", "Teh", "Croissant", "Soto"]
    assert merge_sort([]) == []


def test_linear_and_binary_search():
    numbers = [3, 8, 15, 23, 42]
    assert linear_search([42, 3, 15], 15) == 2
    assert linear_search([42, 3, 15], 7) == -1
    assert binary_search(numbers, 23) == 3
    assert binary_search(numbers, 3) == 0
    assert binary_search(numbers, 7) == -1


def test_recursive_sum_and_group():
    items = [Item("Kopi", 18000), Item("Teh", 5000), Item("Kopi", 20000)]
    assert recursive_sum(items, lambda item: item.price) == 43000
    assert recursive_sum([], lambda item: item.price) == 0
    assert recursive_group(items, lambda item: item.name, lambda item: 1) == {"Kopi": 2, "Teh": 1}


def test_recursive_sum_handles_large_input():
    numbers = list(range(100_000))
    assert recursive_sum(numbers, lambda number: number) == 4_999_950_000
